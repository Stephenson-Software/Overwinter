from overwinter import facts, premise
from overwinter.state import State


def test_every_lead_points_at_a_fact_and_never_names_it():
    for factId, fact in facts.FACTS.items():
        for target, line in facts.leads(factId):
            assert target in facts.FACTS, (factId, target)
            assert target != factId
            assert facts.title(target).lower() not in line.lower(), (factId, target)


def test_every_fact_but_the_first_and_the_endings_is_led_to():
    ledTo = {target for f in facts.FACTS for target, _ in facts.leads(f)}
    roots = {facts.THE_STORE}
    # Learned by doing rather than by rumour: reading the log, or listening
    # to the schedule, or the endings themselves.
    unled = {facts.TEOS_NIGHTS, facts.THE_ICE} | set(facts.ENDINGS)
    for factId in facts.FACTS:
        if factId in roots or factId in unled:
            continue
        assert factId in ledTo, factId


def test_the_trail_is_connected_by_leads():
    for earlier, later in zip(facts.TRAIL, facts.TRAIL[1:]):
        assert later in [t for t, _ in facts.leads(earlier)], (earlier, later)


def test_the_premise_page_grows_with_what_is_known_and_says_the_ending():
    state = State()
    empty = premise.text(state)
    assert "WHERE YOU ARE" in empty
    assert "WHAT IS HAPPENING TO YOU" not in empty
    assert "(1 of %d parts" % len(premise.PARAGRAPHS) in empty
    state.learn(facts.THE_STORE)
    assert "WHAT IS HAPPENING TO YOU. There is not enough food." in premise.text(state)
    for factId in facts.FACTS:
        if factId not in facts.ENDINGS:
            state.learn(factId)
    state.learn(facts.FIVE_OUT)
    full = premise.text(state)
    assert "WHAT YOU DID. You found where the food went" in full
    assert (
        "(%d of %d parts" % (len(premise.PARAGRAPHS) - 2, len(premise.PARAGRAPHS))
        in full
    )


def test_every_fact_is_needed_by_some_premise_paragraph():
    needed = {f for needs, _ in premise.PARAGRAPHS for f in needs}
    # Two facts are practical rather than story: what the plane needs and
    # when the ice bears. The story page does not depend on them.
    for factId in facts.FACTS:
        if factId in (facts.THE_PLANE, facts.THE_ICE):
            continue
        assert factId in needed, factId
