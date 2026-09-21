# @author Daniel McCoy Stephenson
from overwinter import people
from overwinter.scenes.base import Scene


class Shed(Scene):
    id = "shed"
    travelTo = ("galley", "office", "radio", "bunks", "strip")

    def descriptor(self):
        return (
            "The generator shed, across the yard: the diesel, the day-tank, "
            "the snowmobile under a tarpaulin, and Teo, who lives out here "
            "more than he needs to."
        )

    def run(self):
        options, actions, unavailable = [], [], {}
        options.append("Talk to Teo")
        actions.append(("teo", None))
        options.append("Look over the snowmobile and the sledge")
        actions.append(("look", None))
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "teo":
            self.talk(people.teo(self.game))
            return self.after()
        self.ui.showDialogue(
            "A snowmobile, a sledge with iron runners, and a maintenance book "
            "in Teo's careful hand starting the day he arrived: hour-meter "
            "reading, fuel, oil. The first line has a figure crossed out and "
            "written again, as if he had not believed it. He would know what "
            "it meant."
        )
        return self.spend(1)
