# @author Daniel McCoy Stephenson
"""The four other people on the island, and what they will say to someone
who knows enough.

Every conditional line is gated on a fact or a choice, never on the day:
what opens a door in Overwinter is what you know. Responses that teach
something are callables, so the fact is learned when the line is heard
and not when the menu is built. Some questions are choices, not
questions - they set a flag that nothing forgets - and the scene says
"X will remember that" after them.
"""

from tak import NPC

from overwinter import facts
from overwinter.flags import (
    AKSEL_WALKED_IN,
    BROUGHT_AKSEL_IN,
    COVERED_FOR_TEO,
    DOV_HOLDS,
    DOV_REPORTED,
    GENERATOR_RAN_DRY,
    KEPT_MARITS_SECRET,
    LEFT_AKSEL_AT_HUT,
    MARIT_APPROVED_HALF,
    MET_TEO,
    TOLD_DOV,
    TOLD_MARIT_ABOUT_TEO,
)
from overwinter.state import AKSEL_HUT, AKSEL_STATION, STORM_DAYS


def marit(game):
    state = game.state

    def aboutTheStore():
        return (
            "Fifteen days. (She does not look up from the barograph.) You "
            "counted it, then. Good; that is what the cook is for. I signed "
            "for what was landed. Count it again on the fifth day, when the "
            "ice holds, and come and tell me the figure."
        )

    def aboutTheManifest():
        return (
            "Dov gave you the manifest. (Now she looks up.) Then you know what "
            "I signed for, and you know what is on the shelf, and you can do "
            "a sum, and you have. I am not going to do it for you. Nothing "
            "on this island is lost. Everything on it is somewhere."
        )

    def herArithmetic():
        game.learn(facts.MARITS_ARITHMETIC)
        return (
            "(She closes the log.) Yes. I signed him off the ship and I took "
            "his crates across on the sledge the week before the plane, "
            "before the bay went. Four crates is what he eats in a winter. "
            "The station's gap I meant to close myself: the '58 depot on the "
            "headland, once the ice held, and the seals off the point, which "
            "Aksel can get and I cannot. The ice held late this year and "
            "there is a storm coming and I have not been across. The sum "
            "still closes. I did not mean anyone to have to check it, and I "
            "did not tell you because the one person who would have to "
            "report it is Dov, and Dov reports things. (A pause.) So. Now "
            "you know what I know. What are you going to do with it?"
        )

    def undecidedAboutTheSecret():
        return (
            state.knows(facts.MARITS_ARITHMETIC)
            and KEPT_MARITS_SECRET not in state.flags
        )

    def keepIt():
        state.flags[KEPT_MARITS_SECRET] = True
        return (
            "(She nods once.) Then it is yours as much as mine. I will sign "
            "the log 'five' at the other end and answer for it; that was "
            "always the arrangement. Count the store. Tell me the figure."
        )

    def wontKeepIt():
        state.flags[KEPT_MARITS_SECRET] = False
        return (
            "(She looks at you for a while without anything in her face.) "
            "That is your right. I will not ask you again. Close the door on "
            "your way out."
        )

    def halfRations():
        if state.knows(facts.MARITS_ARITHMETIC):
            state.flags[MARIT_APPROVED_HALF] = True
            return (
                "Half rations. (She thinks about it.) Yes. If you are asking, "
                "you have done the sum, and it is your store. Set it when you "
                "judge, and tell them at the table yourself. It leaves a "
                "mark, half rations - on Teo most. You will see it."
            )
        return (
            "No. Half rations in the second week of a winter is how you get "
            "a station that does not speak to each other by the fourth. "
            "Count it again. Then we will talk."
        )

    def undecidedAboutTeo():
        return (
            state.knows(facts.TEOS_NIGHTS)
            and TOLD_MARIT_ABOUT_TEO not in state.flags
            and COVERED_FOR_TEO not in state.flags
            and state.day <= STORM_DAYS[0]
        )

    def aboutTeo():
        state.flags[TOLD_MARIT_ABOUT_TEO] = True
        return (
            "(She is already reaching for her coat.) All night. Every night "
            "since the plane. (She takes the generator key off the board.) "
            "Thank you. I would rather have known a week ago, and I would "
            "rather he had told me than you. He will not thank you. That is "
            "not what you did it for."
        )

    def afterTheDryNight():
        return (
            "Minus twenty in the bunkroom. (Flat.) The night tank was run down "
            "on the night hours. I have the key now. If anyone knew before "
            "the storm, they might have said."
        )

    return NPC(
        "Marit",
        "Marit Solheim runs the station. Eight winters. She keeps the log, "
        "reads the instruments, and says what is needed and nothing over.",
        [
            {
                "question": "How is the station looking?",
                "response": "Standing. The glass is falling; there will be "
                "weather by the end of the week. Is the galley in order?",
            },
            {
                "question": "I've counted the store. Fifteen days.",
                "response": aboutTheStore,
                "condition": lambda: state.knows(facts.THE_STORE)
                and not state.knows(facts.THE_MANIFEST),
            },
            {
                "question": "Four crates on the manifest are not in the store.",
                "response": aboutTheManifest,
                "condition": lambda: state.knows(facts.THE_MANIFEST)
                and not state.knows(facts.THE_FIFTH),
            },
            {
                "question": "I've been across the bay. I've met Aksel.",
                "response": herArithmetic,
                "condition": lambda: state.knows(facts.THE_FIFTH)
                and not state.knows(facts.MARITS_ARITHMETIC),
            },
            # A choice, not a question, and she holds you to it all winter.
            {
                "question": "I'll keep it.",
                "response": keepIt,
                "condition": undecidedAboutTheSecret,
            },
            {
                "question": "I won't keep it. Dov has to know.",
                "response": wontKeepIt,
                "condition": undecidedAboutTheSecret,
            },
            {
                "question": "I want to put the station on half rations.",
                "response": halfRations,
                "condition": lambda: state.knows(facts.THE_STORE)
                and not state.flags.get(MARIT_APPROVED_HALF),
            },
            {
                "question": "Teo's been running the generator all night, every night.",
                "response": aboutTeo,
                "condition": undecidedAboutTeo,
            },
            {
                "question": "About the storm night.",
                "response": afterTheDryNight,
                "condition": lambda: bool(state.flags.get(GENERATOR_RAN_DRY)),
            },
        ],
    )


