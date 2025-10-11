import httpx
import json
import os
from typing import Optional, Dict, Any, List, Generator
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions


from . import config

# --- Custom Exceptions ---
class KlaiError(Exception):
    """Base exception for all klai client errors."""
    pass

class ConfigError(KlaiError):
    """Errors related to the configuration file."""
    pass

class NetworkError(KlaiError):
    """Errors related to network connectivity."""
    pass

class APIError(KlaiError):
    """Errors reported by the provider's API."""
    def __init__(self, message, status_code=None, response_text=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

# --- Helper Functions (remain the same) ---
def _get_nested_value(data: Dict, path: str, default=None):
    if not path: return default
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, list) and key.isdigit():
            try:
                current = current[int(key)]
            except IndexError:
                return default
        else:
            return default
    return current if current is not None else default

def _format_messages(messages: List[Dict], style: str) -> Any:
    """Formats the standard message list into provider-specific formats."""
    system_prompt = next((msg['content'] for msg in messages if msg['role'] == 'system'), None)
    
    if style == "openai":
        return messages

    if style == "gemini":
        # The SDK expects a list of 'Content' objects (dicts).
        # The role should be 'user' or 'model'.
        formatted = []
        for msg in messages:
            if msg['role'] == 'system': continue
            role = "model" if msg['role'] == 'assistant' else 'user'
            formatted.append(types.Content(role=role, parts=[types.Part.from_text(msg['content'])]))
        return formatted

    if style == "anthropic":
        # Anthropic requires a different structure and no system message in the main list.
        return [msg for msg in messages if msg['role'] == 'user' or msg['role'] == 'assistant']
    
    if style == "anthropic_system":
        return system_prompt

    raise ValueError(f"Unknown message format style: {style}")

def _build_payload_recursive(template_part: Any, replacements: Dict) -> Any:
    if isinstance(template_part, dict):
        result = {k: new_v for k, v in template_part.items() if (new_v := _build_payload_recursive(v, replacements)) is not None}
        return result if result else None
    if isinstance(template_part, list): return [_build_payload_recursive(i, replacements) for i in template_part]
    if isinstance(template_part, str) and template_part.startswith('{') and template_part.endswith('}'):
        return replacements.get(template_part.strip('{}'))
    return template_part

