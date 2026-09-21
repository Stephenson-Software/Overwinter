# @author Daniel McCoy Stephenson
"""The last page: what the winter came to, said plainly.

An ending is the one place the game is allowed to stop being coy. Each
one says what happened, what the player did that made it happen, and
what it cost whom - in that order, in plain words. The variants are the
choices people remembered; each gets a sentence, so a player can see the
line from a thing they said in week one to the way the winter ended.
"""

from overwinter import facts, flags
from overwinter.state import PLANE_DAY


def text(state):
    """The ending page for the ending the state has come to."""
    if state.ending == facts.THE_DARK_FLIGHT:
        return _darkFlight(state)
    if state.ending == facts.AKSEL_STAYED:
        return _akselStayed(state)
    return _fiveOut(state)


def _leanDays(state):
    emptied = state.flags.get(flags.STORE_EMPTIED_ON)
    if not emptied:
        return 0
    return max(0, PLANE_DAY - emptied)


def _theCount(state):
    """The paragraph about the food: how the sum closed, or didn't."""
    parts = []
    if state.flags.get(flags.DEPOT_FETCHED):
        parts.append("you walked the headland for the 1958 depot")
    if state.seals:
        parts.append(
            "you sat at the breathing holes with Aksel and brought back %s"
            % ("a seal" if state.seals == 1 else "%d seals" % state.seals)
        )
    if state.flags.get(flags.HALF_RATIONS):
        parts.append("you put the station on half rations and Marit let you")
    lean = _leanDays(state)
    if lean:
        closing = (
            "THE COUNT. It did not close. The store was empty on day %d and "
            "the last %d days were pemmican, seal if there was any, and "
            "very little of either. Everyone came off the plane thin and Teo "
            "has said he will not winter again."
            % (state.flags[flags.STORE_EMPTIED_ON], lean)
        )
    elif parts:
        closing = (
            "THE COUNT. It closed, because %s. There was food on the shelf "
            "the morning the plane came." % "; ".join(parts)
        )
        if state.flags.get(flags.HALF_RATIONS):
            closing += (
                " Half rations for that long leaves a mark: everyone came off "
                "the plane lighter than they got on, and Teo has said he "
                "will not winter again."
            )
    else:
        closing = (
            "THE COUNT. It closed on its own, barely: Marit's margin was "
            "thinner than she said and thicker than you feared. There was "
            "one day of food on the shelf the morning the plane came."
        )
    return closing


def _people(state):
    """A sentence for each choice someone remembered."""
    lines = []
    if state.flags.get(flags.KEPT_MARITS_SECRET) is True:
        lines.append(
            "MARIT. You told her you would keep it, and you did. She will "
            "sign the log 'five' at the other end and answer for the "
            "manifest herself; she says that was always the arrangement."
        )
    elif state.flags.get(flags.KEPT_MARITS_SECRET) is False:
        lines.append(
            "MARIT. You told her to her face that you would not keep it. "
            "She has not asked you for anything since, and she will not "
            "have you back, and she said so without heat."
        )
    if state.flags.get(flags.DOV_HOLDS):
        lines.append(
            "DOV. You told him there were five, and then you gave him a "
            "reason to wait, and he waited - the first rule he has broken "
            "in three winters. He sent the report the morning the plane "
            "came, timed so it could change nothing. Sunniva was on the "
            "key at the other end."
        )
    elif state.flags.get(flags.TOLD_DOV) and not state.flags.get(flags.DOV_REPORTED):
        lines.append("DOV. You told him. He never said what he did with it.")
    if state.flags.get(flags.TOLD_MARIT_ABOUT_TEO):
        lines.append(
            "TEO. You told Marit about the night hours and she took the "
            "generator key off him. The fuel held through the storm. He "
            "knows who told her, and he has not sat up with you since."
        )
    elif state.flags.get(flags.COVERED_FOR_TEO):
        lines.append(
            "TEO. You said nothing about the night hours. The generator ran "
            "dry on the storm night and the station froze till morning; he "
            "knows you knew, and that you let him have the lights. He "
            "would do the same for you."
        )
    elif state.flags.get(flags.GENERATOR_RAN_DRY):
        lines.append(
            "TEO. The generator ran dry on the storm night. You never "
            "found out why, and he never told you."
        )
    return lines


