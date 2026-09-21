# @author Daniel McCoy Stephenson
from overwinter import progression, winter
from overwinter.flags import MET_TEO
from overwinter.scenes.base import Scene
from overwinter.state import EVENING


class Bunks(Scene):
    id = "bunks"
    travelTo = ("galley", "office", "radio", "shed", "strip")

    def descriptor(self):
        return (
            "The bunkroom: four bunks, a stove, your notebook under the pillow. "
            "Teo's light is on. Teo's light is always on."
        )

    def run(self):
        state = self.state
        options, actions, unavailable = [], [], {}
        options.append("Open your journal")
        actions.append(("journal", None))
        if not progression.isUnlocked(state, progression.JOURNAL):
            unavailable[len(options)] = "nothing to write yet"
        options.append("Sit up with Teo")
        actions.append(("teo", None))
        if state.watch != EVENING:
            unavailable[len(options)] = "he's out at the shed till evening"
        options.append("Turn in for the night")
        actions.append(("sleep", None))
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "journal":
            return self.go("journal")
        if kind == "teo":
            state.flags[MET_TEO] = True
            self.ui.showDialogue(
                "Teo does not sleep. He talks - about engines, about his "
                "mother's kitchen, about the dark, which he did not know "
                "would be like this. Around midnight he says, 'I'll just "
                "check the generator,' and goes out, and the lights stay on "
                "all night. If you asked him about the fuel, he would tell "
                "you. He wants to tell somebody."
            )
            return self.spend(1)
        # Turn in: whatever is left of the day is slept through.
        outcome = winter.advance(self.game, len(winter.WATCHES) - state.watch)
        if outcome.lines:
            self.ui.showDialogue("\n\n".join(outcome.lines))
        self.game.prompt.text = "Morning watch. What would you like to do?"
        return self.after(outcome)
