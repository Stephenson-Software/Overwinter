"""The rows on each place's menu that no playthrough takes: looking around,
sitting up, going back on full rations, the epilogue. One run() each, against
FakeGame, so the time they cost and what they say are pinned down."""

from conftest import FakeGame, ScriptedUI

from overwinter import facts, flags, premise
from overwinter.scenes.bunks import Bunks
from overwinter.scenes.epilogue import Epilogue
from overwinter.scenes.galley import Galley
from overwinter.scenes.hut import Hut
from overwinter.scenes.shed import Shed
from overwinter.state import AKSEL_HUT, AKSEL_STATION, EVENING, MORNING, State
from test_game import SLEEP, TURN_IN


def scene(sceneClass, script, location):
    game = FakeGame(ScriptedUI(list(script)))
    game.state.location = location
    return game, sceneClass(game)


def reasonFor(ui, label):
    _, options, reasons, _ = ui.menus[-1]
    return reasons[options.index(label)]


def test_teo_is_only_there_to_sit_up_with_in_the_evening():
    game, bunks = scene(Bunks, ["Quit"], "bunks")
    assert bunks.run() == "quit"
    assert reasonFor(game.ui, "Sit up with Teo") == "he's out at the shed till evening"


def test_sitting_up_with_teo_meets_him_and_spends_the_evening():
    game, bunks = scene(Bunks, ["Sit up with Teo"], "bunks")
    game.state.watch = EVENING
    assert bunks.run() == "bunks"
    assert game.state.flags[flags.MET_TEO] is True
    assert game.ui.saw("'I'll just check the generator,'")
    # The evening was the last watch: the night came and the day turned.
    assert game.state.day == 2
    assert game.state.watch == MORNING


def test_looking_over_the_snowmobile_points_at_teos_book_and_costs_a_watch():
    game, shed = scene(Shed, ["Look over the snowmobile"], "shed")
    assert shed.run() == "shed"
    assert game.ui.saw("a maintenance book in Teo's careful hand")
    assert game.state.watch == MORNING + 1
    assert not game.state.facts


def test_full_rations_undo_half_rations_and_the_row_turns_back():
    game, galley = scene(
        Galley, ["Put the station back on full rations", "Quit"], "galley"
    )
    game.state.learn(facts.THE_STORE)
    game.state.flags[flags.HALF_RATIONS] = True
    game.state.flags[flags.MARIT_APPROVED_HALF] = True
    assert game.state.dailyRations == 2
    assert galley.run() == "galley"
    assert game.state.flags[flags.HALF_RATIONS] is False
    assert game.ui.saw("Full rations again.")
    assert game.state.watch == MORNING + 1
    assert game.state.dailyRations == 4

    assert galley.run() == "quit"
    assert reasonFor(game.ui, "Put the station on half rations") is None


def test_the_first_morning_count_is_the_store_as_landed():
    game, galley = scene(Galley, ["Count the store"], "galley")
    assert galley.run() == "galley"
    assert game.ui.saw("60 rations. Fifteen days at four")
    assert game.ui.saw("You check the shelf twice. Fifteen.")


def test_a_first_count_put_off_a_week_says_what_is_left(scripted):
    script = (
        ["Create New Save"]
        + TURN_IN
        + SLEEP * 5
        + ["Go to the galley", "Count the store", "Quit"]
    )
    game, ui = scripted(script)
    game.play()
    assert game.state.day == 7
    assert game.state.food == 36
    assert ui.saw("36 rations left, at 4 a day")
    assert ui.saw("You check the shelf twice. 9 days.")
    assert not ui.saw("Fifteen")


def test_a_first_count_with_aksel_at_the_table_divides_by_five():
    game, galley = scene(Galley, ["Count the store"], "galley")
    game.state.akselAt = AKSEL_STATION
    assert galley.run() == "galley"
    assert game.ui.saw("60 rations left, at 5 a day")
    assert game.ui.saw("You check the shelf twice. 12 days.")
    assert not game.ui.saw("Fifteen")


def test_the_stores_journal_line_stays_true_after_the_store_is_eaten_into():
    assert "started the winter at fifteen days" in facts.text(facts.THE_STORE)
    state = State()
    state.learn(facts.THE_STORE)
    assert "started at fifteen days" in premise.text(state)


def test_looking_around_the_hut_with_aksel_in_it_finds_the_crates():
    game, hut = scene(Hut, ["Look around the hut"], "hut")
    assert game.state.akselAt == AKSEL_HUT
    assert hut.run() == "hut"
    assert game.state.knows(facts.THE_FIFTH)
    assert game.ui.saw("the station's stencil, four of them, one open")
    assert game.state.watch == MORNING + 1
    assert game.state.location == "hut"


def test_the_hut_after_aksel_has_come_in_is_cold_and_has_nobody_to_talk_to():
    game, hut = scene(Hut, ["Look around the hut"], "hut")
    game.state.akselAt = AKSEL_STATION
    assert hut.run() == "hut"
    assert not game.state.knows(facts.THE_FIFTH)
    assert "Talk to Aksel" not in game.ui.menus[-1][1]
    assert "the crates are gone" in game.ui.menus[-1][0]
    assert game.ui.saw("Nothing left in it that was not here in 1961.")


def test_the_epilogue_rereads_the_last_page_and_opens_the_journal_for_free():
    game, epilogue = scene(
        Epilogue,
        ["Read the last page again", "Open your journal", "Quit"],
        "epilogue",
    )
    game.state.ending = facts.FIVE_OUT
    assert epilogue.run() == "epilogue"
    assert game.ui.saw("WHAT HAPPENED.")
    assert "five on the plane" in game.ui.menus[-1][0]
    assert epilogue.run() == "journal"
    assert game.state.location == "journal"
    assert epilogue.run() == "quit"
    # Nothing after the ending costs time.
    assert game.state.watch == MORNING
    assert game.state.day == 1
