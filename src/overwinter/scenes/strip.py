# @author Daniel McCoy Stephenson
from overwinter import endings, facts, progression
from overwinter.flags import (
    AKSEL_ASKED_TO_STAY,
    BACKED_AKSEL_STAYING,
    DEPOT_FETCHED,
    HUNTED_TODAY,
    PLANE_ON_STRIP,
)
from overwinter.scenes.base import Scene
from overwinter.state import (
    AKSEL_HUT,
    AKSEL_STATION,
    AKSEL_STAYED,
    DEPOT_FOOD,
    SEAL_FOOD,
)

# A wait at the holes: two waits in three bring a seal back.
HUNT_DRAWS = ("seal", "seal", "nothing")


class Strip(Scene):
    id = "strip"
    travelTo = ("galley", "office", "radio", "shed", "bunks")

    def descriptor(self):
        state = self.state
        if state.stormy:
            return "The door. Beyond it the wind is a wall, and Marit's order stands."
        return (
            "The strip: gravel under snow, the windsock straight out, the bay "
            "to the west a flat grey nothing, the ridge behind. The dark is "
            "not total - the snow gives back what light there is."
        )

    def run(self):
        state = self.state
        if state.flags.get(PLANE_ON_STRIP):
            return self.thePlane()
        options, actions, unavailable = [], [], {}
        if progression.isUnlocked(state, progression.THE_BAY):
            options.append("Cross the bay to the old hut")
            actions.append(("cross", None))
            if state.stormy:
                unavailable[len(options)] = "the storm"
            elif not state.iceSafe:
                unavailable[len(options)] = (
                    "the ice won't bear until the fifth day"
                    if state.knows(facts.THE_ICE)
                    else "the bay is open water and new ice - you don't know if it holds"
                )
        if progression.isUnlocked(state, progression.THE_HEADLAND):
            options.append("Walk the headland to the 1958 cairn")
            actions.append(("depot", None))
            if state.stormy:
                unavailable[len(options)] = "the storm"
            elif state.flags.get(DEPOT_FETCHED):
                unavailable[len(options)] = "you've emptied it"
        if progression.isUnlocked(state, progression.THE_HOLES):
            options.append("Wait at the breathing holes with Aksel")
            actions.append(("hunt", None))
            if state.stormy:
                unavailable[len(options)] = "the storm"
            elif state.akselAt not in (AKSEL_HUT, AKSEL_STATION):
                unavailable[len(options)] = "Aksel is gone"
            elif state.flags.get(HUNTED_TODAY):
                unavailable[len(options)] = "one wait a day is all the cold allows"
        options.append("Stand on the strip a while")
        actions.append(("stand", None))
        if state.stormy:
            unavailable[len(options)] = "the storm"
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "cross":
            self.ui.showDialogue(
                "An hour on the ice, the station's lights behind you and "
                "nothing ahead until there is: a low shape against the "
                "snow, and a line of smoke going straight up from it."
            )
            # The loop reads state.location, so the hour spent on the ice is
            # charged here and the hut is where the next menu is shown.
            self.state.location = "hut"
            self.game.prompt.reset()
            return self.spend(1)
        if kind == "depot":
            self.depot()
        elif kind == "hunt":
            self.hunt()
        else:
            self.ui.showDialogue(
                "You stand on the strip until the cold gets into your boots. "
                "Across the bay, if you look long enough, there is a point "
                "of light that is not a star. Or there isn't."
                if state.akselAt == AKSEL_HUT and not state.knows(facts.THE_FIFTH)
                else "You stand on the strip until the cold gets into your "
                "boots. The windsock does not change its mind."
            )
        return self.spend(1)

    def depot(self):
        state = self.state
        state.flags[DEPOT_FETCHED] = True
        state.food += DEPOT_FOOD
        self.ui.showDialogue(
            "A mile north along the headland, the cairn is where the log put "
            "it, and sound. Inside, under fifty years of 'inspected': two "
            "dozen tins. Half are swollen and you leave them. The rest is "
            "pemmican and hard bread from 1958, and it is food - %d rations "
            "of it, three days at four. You carry it back on your shoulders "
            "and put it in the store, and the count is better than it was." % DEPOT_FOOD
        )

    def hunt(self):
        state = self.state
        state.flags[HUNTED_TODAY] = True
        fetch = (
            "You cross to the hut first and Aksel comes back with you. "
            if state.akselAt == AKSEL_HUT
            else ""
        )
        if state.draw(HUNT_DRAWS) == "seal":
            state.seals += 1
            state.food += SEAL_FOOD
            self.ui.showDialogue(
                fetch + "Off the point the ice is thin over the current and "
                "there are holes in it, black and steaming. Aksel stands at "
                "one, and you at another, and nothing happens for a very "
                "long time, and then he moves once. A seal. He shows you "
                "how to sledge it. %d rations in the store by evening - two "
                "days for the station." % SEAL_FOOD
            )
        else:
            self.ui.showDialogue(
                fetch + "Off the point the holes are there, black and "
                "steaming, and you stand at one until you cannot feel your "
                "feet, and nothing comes up. Aksel says that is most days. "
                "You go back with nothing and he does not apologise for it."
            )

    # --- the twentieth morning --------------------------------------------
    def thePlane(self):
        state = self.state
        self.ui.showDialogue(
            "The Otter comes over the ridge at eleven with its lights on, "
            "turns once over the bay, and puts down on the strip in a "
            "cloud of its own snow. The pilot does not shut down. He "
            "counts heads through the windscreen."
        )
        # Whoever has not met him has by now: the store runs out before the
        # twentieth day unless someone who knows about him closed the count,
        # and the night it runs out he walks in on his own (winter._eat).
        if state.akselAt == AKSEL_HUT:
            self.ui.showDialogue(
                "Aksel is on the strip before the plane is; he crossed in the "
                "dark with a pack and stood at the edge of the gravel."
            )
        if state.knows(facts.AKSELS_WINTER):
            return self.akselAsks()
        return self.endWith(facts.FIVE_OUT)

    def akselAsks(self):
        state = self.state
        state.flags[AKSEL_ASKED_TO_STAY] = True
        choice = int(
            self.ui.showOptions(
                "Aksel takes your arm at the edge of the strip, while the "
                "pilot is counting. 'Say four,' he says. 'The ship comes in "
                "August. I have the hut and the holes and I would rather. "
                "Let me go back across before he looks again.' Marit is "
                "watching the two of you and has not moved.",
                ["He's coming with us.", "Let him go."],
            )
        )
        if choice == 1:
            state.flags[BACKED_AKSEL_STAYING] = False
            self.ui.showDialogue(
                "'No,' you say. 'Five.' He looks at you, and at the bay, and "
                "gets on the plane, and does not look at the bay again."
            )
            self.remember("Aksel")
            return self.endWith(facts.FIVE_OUT)
        state.flags[BACKED_AKSEL_STAYING] = True
        state.akselAt = AKSEL_STAYED
        self.ui.showDialogue(
            "You say nothing. He is off the gravel and onto the ice before "
            "the pilot looks up again, and the pilot counts four, and Marit "
            "gets on the plane last and does not say a word to anyone."
        )
        self.remember("Aksel")
        return self.endWith(facts.AKSEL_STAYED)

    def endWith(self, endingFact):
        state = self.state
        state.ending = endingFact
        self.game.learn(endingFact)
        state.flags.pop(PLANE_ON_STRIP, None)
        self.ui.showDialogue(endings.text(state))
        return self.go("epilogue")
