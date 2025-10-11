import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text
import sys
import subprocess
import os
import time
from typing import List, Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

from prompt_toolkit.formatted_text import FormattedText
from . import db
from . import config
from .client import AIClient, KlaiError, ConfigError, APIError, NetworkError

# --- App Initialization ---

# --- App Initialization ---
app = typer.Typer(add_completion=False, help="[bold purple]klai[/bold purple]: A Local-First AI Terminal Companion.")
console = Console(highlight=False)
conv_app = typer.Typer(help="Manage and review past conversations.")
config_app = typer.Typer(help="Manage models, API keys, and other settings.")
app.add_typer(conv_app, name="conversations")
app.add_typer(config_app, name="config")

# --- Helper Functions ---
def handle_error(e: Exception):
    """Displays a formatted error message and exits."""
    title = "Error"
    message = str(e)
    if isinstance(e, ConfigError):
        title = "Configuration Error"
    elif isinstance(e, NetworkError):
        title = "Network Error"
    elif isinstance(e, APIError):
        title = f"API Error (Status: {e.status_code})"
        message = f"{e}\n\n[bold]Response:[/bold]\n{e.response_text}"
    
    console.print(Panel(str(message), title=f"[bold red]{title}[/bold red]", border_style="red", expand=False))
    raise typer.Exit(code=1)

def get_all_model_handles() -> List[str]:
    """Returns a sorted list of all available model handles."""
    cfg = config.get_config()
    handles = [f"{provider}/{model_name}" for provider, data in cfg.get("providers", {}).items() for model_name in data.get("models", [])]
    return sorted(handles)

def show_welcome_tui():
    """Displays a welcome screen with main command info."""
    welcome_panel = Panel(
        "[bold]Welcome to [purple]klai[/purple]! Your local-first AI terminal companion.[/bold]\n\n"
        "Here are the main things you can do:",
        title="[bold green]klai[/bold green]",
        border_style="green"
    )
    table = Table.grid(padding=(0, 2))
    table.add_column(style="cyan", no_wrap=True)
    table.add_column()
    table.add_row("klai prompt", "Ask a single, one-shot question.")
    table.add_row("klai chat", "Start an interactive, multi-turn chat session.")
    table.add_row("klai config", "Manage models and API keys.")
    table.add_row("klai conversations", "Review your chat history.")
    console.print(welcome_panel)
    console.print(table)
    console.print("\nRun [bold]klai [COMMAND] --help[/bold] for more options.")

def select_model_tui() -> str:
    """Displays an interactive TUI to select a model and returns the handle."""
    cfg = config.get_config()
    all_handles = get_all_model_handles()
    if not all_handles: handle_error(ConfigError("No models found in configuration."))
    
    default_model = cfg.get("default_model")
    table = Table("Index", "Model Handle", "Default", title="[bold purple]Select a Model[/bold purple]")
    
    handles_by_provider = {}
    for handle in all_handles:
        provider, _ = handle.split('/', 1)
        handles_by_provider.setdefault(provider, []).append(handle)

    indexed_handles = []
    for provider, handles in sorted(handles_by_provider.items()):
        provider_label = cfg["providers"].get(provider, {}).get("label", provider)
        table.add_row(f"--- [bold magenta]{provider_label}[/bold magenta] ---", "", "", style="dim")
        for handle in sorted(handles):
            is_default = "[green]✓[/green]" if handle == default_model else ""
            table.add_row(str(len(indexed_handles) + 1), f"[cyan]{handle}[/cyan]", is_default)
            indexed_handles.append(handle)
    
    console.print(table)
    try:
        choice = typer.prompt("\nSelect a model by its index number", type=int)
        if 1 <= choice <= len(indexed_handles):
            return indexed_handles[choice - 1]
        else:
            handle_error(KlaiError("Invalid index selected."))
    except typer.Abort:
        console.print("\n[yellow]Selection cancelled.[/yellow]")
        raise typer.Exit()
    return ""

def resolve_model_handle(model: Optional[str], select_model: bool) -> str:
    if select_model: return select_model_tui()
    if model: return model
    default_handle = config.get_config().get("default_model")
    if not default_handle: handle_error(ConfigError("Default model is not set. Run `klai config set-default`."))
    return default_handle

