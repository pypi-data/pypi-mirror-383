"""CLI for interacting with local chat model endpoints."""

import sys

try:
    import click
except ImportError as e:
    raise ImportError("Required package not installed. Run: pip install click") from e

from ..logger import init_logging, logger
from ..core.chatbot import Chatbot


@click.command()
@click.option(
    "--url",
    "-u",
    default="http://localhost:11434",
    help="Base URL of the chat model API",
)
@click.option("--model", "-m", default="llama3.2:latest", help="Model name to use")
@click.option("--stream", "-s", is_flag=True, help="Use streaming response")
@click.option(
    "--timeout", "-t", type=int, default=30, help="Request timeout in seconds"
)
@click.option("--interactive", "-i", is_flag=True, help="Interactive chat mode")
@click.option(
    "--list-models", "-l", is_flag=True, help="List available models and exit"
)
@click.option(
    "--health-check",
    "-h",
    is_flag=True,
    help="Check if the endpoint is healthy and exit",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.argument("prompt", required=False)
def main(
    url: str,
    model: str,
    stream: bool,
    timeout: int,
    interactive: bool,
    list_models: bool,
    health_check: bool,
    verbose: bool,
    prompt: str,
) -> None:
    """Interact with local chat model endpoints (Ollama, etc.)."""

    # Initialize logging
    init_logging(level=20 if verbose else 30)  # DEBUG if verbose, else WARNING

    try:
        # Create chatbot instance
        chatbot = Chatbot(base_url=url, timeout=timeout)

        # Health check mode
        if health_check:
            if chatbot.health_check():
                click.echo(f"✓ Endpoint {url} is healthy")
                sys.exit(0)
            else:
                click.echo(f"✗ Endpoint {url} is not responding", err=True)
                sys.exit(1)

        # List models mode
        if list_models:
            models = chatbot.list_models()
            if models:
                click.echo("Available models:")
                for model_name in models:
                    click.echo(f"  {model_name}")
            else:
                click.echo("No models found or endpoint not available")
            return

        # Interactive mode
        if interactive:
            click.echo(f"Interactive chat with {model} at {url}")
            click.echo("Type 'quit', 'exit', or press Ctrl+C to exit\n")

            try:
                while True:
                    user_input = click.prompt("You", type=str)

                    if user_input.lower() in ["quit", "exit"]:
                        break

                    if not user_input.strip():
                        continue

                    try:
                        response = chatbot.ask(user_input, model=model, stream=stream)
                        click.echo(f"Bot: {response}\n")
                    except Exception as e:
                        click.echo(f"Error: {e}", err=True)

            except KeyboardInterrupt:
                click.echo("\nGoodbye!")
                return

        # Single prompt mode
        elif prompt:
            try:
                response = chatbot.ask(prompt, model=model, stream=stream)
                click.echo(response)
            except Exception as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)

        else:
            # No prompt provided and not interactive
            click.echo(
                "Error: Please provide a prompt or use --interactive mode", err=True
            )
            click.echo("Use --help for more information")
            sys.exit(2)

    except Exception as e:
        logger.exception("Unexpected error occurred")
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