def dov(game):
    state = game.state

    def thePlane():
        game.learn(facts.THE_PLANE)
        return (
            "The Otter needs an hour of light on the strip and wind under "
            "thirty. Light is the twentieth day; I have it in the almanac. "
            "It carries six. (He taps the log-book.) It has come in the dark "
            "once, in 1971. Read that entry before you ask me for it."
        )

    def theManifest():
        game.learn(facts.THE_MANIFEST)
        return (
            "September the ninth: fourteen crates of stores landed and signed "
            "for, M. Solheim. Twenty-one days at four; I sent the figure to "
            "Base myself. (He looks at you properly.) You have ten. I count "
            "things too. I had not counted those."
        )

    def theRule():
        game.learn(facts.THE_RULE)
        return (
            "Standing orders, paragraph six: any person on the island not on "
            "the wintering list is reported to Base on the next schedule, "
            "and Base decides. No exceptions, no discretion, and I would not "
            "want any. (He shrugs.) Why?"
        )

    def theFifth():
        state.flags[TOLD_DOV] = True
        return (
            "(He does not move for a long moment.) Where. ... The old hut. "
            "Since August. And Marit knows. (He turns the log-book round and "
            "writes the time.) Then I send it on the evening schedule. That "
            "is not a choice, it is the order - unless you can give me a "
            "reason that is not 'she asked'. I don't have one."
        )

    def undecidedAboutSending():
        return (
            state.flags.get(TOLD_DOV)
            and DOV_HOLDS not in state.flags
            and DOV_REPORTED not in state.flags
        )

    def sendIt():
        state.flags[DOV_REPORTED] = True
        return (
            "(He nods, and does not thank you.) Twenty hundred. Base will "
            "have it by five past, and they will send the plane on the first "
            "window they get, dark or not. That is theirs to decide. It is "
            "what I am here for."
        )

    def seventyOne():
        state.flags[DOV_HOLDS] = True
        return (
            "(He stops writing.) Haugen. ... I have read it. Every operator "
            "on this coast has read it. (A long silence on the key, which "
            "is a thing you have never heard in this room.) All right. I "
            "will send it on the twentieth, with the plane already on the "
            "strip, and it can be my rule that I broke. Do not tell Marit "
            "you got that out of me."
        )

    def sunniva():
        state.flags[DOV_HOLDS] = True
        return (
            "(Very quietly.) That is not fair. ... No. She would not. She "
            "sat on the key for two days when they sent the '71 flight and "
            "she was nineteen. (He closes the log-book.) The twentieth, "
            "then, with the plane on the strip, and it is my rule I am "
            "breaking. Go and cook something."
        )

    def theGame():
        return (
            "(He does not pretend.) It is chess. It is also the only hour "
            "of the day that is mine, and the only voice I hear that is not "
            "in this hut. Her name is Sunniva. She is at Base. That is all "
            "you are getting, and you can keep it off the schedule."
        )

    def afterTheDryNight():
        return (
            "I missed the schedule. (He says it the way another man would say "
            "he had dropped a child.) First time in three winters. She will "
            "have sat on the key for an hour with nothing coming. If "
            "somebody knew the tank was being run down, it would have been "
            "a kindness to say."
        )

    def whenIsThePlane():
        return "The twelfth, if the window holds. They are watching the glass."

    return NPC(
        "Dov",
        "Dov Lindqvist keeps the radio. Three winters. Weather to Base at "
        "eight and twenty, and a game of chess by Morse at twenty-two "
        "that he has never missed.",
        [
            {
                "question": "What's on the schedule?",
                "response": "Weather to Base at eight and twenty. The long "
                "game at twenty-two. Then nothing, until eight. It has not "
                "varied in three winters and it will not vary in this one.",
            },
            {
                "question": "When can the plane actually come?",
                "response": thePlane,
                "condition": lambda: not state.knows(facts.THE_PLANE),
            },
            {
                "question": "What did the manifest say was landed?",
                "response": theManifest,
                "condition": lambda: state.knows(facts.THE_STORE)
                and not state.knows(facts.THE_MANIFEST),
            },
            {
                "question": "What are your standing orders about people on the island?",
                "response": theRule,
                "condition": lambda: state.knows(facts.THE_FIFTH)
                and not state.knows(facts.THE_RULE),
            },
            {
                "question": "There is a fifth man on the island.",
                "response": theFifth,
                "condition": lambda: state.knows(facts.THE_FIFTH)
                and not state.flags.get(TOLD_DOV),
            },
            # What you say next - or don't - is what Dov does with it.
            {
                "question": "Send it.",
                "response": sendIt,
                "condition": undecidedAboutSending,
            },
            {
                "question": "Haugen went into the ridge in '71 for a man with a fever.",
                "response": seventyOne,
                "condition": lambda: undecidedAboutSending()
                and state.knows(facts.SEVENTY_ONE),
            },
            {
                "question": "Would Sunniva want you to send it?",
                "response": sunniva,
                "condition": lambda: undecidedAboutSending()
                and state.knows(facts.DOVS_GAME),
            },
            {
                "question": "When is the plane coming?",
                "response": whenIsThePlane,
                "condition": lambda: bool(state.flags.get(DOV_REPORTED)),
            },
            {
                "question": "About the chess.",
                "response": theGame,
                "condition": lambda: state.knows(facts.DOVS_GAME),
            },
            {
                "question": "You missed your schedule in the storm.",
                "response": afterTheDryNight,
                "condition": lambda: bool(state.flags.get(GENERATOR_RAN_DRY)),
            },
        ],
    )


