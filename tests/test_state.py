import json
import os
import re

from tak.saves import validateAgainstSchema

from overwinter import facts, flags
from overwinter.state import (
    AKSEL_STATION,
    PLANE_DAY,
    START_FOOD,
    STORM_DAYS,
    State,
    WORLD_SEED,
)
from overwinter.scenes.galley import TABLE_TALK
from overwinter.scenes.strip import HUNT_DRAWS


def test_a_fresh_winter_validates_and_round_trips():
    state = State()
    data = state.toDict()
    validateAgainstSchema(data, "schemas/save.json")
    again = State.fromDict(json.loads(json.dumps(data)))
    assert again.toDict() == data


def test_learning_records_the_day_and_refuses_unknown_facts():
    state = State()
    state.day = 4
    assert state.learn(facts.THE_STORE) is True
    assert state.learn(facts.THE_STORE) is False
    assert state.learnedOn(facts.THE_STORE) == 4
    try:
        state.learn("the_kraken")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown fact accepted")


def test_loading_drops_facts_the_game_no_longer_has():
    data = State().toDict()
    data["facts"] = [facts.THE_STORE, "retired_fact"]
    data["factDays"] = {facts.THE_STORE: 2, "retired_fact": 3}
    state = State.fromDict(data)
    assert state.facts == [facts.THE_STORE]
    assert state.factDays == {facts.THE_STORE: 2}


def test_the_count_is_arithmetic_the_player_can_check():
    state = State()
    assert state.food == START_FOOD
    assert state.mouths == 4
    assert state.dailyRations == 4
    assert state.foodDays == 15
    assert state.daysUntilPlane == PLANE_DAY - 1
    state.akselAt = AKSEL_STATION
    assert state.mouths == 5
    state.flags[flags.HALF_RATIONS] = True
    assert state.dailyRations == 3  # five mouths at half, rounded up
    state.akselAt = "hut"
    assert state.dailyRations == 2


def test_each_draw_is_a_function_of_the_seed_and_its_index_only():
    first = State()
    a = [first.draw(TABLE_TALK) for _ in range(6)]
    # A save reloaded after three draws continues the same sequence, even
    # though random.choice consumes a different amount of randomness per
    # call for populations that are not a power of two.
    reloaded = State.fromDict(State().toDict())
    for _ in range(3):
        reloaded.draw(HUNT_DRAWS)  # a different population, same indices
    b = [reloaded.draw(TABLE_TALK) for _ in range(3)]
    assert a[3:] == b
    assert first.rngDraws == 6
    assert WORLD_SEED == 1958


def test_the_storm_night_is_a_property_not_a_day_number():
    state = State()
    assert not state.stormNightPassed
    state.day = STORM_DAYS[0]
    assert state.stormy and not state.stormNightPassed
    state.day = STORM_DAYS[0] + 1
    assert state.stormNightPassed


def test_no_person_or_scene_gates_on_the_day_number():
    """What opens a line or a menu row is what you know, a flag, or a
    state property - never a comparison against the day, and never a
    calendar constant carried out of state.py. The people and the scenes
    may still print the day; they may not decide on it."""
    root = os.path.join(os.path.dirname(__file__), "..", "src", "overwinter")
    paths = [os.path.join(root, "people.py")]
    scenes = os.path.join(root, "scenes")
    paths += [os.path.join(scenes, n) for n in os.listdir(scenes) if n.endswith(".py")]
    compared = re.compile(r"\.day\b\s*(?:[<>=!]=?|\bin\b)|(?:[<>=!]=?)\s*\w+\.day\b")
    calendar = re.compile(r"\b(?:PLANE_DAY|ICE_SAFE_DAY|STORM_DAYS|DARK_FLIGHT_DAY)\b")
    for path in paths:
        with open(path) as f:
            source = f.read()
        name = os.path.relpath(path, root)
        assert not compared.search(source), (name, compared.search(source).group())
        assert not calendar.search(source), (name, calendar.search(source).group())


def test_every_flag_the_game_sets_is_declared_in_one_place():
    """Every flags.NAME the source writes is listed in flags.ALL, and no
    string key is written to state.flags directly."""
    root = os.path.join(os.path.dirname(__file__), "..", "src", "overwinter")
    used = set()
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if not name.endswith(".py") or name == "flags.py":
                continue
            with open(os.path.join(dirpath, name)) as f:
                source = f.read()
            assert 'flags["' not in source and "flags['" not in source, name
            assert 'flags.get("' not in source and "flags.get('" not in source, name
            used.update(re.findall(r"flags\.([A-Z_]+)\b", source))
            used.update(re.findall(r"state\.flags\[([A-Z_]+)\]", source))
    declared = {name for name in dir(flags) if name.isupper() and name != "ALL"}
    assert used <= declared, used - declared
    assert set(getattr(flags, n) for n in declared) == set(flags.ALL)
