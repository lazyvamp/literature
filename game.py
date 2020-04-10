from core import *
import traceback
from players  import *
import std
from commands import CommandManager
from errors import InvalidCommandException

class PlayerManager(object):
    def __init__(self):
        self.players = {}
        self.AI = None
        self.opponents = []
        self.currentPlayerName = None

    def create_bot(self):
        self.AI = BotPlayer("ai")
        self._add_player(self.AI)

    def create_human_player(self, name):
        p = HumanPlayer(name)
        p.initProbability()
        self._add_player(p)

    def _add_player(self, p):
        if p.name in self.players.keys():
            raise Exception("Duplicate player name. Please provide another name")
        self.players[p.name] = p

    def all_player_names(self):
        return self.players.keys()

    def assign_bot_partner(self, name):
        if name not in self.all_player_names():
            raise Exception("Invalid Partner Name: %s" %name)
        if name == self.AI.name:
            raise Exception("How can I be my own partner??? Choose another name!")
        self.AI.partner = self.players[name]
        for name in self.players.keys():
            if name not in [self.AI.getName(), self.AI.partner.getName()]:
                self.opponents.append(self.players[name])
        self.opponents[0].partner = self.opponents[1]
        self.opponents[1].partner = self.opponents[0]

    def assign_bot_cards(self, cards):
        self.AI.validate_cards(cards)
        self.AI.updateProbabilityForCards(100, cards)

        for name in self.players.keys():
            if name != self.AI.name:
                self.players[name].updateProbabilityForCards(0, cards)

    def handle_request(self, _who, _from, card_str, success=None):
        self._validate_request(_who, _from, card_str, success)
        if self.players[_who].getProbabilityOf(card_str) > 0:
            self.players[_who].increaseGroupCardsProbability(card_str)
            self.players[_who].increaseAdjacentCardsProbability(card_str)

        if _from == self.AI.getName():
            self.currentPlayerName = self._handle_ai_request(_who, card_str)
        else:
            self.currentPlayerName = self._handle_player_request(_who, _from, card_str, success)

        if self.currentPlayerName == self.AI.getName():
            self._ai_action()

    def _ai_action(self):
        self._declare_group()
        self._ask_for_card()

    def _declare_group(self):
        for group in CardGroup.GROUP.keys():
            if CardGroup.can_declare(self.AI, self.AI.partner, group):
                std.info("I am declaring a group: %s" %group)
                for c in CardGroup.GROUP.get(group):
                    _with = self.AI if (self.AI.has_card(c)) else self.AI.partner
                    std.info("%s has card: %s" % (_with.getName(), _with.cards.get(c).display()))
                    # reset probabiliy to 0 for the declared group
                    self.AI.setProbabilityOf(c, 0)

    def _ask_for_card(self):
        available_groups = self.AI.get_available_groups()
        if(len(available_groups) == 0):
            std.info("I don't have any cards to ask now! I'm done")
            return
        opp0_card = self.opponents[0].fetchHighestProbabilityCard(available_groups)
        opp1_card = self.opponents[1].fetchHighestProbabilityCard(available_groups)

        if opp0_card is None and opp1_card is None:
            std.debug("Both opponents have no cards. game End!")
            return
        if opp0_card is None:
            _from, _which = (self.opponents[1], opp1_card)
        elif opp1_card is None:
            _from, _which = (self.opponents[0], opp0_card)
        else:
            _from, _which = (self.opponents[0], opp0_card) if (opp0_card.probability > opp1_card.probability) else (self.opponents[1], opp1_card)
        std.debug("probability of %s having '%s': %s" % (_from.getName(), _which.display(), _which.getProbability()))
        std.info("%s give me %s" % (_from.getName(), _which.display()))
        if _from.has_card(_which.short()):
            response = 'y'
            std.INPUT.enter()
        else:
            response = std.INPUT.yesno("does %s have the card?" %_from.getName(), ['y', 'n'])
        if response == 'y':
            std.info("Yay!")
            self.AI.setProbabilityOf(_which.short(), 100)
            _from.setProbabilityOf(_which.short(), 0)
            _from.partner.setProbabilityOf(_which.short(), 0)
            self.AI.partner.setProbabilityOf(_which.short(), 0)
            std.debug("AI got the card from %s." %_from.getName())
            self._ai_action()
        else:
            std.info("Darn it! :(")
            std.debug("this means p=0 for %s with %s" %(_which.display(), _from.getName()))
            std.debug("Also probability will increase for same card for other players")
            _from.setProbabilityOf(_which.short(), 0)
            self.AI.partner.increaseProbabilityOf(_which.short(), 50)
            _from.partner.increaseProbabilityOf(_which.short(), 50)
            self.currentPlayerName = _from.getName()


    def _validate_request(self, _who, _from, card_str, success):
        if _who not in self.players.keys() and _from not in self.players.keys():
            raise Exception("invalid player name. Valid players: %s" %self.players.keys())
        if self.currentPlayerName and self.currentPlayerName != _who:
            raise Exception("Cannot register request: its %s's turn" %self.currentPlayerName)
        if success == None and _from != self.AI.getName():
            raise Exception("Please provide status of request. y - if successful, n - if failed")

    def _handle_ai_request(self, _who, card_str):
        if self.AI.has_card(card_str):
            std.info("Damn! take it!")
            self.AI.setProbabilityOf(card_str, 0)
            self.players[_who].setProbabilityOf(card_str, 100)
            return _who
        else:
            std.info("Sorry! I don't have that card. It's my turn now!")
            self.players[_who].setProbabilityOf(card_str, 0)
            self.AI.partner.increaseProbabilityOf(card_str, 50)
            self.players[_who].partner.increaseProbabilityOf(card_str, 50)
            return self.AI.getName()

    def _handle_player_request(self, _who, _from, card_str, success):
        if success == 'y':
            self.players[_who].setProbabilityOf(card_str, 100)
            self.players[_from].setProbabilityOf(card_str, 0)
            std.debug("request registered")
            return _who
        else:
            self.players[_who].setProbabilityOf(card_str, 0)
            self.players[_from].setProbabilityOf(card_str, 0)
            if not self.AI.has_card(card_str):
                for name in self.players.keys():
                    if name not in [_who, _from, 'ai']:
                        self.players[name].setProbabilityOf(card_str, 100)
                        break
            std.debug("request registered")
            return _from


