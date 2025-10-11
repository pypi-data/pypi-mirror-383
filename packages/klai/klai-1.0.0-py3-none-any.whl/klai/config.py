import json
from pathlib import Path

APP_DIR = Path.home() / ".config" / "klai"
CONFIG_PATH = APP_DIR / "config.json"

DEFAULT_CONFIG = {
    "default_model": "openai/gpt-4o",
    "providers": {
        "openai": {
            "label": "OpenAI (Direct)",
            "api_key": "YOUR_OPENAI_API_KEY",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "headers": {},
            "auth_header": "Authorization",
            "auth_scheme": "Bearer",
            "models": [
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ],
            "payload_template": {
                "model": "{model}",
                "messages": "{messages_openai_format}",
                "temperature": "{temperature}",
                "top_p": "{top_p}",
                "frequency_penalty": "{frequency_penalty}",
                "presence_penalty": "{presence_penalty}",
                "seed": "{seed}",
                "max_tokens": "{max_tokens}",
                "stream": "{stream}"
            },
            "response_path": "choices.0.message.content",
            "stream_response_path": "choices.0.delta.content",
            "usage_prompt_path": "usage.prompt_tokens",
            "usage_completion_path": "usage.completion_tokens"
        },
        "anthropic": {
            "label": "Anthropic (Direct)",
            "api_key": "YOUR_ANTHROPIC_API_KEY",
            "api_url": "https://api.anthropic.com/v1/messages",
            "headers": {
                "anthropic-version": "2023-06-01"
            },
            "auth_header": "x-api-key",
            "auth_scheme": None,
            "models": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            "payload_template": {
                "model": "{model}",
                "system": "{system_prompt_anthropic}",
                "messages": "{messages_anthropic_format}",
                "temperature": "{temperature}",
                "top_p": "{top_p}",
                "top_k": "{top_k}",
                "max_tokens": "{max_tokens}",
                "stream": "{stream}"
            },
            "response_path": "content.0.text",
            "stream_response_path": "delta.text", # Note: Special handling needed for event types
            "usage_prompt_path": "usage.input_tokens",
            "usage_completion_path": "usage.output_tokens"
        },
        "openrouter": {
            "label": "OpenRouter",
            "api_key": "YOUR_OPENROUTER_API_KEY",
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
            "headers": {},
            "auth_header": "Authorization",
            "auth_scheme": "Bearer",
            "models": [
                "openai/gpt-4o",
                "anthropic/claude-3-opus",
                "anthropic/claude-3-sonnet",
                "google/gemini-pro-1.5",
                "meta-llama/llama-3-70b-instruct",
                "mistralai/mistral-large"
            ],
            "payload_template": {
                "model": "{model}",
                "messages": "{messages_openai_format}",
                "temperature": "{temperature}",
                "top_p": "{top_p}",
                "top_k": "{top_k}",
                "frequency_penalty": "{frequency_penalty}",
                "presence_penalty": "{presence_penalty}",
                "seed": "{seed}",
                "max_tokens": "{max_tokens}",
                "stream": "{stream}"
            },
            "response_path": "choices.0.message.content",
            "stream_response_path": "choices.0.delta.content",
            "usage_prompt_path": "usage.prompt_tokens",
            "usage_completion_path": "usage.completion_tokens"
        },
        "google": {
            "label": "Google Gemini (Direct)",
            "api_key": "YOUR_GOOGLE_API_KEY",
            "headers": {},
            "auth_header": None,
            "auth_scheme": None,
            "models": [
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                "gemini-2.0-flash-001",
                "gemma-3-27b-it"
            ]
        },
        "ollama": {
            "label": "Ollama (Local)",
            "api_key": None,
            "api_url": "http://localhost:11434/api/chat",
            "headers": {},
            "auth_header": None,
            "auth_scheme": None,
            "models": ["llama3", "mistral", "codellama"],
            "payload_template": {
                "model": "{model}",
                "messages": "{messages_openai_format}",
                "stream": "{stream}",
                "options": {
                    "temperature": "{temperature}",
                    "top_p": "{top_p}",
                    "top_k": "{top_k}",
                    "seed": "{seed}"
                }
            },
            "response_path": "message.content",
            "stream_response_path": "message.content",
            "usage_prompt_path": "prompt_eval_count",
            "usage_completion_path": "eval_count"
        }
    }
}

def merge_configs(default, user):
    """Recursively merge user config into default config."""
    if isinstance(default, dict) and isinstance(user, dict):
        for k, v in default.items():
            if k in user:
                user[k] = merge_configs(v, user[k])
            else:
                user[k] = v
        return user
    return user

def get_config():
    """
    Loads the user's config, merges it with the default config to ensure
    all keys are present, and saves it back if changes were made.
    """
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    with open(CONFIG_PATH, "r") as f:
        user_config = json.load(f)

    # Create copies to avoid modifying the original objects in memory
    user_config_copy = json.loads(json.dumps(user_config))
    default_config_copy = json.loads(json.dumps(DEFAULT_CONFIG))

    updated_config = merge_configs(default_config_copy, user_config_copy)

    # Save back only if the structure has changed.
    if updated_config != user_config:
        save_config(updated_config)
        
    return updated_config

def save_config(config_data):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=4)

def set_config_value(key_path: str, value: any):
    config_data = get_config()
    keys = key_path.split('.')
    current = config_data
    for key in keys[:-1]:
        current = current.setdefault(key, {})
    current[keys[-1]] = value
    save_config(config_data)