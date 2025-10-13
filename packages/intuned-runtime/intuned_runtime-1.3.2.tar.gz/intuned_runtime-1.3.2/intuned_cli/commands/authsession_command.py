import arguably

from intuned_cli.utils.help import print_help_and_exit
from intuned_cli.utils.wrapper import cli_command


@arguably.command  # type: ignore
@cli_command
async def authsession():
    """Manage Auth Sessions"""

    print_help_and_exit()
