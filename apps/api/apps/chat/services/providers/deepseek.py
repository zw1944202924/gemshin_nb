import json

from django.conf import settings
import requests

from apps.chat.services.providers.base import BaseChatProvider, ProviderChunk, ProviderError


class DeepSeekChatProvider(BaseChatProvider):
    def stream_messages(self, messages, *, model_code, system_prompt=""):
        if not settings.DEEPSEEK_API_KEY:
            raise ProviderError("DeepSeek API Key 未配置", error_code="provider_not_configured")

        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        response = requests.post(
            f"{settings.DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_code,
                "stream": True,
                "messages": payload_messages,
            },
            stream=True,
            timeout=settings.DEEPSEEK_TIMEOUT_SECONDS,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            try:
                error_payload = response.json()
                message = error_payload.get("error", {}).get("message") or str(exc)
            except ValueError:
                message = str(exc)
            raise ProviderError(message) from exc

        provider_message_id = ""
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line or not raw_line.startswith("data:"):
                continue

            data = raw_line[5:].strip()
            if data == "[DONE]":
                break

            payload = json.loads(data)
            choice = (payload.get("choices") or [{}])[0]
            delta = choice.get("delta") or {}
            provider_message_id = payload.get("id") or provider_message_id
            yield ProviderChunk(
                delta_text=delta.get("content") or "",
                finish_reason=choice.get("finish_reason") or "",
                provider_message_id=provider_message_id,
            )
