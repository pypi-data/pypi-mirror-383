from pathlib import Path
import re
import logging
from typing import List, Optional, Union
import openai
from pydantic import Field
import yaml

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool


from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_openai.chat_models.base import _convert_dict_to_message, _create_usage_metadata
from langchain_core.messages.base import get_msg_title_repr


AUX_MODEL = "gpt-4o-mini"


REASONING_BOS = ""
REASONING_EOS = ""

def load_config():
    with Path("llm.yml").open("r") as f:
        llm_config = yaml.safe_load(f)

    api_key = llm_config.get("api-key", None)
    api_base = llm_config.get("base-url", None)
    return api_base, api_key


def pretty_repr(
        msg: BaseMessage,
        html: bool = False,  # noqa: FBT001,FBT002
    ) -> str:
        """Get a pretty representation of the message.

        Args:
            html: Whether to format the message as HTML. If True, the message will be
                formatted with HTML tags. Default is False.

        Returns:
            A pretty representation of the message.
        """

        title = get_msg_title_repr(msg.type.title() + " Message", bold=html)
        # TODO: handle non-string content.
        if msg.name is not None:
            title += f"\nName: {msg.name}"
        if "reasoning_content" in msg.additional_kwargs and msg.additional_kwargs["reasoning_content"] and msg.additional_kwargs["reasoning_content"] not in msg.content:
            return f"{title}\n\n<think>\n{msg.additional_kwargs['reasoning_content']}\n</think>\n{msg.content}"
        return f"{title}\n\n{msg.content}"
BaseMessage.pretty_repr = pretty_repr


def extract_summary(response:str):
    if "</think>" not in response:
        return response.strip()
    return response.split("</think>")[1].strip()

def clean_response(response:str):
    lines = response.split("\n")
    cleaned_lines = [line for line in lines if not line.strip().startswith("```")]
    return "\n".join(cleaned_lines).strip()

class LLM(ChatOpenAI):
    merge_reasoning: Optional[bool] = Field(default=False)

    def __init__(self, merge_reasoning=False, **kwargs):
        super(ChatOpenAI, self).__init__(**kwargs)
        self.merge_reasoning = merge_reasoning

    @classmethod
    def get_by_name(cls, model="gpt-4o-mini", temperature=1.0, num_pred=16*1024, tools=[], merge_reasoning=False, verbose=True):
        api_base, api_key = load_config()

        llm = cls(merge_reasoning=merge_reasoning, model=model, openai_api_key=api_key, openai_api_base=api_base, temperature=temperature, max_completion_tokens=num_pred, verbose=verbose)
        if len(tools) > 0:
            llm.bind_tools(tools)
        llm.seed = 42
        return llm

    def _create_chat_result(
        self,
        response: Union[dict, openai.BaseModel],
        generation_info: Optional[dict] = None,
    ) -> ChatResult:
        generations = []

        response_dict = (
            response if isinstance(response, dict) else response.model_dump()
        )
        logging.info(response_dict)
        # Sometimes the AI Model calling will get error, we should raise it.
        # Otherwise, the next code 'choices.extend(response["choices"])'
        # will throw a "TypeError: 'NoneType' object is not iterable" error
        # to mask the true error. Because 'response["choices"]' is None.
        if response_dict.get("error"):
            raise ValueError(response_dict.get("error"))

        token_usage = response_dict.get("usage")
        for res in response_dict["choices"]:
            message = _convert_dict_to_message(res["message"])
            if token_usage and isinstance(message, AIMessage):
                message.usage_metadata = _create_usage_metadata(token_usage)
            generation_info = generation_info or {}
            generation_info["finish_reason"] = (
                res.get("finish_reason")
                if res.get("finish_reason") is not None
                else generation_info.get("finish_reason")
            )
            if "logprobs" in res:
                generation_info["logprobs"] = res["logprobs"]
            gen = ChatGeneration(message=message, generation_info=generation_info)
            generations.append(gen)
        llm_output = {
            "token_usage": token_usage,
            "model_name": response_dict.get("model", self.model_name),
            "system_fingerprint": response_dict.get("system_fingerprint", ""),
        }
        if "id" in response_dict:
            llm_output["id"] = response_dict["id"]

        if isinstance(response, openai.BaseModel) and getattr(
            response, "choices", None
        ):
            message = response.choices[0].message  # type: ignore[attr-defined]
            if hasattr(message, "parsed"):
                generations[0].message.additional_kwargs["parsed"] = message.parsed
            if hasattr(message, "refusal"):
                generations[0].message.additional_kwargs["refusal"] = message.refusal

            if hasattr(message, "reasoning_content"):
                generations[0].message.additional_kwargs["reasoning_content"] = message.reasoning_content
            if self.merge_reasoning and hasattr(message, "reasoning_content"):
                generations[0].message.content = f"{REASONING_BOS}\n{message.reasoning_content.lstrip()}{REASONING_EOS}" + (message.content if isinstance(message.content, str) else "")
            elif self.merge_reasoning and isinstance(message.content, str) and "</think>" in message.content:
                thought, summary, _ = message.content.split("</think>")
                thought = thought.replace("<think>", "")
                generations[0].message.content = f"{REASONING_BOS}\n{thought.lstrip()}{REASONING_EOS}" + summary

        return ChatResult(generations=generations, llm_output=llm_output)

    def request(self, messages: Union[str, list, dict], tools=None) -> str:
        """
        Send a request to the LLM with structured message format.
        
        Args:
            messages: Can be:
                - str: Single message treated as user input
                - list: List of message dictionaries or (role, content) tuples
                - dict: Single message dictionary
            tools: Optional list of tools to bind
            
        Returns:
            str: The model's response with any reasoning extracted
        """
        # Convert input to standardized message format
        if isinstance(messages, str):
            # Single string becomes a user message
            structured_messages = [{"role": "user", "content": messages}]
        elif isinstance(messages, dict):
            # Single dict message
            structured_messages = [messages]
        else:
            # List of messages
            structured_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    # Already in dict format
                    structured_messages.append(msg)
                elif isinstance(msg, tuple):
                    # Convert (role, content) tuple
                    role, content = msg
                    role = role.lower()
                    structured_messages.append({"role": role, "content": content})
                else:
                    # Treat as user message
                    structured_messages.append({"role": "user", "content": str(msg)})
        
        # Convert to langchain message objects
        langchain_messages = []
        for msg in structured_messages:
            content = self.escape_format_string(msg["content"])
            if msg["role"] == "system":
                langchain_messages.append(SystemMessage(content))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content))
            else:  # user or human
                langchain_messages.append(HumanMessage(content))
        
        # Handle tools
        if tools is None:
            tools = []
        _llm = self.bind_tools([tool(t) for t in tools]) if tools else self
        
        # Log request details
        logging.info(f"===== INVOKE {self.model_name} =====")
        logging.info(f"##### TOOLS #####\n{tools}")
        logging.info(f"##### MESSAGES #####\n{chr(10).join(msg.pretty_repr() for msg in langchain_messages)}")
        
        # Generate response
        response = _llm.generate([langchain_messages], n=1).generations[0][0]
        logging.info(f"===== RESPONSE =====\n{response.message.pretty_repr()}")
        
        # Extract main content from response
        response = extract_summary(response.message.content)
        return clean_response(response)

    def escape_format_string(self, s):
        # Replace single { not followed by another {
        s = re.sub(r'(?<!{){(?!{)', '{{', s)
        # Replace single } not preceded by another }
        s = re.sub(r'(?<!})}(?!})', '}}', s)
        return s