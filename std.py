from colorama import Fore, Back, Style
from commands import *

def output(message):
    print(message)

def error(message):
    print(Fore.RED + 'ERROR: %s' %message)
    print(Style.RESET_ALL)

def input(display):
    return raw_input(display)

def info(message):
    print(Fore.BLUE + message)
    print(Style.RESET_ALL)

def debug(message):
    print(Fore.LIGHTBLACK_EX + 'INFO: %s' %message)
    print(Style.RESET_ALL)


class Output(object):
    def output(self, message):
        print(message)

    def error(self, message):
        print(Fore.RED + 'ERROR: %s' %message)
        print(Style.RESET_ALL)

    def input(self, display):
        return raw_input(display)

    def info(self, message):
        print(Fore.BLUE + message + Style.RESET_ALL)

    def debug(self, message):
        print(Fore.LIGHTBLACK_EX + 'INFO: %s' %message)
        print(Style.RESET_ALL)

class Input(object):
    def __init__(self):
        pass

    def enter(self):
        input("press Enter to proceed")

    def yesno(self, display_message, values):
        result = input(display_message + "\nvalues: %s" %values)
        if result not in values:
            self.yesno(display_message, values)
        return result

    def input(self, display):
        return raw_input(display)

INPUT = Input()
OUTPUT = Output()
