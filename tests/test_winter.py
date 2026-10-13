from conftest import FakeGame

from overwinter import facts, flags, winter
from overwinter.state import (
    AKSEL_CRATES,
    AKSEL_FLOWN,
    AKSEL_HUT,
    AKSEL_STATION,
    AFTERNOON,
    DARK_FLIGHT_DAY,
    EVENING,
    ICE_SAFE_DAY,
    MORNING,
    PLANE_DAY,
    START_FOOD,
    STORM_DAYS,
)


def onTheEveningOf(day):
    """A FakeGame one watch from the end of the given day."""
    game = FakeGame()
    game.state.day = day
    game.state.watch = EVENING
    return game


def test_three_watches_make_a_day_and_the_night_eats_the_store():
    game = FakeGame()
    outcome = winter.advance(game)
    assert game.state.watch == AFTERNOON
    assert not outcome.dayEnded
    assert game.state.food == START_FOOD
    outcome = winter.advance(game, watches=2)
    assert outcome.dayEnded
    assert game.state.day == 2
    assert game.state.watch == MORNING
    assert game.state.food == START_FOOD - 4
    # Aksel eats one of his own crates' rations a night while he is in the hut.
    assert game.state.akselFood == AKSEL_CRATES - 1


def test_half_rations_eat_half_the_mouths_rounded_up():
    game = onTheEveningOf(2)
    game.state.akselAt = AKSEL_STATION
    game.state.flags[flags.HALF_RATIONS] = True
    winter.advance(game)
    assert game.state.food == START_FOOD - 3
    # His crates are not eaten from the hut once he is at the table.
    assert game.state.akselFood == AKSEL_CRATES


def test_the_clock_stops_once_the_winter_has_an_ending():
    game = onTheEveningOf(3)
    game.state.ending = facts.FIVE_OUT
    outcome = winter.advance(game, watches=3)
    assert (game.state.day, game.state.watch) == (3, EVENING)
    assert not outcome.dayEnded


def test_the_fixed_days_open_with_their_line_once():
    for day in (ICE_SAFE_DAY, STORM_DAYS[0], STORM_DAYS[-1] + 1):
        game = onTheEveningOf(day - 1)
        outcome = winter.advance(game)
        assert winter.DAY_LINES[day] in outcome.lines
    game = onTheEveningOf(ICE_SAFE_DAY)
    assert winter.advance(game).lines == []


def test_told_dov_and_given_no_reason_he_sends_it_that_night():
    game = onTheEveningOf(3)
    game.state.flags[flags.TOLD_DOV] = True
    outcome = winter.advance(game)
    assert game.state.flags[flags.DOV_REPORTED] is True
    assert any("[Dov will remember that.]" in line for line in outcome.lines)


def test_a_reason_to_wait_keeps_the_report_off_the_schedule():
    game = onTheEveningOf(3)
    game.state.flags[flags.TOLD_DOV] = True
    game.state.flags[flags.DOV_HOLDS] = True
    outcome = winter.advance(game)
    assert flags.DOV_REPORTED not in game.state.flags
    assert outcome.lines == []


def test_the_storm_night_holds_only_if_marit_cut_the_night_hours():
    game = onTheEveningOf(STORM_DAYS[0])
    winter.advance(game)
    assert game.state.flags[flags.GENERATOR_RAN_DRY] is True

    game = onTheEveningOf(STORM_DAYS[0])
    game.state.flags[flags.TOLD_MARIT_ABOUT_TEO] = True
    outcome = winter.advance(game)
    assert flags.GENERATOR_RAN_DRY not in game.state.flags
    assert any("The heaters held." in line for line in outcome.lines)


def test_an_empty_store_brings_aksel_in_with_what_is_left_of_his_crates():
    game = onTheEveningOf(15)
    game.state.food = 4
    game.state.akselFood = 10
    outcome = winter.advance(game)
    assert game.state.flags[flags.STORE_EMPTIED_ON] == 15
    assert game.state.flags[flags.AKSEL_WALKED_IN] is True
    assert game.state.akselAt == AKSEL_STATION
    # He ate his ration in the hut that night, then carried the rest in.
    assert (game.state.food, game.state.akselFood) == (9, 0)
    assert game.state.knows(facts.THE_FIFTH)
    assert any("there were five" in line for line in outcome.lines)


def test_an_empty_store_with_aksel_already_at_the_table_is_only_empty():
    game = onTheEveningOf(15)
    game.state.food = 5
    game.state.akselAt = AKSEL_STATION
    outcome = winter.advance(game)
    assert game.state.food == 0
    assert game.state.flags[flags.STORE_EMPTIED_ON] == 15
    assert flags.AKSEL_WALKED_IN not in game.state.flags
    assert len(outcome.lines) == 1
    # The second empty night says nothing new and keeps the first day.
    outcome = winter.advance(game, watches=3)
    assert game.state.flags[flags.STORE_EMPTIED_ON] == 15
    assert outcome.lines == []


def test_a_report_on_the_schedule_brings_the_dark_flight_on_its_day():
    game = onTheEveningOf(DARK_FLIGHT_DAY - 1)
    game.state.flags[flags.DOV_REPORTED] = True
    outcome = winter.advance(game)
    assert outcome.ending == facts.THE_DARK_FLIGHT
    assert game.state.ending == facts.THE_DARK_FLIGHT
    assert game.state.akselAt == AKSEL_FLOWN
    assert game.state.knows(facts.THE_DARK_FLIGHT)
    assert flags.PLANE_ON_STRIP not in game.state.flags


def test_a_report_sent_after_the_dark_flight_day_brings_no_flight():
    # Current behaviour, recorded rather than endorsed: the dark flight only
    # fires on the morning of DARK_FLIGHT_DAY, so a report sent later never
    # brings it, and the winter runs on to the plane. Issue #18 tracks what a
    # late report should do.
    game = onTheEveningOf(DARK_FLIGHT_DAY)
    game.state.flags[flags.TOLD_DOV] = True
    winter.advance(game)
    assert game.state.flags[flags.DOV_REPORTED] is True
    while game.state.day < PLANE_DAY:
        winter.advance(game, watches=3)
    assert game.state.ending is None
    assert game.state.flags[flags.PLANE_ON_STRIP] is True


def test_the_plane_morning_puts_everyone_on_the_strip():
    game = onTheEveningOf(PLANE_DAY - 1)
    game.state.location = "galley"
    outcome = winter.advance(game)
    assert game.state.flags[flags.PLANE_ON_STRIP] is True
    assert game.state.location == "strip"
    assert game.state.ending is None
    assert any("Marit wants everyone on the strip" in line for line in outcome.lines)
    assert game.state.akselAt == AKSEL_HUT
