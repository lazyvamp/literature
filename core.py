class Suit:
    def __init__(self, _short, _full, _display):
        self.short = _short
        self.full = _full
        self.display = _display
HEARTS = Suit("h", "heart", "Heart")
DIAMONDS = Suit("d", "diamond", "Diamond")
CLUBS = Suit("c", "club", "Club")
SPADES = Suit("s", "spade", "Spade")

class Value:
    def __init__(self, _short, _full, _display):
        self.short = _short
        self.full = _full
        self.display = _display

TWO = Value("2", "two", "2")
THREE = Value("3", "three", "3")
FOUR = Value("4", "four", "4")
FIVE = Value("5", "five", "5")
SIX = Value("6", "six", "6")
SEVEN = Value("7", "seven", "7")
EIGHT = Value("8", "eight", "8")
NINE = Value("9", "nine", "9")
TEN = Value("10", "ten", "10")
JACK = Value("j", "jack", "Jack")
QUEEN = Value("q", "queen", "Queen")
KING = Value("k", "king", "King")
ACE = Value("a", "ace", "Ace")

class Card(object):
    def __init__(self, _suit, _value):
        self.suit = _suit
        self.value = _value

    def display(self):
        return "%s of %s" %(self.value.display, self.suit.display)

    def short(self):
        return "%s%s" %(self.value.short, self.suit.short)

    def __str__(self):
        return "%s of %s" %(self.value.display, self.suit.display)

    def __repr__(self):
        return "%s of %s" %(self.value.display, self.suit.display)

    def getAdjacentCards(self):
        left, right = None, None
        if self.value == ACE:
            return Card(self.suit, KING).short(), None
        if self.value == KING:
            return Card(self.suit, QUEEN).short(), Card(self.suit, ACE).short()
        if self.value == QUEEN:
            return Card(self.suit, JACK).short(), Card(self.suit, KING).short()
        if self.value == JACK:
            return Card(self.suit, TEN).short(), Card(self.suit, QUEEN).short()
        if self.value == TEN:
            return Card(self.suit, NINE).short(), Card(self.suit, JACK).short()
        if self.value == NINE:
            return None, Card(self.suit, TEN).short()
        if self.value == SEVEN:
            return Card(self.suit, SIX).short(), None
        if self.value == SIX:
            return Card(self.suit, FIVE).short(), Card(self.suit, SEVEN).short()
        if self.value == FIVE:
            return Card(self.suit, FOUR).short(), Card(self.suit, SIX).short()
        if self.value == FOUR:
            return Card(self.suit, THREE).short(), Card(self.suit, FIVE).short()
        if self.value == THREE:
            return Card(self.suit, TWO).short(), Card(self.suit, FOUR).short()
        if self.value == TWO:
            return None, Card(self.suit, THREE).short()



class ProbabilityCard(Card):
    def __init__(self, _suit, _value):
        super(ProbabilityCard, self).__init__(_suit, _value)
        self.probability = 0

    def getProbability(self):
        return self.probability

    def setProbability(self, _p):
        self.probability = _p

    def increaseProbability(self, incr):
        self.probability = min(self.probability+incr, 100)

    def decreaseProbability(self, decr):
        self.probability = max(0, self.probability - decr)
