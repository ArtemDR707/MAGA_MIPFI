"""Entry-point for the `project` script (Poetry)."""

from valutatrade_hub.cli.interface import main as cli_main


def main() -> None:
    """Run ValutaTrade Hub CLI."""
    cli_main()


if __name__ == "__main__":
    main()