def teo(game):
    state = game.state

    def howIsIt():
        state.flags[MET_TEO] = True
        return (
            "Running. (He has a rag in his hands and does not put it down.) "
            "It's the dark I mind, not the cold. It's dark at two in the "
            "afternoon. Is it always like this? You don't know either. "
            "Right."
        )

    def theSledge():
        game.learn(facts.THE_SLEDGE)
        return (
            "Before we came? (He thinks.) The snowmobile had three hours on "
            "the meter the day I got here, and I know because I wrote it in "
            "the book, and the sledge runners were wet - they'd been on the "
            "bay. Someone went across with a load and came back. Before the "
            "plane. Why?"
        )

    def theFuel():
        game.learn(facts.TEOS_NIGHTS)
        return (
            "(He does not look at the gauge. He looks at the floor.) I've "
            "been running it all night. For the lights. Since the plane. I "
            "can't - I lie there in the dark and I can't. (Quickly:) It's "
            "only the night tank. It's only - (He stops, because he has "
            "done the sum too.) The storm margin's gone. If it blows for "
            "two days on the night hours, it runs dry. I know. I know."
        )

    def undecidedAboutCovering():
        return (
            state.knows(facts.TEOS_NIGHTS)
            and TOLD_MARIT_ABOUT_TEO not in state.flags
            and COVERED_FOR_TEO not in state.flags
            and state.day <= STORM_DAYS[0]
        )

    def coverForHim():
        state.flags[COVERED_FOR_TEO] = True
        return (
            "(He looks up.) You won't - ... Thank you. I'll cut it. I'll cut "
            "it down. (He will not, and you both know it, and he is grateful "
            "anyway.)"
        )

    def afterTheDryNight():
        if state.flags.get(TOLD_MARIT_ABOUT_TEO):
            return (
                "(He has the rag again.) She's got the key. It held. ... You "
                "told her. (Not a question.) Right. (He goes back to the "
                "engine.)"
            )
        if state.flags.get(COVERED_FOR_TEO):
            return (
                "(Grey.) It ran dry at three. Minus twenty. Dov missed his "
                "hour. That's mine, that is - and you knew, and you let me "
                "have the lights. I don't know what to do with that. I'd "
                "have done it for you."
            )
        return (
            "(Grey.) It ran dry at three. Night tank. Don't ask me why. "
            "(You could. You don't.)"
        )

    return NPC(
        "Teo",
        "Teo Brandt keeps the generator, the snowmobile and the fuel. "
        "Twenty-four; his first winter. He counts the diesel every night.",
        [
            {"question": "How is the generator?", "response": howIsIt},
            {
                "question": "Did anyone use the snowmobile before we came?",
                "response": theSledge,
                "condition": lambda: state.knows(facts.THE_MANIFEST)
                and not state.knows(facts.THE_SLEDGE),
            },
            {
                "question": "Let's go over the fuel together.",
                "response": theFuel,
                "condition": lambda: state.flags.get(MET_TEO)
                and not state.knows(facts.TEOS_NIGHTS),
            },
            {
                "question": "I'll say nothing to Marit. Keep your lights.",
                "response": coverForHim,
                "condition": undecidedAboutCovering,
            },
            {
                "question": "About the storm night.",
                "response": afterTheDryNight,
                "condition": lambda: state.day > STORM_DAYS[0],
            },
        ],
    )


