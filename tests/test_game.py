import json
import os

from overwinter import facts, flags
from overwinter.game import describeSlot
from overwinter.state import AKSEL_STATION, AKSEL_STAYED, PLANE_DAY

# The whole solution, from a fresh save, to the plane with five aboard and
# the count closed. Every label here is a menu row or a dialogue question;
# the ScriptedUI fails loudly if one is missing or unavailable, so this is
# the test that says the game is solvable.
# From anywhere else, and from the bunkroom itself (where each morning starts).
TURN_IN = ["Go to the bunkroom", "Turn in"]
SLEEP = ["Turn in"]

DAY_ONE = [
    "Create New Save",
    "Count the store",  # THE_STORE; watch 1
    "Go to the radio room",
    "Talk to Dov",
    "What did the manifest",  # THE_MANIFEST
    "When can the plane",  # THE_PLANE
    "[Back]",
    "Go out to the generator shed",
    "Talk to Teo",
    "How is the generator",  # MET_TEO
    "Did anyone use the snowmobile",  # THE_SLEDGE
    "Let's go over the fuel",  # TEOS_NIGHTS
    "[Back]",
    "Go to Marit's office",
    "Read the station log",
    "1961",  # THE_OLD_HUT; watch 2
    "Read the station log",
    "The ice table",  # THE_ICE; day ends -> day 2
]
DAY_TWO = [
    "Read the station log",
    "1971",  # SEVENTY_ONE; watch 1
    "Read the station log",
    "1958",  # THE_DEPOT; watch 2
    "Talk to Marit",
    "Teo's been running the generator",  # TOLD_MARIT_ABOUT_TEO
    "[Back]",
] + TURN_IN  # -> day 3
DAYS_THREE_AND_FOUR = SLEEP + SLEEP  # -> day 5, the ice holds
DAY_FIVE = [
    "Go outside",
    "Cross the bay",  # THE_FIFTH; watch 1
    "Talk to Aksel",
    "Why are you out here",  # AKSELS_WINTER
    "Is there any way to make the food last",  # THE_SEALS
    "Come back to the station",  # BROUGHT_AKSEL_IN; crossing back; watch 2
    "[Back]",
    "Go to Marit's office",
    "Talk to Marit",
    "I've been across the bay",  # MARITS_ARITHMETIC
    "I'll keep it",  # KEPT_MARITS_SECRET
    "[Back]",
] + TURN_IN  # -> day 6
DAY_SIX = [
    "Go outside",
    "Walk the headland",  # DEPOT_FETCHED; watch 1
    "Wait at the breathing holes",  # draw 1; watch 2
] + TURN_IN  # -> day 7
DAY_SEVEN = [
    "Go outside",
    "Wait at the breathing holes",  # draw 2; watch 1
] + TURN_IN  # -> day 8, storm
STORM = SLEEP + SLEEP  # -> day 10
DAY_TEN = [
    "Go to the radio room",
    "Talk to Dov",
    "What are your standing orders",  # THE_RULE
    "There is a fifth man",  # TOLD_DOV
    "Haugen went into the ridge",  # DOV_HOLDS
    "[Back]",
] + TURN_IN  # -> day 11
TO_THE_PLANE = SLEEP * (PLANE_DAY - 11)  # -> day 20
ON_THE_STRIP = ["He's coming with us", "Quit"]

FULL_RUN = (
    DAY_ONE
    + DAY_TWO
    + DAYS_THREE_AND_FOUR
    + DAY_FIVE
    + DAY_SIX
    + DAY_SEVEN
    + STORM
    + DAY_TEN
    + TO_THE_PLANE
    + ON_THE_STRIP
)


