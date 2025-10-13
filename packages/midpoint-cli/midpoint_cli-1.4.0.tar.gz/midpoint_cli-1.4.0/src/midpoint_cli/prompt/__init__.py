import sys
from cmd import Cmd
from pathlib import Path
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from midpoint_cli.client import MidpointClient
from midpoint_cli.prompt.console import get_console, print_error
from midpoint_cli.prompt.delete import DeleteClientPrompt
from midpoint_cli.prompt.get import GetClientPrompt
from midpoint_cli.prompt.org import OrgClientPrompt
from midpoint_cli.prompt.put import PutClientPrompt
from midpoint_cli.prompt.resource import ResourceClientPrompt
from midpoint_cli.prompt.script import ScriptClientPrompt
from midpoint_cli.prompt.task import TaskClientPrompt
from midpoint_cli.prompt.user import UserClientPrompt


class MidpointCompleter(Completer):
    """Custom completer for Midpoint CLI commands."""

    def __init__(self):
        # Main commands
        self.commands = {
            'exit': 'Exit the shell',
            'help': 'Show help',
            'get': 'Get a server object',
            'put': 'Create/Update a server object',
            'delete': 'Delete a server object',
            'task': 'Manage server tasks',
            'tasks': 'List all server tasks',
            'resource': 'Manage resources',
            'resources': 'List all server resources',
            'user': 'Manage users',
            'users': 'List all server users',
            'org': 'Manage organizations',
            'orgs': 'List all server organizations',
            'script': 'Execute server-side scripts',
        }

        # Subcommands for each main command
        self.subcommands = {
            'task': ['ls', 'get', 'run', 'wait', 'suspend', 'resume'],
            'user': ['ls', 'search', 'get'],
            'org': ['ls', 'search'],
            'resource': ['ls', 'test'],
        }

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        words = text_before_cursor.split()

        # Complete main commands
        if len(words) == 0 or (len(words) == 1 and not text_before_cursor.endswith(' ')):
            word = words[0] if words else ''
            for cmd, desc in self.commands.items():
                if cmd.startswith(word.lower()):
                    yield Completion(cmd, start_position=-len(word), display_meta=desc)

        # Complete subcommands
        elif len(words) >= 1:
            main_cmd = words[0]
            if main_cmd in self.subcommands:
                if len(words) == 1 or (len(words) == 2 and not text_before_cursor.endswith(' ')):
                    word = words[1] if len(words) == 2 else ''
                    for subcmd in self.subcommands[main_cmd]:
                        if subcmd.startswith(word.lower()):
                            yield Completion(subcmd, start_position=-len(word))


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
        self._is_tty = is_a_tty

        # Initialize prompt-toolkit session for interactive mode
        self._session: Optional[PromptSession] = None
        if is_a_tty:
            history_file = Path.home() / '.midpoint-cli-history'
            prompt_style = Style.from_dict({'prompt': 'fg:green bold'})
            self._session = PromptSession(
                history=FileHistory(str(history_file)),
                completer=MidpointCompleter(),
                style=prompt_style,
                complete_while_typing=True,
                enable_history_search=True,
            )

    def _reset_error(self):
        self.error_code = 0
        self.error_message = None

    def _log_error(self):
        if self.error_message:
            print_error(self.error_message)

    def onecmd(self, line):
        self._reset_error()

        res = Cmd.onecmd(self, line) if line.strip() != '' else 0

        self._log_error()
        return res

    def can_exit(self):
        return True

    def do_EOF(self, inp):
        console = get_console()
        console.print()
        return self.do_exit(inp)

    def do_exit(self, inp):
        return True

    def help_exit(self):
        print('Exit the shell')

    def cmdloop(self, intro=None):
        """Enhanced cmdloop using prompt-toolkit for interactive mode."""
        if self._session and self._is_tty:
            # Use prompt-toolkit for enhanced interactive experience
            console = get_console()
            if intro or self.intro:
                console.print(intro or self.intro, style='cyan')

            stop = None
            while not stop:
                try:
                    line = self._session.prompt([('class:prompt', 'midpoint> ')])
                    line = self.precmd(line)
                    stop = self.onecmd(line)
                    stop = self.postcmd(stop, line)
                except KeyboardInterrupt:
                    console.print('^C')
                    continue
                except EOFError:
                    console.print()
                    break
                except Exception as e:
                    print_error(f'Unexpected error: {e}')
                    continue

            self.postloop()
        else:
            # Fall back to standard cmd.Cmd for non-TTY
            Cmd.cmdloop(self, intro)
