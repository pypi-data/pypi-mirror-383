import logging

from brainary.core.registry import CAPABILITIES

logging.basicConfig(level=logging.INFO)

print(CAPABILITIES["critical_thinking"].list_all())