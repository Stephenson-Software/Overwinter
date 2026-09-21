# @author Daniel McCoy Stephenson
from tak import formatHour

from overwinter import endings, facts, flags
from overwinter.state import AKSEL_STATION, PLANE_DAY, WATCH_HOURS
from overwinter.winter import watchName

LOCATION_NAMES = {
    "galley": "The Galley",
    "office": "Marit's Office",
    "radio": "The Radio Room",
    "shed": "The Generator Shed",
    "bunks": "The Bunkroom",
    "strip": "The Strip",
    "hut": "The Old Hut",
    "journal": "Your Journal",
    "epilogue": "After",
}


def buildHeader(game):
    """The status line: the day, the watch, where the player is, the count,
    the weather, how much they know."""
    state = game.state
    if state.over:
        first = "After %s" % endings.name(state)
    else:
        first = "Day %d of %d" % (state.day, PLANE_DAY)
    chips = [first]
    if not state.over:
        chips.append(
            "%s, %s" % (watchName(state), formatHour(WATCH_HOURS[state.watch]))
        )
    chips.append(LOCATION_NAMES.get(state.location, ""))
    if state.knows(facts.THE_STORE) and not state.over:
        foodChip = {"text": "Food: %d days" % state.foodDays}
        if state.foodDays < state.daysUntilPlane:
            foodChip["class"] = "low"
        chips.append(foodChip)
    if state.stormy:
        chips.append({"text": "Storm", "class": "low"})
    if state.flags.get(flags.HALF_RATIONS):
        chips.append("Half rations")
    if state.akselAt == AKSEL_STATION:
        chips.append("Five at the table")
    chips.append("Known: %d/%d" % (len(state.facts), len(facts.FACTS)))
    return {"title": "Overwinter - %s" % first, "chips": chips}
