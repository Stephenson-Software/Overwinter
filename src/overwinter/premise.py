# @author Daniel McCoy Stephenson
"""The story, said plainly.

Everything here is also in the facts, the crew's mouths and the endings -
but scattered, in character, and in the order the player happens to find
it. This is the same story told straight, in the journal, growing as the
player learns: each paragraph is shown once its facts are known, so it
never says more than the player has earned, and never less than they
have.

It exists because a playtester of the last game finished an ending and
said: I got no answers. The answers were there. They were not in one
place, in plain words. This page is built in from the first day.
"""

from overwinter import facts

OPENING = (
    "Cape Ferrin weather station. Four huts on a gravel strip between the "
    "ridge and the bay, on an island that has no other people on it. The "
    "plane that brought you here left an hour ago and cannot come back "
    "until there is light enough to land on: twenty days. You are the "
    "cook. You took the job because nobody else would, and because there "
    "was nothing else."
    "\n\n"
    "There are three others. Marit Solheim runs the station; this is her "
    "eighth winter. Dov Lindqvist keeps the radio and sends the weather to "
    "Base twice a day. Teo Brandt keeps the generator; it is his first "
    "winter, like yours."
    "\n\n"
    "The store is in the galley, and the store is your job. Nobody has "
    "asked you to count it."
)

# (needed facts, paragraph). Shown in order; a paragraph appears once every
# fact it needs is known. The first needs nothing.
PARAGRAPHS = [
    (
        (),
        "WHERE YOU ARE. A weather station on an island, four people, the "
        "polar dark, and twenty days until a plane can land. You are the "
        "cook, and the food is yours to count.",
    ),
    (
        (facts.THE_STORE,),
        "WHAT IS HAPPENING TO YOU. There is not enough food. Fifteen days "
        "of it, at four, and the plane comes on the twentieth. Nobody has "
        "said so, and the woman who signed for it does not miscount. "
        "Something is being kept from you, and it is being kept in your "
        "own galley. Everything you learn about this station goes in your "
        "journal; under each thing is where it points that you have not "
        "been. That is how you will find out.",
    ),
    (
        (facts.THE_MANIFEST,),
        "WHAT IS MISSING. Four crates. They were landed and signed for and "
        "they are not in the store. Twenty-four days of food for one "
        "person, or six for four.",
    ),
    (
        (facts.THE_SLEDGE, facts.THE_OLD_HUT),
        "WHERE IT WENT. Across the bay, on the sledge, before you arrived. "
        "There is a hut over there with a stove in it.",
    ),
    (
        (facts.THE_FIFTH,),
        "WHO IS OVER THERE. Aksel Rue, the cook before you, who was on the "
        "ship out in August on paper and never went. There are five people "
        "on this island and the paperwork says four. The four crates are "
        "his, and they are why your store is short: Marit gave him a share "
        "of the station's food to winter on.",
    ),
    (
        (facts.AKSELS_WINTER,),
        "WHY. He is sixty-seven and failed his medical on age, and was told "
        "he would not winter again. He asked Marit for one more, and there "
        "is nowhere else he wants to be. She said yes.",
    ),
    (
        (facts.MARITS_ARITHMETIC,),
        "MARIT'S SUM. She signed him off the manifest and carried his crates "
        "across. The station's gap she meant to close with the old depot "
        "on the headland and the seals off the point, once the ice held. "
        "The ice held late and the storm is coming, and she told nobody, "
        "because the one person who would have to report it is Dov.",
    ),
    (
        (facts.THE_RULE,),
        "DOV'S RULE. A person not on the wintering list is reported to Base "
        "on the next schedule, and Base sends a flight. Dov does not break "
        "rules. That is why he has not been told.",
    ),
    (
        (facts.DOVS_GAME,),
        "WHAT DOV HAS. The nightly chess by Morse is with Sunniva, the "
        "operator at Base, and it is not chess. It is the one thing on this "
        "island that is his, and it is why the schedule is sacred to him - "
        "and why, if anyone could talk him into waiting, it would be in her "
        "name.",
    ),
    (
        (facts.SEVENTY_ONE,),
        "WHAT A FLIGHT COSTS. In 1971 Base sent the plane in the dark for a "
        "man with a fever. It went into the ridge and the pilot died; the "
        "man got better on his own. Reporting Aksel means asking a "
        "stranger to try that again.",
    ),
    (
        (facts.THE_DEPOT, facts.THE_SEALS),
        "HOW THE SUM CLOSES. The 1958 depot on the headland is worth about "
        "three days at four. A seal, with Aksel at the hole, is two. Half "
        "rations double whatever is left, at a cost. Any two of those and "
        "there is food on the shelf when the plane comes.",
    ),
    (
        (facts.TEOS_NIGHTS,),
        "THE OTHER COUNT. Teo has been running the generator all night "
        "because he cannot sleep in the dark. The storm margin of fuel is "
        "gone. Marit can fix that if she knows; Teo will know who told her.",
    ),
    (
        (facts.THE_DARK_FLIGHT,),
        "WHAT YOU DID. You told Dov, and Dov sent it, and the plane came in "
        "the dark on the twelfth day and took Aksel and Marit. It landed. "
        "It could not have. Three of you finished the winter.",
    ),
    (
        (facts.FIVE_OUT,),
        "WHAT YOU DID. You found where the food went and who was eating it, "
        "and made the count close - or didn't - and five of you got on the "
        "plane on the twentieth day. The last page of the journal says "
        "what it cost.",
    ),
    (
        (facts.AKSEL_STAYED,),
        "WHAT YOU DID. Four of you got on the plane. Aksel asked to go back "
        "across the bay and you let him. The ship comes in August.",
    ),
]


def text(state):
    """The story so far, in plain words, for the journal."""
    shown = [p for needed, p in PARAGRAPHS if all(state.knows(f) for f in needed)]
    known = len(shown)
    footer = "\n\n(%d of %d parts of the story known. The rest is on the station.)" % (
        known,
        len(PARAGRAPHS),
    )
    return "\n\n".join(shown) + footer
