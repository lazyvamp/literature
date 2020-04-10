import std
from errors import InvalidCommandException

class Command(object):
    def __init__(self, name, short_name=None, verbose=None, callback=None):
        self.name = name
        self.short_name = short_name
        self.verbose = verbose
        self.secondary_commands = {}
        self.callback = callback

    def setSecondaryCommand(self, command, callback=None):
        self.secondary_commands[command.name] = {
            "command": command,
            "callback": callback
        }

    def execute(self, callback=None, *args):
        if args:
            if args[0].startswith("-"):
                self._exec_sec(args[0][1:], *args[1:])
                return
        callback = callback or self.callback
        if callback:
            callback(*args)

    def _exec_sec(self, name, *args):
        if name == 'help':
            self._help()
            return
        command_dict = self.secondary_commands.get(name)
        if not command_dict:
            raise InvalidCommandException(name, self.secondary_commands.keys())
        command_dict["command"].execute(command_dict["callback"], *args)

    def _help(self):
        if self.verbose:
            std.OUTPUT.info(self.verbose)
        if self.secondary_commands:
            std.OUTPUT.info("Available secondary commands:")
            for k,v in self.secondary_commands.items():
                std.OUTPUT.info("\t-%s: %s" %(k, v.get('command').verbose))


class CommandManager(object):
    AVAILABLE_COMMANDS = {}
    callbacks = {}

    @staticmethod
    def register_commands(game):
        INIT = Command("init", "i", "initialize the game", game.init)
        QUIT = Command("quit", "q", "quit the game", game.exit)
        PRINT = Command("print", "p", "print players information", None)
        REGISTER = Command("register", "r", "register players action", game.register_request)
        CommandManager.AVAILABLE_COMMANDS = {
            INIT.name:INIT,
            QUIT.name:QUIT,
            PRINT.name:PRINT,
            REGISTER.name:REGISTER
        }
        PRINT.setSecondaryCommand(
            Command("p", callback=game.print_player_probability)
        )
        PRINT.setSecondaryCommand(
            Command("turn", callback=game.print_player_turn)
        )
        PRINT.setSecondaryCommand(
            Command("next", callback=game.print_ai_next_card)
        )
        PRINT.setSecondaryCommand(
            Command("has", callback=game.print_has_card)
        )

    @staticmethod
    def handle_command(game, command_str, *args):
        command = CommandManager.AVAILABLE_COMMANDS.get(command_str)
        if not command:
            raise InvalidCommandException(command_str, CommandManager.AVAILABLE_COMMANDS.keys())
        command.execute(CommandManager.callbacks.get(command_str), *args)
