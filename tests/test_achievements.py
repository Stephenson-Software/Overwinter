"""Arcade achievements: every declared one is reachable, each route reports
what it should at the moment it happens, and none of it touches the save."""

import json
import re

import pytest

from overwinter import achievements, facts, flags
from overwinter.state import DARK_FLIGHT_DAY, State
from test_endings import TELL_DOV
from test_game import (
    DAY_FIVE,
    DAY_ONE,
    DAY_SEVEN,
    DAY_SIX,
    DAY_TEN,
    DAY_TWO,
    DAYS_THREE_AND_FOUR,
    FULL_RUN,
    ON_THE_STRIP,
    SLEEP,
    STORM,
    TO_THE_PLANE,
    TURN_IN,
)


@pytest.fixture
def unlocked(monkeypatch):
    """Record every tak.arcade.unlock call instead of making it."""
    calls = []
    monkeypatch.setattr(achievements.arcade, "unlock", calls.append)
    return calls


# FULL_RUN, plus an evening at the radio on day eleven so Dov's game is
# learned too: everything the station can tell you, then five on the plane.
EVERYTHING_RUN = (
    DAY_ONE
    + DAY_TWO
    + DAYS_THREE_AND_FOUR
    + DAY_FIVE
    + DAY_SIX
    + DAY_SEVEN
    + STORM
    + DAY_TEN
    + [
        "Go to the galley",
        "Count the store",  # -> afternoon
        "Cook the meal",  # -> evening
        "Go to the radio room",
        "Sit in on the evening schedule",  # DOVS_GAME; day ends -> day 12
    ]
    + TURN_IN
    + TO_THE_PLANE[2:]
    + ON_THE_STRIP
)

DARK_FLIGHT_RUN = (
    DAY_ONE
    + DAY_TWO
    + DAYS_THREE_AND_FOUR
    + TELL_DOV
    + ["Send it.", "[Back]"]
    + TURN_IN
    + SLEEP * (DARK_FLIGHT_DAY - 6)
    + ["Quit"]
)


def _stayRun():
    script = list(FULL_RUN)
    script[script.index("He's coming with us")] = "Let him go"
    return script


def test_the_declarations_are_valid_and_unique():
    pattern = re.compile(r"^[a-z][a-z0-9-]{1,30}$")
    assert 6 <= len(achievements.ACHIEVEMENTS) <= 12
    assert len(set(achievements.IDS)) == len(achievements.IDS)
    for achievement in achievements.ACHIEVEMENTS:
        assert pattern.match(achievement["id"]), achievement
        assert achievement["title"] and achievement["description"]
        assert isinstance(achievement["hidden"], bool)
    # The one spoiler is the one hidden.
    assert [a["id"] for a in achievements.ACHIEVEMENTS if a["hidden"]] == ["his-choice"]
    for achievementId in achievements.FACT_ACHIEVEMENTS.values():
        assert achievementId in achievements.IDS
    # One per ending.
    for ending in facts.ENDINGS:
        assert ending in achievements.FACT_ACHIEVEMENTS


def test_five_on_the_plane_with_everything_known(scripted, unlocked):
    game, ui = scripted(list(EVERYTHING_RUN))
    game.play()
    assert game.state.ending == facts.FIVE_OUT
    assert all(game.state.knows(f) for f in achievements.CLUE_FACTS)
    assert set(unlocked) == {
        "counted",
        "signed-for",
        "old-stores",
        "the-answer",
        "the-whole-winter",
        "remembered",
        "twentieth-morning",
    }
    # Each fact's achievement is reported once, when it is learned.
    assert unlocked.count("counted") == 1
    assert unlocked.count("the-whole-winter") == 1
    assert unlocked[-1] == "twentieth-morning"


def test_the_full_run_without_doves_game_is_not_the_whole_winter(scripted, unlocked):
    game, ui = scripted(list(FULL_RUN))
    game.play()
    assert "twentieth-morning" in unlocked
    assert "the-whole-winter" not in unlocked


def test_letting_aksel_stay(scripted, unlocked):
    game, ui = scripted(_stayRun())
    game.play()
    assert game.state.ending == facts.AKSEL_STAYED
    assert "his-choice" in unlocked
    assert "twentieth-morning" not in unlocked
    assert unlocked[-1] == "his-choice"


def test_the_dark_flight(scripted, unlocked):
    game, ui = scripted(list(DARK_FLIGHT_RUN))
    game.play()
    assert game.state.ending == facts.THE_DARK_FLIGHT
    assert "in-the-dark" in unlocked
    assert "the-answer" in unlocked
    assert "remembered" in unlocked
    assert "twentieth-morning" not in unlocked


def test_every_declared_achievement_is_reached_by_some_route(scripted, unlocked):
    for script in (EVERYTHING_RUN, _stayRun(), DARK_FLIGHT_RUN):
        game, ui = scripted(list(script))
        game.play()
    assert set(unlocked) == set(achievements.IDS)


def test_a_new_game_reports_nothing_before_anything_happens(scripted, unlocked):
    game, ui = scripted(["Create New Save", "Quit"])
    game.play()
    assert unlocked == []


def test_a_loaded_save_reports_what_it_already_earned_and_is_not_changed(
    scripted, unlocked
):
    game, ui = scripted(list(DARK_FLIGHT_RUN))
    game.play()
    path = game.saveFileManager.get_save_path("save.json")
    with open(path, "rb") as saveFile:
        before = saveFile.read()
    del unlocked[:]

    game2, ui2 = scripted(["Load Slot 1", "Quit"])
    game2.play()
    # Loading reports the save's achievements without playing anything.
    assert set(unlocked) == {
        "counted",
        "signed-for",
        "old-stores",
        "the-answer",
        "remembered",
        "in-the-dark",
    }
    # The quit itself saves; the save holds no trace of any achievement.
    with open(path, "rb") as saveFile:
        after = json.loads(saveFile.read())
    assert after == json.loads(before)
    assert "achievements" not in after


def test_catch_up_only_reads_the_state(unlocked):
    state = State()
    for fact in achievements.CLUE_FACTS + [facts.AKSEL_STAYED]:
        state.learn(fact)
    state.flags[flags.BACKED_AKSEL_STAYING] = True
    before = json.dumps(state.toDict(), sort_keys=True)
    achievements.catchUp(state)
    assert json.dumps(state.toDict(), sort_keys=True) == before
    assert "the-whole-winter" in unlocked
    assert "his-choice" in unlocked
    assert "remembered" in unlocked


def test_an_unlock_that_raises_never_reaches_the_game(monkeypatch):
    def boom(achievementId):
        raise RuntimeError("no arcade")

    monkeypatch.setattr(achievements.arcade, "unlock", boom)
    achievements.unlock("counted")  # does not raise
