"""The other ways the winter ends, played through the real game."""

from overwinter import facts, flags
from overwinter.state import AKSEL_FLOWN, AKSEL_STATION, DARK_FLIGHT_DAY, PLANE_DAY
from test_game import DAY_ONE, DAY_TWO, DAYS_THREE_AND_FOUR, SLEEP, TURN_IN

# Day five: across the bay, meet Aksel, straight to Dov with it.
TELL_DOV = [
    "Go outside",
    "Cross the bay",  # THE_FIFTH
    "Go back across the bay",
    "Go to the radio room",
    "Talk to Dov",
    "There is a fifth man",  # TOLD_DOV
]


def test_telling_dov_and_sending_it_brings_the_dark_flight(scripted):
    script = (
        DAY_ONE
        + DAY_TWO
        + DAYS_THREE_AND_FOUR
        + TELL_DOV
        + ["Send it.", "[Back]"]
        + TURN_IN
        + SLEEP * (DARK_FLIGHT_DAY - 6)
        + ["Quit"]
    )
    game, ui = scripted(script)
    game.play()
    state = game.state
    assert state.flags[flags.DOV_REPORTED] is True
    assert state.ending == facts.THE_DARK_FLIGHT
    assert state.day == DARK_FLIGHT_DAY
    assert state.akselAt == AKSEL_FLOWN
    assert ui.saw("[Dov will remember that.]")
    assert ui.saw("Day twelve. Base called at eight with a window")
    assert ui.saw("WHAT HAPPENED. You told Dov there were five of you, and Dov sent it")
    assert ui.saw("The flight went well. It could not have.")
    # After the ending there is only the last page and the journal.
    assert ui.menus[-1][0].startswith("The winter is over: the dark flight")


def test_walking_away_from_dov_is_sending_it(scripted):
    script = (
        DAY_ONE
        + DAY_TWO
        + DAYS_THREE_AND_FOUR
        + TELL_DOV
        + ["[Back]"]
        + TURN_IN
        + ["Quit"]
    )
    game, ui = scripted(script)
    game.play()
    assert game.state.flags[flags.DOV_REPORTED] is True
    assert ui.saw("you had not given him a reason to wait")
    assert ui.saw("[Dov will remember that.]")


def test_sunniva_is_the_other_reason_dov_will_wait(scripted):
    # Sit in on the evening schedule first (day 1, evening), then day 5.
    dayOne = [
        "Create New Save",
        "Count the store",
        "Cook the meal",  # -> evening
        "Go to the radio room",
        "Sit in on the evening schedule",  # DOVS_GAME; day ends
        "Go to Marit's office",
        "Read the station log",
        "1961",
        "Read the station log",
        "The ice table",
    ]
    script = (
        dayOne + TURN_IN + SLEEP * 2 + TELL_DOV + ["Would Sunniva", "[Back]", "Quit"]
    )
    game, ui = scripted(script)
    game.play()
    state = game.state
    assert state.knows(facts.DOVS_GAME)
    assert state.flags[flags.DOV_HOLDS] is True
    assert flags.DOV_REPORTED not in state.flags


def test_never_crossing_the_bay_still_answers_the_count(scripted):
    # Count the store, read nothing, sleep through the winter. The store
    # runs out on the fifteenth night and the answer walks in by itself.
    script = ["Create New Save", "Count the store"] + TURN_IN + SLEEP * 18 + ["Quit"]
    game, ui = scripted(script)
    game.play()
    state = game.state
    assert state.day == PLANE_DAY
    assert state.ending == facts.FIVE_OUT
    assert state.knows(facts.THE_FIFTH)
    assert state.flags[flags.STORE_EMPTIED_ON] == 15
    assert ui.saw("AKSEL. He walked in on his own the night the store ran out")
    assert ui.saw("THE COUNT. It did not close.")
    assert ui.saw("WHAT IT WAS. A winter with five people and four people's food")