# --- Main Client Class ---
class AIClient:
    def __init__(self):
        self.full_config = config.get_config()

    def _prepare_request(self, model_handle: str, messages: List[Dict], stream: bool, **kwargs) -> Dict:
        """Prepares the API request parameters (URL, headers, payload)."""
        try:
            provider_name, model_name = model_handle.split('/', 1)
        except ValueError:
            raise ConfigError(f"Invalid model handle: '{model_handle}'. Must be in 'provider/model_name' format.")

        provider_config = self.full_config["providers"].get(provider_name)
        if not provider_config:
            raise ConfigError(f"Provider '{provider_name}' not configured.")

        # This function will now handle non-Google providers
        if provider_name == "google":
            # Google SDK logic is now handled directly in the get_chat_response methods
            return {"provider_name": "google"}

        env_key = f"KLAI_{provider_name.upper()}_API_KEY"
        api_key = os.environ.get(env_key) or provider_config.get("api_key")
        if provider_name != "ollama" and (not api_key or "YOUR_" in api_key):
            raise ConfigError(f"API key for '{provider_name}' is not set.")

        api_url = provider_config["api_url"].format(model=model_name)
        
        headers = {"Content-Type": "application/json", **provider_config.get("headers", {})}
        if auth_header := provider_config.get("auth_header"):
            auth_scheme = provider_config.get("auth_scheme", "")
            headers[auth_header] = f"{auth_scheme} {api_key}".strip()

        replacements = {
            "model": model_name, "stream": stream,
            "messages_openai_format": _format_messages(messages, "openai"),
            "messages_anthropic_format": _format_messages(messages, "anthropic"),
            "system_prompt_anthropic": _format_messages(messages, "anthropic_system"),
            **kwargs
        }
        
        payload = _build_payload_recursive(provider_config["payload_template"], replacements)
        
        return {"provider_name": provider_name, "provider_config": provider_config, "url": api_url, "headers": headers, "json": payload}

    def get_chat_response(self, model_handle: str, messages: List[Dict], **kwargs) -> Dict:
        """Gets a complete, non-streaming chat response."""
        try:
            provider_name, model_name = model_handle.split('/', 1)
        except ValueError:
            raise ConfigError(f"Invalid model handle: '{model_handle}'. Must be in 'provider/model_name' format.")

        # --- Google SDK Integration ---
        if provider_name == "google":
            provider_config = self.full_config["providers"].get(provider_name)
            env_key = "KLAI_GOOGLE_API_KEY"
            api_key = os.environ.get(env_key) or provider_config.get("api_key")
            if not api_key or "YOUR_" in api_key:
                raise ConfigError("API key for 'google' is not set.")

            try:
                client = genai.Client(api_key=api_key)
                system_prompt = next((msg['content'] for msg in messages if msg['role'] == 'system'), None)
                
                gen_config = types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=kwargs.get("temperature"),
                    top_p=kwargs.get("top_p"),
                    top_k=kwargs.get("top_k"),
                    max_output_tokens=kwargs.get("max_tokens"),
                )

                contents = _format_messages(messages, "gemini")
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=gen_config,
                )
                
                usage = {
                    "promptTokenCount": response.usage_metadata.prompt_token_count,
                    "candidatesTokenCount": response.usage_metadata.candidates_token_count
                }
                return {"text": response.text, "usage": usage}
            except google_exceptions.GoogleAPICallError as e:
                raise APIError(f"Google API Error: {e.message}", status_code=e.code) from e
            except Exception as e:
                raise APIError(f"An unexpected error occurred with the Google SDK: {e}")

        # --- Other Providers ---
        request_params = self._prepare_request(model_handle, messages, stream=False, **kwargs)
        provider_config = request_params["provider_config"]
        
        try:
            response = httpx.post(**{k: v for k, v in request_params.items() if k in ('url', 'headers', 'json')}, timeout=120.0)
            response.raise_for_status()
            data = response.json()

            full_text = _get_nested_value(data, provider_config["response_path"], "")
            if not full_text and response.status_code == 200:
                 error_in_response = _get_nested_value(data, "error.message", json.dumps(data))
                 raise APIError(f"API returned an empty response: {error_in_response}", response.status_code, response.text)

            usage = {
                "promptTokenCount": _get_nested_value(data, provider_config["usage_prompt_path"], 0),
                "candidatesTokenCount": _get_nested_value(data, provider_config["usage_completion_path"], 0)
            }
            return {"text": full_text, "usage": usage}

        except httpx.HTTPStatusError as e:
            raise APIError(f"API Error", e.response.status_code, e.response.text) from e
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            raise NetworkError(f"Connection failed: {e.request.url}") from e
        except json.JSONDecodeError:
            raise APIError("Failed to decode API response.", response.status_code, response.text)

    def get_chat_response_stream(self, model_handle: str, messages: List[Dict], **kwargs) -> Generator[Dict, None, None]:
        """Gets a streaming chat response."""
        try:
            provider_name, model_name = model_handle.split('/', 1)
        except ValueError:
            raise ConfigError(f"Invalid model handle: '{model_handle}'. Must be in 'provider/model_name' format.")

        # --- Google SDK Integration ---
        if provider_name == "google":
            provider_config = self.full_config["providers"].get(provider_name)
            env_key = "KLAI_GOOGLE_API_KEY"
            api_key = os.environ.get(env_key) or provider_config.get("api_key")
            if not api_key or "YOUR_" in api_key:
                raise ConfigError("API key for 'google' is not set.")
            
            try:
                client = genai.Client(api_key=api_key)
                system_prompt = next((msg['content'] for msg in messages if msg['role'] == 'system'), None)
                
                gen_config = types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=kwargs.get("temperature"),
                    top_p=kwargs.get("top_p"),
                    top_k=kwargs.get("top_k"),
                    max_output_tokens=kwargs.get("max_tokens"),
                )
                contents = _format_messages(messages, "gemini")

                response_stream = client.models.generate_content_stream(
                    model=model_name,
                    contents=contents,
                    config=gen_config,
                )
                
                for chunk in response_stream:
                    if chunk.text:
                        yield {"text": chunk.text}
                return
            except google_exceptions.GoogleAPICallError as e:
                raise APIError(f"Google API Error: {e.message}", status_code=e.code) from e
            except Exception as e:
                raise APIError(f"An unexpected error occurred with the Google SDK stream: {e}")

        # --- Other Providers ---
        request_params = self._prepare_request(model_handle, messages, stream=True, **kwargs)
        provider_name = request_params["provider_name"]
        provider_config = request_params["provider_config"]

        try:
            with httpx.stream("POST", **{k: v for k, v in request_params.items() if k in ('url', 'headers', 'json')}, timeout=120.0) as response:
                response.raise_for_status()
                buffer = ""
                for chunk in response.iter_text():
                    buffer += chunk
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if not line.strip(): continue

                        if provider_name == "ollama":
                            try:
                                data = json.loads(line)
                                if text_chunk := _get_nested_value(data, provider_config["stream_response_path"], ""):
                                    yield {"text": text_chunk}
                                if data.get("done"): return
                            except json.JSONDecodeError: continue
                            continue

                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str == '[DONE]': return
                            try:
                                data = json.loads(data_str)
                                if provider_name == "anthropic":
                                    if data.get("type") == "content_block_delta":
                                        if text_chunk := _get_nested_value(data, provider_config["stream_response_path"], ""):
                                            yield {"text": text_chunk}
                                    elif data.get("type") == "message_delta" and (usage := data.get("usage")):
                                        yield {"usage": {"promptTokenCount": usage.get("input_tokens", 0), "candidatesTokenCount": usage.get("output_tokens", 0)}}
                                else:
                                    if text_chunk := _get_nested_value(data, provider_config["stream_response_path"], ""):
                                        yield {"text": text_chunk}
                            except json.JSONDecodeError: continue
        
        except httpx.HTTPStatusError as e:
            raise APIError(f"API Error", e.response.status_code, e.response.text) from e
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            raise NetworkError(f"Connection failed: {e.request.url}") from e
        except Exception as e:
            raise KlaiError(f"An unexpected streaming error occurred: {e}") from e