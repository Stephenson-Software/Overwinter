from overwinter import facts, progression
from overwinter.state import State


def test_nothing_is_unlocked_on_the_first_morning():
    state = State()
    assert progression.getNextUnlock(state) is None
    assert state.unlocked == []


def test_the_journal_opens_with_the_first_fact_of_any_kind():
    state = State()
    state.learn(facts.THE_STORE)
    unlock = progression.getNextUnlock(state)
    assert unlock["id"] == progression.JOURNAL
    assert progression.isUnlocked(state, progression.JOURNAL)
    # Announced once: the next screen has nothing new to say.
    assert progression.getNextUnlock(state) is None


def test_each_place_off_the_station_opens_on_its_own_fact():
    for factId, featureId in (
        (facts.THE_OLD_HUT, progression.THE_BAY),
        (facts.THE_DEPOT, progression.THE_HEADLAND),
        (facts.THE_SEALS, progression.THE_HOLES),
    ):
        state = State()
        state.unlocked.append(progression.JOURNAL)
        assert not progression.isUnlocked(state, featureId)
        state.learn(factId)
        assert progression.getNextUnlock(state)["id"] == featureId
        assert progression.isUnlocked(state, featureId)


def test_several_earned_at_once_arrive_one_screen_at_a_time_in_order():
    state = State()
    for factId in (facts.THE_SEALS, facts.THE_DEPOT, facts.THE_OLD_HUT):
        state.learn(factId)
    order = []
    while True:
        unlock = progression.getNextUnlock(state)
        if unlock is None:
            break
        order.append(unlock["id"])
    assert order == [
        progression.JOURNAL,
        progression.THE_BAY,
        progression.THE_HEADLAND,
        progression.THE_HOLES,
    ]


def test_catching_up_a_loaded_save_grants_everything_it_has_earned_at_once():
    state = State()
    state.learn(facts.THE_STORE)
    state.learn(facts.THE_DEPOT)
    progression.catchUp(state)
    assert state.unlocked == [progression.JOURNAL, progression.THE_HEADLAND]
    assert not progression.isUnlocked(state, progression.THE_BAY)
    assert progression.getNextUnlock(state) is None


def test_every_unlock_announces_itself_in_words():
    for unlock in progression.UNLOCKS:
        assert unlock["name"]
        assert unlock["announcement"].strip()
