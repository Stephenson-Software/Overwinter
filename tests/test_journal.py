from conftest import FakeGame, ScriptedUI

from overwinter import endings, facts, flags, premise, winter
from overwinter.scenes.galley import Galley
from overwinter.scenes.journal import Journal
from overwinter.state import (
    AKSEL_STATION,
    DARK_FLIGHT_DAY,
    ICE_SAFE_DAY,
    MANIFEST_FOOD,
    PLANE_DAY,
    STORM_DAYS,
)


def journal(script=()):
    game = FakeGame(ScriptedUI(list(script)))
    game.scenes = {"galley": Galley(game)}
    return game, Journal(game)


def calendarDays(state):
    return [day for day, _ in winter.calendar(state)]


def test_the_descriptor_counts_what_is_known_and_how_far_along_the_trail():
    game, page = journal()
    game.state.day = 3
    game.learn(facts.THE_STORE)
    game.learn(facts.THE_ICE)
    assert page.descriptor() == (
        "Day 3. 2 of %d things known; 1 of %d on the trail of the count."
        % (len(facts.FACTS), len(facts.TRAIL))
    )


def test_nothing_known_is_said_plainly_and_leads_nowhere():
    _, page = journal()
    assert page.knownText() == "Nothing yet."
    assert page.leadsText() == ""


def test_what_you_know_is_in_registry_order_with_the_day_and_the_trail_marked():
    game, page = journal()
    game.state.day = 6
    game.learn(facts.THE_ICE)
    game.state.day = 2
    game.learn(facts.THE_STORE)
    text = page.knownText()
    store, ice = facts.title(facts.THE_STORE), facts.title(facts.THE_ICE)
    assert text.index(store) < text.index(ice)
    assert "* %s - day 2\n  %s" % (store, facts.text(facts.THE_STORE)) in text
    assert "- %s - day 6\n  %s" % (ice, facts.text(facts.THE_ICE)) in text
    assert text.endswith("(* marks the trail of the count.)")


def test_leads_list_where_to_look_and_drop_what_has_been_found():
    game, page = journal()
    game.learn(facts.THE_STORE)
    text = page.leadsText()
    assert text.startswith("\n\nThere's more to learn:\n")
    for _, line in facts.leads(facts.THE_STORE):
        assert "? " + line in text
    game.learn(facts.THE_MANIFEST)
    text = page.leadsText()
    assert dict(facts.leads(facts.THE_STORE))[facts.THE_MANIFEST] not in text
    for _, line in facts.leads(facts.THE_MANIFEST):
        assert "? " + line in text


def test_the_calendar_starts_with_only_the_plane():
    game, page = journal()
    assert calendarDays(game.state) == [PLANE_DAY]
    assert page.calendarText() == (
        "Day 20  The plane. Light enough on the strip; the Otter comes."
    )


def test_the_calendar_learns_the_ice_by_hearing_or_living_it():
    game, _ = journal()
    game.learn(facts.THE_ICE)
    assert calendarDays(game.state) == [ICE_SAFE_DAY, PLANE_DAY]
    game, _ = journal()
    game.state.day = ICE_SAFE_DAY
    assert calendarDays(game.state) == [ICE_SAFE_DAY, PLANE_DAY]


def test_the_storm_is_on_the_calendar_once_it_has_come():
    game, _ = journal()
    game.state.day = STORM_DAYS[0] - 1
    assert STORM_DAYS[0] not in calendarDays(game.state)
    game.state.day = STORM_DAYS[0]
    assert calendarDays(game.state) == [ICE_SAFE_DAY, STORM_DAYS[0], PLANE_DAY]


def test_the_dark_flight_is_listed_only_while_it_is_coming():
    game, page = journal()
    game.state.flags[flags.DOV_REPORTED] = True
    assert DARK_FLIGHT_DAY in calendarDays(game.state)
    assert "Day 12  Base sends the plane in the dark." in page.calendarText()
    game.state.ending = facts.THE_DARK_FLIGHT
    assert DARK_FLIGHT_DAY not in calendarDays(game.state)


def test_the_count_says_how_short_the_sum_is():
    game, _ = journal()
    game.learn(facts.THE_STORE)
    assert game.scenes["galley"].sum() == (
        "60 rations on the shelf.\n"
        "4 people eating, at full rations: 4 rations a day.\n"
        "15 days of food. 19 days until the plane.\n"
        "The sum is 4 days short."
    )


def test_the_count_with_aksel_on_half_rations_closes_and_names_the_manifest():
    game, _ = journal()
    state = game.state
    state.day = 10
    state.food = 30
    state.akselAt = AKSEL_STATION
    state.flags[flags.HALF_RATIONS] = True
    game.learn(facts.THE_MANIFEST)
    total = game.scenes["galley"].sum()
    assert "5 people eating, at half rations: 3 rations a day." in total
    assert "10 days of food. 10 days until the plane." in total
    assert "The sum closes, with 0 days over." in total
    assert (
        "The manifest says %d rations were landed: 21 days at four. "
        "24 rations are not in this store." % MANIFEST_FOOD
    ) in total


def test_the_menu_offers_the_count_once_counted_and_the_last_page_once_over():
    game, page = journal(["Close the journal"])
    assert page.run() == "bunks"
    labels = game.ui.menus[-1][1]
    assert "The count" not in labels
    assert "The last page" not in labels

    game, page = journal(["The count", "The last page", "Close the journal"])
    game.learn(facts.THE_STORE)
    game.state.ending = facts.FIVE_OUT
    assert page.run() == "journal"
    assert game.ui.saw("60 rations on the shelf.")
    assert page.run() == "journal"
    assert game.ui.dialogues[-1] == endings.text(game.state)
    assert page.run() == "epilogue"
    assert game.state.location == "epilogue"


def test_each_page_of_the_journal_shows_its_own_text():
    game, page = journal(
        ["What is happening to you", "What you know", "The winter, as you know it"]
    )
    game.learn(facts.THE_STORE)
    page.run()
    page.run()
    page.run()
    premisePage, knownPage, calendarPage = game.ui.dialogues
    assert premisePage == premise.text(game.state)
    assert knownPage == page.knownText() + page.leadsText()
    assert calendarPage == page.calendarText()
