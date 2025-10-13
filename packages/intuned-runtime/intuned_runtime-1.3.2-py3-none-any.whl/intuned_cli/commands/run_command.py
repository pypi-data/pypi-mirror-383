import arguably

from intuned_cli.utils.help import print_help_and_exit
from intuned_cli.utils.wrapper import cli_command


@arguably.command  # type: ignore
@cli_command
async def run():
    """Executes an Intuned run."""

    print_help_and_exit()
