import typer

from ctfbridge.cli.ui import STYLES, console
from ctfbridge.platforms.registry import PLATFORM_CLIENTS

app = typer.Typer(
    name="platforms",
    help="Lists all platforms officially supported by the library.",
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def platforms():
    """Lists all platforms officially supported by the library."""
    console.print("✅ Supported Platforms:", style=STYLES["success"])
    for name in PLATFORM_CLIENTS.keys():
        console.print(f"- {name}")
