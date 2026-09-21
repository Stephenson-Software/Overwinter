# @author Daniel McCoy Stephenson
from overwinter import facts, people
from overwinter.scenes.base import Scene
from overwinter.state import AKSEL_HUT


class Hut(Scene):
    """The old hut across the bay. Travel to and from it is by the strip and
    costs a watch each way; the hut has no travel rows of its own."""

    id = "hut"
    travelTo = ()

    def descriptor(self):
        if self.state.akselAt == AKSEL_HUT:
            return (
                "The old hut. A stove going, a lamp, two bunks, four crates "
                "with the station's stencil on them, and Aksel Rue at the "
                "table as if he had been expecting you for a week."
            )
        return (
            "The old hut, cold. The stove is out, the lamp is on its hook, "
            "and the crates are gone. The wire is back on the door."
        )

    def run(self):
        state = self.state
        if state.akselAt == AKSEL_HUT and self.game.learn(facts.THE_FIFTH):
            self.ui.showDialogue(
                "The door is not wired. Inside is warm. A man of about "
                "seventy looks up from a book and says, 'You'll be the new "
                "cook. Kettle's on.' Aksel Rue - you have seen the name on "
                "four winters of the galley's inventory sheets, in a hand "
                "you have been reading since you arrived. He was on the ship "
                "out in August. On paper. The four crates are stacked under "
                "the window."
            )
        options, actions = [], []
        if state.akselAt == AKSEL_HUT:
            options.append("Talk to Aksel")
            actions.append(("aksel", None))
        options.append("Look around the hut")
        actions.append(("look", None))
        options.append("Go back across the bay")
        actions.append(("back", None))
        options.append("Quit")
        actions.append(("quit", None))

        kind, _ = self.choose(self.descriptor(), options, actions)
        if kind == "quit":
            return "quit"
        if kind == "aksel":
            self.talk(people.aksel(self.game))
            if state.akselAt != AKSEL_HUT:
                # He is coming with you: the crossing is the same hour.
                self.ui.showDialogue(
                    "You cross back together, the sledge between you, and "
                    "the crates go into the store before supper."
                )
                self.state.location = "galley"
                return self.spend(1)
            return self.after()
        if kind == "look":
            self.ui.showDialogue(
                "Two bunks, one slept in. A shelf of books, most of them "
                "read. Fuel for the stove, stacked the way a careful man "
                "stacks it. The crates: OVERWINTER STORES / CAPE FERRIN, the "
                "station's stencil, four of them, one open."
                if state.akselAt == AKSEL_HUT
                else "Nothing left in it that was not here in 1961."
            )
            return self.spend(1)
        self.state.location = "galley"
        self.game.prompt.reset()
        return self.spend(1)
