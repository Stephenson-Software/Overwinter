import json
import os
import re

from tak.saves import validateAgainstSchema

from overwinter import facts, flags
from overwinter.state import (
    AKSEL_STATION,
    PLANE_DAY,
    START_FOOD,
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
            used.update(re.findall(r"flags\.([A-Z_]+)\b", source))
            used.update(re.findall(r"state\.flags\[([A-Z_]+)\]", source))
    declared = {name for name in dir(flags) if name.isupper() and name != "ALL"}
    assert used <= declared, used - declared
    assert set(getattr(flags, n) for n in declared) == set(flags.ALL)
