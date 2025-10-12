import sys
from cmd import Cmd

from midpoint_cli.client import MidpointClient
from midpoint_cli.prompt.delete import DeleteClientPrompt
from midpoint_cli.prompt.get import GetClientPrompt
from midpoint_cli.prompt.org import OrgClientPrompt
from midpoint_cli.prompt.put import PutClientPrompt
from midpoint_cli.prompt.resource import ResourceClientPrompt
from midpoint_cli.prompt.script import ScriptClientPrompt
from midpoint_cli.prompt.task import TaskClientPrompt
from midpoint_cli.prompt.user import UserClientPrompt


class MidpointClientPrompt(
    Cmd,
    TaskClientPrompt,
    GetClientPrompt,
    PutClientPrompt,
    DeleteClientPrompt,
    ResourceClientPrompt,
    UserClientPrompt,
    OrgClientPrompt,
    ScriptClientPrompt,
):
    def __init__(self, client: MidpointClient):
        Cmd.__init__(self)
        is_a_tty = hasattr(sys.stdin, 'isatty') and sys.stdin.isatty()
        self.client = client
        self.prompt = '\033[32mmidpoint\033[0m> ' if is_a_tty else ''
        self.intro = 'Welcome to Midpoint client ! Type ? for a list of commands' if is_a_tty else None

    def _reset_error(self):
        self.error_code = 0
        self.error_message = None

    def _log_error(self):
        if self.error_message:
            print(f'Error: {self.error_message}')

    def onecmd(self, line):
        self._reset_error()

        res = Cmd.onecmd(self, line) if line.strip() != '' else 0

        self._log_error()
        return res

    def can_exit(self):
        return True

    def do_EOF(self, inp):
        print()
        return self.do_exit(inp)

    def do_exit(self, inp):
        return True

    def help_exit(self):
        print('Exit the shell')