def test_when_the_store_runs_out_aksel_walks_in_on_his_own(scripted):
    script = ["Create New Save", "Count the store"] + TURN_IN + SLEEP * 14 + ["Quit"]
    game, ui = scripted(script)
    game.play()
    state = game.state
    assert state.day == 16
    assert state.flags[flags.STORE_EMPTIED_ON] == 15
    assert state.flags[flags.AKSEL_WALKED_IN] is True
    assert state.akselAt == AKSEL_STATION
    assert state.knows(facts.THE_FIFTH)
    assert ui.saw("a man walked in out of the dark with a sledge behind him")
    # He brought what was left of his crates: 24, less one a day for 15 days.
    assert state.food == 24 - 15


def test_half_rations_need_marits_leave_and_double_the_days(scripted):
    script = (
        DAY_ONE
        + DAY_TWO
        + DAYS_THREE_AND_FOUR
        + [
            "Go outside",
            "Cross the bay",
            "Talk to Aksel",
            "Why are you out here",
            "Stay, then",  # LEFT_AKSEL_AT_HUT
            "[Back]",
            "Go back across the bay",
            "Go to Marit's office",
            "Talk to Marit",
            "I've been across the bay",
            "I want to put the station on half rations",
            "[Back]",
            "Go to the galley",
            "Put the station on half rations",
            "Quit",
        ]
    )
    game, ui = scripted(script)
    game.play()
    state = game.state
    assert state.flags[flags.MARIT_APPROVED_HALF] is True
    assert state.flags[flags.HALF_RATIONS] is True
    assert state.flags[flags.LEFT_AKSEL_AT_HUT] is True
    assert state.dailyRations == 2
    assert state.foodDays == state.food // 2
    assert ui.saw("[Aksel will remember that.]")


def test_half_rations_are_refused_before_marits_arithmetic_is_known(scripted):
    script = [
        "Create New Save",
        "Count the store",
        "Go to Marit's office",
        "Talk to Marit",
        "I want to put the station on half rations",
        "[Back]",
        "Quit",
    ]
    game, ui = scripted(script)
    game.play()
    assert flags.MARIT_APPROVED_HALF not in game.state.flags
    assert ui.saw("Marit: No. Half rations in the second week")
    # And the galley row is listed, greyed, with the reason.
    galleyMenus = [m for m in ui.menus if m[0].startswith("The galley")]
    reasons = galleyMenus[-1][2]
    labels = galleyMenus[-1][1]
    assert reasons[labels.index("Put the station on half rations")] == (
        "Marit would have to agree to that"
    )


def test_covering_for_teo_lets_the_generator_run_dry_on_the_storm_night(scripted):
    dayOne = DAY_ONE[:-6]  # up to and including the fuel talk
    script = (
        dayOne
        + [
            "[Back]",
            "Talk to Teo",
            "I'll say nothing to Marit",  # COVERED_FOR_TEO
            "[Back]",
        ]
        + TURN_IN
        + SLEEP * 7
        + ["Quit"]
    )
    game, ui = scripted(script)
    game.play()
    state = game.state
    assert state.day == 9
    assert state.flags[flags.COVERED_FOR_TEO] is True
    assert state.flags[flags.GENERATOR_RAN_DRY] is True
    assert ui.saw("[Teo will remember that.]")
    assert ui.saw("At three in the morning the generator stopped.")


def test_the_storm_shuts_the_strip_and_the_shed(scripted):
    script = ["Create New Save"] + TURN_IN + SLEEP * 6 + ["Go to the galley", "Quit"]
    game, ui = scripted(script)
    game.play()
    assert game.state.day == 8
    assert game.state.stormy
    labels, reasons = ui.menus[-1][1], ui.menus[-1][2]
    assert reasons[labels.index("Go outside, onto the strip")]
    assert reasons[labels.index("Go out to the generator shed")]
    assert reasons[labels.index("Go to Marit's office")] is None
    assert ui.saw("Storm. Marit's order is that nobody goes past the door")
