# @author Daniel McCoy Stephenson
from overwinter import facts, people
from overwinter.scenes.base import Scene
from overwinter.state import EVENING


class Radio(Scene):
    id = "radio"
    travelTo = ("galley", "office", "shed", "bunks", "strip")

    def descriptor(self):
        if self.state.watch == EVENING:
            return (
                "The radio room, evening. The set is warm and Dov is at the key "
                "with the weather sheet; after it he will take the chessboard "
                "down from the shelf."
            )
        return (
            "The radio room. Valves, a log-book, a chessboard with a game on "
            "it, and Dov, who has already noted that you came in."
        )

    def run(self):
        state = self.state
        options, actions, unavailable = [], [], {}
        options.append("Talk to Dov")
        actions.append(("dov", None))
        options.append("Sit in on the evening schedule")
        actions.append(("listen", None))
        if state.watch != EVENING:
            unavailable[len(options)] = "the schedule goes out on the evening watch"
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "dov":
            self.talk(people.dov(self.game))
            return self.after()
        return self.listen()

    def listen(self):
        if self.game.learn(facts.DOVS_GAME):
            self.ui.showDialogue(
                "The weather goes out at twenty hundred, clean and fast. Then "
                "Dov looks at the clock for two hours, and at twenty-two "
                "hundred the key starts again and you cannot follow it, but "
                "you can count: a chess move is four characters, and what "
                "goes out on the key is paragraphs. He laughs once, at "
                "something that came back. You have not heard him laugh. "
                "The operator at Base signs herself SUN. It is not chess."
            )
        else:
            self.ui.showDialogue(
                "The weather at twenty hundred; the long game at twenty-two. "
                "You do not ask. He does not offer."
            )
        return self.spend(1)
