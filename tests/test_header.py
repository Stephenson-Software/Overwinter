from conftest import FakeGame

from overwinter import facts, flags
from overwinter.header import LOCATION_NAMES, buildHeader
from overwinter.state import AFTERNOON, AKSEL_STATION, EVENING, PLANE_DAY, STORM_DAYS


def chipTexts(header):
    return [
        chip["text"] if isinstance(chip, dict) else chip for chip in header["chips"]
    ]


def test_the_first_morning_says_the_day_the_watch_and_the_place():
    game = FakeGame()
    header = buildHeader(game)
    assert header["title"] == "Overwinter - Day 1 of %d" % PLANE_DAY
    assert chipTexts(header) == [
        "Day 1 of %d" % PLANE_DAY,
        "Morning, 8:00 AM",
        "The Galley",
        "Known: 0/%d" % len(facts.FACTS),
    ]


def test_the_watch_chip_follows_the_clock():
    game = FakeGame()
    game.state.watch = AFTERNOON
    assert "Afternoon, 2:00 PM" in chipTexts(buildHeader(game))
    game.state.watch = EVENING
    assert "Evening, 8:00 PM" in chipTexts(buildHeader(game))


def test_every_place_the_player_can_stand_has_a_name():
    game = FakeGame()
    for location, name in LOCATION_NAMES.items():
        game.state.location = location
        assert buildHeader(game)["chips"][2] == name


def test_the_count_is_hidden_until_the_store_is_counted():
    game = FakeGame()
    assert not any(text.startswith("Food:") for text in chipTexts(buildHeader(game)))
    game.learn(facts.THE_STORE)
    texts = chipTexts(buildHeader(game))
    assert "Food: 15 days" in texts
    assert "Known: 1/%d" % len(facts.FACTS) in texts


def test_the_food_chip_is_low_only_while_it_will_not_reach_the_plane():
    game = FakeGame()
    game.learn(facts.THE_STORE)
    assert {"text": "Food: 15 days", "class": "low"} in buildHeader(game)["chips"]
    game.state.food += 5 * 4
    assert {"text": "Food: 20 days"} in buildHeader(game)["chips"]


def test_the_storm_half_rations_and_a_fifth_mouth_each_get_a_chip():
    game = FakeGame()
    game.state.day = STORM_DAYS[0]
    game.state.flags[flags.HALF_RATIONS] = True
    game.state.akselAt = AKSEL_STATION
    chips = buildHeader(game)["chips"]
    assert {"text": "Storm", "class": "low"} in chips
    assert "Half rations" in chips
    assert "Five at the table" in chips
    game.state.day = STORM_DAYS[-1] + 1
    assert not any(
        isinstance(chip, dict) and chip["text"] == "Storm"
        for chip in buildHeader(game)["chips"]
    )


def test_once_the_winter_is_over_the_header_names_the_ending_not_the_clock():
    game = FakeGame()
    game.learn(facts.THE_STORE)
    game.state.day = PLANE_DAY
    game.state.location = "epilogue"
    game.state.ending = facts.FIVE_OUT
    header = buildHeader(game)
    assert header["title"] == "Overwinter - After five on the plane"
    assert chipTexts(header) == [
        "After five on the plane",
        "After",
        "Known: 1/%d" % len(facts.FACTS),
    ]


def test_each_ending_has_its_own_name_in_the_header():
    game = FakeGame()
    game.state.ending = facts.THE_DARK_FLIGHT
    assert buildHeader(game)["chips"][0] == "After the dark flight"
    game.state.ending = facts.AKSEL_STAYED
    assert buildHeader(game)["chips"][0] == "After Aksel stayed"