class Game:
    is_running = False

    def __init__(self):
        self.playerManager = PlayerManager()
        self.welcome_screen()
        self.playerManager.create_bot()
        CommandManager.register_commands(self)

    def init(self):
        self.init_players()
        self.input_ai_cards()

    def init_players(self):
        for i in range(0,3):
            name = std.input("Player %s name: " %i)
            self.playerManager.create_human_player(name)
        self.ask_for_partner()

    def ask_for_partner(self):
        try:
            partner_name = std.input("who is my partner: ")
            self.playerManager.assign_bot_partner(partner_name)
        except Exception as e:
            std.error(e)
            self.ask_for_partner()

    def input_ai_cards(self):
        cards = std.input("please provide my cards:").split(' ')
        try:
            self.playerManager.assign_bot_cards(cards)
        except Exception as e:
            std.error(e)
            self.input_ai_cards()

    def run(self):
        Game.is_running = True
        while(Game.is_running):
            command = std.INPUT.input(">>").split(' ')
            try:
                CommandManager.handle_command(self, command[0], *command[1:])
            except InvalidCommandException as e:
                std.error(e.message)
                std.info("available commands: %s" %e.available_commands)
            except Exception as e:
                traceback.print_exc()
                std.error(e)

    def print_player_probability(self, name):
        self.playerManager.players[name].printVerboseCards()

    def exit(self):
        Game.is_running = False

    def register_request(self,who_whom_str, card_str, success=None):
        _who,_from =  who_whom_str.split(':')
        self.playerManager.handle_request(_who, _from, card_str, success)

    def bot_turn(self):
        pass

    def print_player_turn(self):
        pass

    def print_ai_next_card(self):
        pass

    def print_has_card(self, player, card):
        std.OUTPUT.info(str(self.playerManager.players[player].has_card(card)))

    def welcome_screen(self):
        print "----------------============----------------"
        print "                W E L C O M E               "
        print "                      TO                    "
        print "             L I T E R A T U R E            "
        print "--------------------------------------------"

if __name__ == '__main__':
    game = Game()
    game.run()
