from conftest import FakeGame, ScriptedUI

from overwinter import facts, flags, progression
from overwinter.scenes.base import STORM_REASON
from overwinter.scenes.strip import HUNT_DRAWS, Strip
from overwinter.state import (
    AKSEL_FLOWN,
    AKSEL_HUT,
    AKSEL_STATION,
    ICE_SAFE_DAY,
    STORM_DAYS,
    State,
)

CROSS = "Cross the bay to the old hut"
DEPOT = "Walk the headland to the 1958 cairn"
HUNT = "Wait at the breathing holes with Aksel"
STAND = "Stand on the strip a while"


def strip(script=(), knows=()):
    game = FakeGame(ScriptedUI(list(script)))
    game.state.location = "strip"
    for factId in knows:
        game.learn(factId)
    progression.catchUp(game.state)
    return game, Strip(game)


def everything(script=(), knows=()):
    """The strip with every outside row unlocked."""
    return strip(
        script, (facts.THE_OLD_HUT, facts.THE_DEPOT, facts.THE_SEALS) + tuple(knows)
    )


def reasons(ui):
    """The last menu's rows, mapped to why each is unavailable (None if not)."""
    _, options, why, _ = ui.menus[-1]
    return dict(zip(options, why))


def firstEmptyHunt():
    """The index of the first draw in the winter's sequence that brings
    nothing back from the holes."""
    probe = State()
    while probe.draw(HUNT_DRAWS) != "nothing":
        pass
    return probe.rngDraws - 1


def test_nothing_unlocked_leaves_only_standing_and_the_way_back():
    game, scene = strip(["Quit"])
    assert scene.run() == "quit"
    rows = reasons(game.ui)
    assert STAND in rows
    assert CROSS not in rows and DEPOT not in rows and HUNT not in rows


def test_the_storm_shuts_every_row_outside_and_names_marits_order():
    game, scene = everything(["Quit"])
    game.state.day = STORM_DAYS[0]
    assert scene.run() == "quit"
    descriptor = game.ui.menus[-1][0]
    assert "the wind is a wall, and Marit's order stands" in descriptor
    rows = reasons(game.ui)
    for row in (CROSS, DEPOT, HUNT, STAND):
        assert rows[row] == "the storm"
    assert rows["Go out to the generator shed"] == STORM_REASON
    assert rows["Go to the galley"] is None


def test_unsafe_ice_says_why_only_once_you_know_when_it_holds():
    game, scene = everything(["Quit"])
    scene.run()
    assert reasons(game.ui)[CROSS] == (
        "the bay is open water and new ice - you don't know if it holds"
    )

    game, scene = everything(["Quit"], knows=(facts.THE_ICE,))
    scene.run()
    assert reasons(game.ui)[CROSS] == "the ice won't bear until the fifth day"

    game, scene = everything(["Quit"])
    game.state.day = ICE_SAFE_DAY
    scene.run()
    assert reasons(game.ui)[CROSS] is None


def test_an_emptied_depot_is_greyed_with_the_reason():
    game, scene = everything(["Quit"])
    game.state.flags[flags.DEPOT_FETCHED] = True
    scene.run()
    assert reasons(game.ui)[DEPOT] == "you've emptied it"


def test_the_holes_need_aksel_on_the_island_and_take_one_wait_a_day():
    game, scene = everything(["Quit"])
    game.state.akselAt = AKSEL_FLOWN
    scene.run()
    assert reasons(game.ui)[HUNT] == "Aksel is gone"

    game, scene = everything(["Quit"])
    game.state.akselAt = AKSEL_STATION
    game.state.flags[flags.HUNTED_TODAY] = True
    scene.run()
    assert reasons(game.ui)[HUNT] == "one wait a day is all the cold allows"


def test_standing_on_the_strip_shows_the_light_across_the_bay_until_you_know_whose():
    game, scene = strip([STAND])
    assert scene.run() == "strip"
    assert game.ui.saw("a point of light that is not a star")
    assert game.state.watch == 1

    game, scene = strip([STAND], knows=(facts.THE_FIFTH,))
    scene.run()
    assert game.ui.saw("The windsock does not change its mind.")
    assert not game.ui.saw("a point of light")

    game, scene = strip([STAND])
    game.state.akselAt = AKSEL_STATION
    scene.run()
    assert game.ui.saw("The windsock does not change its mind.")


def test_a_wait_that_brings_nothing_back_costs_the_day_and_adds_nothing():
    game, scene = everything([HUNT])
    game.state.rngDraws = firstEmptyHunt()
    food = game.state.food
    assert scene.run() == "strip"
    assert game.ui.saw("nothing comes up. Aksel says that is most days.")
    assert game.ui.saw("You cross to the hut first and Aksel comes back with you.")
    assert game.state.food == food
    assert game.state.seals == 0
    assert game.state.flags[flags.HUNTED_TODAY]


def test_aksel_fetched_from_the_station_is_not_crossed_for():
    game, scene = everything([HUNT])
    game.state.akselAt = AKSEL_STATION
    scene.run()
    assert not game.ui.saw("You cross to the hut first")


def test_quitting_from_the_strip_spends_no_time():
    game, scene = strip(["Quit"])
    assert scene.run() == "quit"
    assert (game.state.day, game.state.watch) == (1, 0)


def test_aksel_in_the_hut_meets_the_plane_and_unasked_it_takes_five():
    game, scene = strip()
    game.state.flags[flags.PLANE_ON_STRIP] = True
    assert game.state.akselAt == AKSEL_HUT
    assert scene.run() == "epilogue"
    assert game.ui.saw("Aksel is on the strip before the plane is")
    assert game.state.ending == facts.FIVE_OUT
    assert flags.AKSEL_ASKED_TO_STAY not in game.state.flags
    assert flags.PLANE_ON_STRIP not in game.state.flags


def test_aksel_already_at_the_station_is_not_said_to_cross_for_the_plane():
    game, scene = strip()
    game.state.flags[flags.PLANE_ON_STRIP] = True
    game.state.akselAt = AKSEL_STATION
    scene.run()
    assert not game.ui.saw("Aksel is on the strip before the plane is")
