from conftest import FakeGame

from overwinter import facts, flags, people
from overwinter.state import AKSEL_STATION, STORM_DAYS


def questions(npc):
    return [option["question"] for option in npc.get_dialogue_options()]


def ask(npc, question):
    """Ask the first available line that starts with the question, the way
    a front-end would: by its index among the lines on offer."""
    for index, asked in enumerate(questions(npc)):
        if asked.startswith(question):
            return npc.get_dialogue_response(index)
    raise AssertionError("%r is not on offer: %r" % (question, questions(npc)))


def afterTheStormNight(game):
    game.state.day = STORM_DAYS[0] + 1


def test_marit_answers_the_count_until_the_manifest_and_the_manifest_until_aksel():
    game = FakeGame()
    marit = people.marit(game)
    assert "I've counted the store. Fifteen days." not in questions(marit)

    game.learn(facts.THE_STORE)
    assert "Count it again on the fifth day" in ask(marit, "I've counted the store")

    game.learn(facts.THE_MANIFEST)
    assert "I've counted the store. Fifteen days." not in questions(marit)
    assert "Nothing on this island is lost" in ask(marit, "Four crates")

    game.learn(facts.THE_FIFTH)
    assert not any(q.startswith("Four crates") for q in questions(marit))
    # Neither line teaches anything; the sum is the player's to do.
    assert not game.state.knows(facts.MARITS_ARITHMETIC)


def test_refusing_to_keep_marits_secret_is_remembered_and_closes_the_choice():
    game = FakeGame()
    marit = people.marit(game)
    game.learn(facts.THE_FIFTH)
    ask(marit, "I've been across the bay")
    assert "I'll keep it." in questions(marit)

    assert "I will not ask you again" in ask(marit, "I won't keep it")
    assert game.state.flags[flags.KEPT_MARITS_SECRET] is False
    assert "I'll keep it." not in questions(marit)
    assert "I won't keep it. Dov has to know." not in questions(marit)
    assert people.REMEMBERED[flags.KEPT_MARITS_SECRET] == "Marit"


def test_marit_refuses_half_rations_until_the_sum_is_hers_too():
    game = FakeGame()
    marit = people.marit(game)
    game.learn(facts.THE_STORE)
    assert "Count it again" in ask(marit, "I want to put the station on half")
    assert flags.MARIT_APPROVED_HALF not in game.state.flags
    # A refusal is not a decision; the line stays on offer.
    assert "I want to put the station on half rations." in questions(marit)


def test_marit_and_dov_speak_about_the_storm_night_only_if_the_tank_ran_dry():
    game = FakeGame()
    marit, dov = people.marit(game), people.dov(game)
    afterTheStormNight(game)
    assert "About the storm night." not in questions(marit)
    assert "You missed your schedule in the storm." not in questions(dov)

    game.state.flags[flags.GENERATOR_RAN_DRY] = True
    assert "Minus twenty in the bunkroom" in ask(marit, "About the storm night")
    assert "First time in three winters" in ask(dov, "You missed your schedule")


def test_dov_talks_about_the_chess_once_the_game_is_known_and_teaches_nothing():
    game = FakeGame()
    dov = people.dov(game)
    assert "About the chess." not in questions(dov)

    game.learn(facts.DOVS_GAME)
    known = set(game.state.facts)
    assert "Her name is Sunniva" in ask(dov, "About the chess")
    assert set(game.state.facts) == known
    # Asking again is allowed; it is not a choice.
    assert "About the chess." in questions(dov)


def test_dov_answers_when_the_plane_is_coming_only_after_the_report():
    game = FakeGame()
    dov = people.dov(game)
    assert "When is the plane coming?" not in questions(dov)

    game.state.flags[flags.DOV_REPORTED] = True
    # Names the twelfth whatever the day; see issue #18.
    assert ask(dov, "When is the plane coming?").startswith("The twelfth")


def test_teo_speaks_about_the_storm_night_by_what_was_done_about_his_nights():
    def teoAfterTheStorm(flag=None):
        game = FakeGame()
        if flag is not None:
            game.state.flags[flag] = True
        afterTheStormNight(game)
        return ask(people.teo(game), "About the storm night")

    assert "You told her" in teoAfterTheStorm(flags.TOLD_MARIT_ABOUT_TEO)
    assert "you let me have the lights" in teoAfterTheStorm(flags.COVERED_FOR_TEO)
    assert "Don't ask me why" in teoAfterTheStorm()


def test_teo_has_nothing_to_say_about_the_storm_night_before_it_passes():
    game = FakeGame()
    game.state.day = STORM_DAYS[0]
    assert "About the storm night." not in questions(people.teo(game))


def test_the_choice_about_teos_nights_closes_once_the_storm_night_has_passed():
    game = FakeGame()
    teo, marit = people.teo(game), people.marit(game)
    game.learn(facts.TEOS_NIGHTS)
    assert "I'll say nothing to Marit. Keep your lights." in questions(teo)
    assert any(q.startswith("Teo's been running") for q in questions(marit))

    afterTheStormNight(game)
    assert "I'll say nothing to Marit. Keep your lights." not in questions(teo)
    assert not any(q.startswith("Teo's been running") for q in questions(marit))


def test_aksel_sends_you_to_marit_until_she_has_told_you_herself():
    game = FakeGame()
    aksel = people.aksel(game)
    assert "Marit signed you off the ship." not in questions(aksel)

    game.learn(facts.AKSELS_WINTER)
    assert "Ask her the rest" in ask(aksel, "Marit signed you off the ship")
    assert not game.state.knows(facts.MARITS_ARITHMETIC)

    game.learn(facts.MARITS_ARITHMETIC)
    assert "Marit signed you off the ship." not in questions(aksel)


def test_aksel_at_the_table_remembers_whether_he_walked_in():
    game = FakeGame()
    aksel = people.aksel(game)
    assert "How are you finding the galley?" not in questions(aksel)

    game.state.akselAt = AKSEL_STATION
    assert "Your galley" in ask(aksel, "How are you finding the galley")

    game.state.flags[flags.AKSEL_WALKED_IN] = True
    assert "I had counted too" in ask(aksel, "How are you finding the galley")