def aksel(game):
    state = game.state

    def hisWinter():
        game.learn(facts.AKSELS_WINTER)
        return (
            "Why. (He pours you something from the kettle.) I failed the "
            "medical in the spring. On age - there is nothing wrong with me "
            "a doctor could name, I am sixty-seven and that was enough. Four "
            "winters here cooking for people like you and they said I would "
            "not winter again. So I came out on the ship as a visitor and I "
            "asked Marit for one more, and she gave it to me. (He looks at "
            "the stove.) There is nobody at home. There is nowhere else I "
            "would rather be than this hut. That is the whole of it."
        )

    def maritsPart():
        return (
            "She signed me off the ship and brought the crates across "
            "herself. (A shrug.) Ask her the rest. It is hers to tell, and "
            "she will tell it plainer than I would."
        )

    def theSeals():
        game.learn(facts.THE_SEALS)
        return (
            "There are holes off the point where the current keeps the ice "
            "thin, and the seals come up to breathe at them. You stand still "
            "at one for as long as it takes. A seal is two days for the "
            "station. I will not tell you where they are; I will take you, "
            "on a still day. And the cairn on the headland, if Marit has not "
            "said - it is in the log, 1958."
        )

    def undecidedAboutComing():
        return (
            state.knows(facts.AKSELS_WINTER)
            and state.akselAt == AKSEL_HUT
            and BROUGHT_AKSEL_IN not in state.flags
            and LEFT_AKSEL_AT_HUT not in state.flags
        )

    def comeIn():
        state.flags[BROUGHT_AKSEL_IN] = True
        state.akselAt = AKSEL_STATION
        state.food += state.akselFood
        state.akselFood = 0
        return (
            "(He looks round the hut for a long time.) All right. I would "
            "rather eat at a table than be counted at one. (He starts "
            "loading the sledge.) Dov will know by supper. That is yours to "
            "carry, cook, not mine."
        )

    def leaveHim():
        state.flags[LEFT_AKSEL_AT_HUT] = True
        return (
            "(He nods.) Good. I have the stove and the crates and I know "
            "where the seals are. Come across when you want to. Bring "
            "coffee; there is none in four crates of stores, and that is "
            "the one thing Marit got wrong."
        )

    def atTheTable():
        if state.flags.get(AKSEL_WALKED_IN):
            return (
                "(He is peeling something.) I had counted too. When the "
                "store ran out over here I knew it, because I know what "
                "fourteen crates is and I know what four is. I was not going "
                "to let you go hungry in my galley."
            )
        return (
            "(He is peeling something.) Your galley. I am not going to tell "
            "you how to run it. (He tells you how to run it.)"
        )

    return NPC(
        "Aksel",
        "Aksel Rue. Sixty-seven, four winters at this station as cook, "
        "not on any list this year. He has a stove, a kettle, and time.",
        [
            {
                "question": "How are you keeping?",
                "response": "Warm. Fed. Read out. (He turns the book over.) "
                "Better than the three of you across there, I should think, "
                "with the lights on all night.",
            },
            {
                "question": "Why are you out here?",
                "response": hisWinter,
                "condition": lambda: not state.knows(facts.AKSELS_WINTER),
            },
            {
                "question": "Marit signed you off the ship.",
                "response": maritsPart,
                "condition": lambda: state.knows(facts.AKSELS_WINTER)
                and not state.knows(facts.MARITS_ARITHMETIC),
            },
            {
                "question": "Is there any way to make the food last?",
                "response": theSeals,
                "condition": lambda: state.knows(facts.AKSELS_WINTER)
                and not state.knows(facts.THE_SEALS),
            },
            # A choice, and he holds you to it.
            {
                "question": "Come back to the station with me.",
                "response": comeIn,
                "condition": undecidedAboutComing,
            },
            {
                "question": "Stay, then. I'll bring across what you need.",
                "response": leaveHim,
                "condition": undecidedAboutComing,
            },
            {
                "question": "How are you finding the galley?",
                "response": atTheTable,
                "condition": lambda: state.akselAt == AKSEL_STATION,
            },
        ],
    )


# Who says "will remember that" when a flag is set in conversation.
REMEMBERED = {
    KEPT_MARITS_SECRET: "Marit",
    TOLD_MARIT_ABOUT_TEO: "Teo",
    TOLD_DOV: "Dov",
    DOV_REPORTED: "Dov",
    DOV_HOLDS: "Dov",
    COVERED_FOR_TEO: "Teo",
    BROUGHT_AKSEL_IN: "Aksel",
    LEFT_AKSEL_AT_HUT: "Aksel",
}