def prompt_for_api_key(provider_name: str) -> str:
    console.print(Panel(f"Your API key for [bold]{provider_name}[/bold] is not set.", title="[yellow]Configuration Needed[/yellow]", border_style="yellow"))
    key = typer.prompt(f"Please paste your {provider_name} API key", hide_input=True)
    if not key or "YOUR_" in key: handle_error(KlaiError("API key cannot be empty or a placeholder."))
    config.set_config_value(f"providers.{provider_name}.api_key", key)
    console.print(f"[green]✓ API key for {provider_name} saved successfully.[/green]")
    return key

def run_with_config_retry(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except ConfigError as e:
        if "API key for" in str(e) and "is not set" in str(e):
            try:
                provider_name = str(e).split("'")[1]
                prompt_for_api_key(provider_name)
                console.print("[cyan]Retrying your request...[/cyan]")
                return func(*args, **kwargs)
            except IndexError: handle_error(e)
        else: handle_error(e)
    except (KlaiError, Exception) as e: handle_error(e)

# --- Chat REPL Class ---
class ChatREPL:
    def __init__(self, model_handle, stream, verbose, **kwargs):
        self.session_stats = {"prompt_tokens": 0, "response_tokens": 0}
        self.stream = stream
        self.verbose = verbose
        self.model_params = kwargs
        self.history = InMemoryHistory()

        conv_id = self.model_params.pop("conversation_id", None)
        system_prompt = self.model_params.pop("system_prompt", None)

        if conv_id:
            self._load_conversation(conv_id)
        else:
            self.model_handle = model_handle
            self.system_prompt = system_prompt or "You are a helpful assistant."
            self._create_new_conversation()

    def _create_new_conversation(self):
        """Creates a new conversation in the database and sets the instance variables."""
        self.conversation_id = db.create_conversation(
            model=self.model_handle, system_prompt=self.system_prompt,
            temperature=self.model_params.get('temperature'), top_p=self.model_params.get('top_p')
        )

    def _load_conversation(self, conv_id: int):
        """Loads an existing conversation from the database."""
        conv = db.get_conversation(conv_id)
        if not conv: handle_error(KlaiError(f"No conversation found with ID {conv_id}."))
        self.conversation_id = conv.id
        self.system_prompt = conv.system_prompt
        self.model_handle = conv.model
        self.model_params['temperature'] = conv.temperature if self.model_params.get('temperature') is None else self.model_params['temperature']
        self.model_params['top_p'] = conv.top_p if self.model_params.get('top_p') is None else self.model_params['top_p']

    def run(self, initial_prompt: Optional[str] = None):
        console.print(Panel(
            f"Chatting in session [bold]#{self.conversation_id}[/bold] with [bold cyan]{self.model_handle}[/bold cyan].\n\n"
            "Type a message to begin, or type [bold]/help[/bold] for a list of commands.",
            border_style="green"
        ))
        
        if initial_prompt:
            console.print(Panel(initial_prompt, title="[bold cyan]User[/bold cyan]", border_style="cyan", title_align="left"))
            self._handle_prompt(initial_prompt)
        
        # prompt-toolkit handles cross-platform input gracefully, even after piping.
        session = PromptSession(history=self.history)
        prompt_style = FormattedText([('bold cyan', 'User > ')])

        while True:
            try:
                user_input = session.prompt(prompt_style)
                if not user_input.strip():
                    continue

                if user_input.startswith('/'):
                    if self._handle_command(user_input):
                        # Re-create session if context was cleared
                        session = PromptSession(history=self.history)
                else:
                    console.print(Panel(user_input, title="[bold cyan]User[/bold cyan]", border_style="cyan", title_align="left"))
                    self._handle_prompt(user_input)
            except (KeyboardInterrupt, EOFError):
                break
        
        console.print("\n[bold green]Chat session ended.[/bold green]")

    def _handle_prompt(self, user_prompt):
        if not user_prompt.strip(): return
        db.add_message(self.conversation_id, "user", user_prompt)
        history = db.get_active_branch(self.conversation_id)
        
        client = AIClient()
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend([{"role": r.role, "content": r.content} for r in history])

        start_time = time.monotonic()
        
        if self.stream:
            full_response, usage = "", {}
            console.print(f"[bold green]Assistant:[/bold green] ", end="")
            def api_call_stream():
                return client.get_chat_response_stream(self.model_handle, messages, **self.model_params)
            
            for chunk in run_with_config_retry(api_call_stream):
                full_response += chunk.get("text", "")
                if "usage" in chunk: usage = chunk["usage"]
                console.print(chunk.get("text", ""), end="")
            console.print()
            response = {"text": full_response, "usage": usage}
        else:
            def api_call_no_stream():
                spinner = Spinner("dots", text="[bold green]AI is thinking...")
                with console.status(spinner):
                    return client.get_chat_response(self.model_handle, messages, **self.model_params)
            response = run_with_config_retry(api_call_no_stream)

        end_time = time.monotonic()

        if response and response.get('text', '').strip():
            md = Markdown(response['text'], code_theme="monokai")
            console.print(Panel(md, title=f"[bold green]Assistant[/bold green] ([italic]{self.model_handle}[/italic])", border_style="green", title_align="left"))
            db.add_message(self.conversation_id, "assistant", response['text'])
            
            if self.verbose:
                usage = response.get('usage', {})
                in_tok = usage.get('promptTokenCount', 0)
                out_tok = usage.get('candidatesTokenCount', 0)
                elapsed = end_time - start_time
                stats = Text.from_markup(f"Time: [cyan]{elapsed:.2f}s[/cyan] | Tokens: [cyan]{in_tok+out_tok}[/cyan] ([yellow]In:[/yellow] {in_tok}, [yellow]Out:[/yellow] {out_tok})")
                console.print(Panel(stats, style="dim", border_style="dim", title="Stats", title_align="left"))

    def _handle_command(self, user_input) -> bool:
        """Handles a slash command. Returns True if the session needs to be reset."""
        parts = user_input.split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""
        
        if cmd in ['/quit', '/exit']: raise KeyboardInterrupt
        
        elif cmd == '/system':
            if args:
                self.system_prompt = args
                db.update_conversation_settings(self.conversation_id, db.get_conversation(self.conversation_id).title, args, self.model_handle, self.model_params.get('temperature'), self.model_params.get('top_p'))
                console.print("[bold purple]System prompt updated.[/bold purple]")
            else:
                console.print(Panel(f"[bold]Model:[/bold] {self.model_handle}\n[bold]System Prompt:[/bold]\n{self.system_prompt}", title="[purple]Session Info[/purple]", border_style="purple"))
        
        elif cmd == '/model':
            if not args:
                console.print(f"Current model: [cyan]{self.model_handle}[/cyan]")
                return False
            if args not in get_all_model_handles():
                console.print(f"[red]Error:[/red] '{args}' is not a valid model handle.")
            else:
                self.model_handle = args
                db.update_conversation_settings(self.conversation_id, db.get_conversation(self.conversation_id).title, self.system_prompt, self.model_handle, self.model_params.get('temperature'), self.model_params.get('top_p'))
                console.print(f"[purple]Model switched to [cyan]{self.model_handle}[/cyan].[/purple]")

        elif cmd == '/temp':
            try:
                temp = float(args)
                self.model_params['temperature'] = temp
                db.update_conversation_settings(self.conversation_id, db.get_conversation(self.conversation_id).title, self.system_prompt, self.model_handle, temp, self.model_params.get('top_p'))
                console.print(f"[purple]Temperature set to [cyan]{temp}[/cyan].[/purple]")
            except (ValueError, IndexError):
                console.print("[red]Error:[/red] Please provide a valid number for temperature (e.g., /temp 0.8).")

        elif cmd == '/topp':
            try:
                top_p = float(args)
                self.model_params['top_p'] = top_p
                db.update_conversation_settings(self.conversation_id, db.get_conversation(self.conversation_id).title, self.system_prompt, self.model_handle, self.model_params.get('temperature'), top_p)
                console.print(f"[purple]Top P set to [cyan]{top_p}[/cyan].[/purple]")
            except (ValueError, IndexError):
                console.print("[red]Error:[/red] Please provide a valid number for top_p (e.g., /topp 0.9).")

        elif cmd == '/params':
            params_table = Table.grid(padding=(0, 2))
            params_table.add_column(style="yellow")
            params_table.add_column()
            params_table.add_row("Model:", self.model_handle)
            params_table.add_row("Temperature:", str(self.model_params.get('temperature')))
            params_table.add_row("Top P:", str(self.model_params.get('top_p')))
            console.print(Panel(params_table, title="[purple]Current Parameters[/purple]", border_style="purple"))

        elif cmd == '/clear':
            self._create_new_conversation()
            self.history = InMemoryHistory() # Reset history for the new session
            console.print(Panel(f"Context cleared. Starting new session [bold]#{self.conversation_id}[/bold] with the same settings.", border_style="green"))
            return True

        elif cmd == '/help':
            table = Table(title="[purple]Chat Commands[/purple]")
            table.add_column("Command", style="cyan")
            table.add_column("Description")
            table.add_row("/system [prompt]", "View or update the system prompt.")
            table.add_row("/model [handle]", "Switch to a different model.")
            table.add_row("/temp [0.0-2.0]", "Set the temperature for the session.")
            table.add_row("/topp [0.0-1.0]", "Set the top_p for the session.")
            table.add_row("/params", "View the current model parameters.")
            table.add_row("/clear", "Clear the current chat context and start a new session.")
            table.add_row("/quit or /exit", "Exit the chat session.")
            console.print(table)
        
        else:
            console.print(f"[bold red]Unknown command:[/bold red] {cmd}")
        
        return False

# --- Constants ---
DEFAULT_PROMPT_PERSONA = """You are an AI assistant for a command-line interface. Your user is a developer.
Your goal is to provide clear, concise, and well-formatted answers suitable for a terminal.

- **If the user asks for a command or code:** Provide the command/code in a runnable code block first, then briefly explain it.
- **For all other questions:** Answer directly and to the point.
- Use Markdown for formatting (lists, bolding, etc.) to improve readability.
- Avoid conversational fluff, apologies, or unnecessary preamble like "Sure, here is..."
"""

# --- Typer Commands ---
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """A Local-First AI Terminal Companion."""
    if ctx.invoked_subcommand is None: show_welcome_tui()

@app.command(help="Ask a single question. Uses the default model unless specified.")
def prompt(
    prompt_parts: Optional[List[str]] = typer.Argument(None, help="The prompt to send to the AI. Can be omitted if piping input."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Specify a model handle (e.g., openai/gpt-4o)."),
    select_model: bool = typer.Option(False, "--select-model", help="Show an interactive menu to select a model."),
    temperature: float = typer.Option(None, help="Control creativity (0.0 to 2.0)."),
    top_p: float = typer.Option(None, help="Control nucleus sampling."),
    top_k: int = typer.Option(None, help="Top-k sampling."),
    seed: int = typer.Option(None, help="Seed for deterministic sampling."),
    max_tokens: int = typer.Option(None, help="Maximum number of tokens to generate."),
    system_prompt: str = typer.Option(None, "--system", "-s", help="Set a system-level instruction for the AI."),
    start_chat: bool = typer.Option(False, "--chat", help="Start an interactive chat session after the prompt."),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show detailed stats after the response.")
):
    db.init_db()
    final_model_handle = resolve_model_handle(model, select_model)
    
    piped_input = ""
    if not sys.stdin.isatty(): piped_input = sys.stdin.read().strip()
    
    full_prompt = " ".join(prompt_parts) if prompt_parts else ""
    
    if not full_prompt and not piped_input:
        handle_error(KlaiError("Please provide a prompt via argument or piped input."))

    final_prompt = f"{piped_input}\n\n{full_prompt}".strip()
    
    # Use the user's system prompt if provided, otherwise use the engineered default.
    final_system_prompt = system_prompt or DEFAULT_PROMPT_PERSONA

    def api_call():
        client = AIClient()
        messages = [
            {"role": "system", "content": final_system_prompt},
            {"role": "user", "content": final_prompt}
        ]
        
        spinner = Spinner("dots", text="[bold green]AI is thinking...")
        with console.status(spinner):
            return client.get_chat_response(
                final_model_handle, messages,
                temperature=temperature, top_p=top_p, top_k=top_k,
                seed=seed, max_tokens=max_tokens
            )

    start_time = time.monotonic()
    response = run_with_config_retry(api_call)
    end_time = time.monotonic()

    if response.get('text') is None:
        console.print(Panel("[yellow]The model returned an empty response.[/yellow]", border_style="yellow"))
        raise typer.Exit()

    md = Markdown(response['text'], code_theme="monokai")
    console.print(Panel(md, title=f"[bold green]Assistant[/bold green] ([italic]{final_model_handle}[/italic])", border_style="green", title_align="left"))

    if verbose:
        usage = response.get('usage', {})
        in_tok = usage.get('promptTokenCount', 0)
        out_tok = usage.get('candidatesTokenCount', 0)
        elapsed = end_time - start_time
        stats = Text.from_markup(f"Time: [cyan]{elapsed:.2f}s[/cyan] | Tokens: [cyan]{in_tok+out_tok}[/cyan] ([yellow]In:[/yellow] {in_tok}, [yellow]Out:[/yellow] {out_tok})")
        console.print(Panel(stats, style="dim", border_style="dim", title="Stats", title_align="left"))

    if start_chat:
        repl = ChatREPL(
            final_model_handle, stream=True, verbose=verbose,
            temperature=temperature, top_p=top_p, top_k=top_k,
            seed=seed, max_tokens=max_tokens, conversation_id=None, system_prompt=system_prompt
        )
        db.add_message(repl.conversation_id, "user", final_prompt)
        if response['text'].strip(): db.add_message(repl.conversation_id, "assistant", response['text'])
        repl.run()

@app.command(help="Start or resume an interactive chat session.")
def chat(
    id: int = typer.Option(None, "--id", help="Resume a previous conversation by its ID."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Start a new chat with a specific model handle."),
    select_model: bool = typer.Option(False, "--select-model", help="Start a new chat by selecting a model from a menu."),
    system_prompt: str = typer.Option(None, "--system", "-s", help="Set a system-level instruction for the new chat session."),
    stream: bool = typer.Option(False, help="Enable streaming to get the response token by token."),
    temperature: float = typer.Option(None, help="Control creativity for the session."),
    top_p: float = typer.Option(None, help="Control nucleus sampling for the session."),
    top_k: int = typer.Option(None, help="Top-k sampling for the session."),
    seed: int = typer.Option(None, help="Seed for deterministic sampling for the session."),
    max_tokens: int = typer.Option(None, help="Maximum number of tokens to generate in the session."),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show detailed stats after each response.")
):
    db.init_db()
    final_model_handle = None
    if not id: final_model_handle = resolve_model_handle(model, select_model)
    
    piped_input = ""
    if not sys.stdin.isatty(): piped_input = sys.stdin.read().strip()
    
    repl = ChatREPL(
        final_model_handle, stream=stream, verbose=verbose,
        temperature=temperature, top_p=top_p, top_k=top_k,
        seed=seed, max_tokens=max_tokens,
        conversation_id=id, system_prompt=system_prompt
    )
    repl.run(initial_prompt=piped_input)

# --- Config Commands (omitted for brevity, no changes) ---
@config_app.command("list-models", help="List all available models from your configuration.")
def config_list_models():
    cfg = config.get_config()
    default_model = cfg.get("default_model")
    table = Table("Handle", "Provider", "Default", title="[bold purple]Available Models[/bold purple]")
    for handle in get_all_model_handles():
        provider, _ = handle.split('/', 1)
        provider_label = cfg["providers"].get(provider, {}).get("label", provider)
        is_default = "[green]✓[/green]" if handle == default_model else ""
        table.add_row(f"[cyan]{handle}[/cyan]", provider_label, is_default)
    console.print(table)

@config_app.command("set-default", help="Set the default model to use for all commands.")
def config_set_default(model_handle: Optional[str] = typer.Argument(None, help="The full handle of the model (e.g., gemini/gemini-1.5-pro-latest).")):
    if not model_handle:
        model_handle = select_model_tui()
    
    if model_handle not in get_all_model_handles():
        handle_error(ConfigError(f"'{model_handle}' is not a valid model handle. Use `klai config list-models` to see options."))
    config.set_config_value("default_model", model_handle)
    console.print(f"[green]✓ Default model set to [bold cyan]{model_handle}[/bold cyan].[/green]")

@config_app.command("set-key", help="Set or update the API key for a provider.")
def config_set_key(provider_name: str = typer.Argument(..., help="The name of the provider (e.g., gemini, openrouter).")):
    prompt_for_api_key(provider_name)

@config_app.command("add-model", help="Add a new model handle to a provider.")
def config_add_model(model_handle: str = typer.Argument(..., help="The full handle of the new model (e.g., provider/new-model-name).")):
    try:
        provider, new_model = model_handle.split('/', 1)
    except ValueError:
        handle_error(ConfigError(f"Invalid model handle: '{model_handle}'. Must be in 'provider/model_name' format."))
    
    cfg = config.get_config()
    if provider not in cfg["providers"]:
        handle_error(ConfigError(f"Provider '{provider}' not found in configuration."))
    
    models = cfg["providers"][provider].get("models", [])
    if new_model in models:
        handle_error(KlaiError(f"Model '{new_model}' already exists for provider '{provider}'."))
    
    models.append(new_model)
    config.set_config_value(f"providers.{provider}.models", models)
    console.print(f"[green]✓ Model [bold cyan]{model_handle}[/bold cyan] added successfully.[/green]")

@config_app.command("remove-model", help="Remove a model handle from a provider.")
def config_remove_model(model_handle: str = typer.Argument(..., help="The full handle of the model to remove.")):
    try:
        provider, model_to_remove = model_handle.split('/', 1)
    except ValueError:
        handle_error(ConfigError(f"Invalid model handle: '{model_handle}'. Must be in 'provider/model_name' format."))

    cfg = config.get_config()
    if provider not in cfg["providers"]:
        handle_error(ConfigError(f"Provider '{provider}' not found in configuration."))
    
    models = cfg["providers"][provider].get("models", [])
    if model_to_remove not in models:
        handle_error(KlaiError(f"Model '{model_to_remove}' not found for provider '{provider}'."))
    
    models.remove(model_to_remove)
    config.set_config_value(f"providers.{provider}.models", models)
    console.print(f"[green]✓ Model [bold cyan]{model_handle}[/bold cyan] removed successfully.[/green]")

@config_app.command("edit", help="Open the config.json file in your default editor.")
def config_edit():
    config_path_str = str(config.CONFIG_PATH)
    try:
        console.print(f"Opening {config_path_str} in your default application...")
        typer.launch(config_path_str, locate=True)
    except Exception as e:
        handle_error(KlaiError(f"Could not open '{config_path_str}': {e}"))

@config_app.command("validate", help="Check the configuration for common issues.")
def config_validate():
    cfg = config.get_config()
    all_handles = get_all_model_handles()
    table = Table("Check", "Status", "Details", title="[bold purple]Configuration Validation[/bold purple]")
    
    default_model = cfg.get("default_model")
    if not default_model:
        table.add_row("Default Model", "[bold red]FAIL[/bold red]", "Default model is not set.")
    elif default_model not in all_handles:
        table.add_row("Default Model", "[bold red]FAIL[/bold red]", f"Default model '[cyan]{default_model}[/cyan]' is not in the list of available models.")
    else:
        table.add_row("Default Model", "[bold green]OK[/bold green]", f"Default model is '[cyan]{default_model}[/cyan]'.")

    for provider, data in cfg.get("providers", {}).items():
        if provider == "ollama":
            table.add_row(f"API Key: {provider}", "[bold green]OK[/bold green]", "Ollama is local and needs no key.")
            continue
        
        key = data.get("api_key")
        if not key or "YOUR_" in key:
            table.add_row(f"API Key: {provider}", "[bold red]FAIL[/bold red]", f"API key for '{provider}' is not set. Use `klai config set-key {provider}`.")
        else:
            table.add_row(f"API Key: {provider}", "[bold green]OK[/bold green]", "API key is set.")
            
    console.print(table)

# --- Conversations Commands ---
@conv_app.command("list", help="List all saved conversations.")
def conversations_list():
    convs = db.list_conversations(page=1, per_page=100)
    table = Table("ID", "Title", "Model Handle", "Started On", title="[purple]Saved Conversations[/purple]")
    for conv in convs:
        table.add_row(str(conv.id), conv.title, f"[cyan]{conv.model}[/cyan]", str(conv.start_time.strftime('%Y-%m-%d %H:%M')))
    console.print(table)

@conv_app.command("view", help="Display the full history of a specific conversation.")
def conversations_view(conversation_id: int = typer.Argument(..., help="The ID of the conversation to view.")):
    messages = db.get_active_branch(conversation_id)
    if not messages: handle_error(KlaiError(f"No conversation found with ID {conversation_id}."))
    for msg in messages:
        color = "cyan" if msg.role == "user" else "green"
        title = f"[bold {color}]{msg.role.capitalize()}[/bold {color}]"
        console.print(Panel(Markdown(msg.content, code_theme="monokai"), title=title, border_style=color, title_align="left"))

@conv_app.command("search", help="Search conversations for specific text.")
def conversations_search(query: str = typer.Argument(..., help="The text to search for.")):
    convs = db.list_conversations(page=1, per_page=100, search=query)
    table = Table("ID", "Title", "Model Handle", "Started On", title=f"[purple]Conversations Matching '{query}'[/purple]")
    for conv in convs:
        table.add_row(str(conv.id), conv.title, f"[cyan]{conv.model}[/cyan]", str(conv.start_time.strftime('%Y-%m-%d %H:%M')))
    console.print(table)

@conv_app.command("delete", help="Delete a conversation and all its messages.")
def conversations_delete(conversation_id: int = typer.Argument(..., help="The ID of the conversation to delete.")):
    conv = db.get_conversation(conversation_id)
    if not conv:
        handle_error(KlaiError(f"No conversation found with ID {conversation_id}."))
    
    console.print(Panel(f"You are about to delete conversation [bold]#{conv.id}[/bold]: '{conv.title}'.", style="yellow"))
    if typer.confirm("Are you sure you want to permanently delete this conversation?"):
        db.delete_conversation(conversation_id)
        console.print(f"[bold green]Conversation #{conversation_id} has been deleted.[/bold green]")
    else:
        console.print("[bold yellow]Deletion cancelled.[/bold yellow]")
        raise typer.Exit()

# --- Web Commands (unchanged) ---
@app.command(name="web-start", help="Launch the web interface as a background service.")
def web_start():
    from . import web
    pid = web.run_server()
    if pid:
        console.print(Panel(f"[bold green]✓ Web server started successfully.[/bold green]\n\n  - URL: [link=http://12from prompt_toolkit.formatted_text import FormattedText7.0.0.1:5001]http://127.0.0.1:5001[/link]\n  - PID: {pid}\n  - To stop, run: [bold]klai web-stop[/bold]", title="[green]Web Server[/green]", border_style="green"))
    else:
        console.print(Panel("[bold yellow]Web server is already running.[/bold yellow]", title="[yellow]Web Server[/yellow]", border_style="yellow"))

@app.command(name="web-stop", help="Stop the background web interface service.")
def web_stop():
    from . import web
    pid = web.stop_server()
    if pid:
        console.print(Panel(f"[bold green]✓ Web server (PID: {pid}) stopped successfully.[/bold green]", title="[green]Web Server[/green]", border_style="green"))
    else:
        console.print(Panel("[bold yellow]Web server is not running.[/bold yellow]", title="[yellow]Web Server[/yellow]", border_style="yellow"))

if __name__ == "__main__":
    app()
