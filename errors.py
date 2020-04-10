class InvalidCommandException(Exception):
    def __init__(self, name, available_commands=None):
        self.message = "Invalid command: %s" %name
        self.available_commands = available_commands
