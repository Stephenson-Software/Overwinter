"""The last pages, built straight from a state: every remembered choice gets
its sentence, and the count says how it closed."""

from overwinter import endings, facts, flags, people
from overwinter.state import State


def _ended(ending, **setFlags):
    state = State()
    state.ending = ending
    state.flags.update(setFlags)
    return state


def _paragraphs(state):
    return endings.text(state).split("\n\n")


def _starting(state, prefix):
    return [p for p in _paragraphs(state) if p.startswith(prefix)]


def test_each_ending_has_its_own_name_and_opening():
    cases = [
        (facts.FIVE_OUT, "five on the plane", "and five of you got on it"),
        (facts.AKSEL_STAYED, "Aksel stayed", "and four of you got on it"),
        (facts.THE_DARK_FLIGHT, "the dark flight", "Base sent the plane in the dark"),
    ]
    for ending, name, opening in cases:
        state = _ended(ending)
        assert endings.name(state) == name
        first = _paragraphs(state)[0]
        assert first.startswith("WHAT HAPPENED.")
        assert opening in first
        assert _paragraphs(state)[-1].startswith("WHAT IT WAS.")


def test_marits_secret_is_remembered_either_way_and_silent_if_never_asked():
    kept = _ended(facts.FIVE_OUT, **{flags.KEPT_MARITS_SECRET: True})
    assert _starting(kept, "MARIT. You told her you would keep it, and you did.")
    refused = _ended(facts.FIVE_OUT, **{flags.KEPT_MARITS_SECRET: False})
    assert _starting(
        refused, "MARIT. You told her to her face that you would not keep it."
    )
    assert not _starting(_ended(facts.FIVE_OUT), "MARIT.")


def test_dov_is_remembered_for_waiting_or_for_being_told():
    holds = _ended(facts.FIVE_OUT, **{flags.TOLD_DOV: True, flags.DOV_HOLDS: True})
    assert _starting(holds, "DOV. You told him there were five, and then you gave him")
    told = _ended(facts.FIVE_OUT, **{flags.TOLD_DOV: True})
    assert _starting(told, "DOV. You told him. He never said what he did with it.")
    reported = _ended(
        facts.FIVE_OUT, **{flags.TOLD_DOV: True, flags.DOV_REPORTED: True}
    )
    assert not _starting(reported, "DOV.")
    assert not _starting(_ended(facts.FIVE_OUT), "DOV.")


def test_teo_is_remembered_for_being_told_on_covered_for_or_never_explained():
    told = _ended(facts.FIVE_OUT, **{flags.TOLD_MARIT_ABOUT_TEO: True})
    assert _starting(told, "TEO. You told Marit about the night hours")
    covered = _ended(
        facts.FIVE_OUT, **{flags.COVERED_FOR_TEO: True, flags.GENERATOR_RAN_DRY: True}
    )
    assert _starting(covered, "TEO. You said nothing about the night hours.")
    unexplained = _ended(facts.FIVE_OUT, **{flags.GENERATOR_RAN_DRY: True})
    assert _starting(unexplained, "TEO. The generator ran dry on the storm night.")
    assert not _starting(_ended(facts.FIVE_OUT), "TEO.")


def test_aksel_on_the_five_out_page_follows_how_he_came_to_the_table():
    cases = [
        ({flags.BROUGHT_AKSEL_IN: True}, "AKSEL. You asked him to come in and he came"),
        ({flags.AKSEL_WALKED_IN: True}, "AKSEL. He walked in on his own"),
        (
            {flags.LEFT_AKSEL_AT_HUT: True},
            "AKSEL. You left him in the hut, as he asked",
        ),
        ({}, "AKSEL. You knew where he was and never said what you wanted of him."),
    ]
    for setFlags, line in cases:
        state = _ended(facts.FIVE_OUT, **setFlags)
        assert len(_starting(state, line)) == 1, setFlags


def test_saying_five_on_the_strip_is_remembered_and_takes_back_his_winter():
    refusal = "On the strip he asked you to say four"
    for setFlags in (
        {flags.BROUGHT_AKSEL_IN: True},
        {flags.AKSEL_WALKED_IN: True},
        {flags.LEFT_AKSEL_AT_HUT: True},
        {},
    ):
        refused = _ended(
            facts.FIVE_OUT, **dict(setFlags, **{flags.BACKED_AKSEL_STAYING: False})
        )
        (aksel,) = _starting(refused, "AKSEL.")
        assert refusal in aksel, setFlags
        assert "the last winter he had asked for" in aksel
        assert "He had his winter" not in aksel, setFlags

        (unasked,) = _starting(_ended(facts.FIVE_OUT, **setFlags), "AKSEL.")
        assert refusal not in unasked, setFlags


def test_the_strip_choice_is_one_people_remember():
    assert people.REMEMBERED[flags.BACKED_AKSEL_STAYING] == "Aksel"


def test_the_count_names_every_way_it_was_closed():
    state = _ended(
        facts.FIVE_OUT, **{flags.DEPOT_FETCHED: True, flags.HALF_RATIONS: True}
    )
    state.seals = 2
    (count,) = _starting(state, "THE COUNT.")
    assert count.startswith(
        "THE COUNT. It closed, because you walked the headland for the 1958 "
        "depot; you sat at the breathing holes with Aksel and brought back 2 "
        "seals; you put the station on half rations and Marit let you."
    )
    assert "Half rations for that long leaves a mark" in count

    one = _ended(facts.FIVE_OUT)
    one.seals = 1
    (count,) = _starting(one, "THE COUNT.")
    assert "brought back a seal." in count
    assert "Half rations" not in count


def test_an_empty_store_is_counted_in_lean_days_before_anything_else():
    state = _ended(
        facts.FIVE_OUT, **{flags.STORE_EMPTIED_ON: 15, flags.DEPOT_FETCHED: True}
    )
    (count,) = _starting(state, "THE COUNT.")
    assert count.startswith(
        "THE COUNT. It did not close. The store was empty on day 15 and the "
        "last 5 days were pemmican"
    )


def test_a_count_nobody_closed_and_that_never_ran_out_says_so():
    (count,) = _starting(_ended(facts.FIVE_OUT), "THE COUNT.")
    assert count.startswith("THE COUNT. It closed on its own, barely")


def test_aksel_staying_keeps_his_own_page_and_the_peoples_sentences():
    state = _ended(
        facts.AKSEL_STAYED,
        **{flags.KEPT_MARITS_SECRET: True, flags.BROUGHT_AKSEL_IN: True},
    )
    assert _starting(state, "AKSEL. He has the old hut, the stove, the seal holes")
    assert not _starting(state, "AKSEL. You asked him to come in")
    assert _starting(state, "MARIT.")
    assert _starting(state, "THE COUNT.")


def test_the_dark_flight_leaves_out_marit_and_dov_but_not_teo():
    state = _ended(
        facts.THE_DARK_FLIGHT,
        **{
            flags.KEPT_MARITS_SECRET: True,
            flags.TOLD_DOV: True,
            flags.TOLD_MARIT_ABOUT_TEO: True,
        },
    )
    assert not _starting(state, "MARIT.")
    assert not _starting(state, "DOV.")
    assert _starting(state, "TEO. You told Marit about the night hours")
    assert _starting(state, "THE REST. Three of you finished the winter")
    assert not _starting(state, "THE COUNT.")
