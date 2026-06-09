from dataclasses import dataclass


@dataclass
class ProviderChunk:
    delta_text: str = ""
    finish_reason: str = ""
    provider_message_id: str = ""
    error_code: str = ""


class ProviderError(Exception):
    def __init__(self, message, error_code="provider_error"):
        super().__init__(message)
        self.error_code = error_code


class BaseChatProvider:
    def stream_messages(self, messages, *, model_code, system_prompt=""):
        raise NotImplementedError
