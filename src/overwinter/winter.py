# @author Daniel McCoy Stephenson
"""The clock, the winter's calendar, and what the end of each day does.

Every action a scene offers costs a watch and goes through advance(). Three
watches make a day, and the end of a day is where the winter happens: the
store is eaten, the calendar fires - the ice holding, the storm, the dark
flight if it was called, the plane on the twentieth morning - and the
count is checked. Scenes never decide any of that for themselves; they
ask here, so the journal's calendar and the scenes can never disagree.
"""

from overwinter import facts, flags
from overwinter.state import (
    AKSEL_FLOWN,
    AKSEL_HUT,
    AKSEL_STATION,
    DARK_FLIGHT_DAY,
    ICE_SAFE_DAY,
    MORNING,
    PLANE_DAY,
    STORM_DAYS,
    WATCHES,
)

# The line each fixed day opens with. Shown once, on the morning.
DAY_LINES = {
    ICE_SAFE_DAY: "Third still night. Marit says the bay ice will hold now - "
    "an hour across to the far shore, if anyone had a reason to go.",
    STORM_DAYS[0]: "The wind has gone round to the north-east and the "
    "anemometer is pinned. Storm. Marit's order is that nobody goes past "
    "the door until it drops.",
    STORM_DAYS[-1] + 1: "The wind dropped in the night. The drifts are to the "
    "eaves on the north side. Outside is open again.",
}


class Outcome:
    """What an advance() had to say, and whether the winter ended.

    lines are shown to the player in order. dayEnded is True when the
    watch rolled over. ending is set when the winter came to one."""

    def __init__(self):
        self.lines = []
        self.dayEnded = False
        self.ending = None


def watchName(state):
    return WATCHES[state.watch]


def advance(game, watches=1):
    """Move the clock a watch at a time, ending the day when it rolls."""
    outcome = Outcome()
    state = game.state
    for _ in range(watches):
        if state.over:
            break
        state.watch += 1
        if state.watch >= len(WATCHES):
            endDay(game, outcome)
    return outcome


def endDay(game, outcome=None):
    """The night: the store is eaten, the day turns, the calendar fires."""
    outcome = outcome if outcome is not None else Outcome()
    state = game.state
    outcome.dayEnded = True
    state.flags.pop(flags.HUNTED_TODAY, None)

    _theSchedule(game, outcome)
    _eat(game, outcome)

    state.day += 1
    state.watch = MORNING

    line = DAY_LINES.get(state.day)
    if line:
        outcome.lines.append(line)
    if state.day == STORM_DAYS[0] + 1:
        _stormNight(game, outcome)
    if state.day == DARK_FLIGHT_DAY and state.flags.get(flags.DOV_REPORTED):
        _darkFlight(game, outcome)
    elif state.day >= PLANE_DAY and not state.over:
        state.flags[flags.PLANE_ON_STRIP] = True
        state.location = "strip"
        outcome.lines.append(
            "There is light on the ridge - not much, a grey line - and Dov "
            "has had the Otter on the set since six. It is coming. Marit "
            "wants everyone on the strip."
        )
    return outcome


def _theSchedule(game, outcome):
    """Dov was told there are five, and nobody gave him a reason to wait.
    Walking away from that conversation is a choice too."""
    state = game.state
    if not state.flags.get(flags.TOLD_DOV):
        return
    if state.flags.get(flags.DOV_HOLDS) or state.flags.get(flags.DOV_REPORTED):
        return
    state.flags[flags.DOV_REPORTED] = True
    outcome.lines.append(
        "At twenty hundred Dov sent the weather, and after it, a second "
        "message. You had told him there were five and you had not given "
        "him a reason to wait, and he had asked you for one. Base has it. "
        "[Dov will remember that.]"
    )


def _eat(game, outcome):
    state = game.state
    if state.akselAt == AKSEL_HUT:
        state.akselFood = max(0, state.akselFood - 1)
    needed = state.dailyRations
    state.food = max(0, state.food - needed)
    if state.food > 0 or flags.STORE_EMPTIED_ON in state.flags:
        return
    state.flags[flags.STORE_EMPTIED_ON] = state.day
    outcome.lines.append(
        "The store is empty. You scraped the last tin tonight and said so, "
        "and nobody at the table said anything back."
    )
    if state.akselAt == AKSEL_HUT:
        # The station eating his margin brings him in whether or not anyone
        # went looking for him: the mystery answers itself, at the worst time.
        state.akselAt = AKSEL_STATION
        state.flags[flags.AKSEL_WALKED_IN] = True
        carried = state.akselFood
        state.akselFood = 0
        state.food += carried
        newly = game.learn(facts.THE_FIFTH)
        outcome.lines.append(
            "An hour after supper a man walked in out of the dark with a "
            "sledge behind him and %s on it. Marit stood up. 'Aksel,' she "
            "said. Aksel Rue, the cook before you, who has been in the old "
            "hut across the bay since August with the four crates that are "
            "not in your store. He put them on the table.%s"
            % (
                "what was left of the station's crates" if carried else "nothing much",
                " Nobody had told you there were five of you." if newly else "",
            )
        )


def _stormNight(game, outcome):
    """The first night of the storm is the night the fuel margin matters."""
    state = game.state
    if state.flags.get(flags.TOLD_MARIT_ABOUT_TEO):
        outcome.lines.append(
            "The generator ran through the night on the hours Marit set, "
            "and no more. The heaters held. Dov kept his schedule."
        )
        return
    state.flags[flags.GENERATOR_RAN_DRY] = True
    outcome.lines.append(
        "At three in the morning the generator stopped. The heaters went "
        "with it and the station was at minus twenty by six. Teo had it "
        "running again by the morning watch on the last of the day-tank, "
        "grey in the face; the night hours had drunk the storm margin. Dov "
        "missed his evening schedule for the first time in three winters."
    )


def _darkFlight(game, outcome):
    state = game.state
    state.akselAt = AKSEL_FLOWN
    state.ending = facts.THE_DARK_FLIGHT
    game.learn(facts.THE_DARK_FLIGHT)
    outcome.ending = facts.THE_DARK_FLIGHT
    outcome.lines.append(
        "Day twelve. Base called at eight with a window - two hours of wind "
        "under thirty - and the Otter was on the strip by ten, in a dark "
        "you could not see the ridge in. It took Aksel, who did not argue, "
        "and Marit, who was told to get on it."
    )


def calendar(state):
    """The winter as the player knows it, for the journal: (day, line) pairs.

    The plane day is common knowledge from the first morning. The ice and
    the storm are listed once they have been lived through or read up;
    the dark flight only if it is coming."""
    rows = [(PLANE_DAY, "The plane. Light enough on the strip; the Otter comes.")]
    if state.knows(facts.THE_ICE) or state.day >= ICE_SAFE_DAY:
        rows.append((ICE_SAFE_DAY, "The bay ice holds. The old hut is an hour across."))
    if state.day >= STORM_DAYS[0]:
        rows.append((STORM_DAYS[0], "The storm. Two days; nobody goes out."))
    if state.flags.get(flags.DOV_REPORTED) and not state.over:
        rows.append((DARK_FLIGHT_DAY, "Base sends the plane in the dark."))
    return sorted(rows)