def test_the_winter_can_be_finished_with_five_on_the_plane(scripted):
    game, ui = scripted(list(FULL_RUN))
    game.play()
    state = game.state

    assert state.ending == facts.FIVE_OUT
    assert state.day == PLANE_DAY
    assert state.akselAt == AKSEL_STATION
    assert state.flags[flags.KEPT_MARITS_SECRET] is True
    assert state.flags[flags.DOV_HOLDS] is True
    assert flags.DOV_REPORTED not in state.flags
    assert state.flags[flags.TOLD_MARIT_ABOUT_TEO] is True
    assert flags.GENERATOR_RAN_DRY not in state.flags
    assert state.flags[flags.DEPOT_FETCHED] is True
    assert state.flags[flags.BACKED_AKSEL_STAYING] is False
    # The count closed: there was food on the shelf on the last morning.
    assert flags.STORE_EMPTIED_ON not in state.flags
    assert state.food > 0
    for fact in facts.FACTS:
        if fact in (facts.THE_DARK_FLIGHT, facts.AKSEL_STAYED, facts.DOVS_GAME):
            continue
        assert state.knows(fact), fact
    assert ui.saw("[Marit will remember that.]")
    assert ui.saw("[Dov will remember that.]")
    assert ui.saw("[Teo will remember that.]")
    assert ui.saw("[Aksel will remember that.]")
    # The ending says what happened, plainly.
    assert ui.saw("WHAT HAPPENED. The plane came on the twentieth morning")
    assert ui.saw("THE COUNT. It closed, because you walked the headland")
    assert ui.saw("DOV. You told him there were five, and then you gave him a reason")
    assert ui.cleanedUp


def test_the_winter_is_saved_after_every_action_and_the_slot_describes_it(scripted):
    game, ui = scripted(list(FULL_RUN))
    game.play()
    path = game.saveFileManager.get_save_path("save.json")
    with open(path) as f:
        data = json.load(f)
    assert data["ending"] == facts.FIVE_OUT
    assert data["day"] == PLANE_DAY
    metadata = game.saveFileManager.list_save_files()[0]["metadata"]
    assert describeSlot(metadata) == "over - five on the plane, %d known" % len(
        data["facts"]
    )


def test_a_saved_winter_resumes_where_it_was(scripted):
    game, ui = scripted(list(DAY_ONE) + ["Quit"])
    game.play()
    assert game.state.day == 2
    known = list(game.state.facts)

    game2, ui2 = scripted(["Load Slot 1", "Quit"])
    game2.play()
    assert game2.state.day == 2
    assert game2.state.facts == known
    assert game2.state.location == "office"
    assert ui2.menus[0][1][0].startswith("Load Slot 1 (Day 2, %d known)" % len(known))


def test_the_new_game_opens_on_the_premise_once(scripted):
    game, ui = scripted(["Create New Save", "Count the store", "Quit"])
    game.play()
    assert ui.dialogues[0].startswith("Cape Ferrin weather station.")
    game2, ui2 = scripted(["Load Slot 1", "Quit"])
    game2.play()
    assert not any(d.startswith("Cape Ferrin") for d in ui2.dialogues)


def test_the_header_runs_on_every_menu_and_shows_the_count_once_known(scripted):
    game, ui = scripted(["Create New Save", "Count the store", "Quit"])
    game.play()
    assert ui.headers[1]["title"] == "Overwinter - Day 1 of 20"
    assert not any("Food" in str(chip) for chip in ui.headers[1]["chips"])
    assert {"text": "Food: 15 days", "class": "low"} in ui.headers[2]["chips"]


def test_quitting_the_save_menu_still_cleans_up(scripted):
    game, ui = scripted(["Quit"])
    game.play()
    assert ui.cleanedUp
    assert game.running is False


def test_a_damaged_save_is_kept_aside_and_a_fresh_winter_starts(scripted, tmp_path):
    game, ui = scripted(["Create New Save", "Quit"])
    game.play()
    path = game.saveFileManager.get_save_path("save.json")
    with open(path, "w") as f:
        f.write('{"version": 1, "day": "seven"}')

    game2, ui2 = scripted(["Load Slot 1", "Quit"])
    game2.play()
    assert game2.failedLoad
    assert ui2.saw("This save could not be read")
    damaged = [n for n in os.listdir(os.path.dirname(path)) if "damaged" in n]
    assert damaged
    assert game2.state.day == 1


def test_letting_aksel_go_is_an_ending_of_its_own(scripted):
    script = list(FULL_RUN)
    script[script.index("He's coming with us")] = "Let him go"
    game, ui = scripted(script)
    game.play()
    assert game.state.ending == facts.AKSEL_STAYED
    assert game.state.akselAt == AKSEL_STAYED
    assert game.state.flags[flags.BACKED_AKSEL_STAYING] is True
    assert ui.saw("WHAT HAPPENED. The plane came on the twentieth morning and four of")
    assert ui.saw("The supply ship comes in August")
