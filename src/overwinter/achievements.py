# @author Daniel McCoy Stephenson
"""Achievements on arcade, reported through tak.arcade (Stephenson-Software
RFC 0014).

Knowledge is the progression in Overwinter, so the achievements are facts:
the first count, the manifest, the old depot, the answer to the count,
everything the station can tell you, and each of the three ways the winter
ends. One more is for the first choice someone will hold you to.

Every id below is declared for the game in the gateway's
config/play/boards.yaml; an id is permanent once it has been used, so a row
here may be retitled but never renamed. Reporting is fire-and-forget:
tak.arcade does nothing off arcade, signed out, or in tests, and never
raises. Nothing here reads or writes the save beyond looking at what the
state already knows - an achievement is never stored in the save file.
"""

from tak import arcade

from overwinter import facts, flags, people

ACHIEVEMENTS = [
    {
        "id": "counted",
        "title": "Counted",
        "description": "Count the station's store for yourself",
        "hidden": False,
    },
    {
        "id": "signed-for",
        "title": "Signed For",
        "description": "Find out what was landed in September",
        "hidden": False,
    },
    {
        "id": "old-stores",
        "title": "Old Stores",
        "description": "Find what an earlier winter left behind",
        "hidden": False,
    },
    {
        "id": "the-answer",
        "title": "The Answer to the Count",
        "description": "Find out where the missing food went",
        "hidden": False,
    },
    {
        "id": "the-whole-winter",
        "title": "The Whole Winter",
        "description": "Learn everything the station can tell you",
        "hidden": False,
    },
    {
        "id": "remembered",
        "title": "They Will Remember That",
        "description": "Make a choice someone will hold you to",
        "hidden": False,
    },
    {
        "id": "twentieth-morning",
        "title": "The Twentieth Morning",
        "description": "See the winter through to the plane",
        "hidden": False,
    },
    {
        "id": "in-the-dark",
        "title": "In the Dark",
        "description": "End the winter before the plane was due",
        "hidden": False,
    },
    {
        "id": "his-choice",
        "title": "His Choice",
        "description": "Let Aksel stay on the island",
        "hidden": True,
    },
]

IDS = [achievement["id"] for achievement in ACHIEVEMENTS]

# Facts that are achievements the moment they are learned. The endings are
# facts too: each is learned at the moment its winter ends.
FACT_ACHIEVEMENTS = {
    facts.THE_STORE: "counted",
    facts.THE_MANIFEST: "signed-for",
    facts.THE_DEPOT: "old-stores",
    facts.THE_FIFTH: "the-answer",
    facts.FIVE_OUT: "twentieth-morning",
    facts.THE_DARK_FLIGHT: "in-the-dark",
    facts.AKSEL_STAYED: "his-choice",
}

# Everything the station can tell you: every fact but the endings.
CLUE_FACTS = [fact for fact in facts.FACTS if fact not in facts.ENDINGS]
WHOLE_WINTER = "the-whole-winter"
REMEMBERED = "remembered"


def unlock(achievementId):
    """Report one unlock. Idempotent on the service; never raises."""
    try:
        arcade.unlock(achievementId)
    except Exception:
        pass


def factLearned(state, factId):
    """A fact was just learned for the first time."""
    achievementId = FACT_ACHIEVEMENTS.get(factId)
    if achievementId is not None:
        unlock(achievementId)
    if factId in CLUE_FACTS and _knowsEveryClue(state):
        unlock(WHOLE_WINTER)


def choiceRemembered():
    """Someone will hold the player to a choice."""
    unlock(REMEMBERED)


def catchUp(state):
    """Report what a loaded save has already earned, so a winter played
    before achievements existed still counts. Only reads the state."""
    for factId in state.facts:
        achievementId = FACT_ACHIEVEMENTS.get(factId)
        if achievementId is not None:
            unlock(achievementId)
    if _knowsEveryClue(state):
        unlock(WHOLE_WINTER)
    if _rememberedSomething(state):
        unlock(REMEMBERED)


def _rememberedSomething(state):
    # Flags are never forgotten in Overwinter, so a remembered choice is
    # still on the state: any of the ones people hold you to, or the last
    # one on the strip.
    if flags.BACKED_AKSEL_STAYING in state.flags:
        return True
    return any(flag in state.flags for flag in people.REMEMBERED)


def _knowsEveryClue(state):
    return all(state.knows(fact) for fact in CLUE_FACTS)