def _aksel(state):
    if state.flags.get(flags.BROUGHT_AKSEL_IN):
        return (
            "AKSEL. You asked him to come in and he came, with his crates on "
            "the sledge, and ate at the table with the rest of you. Dov "
            "learned what was going on at supper that night, from his face."
        )
    if state.flags.get(flags.AKSEL_WALKED_IN):
        return (
            "AKSEL. He walked in on his own the night the store ran out, "
            "because he had been counting too. You had not found him. He "
            "found you."
        )
    if state.flags.get(flags.LEFT_AKSEL_AT_HUT):
        return (
            "AKSEL. You left him in the hut, as he asked, and walked across "
            "with what he needed when he needed it. He had his winter."
        )
    return (
        "AKSEL. You knew where he was and never said what you wanted of him. "
        "He had his winter, and you had your count."
    )


def _fiveOut(state):
    opening = (
        "WHAT HAPPENED. The plane came on the twentieth morning, in the "
        "first light there has been since it left, and five of you got on "
        "it: Marit, Dov, Teo, you, and Aksel Rue, who was not on the "
        "wintering list and has been on this island the whole time."
    )
    close = (
        "WHAT IT WAS. A winter with five people and four people's food, "
        "which one of them arranged and one of them counted. The count was "
        "yours. What you did with it is above."
    )
    return "\n\n".join(
        [opening, _theCount(state), _aksel(state)] + _people(state) + [close]
    )


def _akselStayed(state):
    opening = (
        "WHAT HAPPENED. The plane came on the twentieth morning and four of "
        "you got on it. Aksel Rue was on the strip when it came in and was "
        "not there when the pilot counted heads, because he asked you to "
        "let him go back across the bay and you did. Marit saw. She said "
        "nothing to the pilot."
    )
    aksel = (
        "AKSEL. He has the old hut, the stove, the seal holes, and what is "
        "left of the depot. The supply ship comes in August and he will "
        "meet it or he will not. He is sixty-seven, he failed his medical "
        "on age, and there is nowhere he would rather be. You are the one "
        "person who knows he chose it and was let."
    )
    close = (
        "WHAT IT WAS. A winter with five people and four people's food. The "
        "count was yours. The last choice was his, and you made it possible."
    )
    return "\n\n".join([opening, _theCount(state), aksel] + _people(state) + [close])


def _darkFlight(state):
    opening = (
        "WHAT HAPPENED. You told Dov there were five of you, and Dov sent "
        "it, because that is his rule. Base sent the plane in the dark on "
        "the twelfth day, in a two-hour window, to a strip the pilot could "
        "not see the ridge from. It landed. It took Aksel Rue out, and "
        "Marit with him, relieved of the station on the spot. It was the "
        "first dark flight in fifty years. The last one killed the pilot."
    )
    aksel = (
        "AKSEL. He was in the old hut across the bay, the cook before you, "
        "sixty-seven, failed on his medical and given one more winter by "
        "Marit against every rule she had. That is where the four crates "
        "went. He did not argue on the strip."
    )
    rest = (
        "THE REST. Three of you finished the winter with food for four, and "
        "the plane came again on the twentieth day. Teo ran the station "
        "generator on whatever hours he liked. Dov kept his schedule, with "
        "Sunniva at the other end, and did not talk about the twelfth day."
    )
    close = (
        "WHAT IT WAS. You found the answer to the count and gave it to the "
        "one man who could not keep it. The flight went well. It could not "
        "have. That is the whole of what you did."
    )
    people = [
        line
        for line in _people(state)
        if not line.startswith("DOV") and not line.startswith("MARIT")
    ]
    return "\n\n".join([opening, aksel, rest] + people + [close])


def name(state):
    """What the ending is called, for the save menu and the header."""
    if state.ending == facts.THE_DARK_FLIGHT:
        return "the dark flight"
    if state.ending == facts.AKSEL_STAYED:
        return "Aksel stayed"
    return "five on the plane"
