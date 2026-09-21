# @author Daniel McCoy Stephenson
"""What the station shows the player, and when - see tak.progression.

Conditions read the State: everything that gates a menu in Overwinter is
knowledge, and knowledge lives there. An unlock announces itself once and
stays; the outside menu greys the rows it has not earned yet with the
reason, so the player always knows what is being kept from them and why.
"""

from tak import Progression

from overwinter import facts

JOURNAL = "journal"
THE_BAY = "the_bay"
THE_HEADLAND = "the_headland"
THE_HOLES = "the_holes"

UNLOCKS = [
    {
        "id": JOURNAL,
        "name": "your journal",
        "announcement": "Things worth keeping should be written down. There's "
        "a notebook in your bunk; the page called 'What is happening to you' "
        "says the story so far, plainly, as far as you know it.",
        "condition": lambda state: bool(state.facts),
    },
    {
        "id": THE_BAY,
        "name": "the far shore",
        "announcement": "There's a hut across the bay with a stove in it. The "
        "strip runs down to the ice; when the ice holds, it's an hour across.",
        "condition": lambda state: state.knows(facts.THE_OLD_HUT),
    },
    {
        "id": THE_HEADLAND,
        "name": "the headland",
        "announcement": "The 1958 depot is a cairn on the headland, an "
        "afternoon's walk from the strip. Whatever is still good in it is "
        "food nobody has counted.",
        "condition": lambda state: state.knows(facts.THE_DEPOT),
    },
    {
        "id": THE_HOLES,
        "name": "the breathing holes",
        "announcement": "Aksel will take you out to the holes off the point on "
        "a still day. A seal is two days of food for the station.",
        "condition": lambda state: state.knows(facts.THE_SEALS),
    },
]

progression = Progression(UNLOCKS)


def isUnlocked(state, featureId):
    return progression.isUnlocked(state.unlocked, featureId)


def getNextUnlock(state):
    return progression.getNextUnlock(state, state.unlocked)


def catchUp(state):
    progression.catchUp(state, state.unlocked)
