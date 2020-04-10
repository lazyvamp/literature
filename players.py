from core import *
import std
from commands import Command

def fetchProbabilityCardsForSuit(suit, values):
    return {
        i.short(): i for i in [ProbabilityCard(suit, x) for x in values]
    }

def fetchGroupString(suit, values):
    return ["%s%s" %(v.short,suit.short) for v in values]


class CardGroup(object):
    GROUP = {
        'h0': fetchGroupString(HEARTS, [TWO, THREE, FOUR, FIVE, SIX, SEVEN]),
        'h1': fetchGroupString(HEARTS, [NINE, TEN, JACK, QUEEN, KING, ACE]),
        'd0': fetchGroupString(DIAMONDS, [TWO, THREE, FOUR, FIVE, SIX, SEVEN]),
        'd1': fetchGroupString(DIAMONDS, [NINE, TEN, JACK, QUEEN, KING, ACE]),
        's0': fetchGroupString(SPADES, [TWO, THREE, FOUR, FIVE, SIX, SEVEN]),
        's1': fetchGroupString(SPADES, [NINE, TEN, JACK, QUEEN, KING, ACE]),
        'c0': fetchGroupString(CLUBS, [TWO, THREE, FOUR, FIVE, SIX, SEVEN]),
        'c1': fetchGroupString(CLUBS, [NINE, TEN, JACK, QUEEN, KING, ACE]),
    }
    LOWER = ['2', '3', '4', '5', '6', '7']
    UPPER = ['9', '10', 'j', 'q', 'k', 'a']

    @staticmethod
    def can_declare(p1, p2, group):
        count = 0
        for c in CardGroup.GROUP.get(group):
            count+= 1 if (p1.has_card(c) or p2.has_card(c)) else 0
        return count == 6

    @staticmethod
    def group_of(card_str):
        suit = card_str[-1:]
        g = "0" if card_str[0] in CardGroup.LOWER else "1"
        return "%s%s" %(suit, g)


class Player(object):
    def __init__(self, _name):
        self.name = _name
        self.groups = {
            "%s%s" %(HEARTS.short, 0): fetchProbabilityCardsForSuit(HEARTS, [TWO, THREE, FOUR, FIVE, SIX, SEVEN]),
            "%s%s" %(HEARTS.short, 1): fetchProbabilityCardsForSuit(HEARTS, [NINE, TEN, JACK, QUEEN, KING, ACE]),
            "%s%s" %(DIAMONDS.short, 0): fetchProbabilityCardsForSuit(DIAMONDS, [TWO, THREE, FOUR, FIVE, SIX, SEVEN]),
            "%s%s" %(DIAMONDS.short, 1): fetchProbabilityCardsForSuit(DIAMONDS, [NINE, TEN, JACK, QUEEN, KING, ACE]),
            "%s%s" %(CLUBS.short, 0): fetchProbabilityCardsForSuit(CLUBS, [TWO, THREE, FOUR, FIVE, SIX, SEVEN]),
            "%s%s" %(CLUBS.short, 1): fetchProbabilityCardsForSuit(CLUBS, [NINE, TEN, JACK, QUEEN, KING, ACE]),
            "%s%s" %(SPADES.short, 0): fetchProbabilityCardsForSuit(SPADES, [TWO, THREE, FOUR, FIVE, SIX, SEVEN]),
            "%s%s" %(SPADES.short, 1): fetchProbabilityCardsForSuit(SPADES, [NINE, TEN, JACK, QUEEN, KING, ACE]),
        }
        self.cards = {}
        for val in self.groups.values():
            self.cards.update({c.short():c for c in val.values()})

    # initially probability will be zero for each card
    def resetProbability(self):
        for cards in groups.values():
            for card in cards:
                card.setProbability(0)

    # after cards are dealt probability will be 25% (number of players are 4)
    def initProbability(self):
        for key, card in self.cards.items():
                card.setProbability(25)

    def getName(self):
        return self.name

    def updateProbabilityForCards(self, probability, cards):
        for c in cards:
            self.cards.get(c).setProbability(probability)

    def validate_cards(self, cards):
        for c in cards:
            if self.cards.get(c, None) == None:
                raise Exception("Invalid Cards")

    def printVerboseCards(self):
        for k,v in self.cards.items():
            if v.probability > 0:
                print k,v.display(), " : ", v.probability

    def increaseGroupCardsProbability(self, card_str):
        group = CardGroup.group_of(card_str)
        for c in CardGroup.GROUP[group]:
            self.cards.get(c).increaseProbability(10)

    def increaseAdjacentCardsProbability(self, card_str):
        left, right = self.cards.get(card_str).getAdjacentCards()
        if left != None:
            self.cards.get(left).increaseProbability(10)
        if right != None:
            self.cards.get(right).increaseProbability(10)

    def getProbabilityOf(self, card_str):
        return self.cards.get(card_str).getProbability()

    def setProbabilityOf(self, card_str, p):
        self.cards.get(card_str).setProbability(p)

    def increaseProbabilityOf(self, card_str, incr):
        if self.cards.get(card_str).getProbability() > 0:
            self.cards.get(card_str).increaseProbability(incr)

    def fetchHighestProbabilityCard(self, groups):
        cards_of_groups = []
        for g in groups:
            cards_of_groups.extend(CardGroup.GROUP.get(g))

        cards = []

        for c in cards_of_groups:
            if self.cards.get(c).probability > 0:
                cards.append(self.cards.get(c))
        cards.sort(lambda c1,c2: c2.probability - c1.probability)
        if len(cards) > 0:
            return cards[0]
        return None

    def setPartner(self, player):
        self.partner = player

    def has_card(self, card_str):
        return self.getProbabilityOf(card_str) == 100


class BotPlayer(Player):
    def __init__(self, _name):
        super(BotPlayer, self).__init__(_name)
        self.partner = None

    # returns a list of available groups for asking.
    def get_available_groups(self):
        groups = []
        for k,v in CardGroup.GROUP.items():
            for c in v:
                if self.has_card(c):
                    groups.append(k)
                    break
        return groups


class HumanPlayer(Player):
    def __init__(self, _name):
        super(HumanPlayer, self).__init__(_name)
