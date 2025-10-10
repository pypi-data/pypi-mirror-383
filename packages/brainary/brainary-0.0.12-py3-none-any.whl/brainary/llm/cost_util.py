from langchain.callbacks.openai_info import OpenAICallbackHandler

MODEL_COST_PER_1K_TOKENS = {
    # OpenAI 4.1-nano input
    "gpt-4.1-nano": 0.0001,
    "gpt-4.1-nano-cached": 0.000025,
    # OpenAI 4.1-nano output
    "gpt-4.1-nano-completion": 0.0004,
    # OpenAI 4.1-mini input
    "gpt-4.1-mini": 0.0004,
    "gpt-4.1-mini-cached": 0.0001,
    # OpenAI 4.1-mini output
    "gpt-4.1-mini-completion": 0.0016,
    # OpenAI 4.1 input
    "gpt-4.1": 0.002,
    "gpt-4.1-cached": 0.0005,
    # OpenAI 4.1 output
    "gpt-4.1-completion": 0.008,
    # OpenAI o1 input
    "o1": 0.015,
    "o1-2024-12-17": 0.015,
    "o1-cached": 0.0075,
    "o1-2024-12-17-cached": 0.0075,
    # OpenAI o1 output
    "o1-completion": 0.06,
    "o1-2024-12-17-completion": 0.06,
    # OpenAI o3-mini input
    "o3-mini": 0.0011,
    "o3-mini-2025-01-31": 0.0011,
    "o3-mini-cached": 0.00055,
    "o3-mini-2025-01-31-cached": 0.00055,
    # OpenAI o3-mini output
    "o3-mini-completion": 0.0044,
    "o3-mini-2025-01-31-completion": 0.0044,
    # OpenAI o1-preview input
    "o1-preview": 0.015,
    "o1-preview-cached": 0.0075,
    "o1-preview-2024-09-12": 0.015,
    "o1-preview-2024-09-12-cached": 0.0075,
    # OpenAI o1-preview output
    "o1-preview-completion": 0.06,
    "o1-preview-2024-09-12-completion": 0.06,
    # OpenAI o1-mini input
    "o1-mini": 0.003,
    "o1-mini-cached": 0.0015,
    "o1-mini-2024-09-12": 0.003,
    "o1-mini-2024-09-12-cached": 0.0015,
    # OpenAI o1-mini output
    "o1-mini-completion": 0.012,
    "o1-mini-2024-09-12-completion": 0.012,
    # GPT-4o-mini input
    "gpt-4o-mini": 0.00015,
    "gpt-4o-mini-cached": 0.000075,
    "gpt-4o-mini-2024-07-18": 0.00015,
    "gpt-4o-mini-2024-07-18-cached": 0.000075,
    # GPT-4o-mini output
    "gpt-4o-mini-completion": 0.0006,
    "gpt-4o-mini-2024-07-18-completion": 0.0006,
    # GPT-4o input
    "gpt-4o": 0.0025,
    "gpt-4o-cached": 0.00125,
    "gpt-4o-2024-05-13": 0.005,
    "gpt-4o-2024-08-06": 0.0025,
    "gpt-4o-2024-08-06-cached": 0.00125,
    "gpt-4o-2024-11-20": 0.0025,
    "gpt-4o-2024-11-20-cached": 0.00125,
    # GPT-4o output
    "gpt-4o-completion": 0.01,
    "gpt-4o-2024-05-13-completion": 0.015,
    "gpt-4o-2024-08-06-completion": 0.01,
    "gpt-4o-2024-11-20-completion": 0.01,
    # GPT-4 input
    "gpt-4": 0.03,
    "gpt-4-0314": 0.03,
    "gpt-4-0613": 0.03,
    "gpt-4-32k": 0.06,
    "gpt-4-32k-0314": 0.06,
    "gpt-4-32k-0613": 0.06,
    "gpt-4-vision-preview": 0.01,
    "gpt-4-1106-preview": 0.01,
    "gpt-4-0125-preview": 0.01,
    "gpt-4-turbo-preview": 0.01,
    "gpt-4-turbo": 0.01,
    "gpt-4-turbo-2024-04-09": 0.01,
    # GPT-4 output
    "gpt-4-completion": 0.06,
    "gpt-4-0314-completion": 0.06,
    "gpt-4-0613-completion": 0.06,
    "gpt-4-32k-completion": 0.12,
    "gpt-4-32k-0314-completion": 0.12,
    "gpt-4-32k-0613-completion": 0.12,
    "gpt-4-vision-preview-completion": 0.03,
    "gpt-4-1106-preview-completion": 0.03,
    "gpt-4-0125-preview-completion": 0.03,
    "gpt-4-turbo-preview-completion": 0.03,
    "gpt-4-turbo-completion": 0.03,
    "gpt-4-turbo-2024-04-09-completion": 0.03,
    # GPT-3.5 input
    # gpt-3.5-turbo points at gpt-3.5-turbo-0613 until Feb 16, 2024.
    # Switches to gpt-3.5-turbo-0125 after.
    "gpt-3.5-turbo": 0.0015,
    "gpt-3.5-turbo-0125": 0.0005,
    "gpt-3.5-turbo-0301": 0.0015,
    "gpt-3.5-turbo-0613": 0.0015,
    "gpt-3.5-turbo-1106": 0.001,
    "gpt-3.5-turbo-instruct": 0.0015,
    "gpt-3.5-turbo-16k": 0.003,
    "gpt-3.5-turbo-16k-0613": 0.003,
    # GPT-3.5 output
    # gpt-3.5-turbo points at gpt-3.5-turbo-0613 until Feb 16, 2024.
    # Switches to gpt-3.5-turbo-0125 after.
    "gpt-3.5-turbo-completion": 0.002,
    "gpt-3.5-turbo-0125-completion": 0.0015,
    "gpt-3.5-turbo-0301-completion": 0.002,
    "gpt-3.5-turbo-0613-completion": 0.002,
    "gpt-3.5-turbo-1106-completion": 0.002,
    "gpt-3.5-turbo-instruct-completion": 0.002,
    "gpt-3.5-turbo-16k-completion": 0.004,
    "gpt-3.5-turbo-16k-0613-completion": 0.004,
    # Azure GPT-35 input
    "gpt-35-turbo": 0.0015,  # Azure OpenAI version of ChatGPT
    "gpt-35-turbo-0125": 0.0005,
    "gpt-35-turbo-0301": 0.002,  # Azure OpenAI version of ChatGPT
    "gpt-35-turbo-0613": 0.0015,
    "gpt-35-turbo-instruct": 0.0015,
    "gpt-35-turbo-16k": 0.003,
    "gpt-35-turbo-16k-0613": 0.003,
    # Azure GPT-35 output
    "gpt-35-turbo-completion": 0.002,  # Azure OpenAI version of ChatGPT
    "gpt-35-turbo-0125-completion": 0.0015,
    "gpt-35-turbo-0301-completion": 0.002,  # Azure OpenAI version of ChatGPT
    "gpt-35-turbo-0613-completion": 0.002,
    "gpt-35-turbo-instruct-completion": 0.002,
    "gpt-35-turbo-16k-completion": 0.004,
    "gpt-35-turbo-16k-0613-completion": 0.004,
    # Others
    "text-ada-001": 0.0004,
    "ada": 0.0004,
    "text-babbage-001": 0.0005,
    "babbage": 0.0005,
    "text-curie-001": 0.002,
    "curie": 0.002,
    "text-davinci-003": 0.02,
    "text-davinci-002": 0.02,
    "code-davinci-002": 0.02,
    # Fine Tuned input
    "babbage-002-finetuned": 0.0016,
    "davinci-002-finetuned": 0.012,
    "gpt-3.5-turbo-0613-finetuned": 0.003,
    "gpt-3.5-turbo-1106-finetuned": 0.003,
    "gpt-3.5-turbo-0125-finetuned": 0.003,
    "gpt-4o-mini-2024-07-18-finetuned": 0.0003,
    "gpt-4o-mini-2024-07-18-finetuned-cached": 0.00015,
    # Fine Tuned output
    "babbage-002-finetuned-completion": 0.0016,
    "davinci-002-finetuned-completion": 0.012,
    "gpt-3.5-turbo-0613-finetuned-completion": 0.006,
    "gpt-3.5-turbo-1106-finetuned-completion": 0.006,
    "gpt-3.5-turbo-0125-finetuned-completion": 0.006,
    "gpt-4o-mini-2024-07-18-finetuned-completion": 0.0012,
    # Azure Fine Tuned input
    "babbage-002-azure-finetuned": 0.0004,
    "davinci-002-azure-finetuned": 0.002,
    "gpt-35-turbo-0613-azure-finetuned": 0.0015,
    # Azure Fine Tuned output
    "babbage-002-azure-finetuned-completion": 0.0004,
    "davinci-002-azure-finetuned-completion": 0.002,
    "gpt-35-turbo-0613-azure-finetuned-completion": 0.002,
    # Legacy fine-tuned models
    "ada-finetuned-legacy": 0.0016,
    "babbage-finetuned-legacy": 0.0024,
    "curie-finetuned-legacy": 0.012,
    "davinci-finetuned-legacy": 0.12,
}

def get_openai_cost(model:str, cb: OpenAICallbackHandler):
    if model not in MODEL_COST_PER_1K_TOKENS:
        return 0
    prompt_tokens = cb.prompt_tokens
    prompt_tokens_cached = cb.prompt_tokens_cached
    prompt_tokens_uncached = prompt_tokens - prompt_tokens_cached
    uncached_prompt_cost = MODEL_COST_PER_1K_TOKENS[model] * prompt_tokens_uncached
    cached_prompt_cost = MODEL_COST_PER_1K_TOKENS[f"{model}-cached"] * prompt_tokens_cached
    prompt_cost = uncached_prompt_cost + cached_prompt_cost
    completion_cost = MODEL_COST_PER_1K_TOKENS[f"{model}-completion"] * prompt_tokens_cached
    return (prompt_cost + completion_cost) / 1000