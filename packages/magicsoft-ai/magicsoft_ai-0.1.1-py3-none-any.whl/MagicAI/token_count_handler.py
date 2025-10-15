
from langchain.callbacks.base import BaseCallbackHandler
import logging

class TokenCountingCallbackHandler(BaseCallbackHandler):
    """Callback handler to count tokens used during LLM calls."""
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def on_llm_end(self, response, **kwargs):
        """Run when LLM ends running."""

        if hasattr(response,"generations"):
            if response.generations and isinstance(response.generations, list):
                last_generation = response.generations[-1]
                if last_generation and isinstance(last_generation, list):
                    if hasattr(last_generation[-1],"message"):
                        message = last_generation[-1].message
                        if hasattr(message,"usage_metadata"):
                            meta_data = message.usage_metadata
                            self.prompt_tokens += meta_data["input_tokens"]
                            self.completion_tokens += meta_data["output_tokens"]
                            self.total_tokens += meta_data["total_tokens"]
                    elif hasattr(last_generation[-1], "generation_info"):
                        generation_info = last_generation[-1].generation_info
                        if "usage_metadata" in  generation_info:
                            meta_data = generation_info["usage_metadata"]
                            self.prompt_tokens += meta_data["input_tokens"]
                            self.completion_tokens += meta_data["output_tokens"]
                            self.total_tokens += meta_data["total_tokens"]

    def on_llm_error(self, error, **kwargs):
        """Run when LLM errors."""
        logging.debug(f"LLM Error: {error}")

    def get_token_counts(self):
        """Returns the accumulated token counts."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }