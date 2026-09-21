# @author Daniel McCoy Stephenson
from overwinter import facts, people
from overwinter.flags import HALF_RATIONS, MARIT_APPROVED_HALF
from overwinter.scenes.base import Scene
from overwinter.state import (
    AKSEL_STATION,
    EVENING,
    MANIFEST_FOOD,
    START_FOOD,
    STATION_MOUTHS,
)

# What gets said at the table, in no order anyone chose. Drawn from the
# winter's fixed sequence, so a reloaded save hears the same supper.
TABLE_TALK = (
    "Teo asks whether it is always this dark. Dov says yes. Marit says nothing.",
    "Dov says the glass is falling and there will be weather by the end of "
    "the week. Marit says she has seen the glass.",
    "Teo says the snowmobile was warm the day he arrived, and then that he "
    "probably imagined it. Marit passes him the bread.",
    "Dov looks at the clock through the whole meal. At ten to ten he is gone.",
    "Marit eats what is put in front of her and says it was good, which is "
    "the most she says at any meal.",
    "Teo talks about his mother's kitchen for a quarter of an hour and "
    "nobody stops him.",
    "Dov says Base asked after the station's stores today, as they do every "
    "week, and he told them what the manifest says.",
    "Nobody talks about the far side of the bay. Nobody has, since you came.",
)


class Galley(Scene):
    id = "galley"
    travelTo = ("office", "radio", "shed", "bunks", "strip")

    def descriptor(self):
        state = self.state
        if state.watch == EVENING:
            who = "five" if state.akselAt == AKSEL_STATION else "four"
            return (
                "The galley, evening watch. The stove is lit, the table is "
                "laid for %s, and the store is behind the door at your back." % who
            )
        return (
            "The galley. Your stove, your table, and the store behind the "
            "door: ten crates, a shelf of tins, and the flour bin."
        )

    def run(self):
        state = self.state
        options, actions, unavailable = [], [], {}
        options.append("Count the store")
        actions.append(("count", None))
        if state.akselAt == AKSEL_STATION:
            options.append("Talk to Aksel")
            actions.append(("aksel", None))
        options.append("Cook the meal")
        actions.append(("cook", None))
        if state.knows(facts.THE_STORE):
            if state.flags.get(HALF_RATIONS):
                options.append("Put the station back on full rations")
                actions.append(("full", None))
            else:
                options.append("Put the station on half rations")
                actions.append(("half", None))
                if not state.flags.get(MARIT_APPROVED_HALF):
                    unavailable[len(options)] = "Marit would have to agree to that"
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "count":
            self.count()
        elif kind == "aksel":
            self.talk(people.aksel(self.game))
            return self.after()
        elif kind == "cook":
            self.ui.showDialogue(
                "You cook. " + state.draw(TABLE_TALK)
                if state.watch == EVENING
                else "You cook. The others eat where they work, and the "
                "plates come back."
            )
        elif kind == "half":
            state.flags[HALF_RATIONS] = True
            self.ui.showDialogue(
                "You say it at the table: half rations from tomorrow, until "
                "the count says otherwise. Dov nods. Teo looks at his plate. "
                "Marit says, 'The cook has the store,' and that is the end "
                "of it."
            )
        elif kind == "full":
            state.flags[HALF_RATIONS] = False
            self.ui.showDialogue("Full rations again. Teo says thank you to his plate.")
        return self.spend(1)

    def count(self):
        state = self.state
        first = self.game.learn(facts.THE_STORE)
        if first:
            self.ui.showDialogue(
                "You count it properly, crate by crate and tin by tin: ten "
                "crates and the shelf. %d rations. Fifteen days at four, and "
                "the plane comes on the twentieth.\n\nNobody has said so. "
                "You check the shelf twice. Fifteen. Marit signed for this; "
                "the plane's manifest was on the seat beside you, and you "
                "remember it being longer than this." % state.food
            )
            return
        self.ui.showDialogue(self.sum())

    def sum(self):
        """The count, as plain arithmetic, for the galley and the journal."""
        state = self.state
        lines = [
            "%d rations on the shelf." % state.food,
            "%d %s eating, at %s rations: %d rations a day."
            % (
                state.mouths,
                "people" if state.mouths != 1 else "person",
                "half" if state.flags.get(HALF_RATIONS) else "full",
                state.dailyRations,
            ),
            "%d days of food. %d days until the plane."
            % (state.foodDays, state.daysUntilPlane),
        ]
        gap = state.daysUntilPlane - state.foodDays
        if gap > 0:
            lines.append("The sum is %d days short." % gap)
        else:
            lines.append("The sum closes, with %d days over." % -gap)
        if state.knows(facts.THE_MANIFEST):
            lines.append(
                "The manifest says %d rations were landed: %d days at four. "
                "%d rations are not in this store."
                % (
                    MANIFEST_FOOD,
                    MANIFEST_FOOD // STATION_MOUTHS,
                    MANIFEST_FOOD - START_FOOD,
                )
            )
        return "\n".join(lines)
