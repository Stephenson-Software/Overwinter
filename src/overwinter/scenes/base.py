# @author Daniel McCoy Stephenson
from overwinter import endings, people, winter
from overwinter.flags import PLANE_ON_STRIP

STORM_REASON = "the storm - Marit's order is nobody past the door"

TRAVEL_LABELS = {
    "galley": "Go to the galley",
    "office": "Go to Marit's office",
    "radio": "Go to the radio room",
    "shed": "Go out to the generator shed",
    "bunks": "Go to the bunkroom",
    "strip": "Go outside, onto the strip",
}

# Places the storm shuts. The shed is a separate hut; the strip is the strip.
STORM_BOUND = ("shed", "strip")


class Scene:
    """Shared menu plumbing: a scene builds paired options/actions lists so
    rows can come and go with the player's progress without the numbers
    drifting - see tak's unavailableReasons - and the travel rows are the
    same on every menu."""

    id = ""
    travelTo = ()

    def __init__(self, game):
        self.game = game

    @property
    def ui(self):
        return self.game.ui

    @property
    def state(self):
        return self.game.state

    def addTravel(self, options, actions, unavailable):
        for destination in self.travelTo:
            options.append(TRAVEL_LABELS[destination])
            actions.append(("go", destination))
            if destination in STORM_BOUND and self.state.stormy:
                unavailable[len(options)] = STORM_REASON
        options.append("Quit")
        actions.append(("quit", None))

    def choose(self, descriptor, options, actions, unavailable=None):
        choice = int(self.ui.showOptions(descriptor, options, unavailable or {}))
        return actions[choice - 1]

    def go(self, destination):
        self.state.location = destination
        self.game.prompt.reset()
        return destination

    def remember(self, who):
        """The beat after a choice someone will hold you to - for good."""
        self.ui.showDialogue("[%s will remember that.]" % who)

    def talk(self, npc):
        """Run a conversation; if it settled a choice, say who will remember."""
        before = set(self.state.flags)
        self.ui.showInteractiveDialogue(npc)
        for flag in self.state.flags:
            if flag not in before and flag in people.REMEMBERED:
                self.remember(people.REMEMBERED[flag])

    def spend(self, watches=1):
        """An action took time. Returns where the game goes next: this scene,
        or the strip on the last morning, or the last page if the winter ended."""
        outcome = winter.advance(self.game, watches)
        if outcome.lines:
            self.ui.showDialogue("\n\n".join(outcome.lines))
        return self.after(outcome)

    def after(self, outcome=None):
        state = self.state
        if state.over:
            if state.location != "epilogue":
                # The winter ended under us (the dark flight): the last page
                # is shown on the way out, the way the strip shows it.
                self.ui.showDialogue(endings.text(state))
            return self.go("epilogue")
        if state.flags.get(PLANE_ON_STRIP) and self.id != "strip":
            return self.go("strip")
        return self.id
