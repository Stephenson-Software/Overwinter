# @author Daniel McCoy Stephenson
from overwinter import endings, facts, premise, winter
from overwinter.scenes.base import Scene


class Journal(Scene):
    """Everything you know, written down. Reading it costs no time: it is
    the player's own memory, laid out."""

    id = "journal"
    travelTo = ()

    def run(self):
        state = self.state
        options = [
            "What is happening to you",
            "What you know",
            "The winter, as you know it",
        ]
        if state.knows(facts.THE_STORE):
            options.append("The count")
        if state.over:
            options.append("The last page")
        options.append("Close the journal")
        choice = int(self.ui.showOptions(self.descriptor(), options))
        label = options[choice - 1]
        if label == "What is happening to you":
            self.ui.showDialogue(premise.text(state))
        elif label == "What you know":
            self.ui.showDialogue(self.knownText() + self.leadsText())
        elif label == "The winter, as you know it":
            self.ui.showDialogue(self.calendarText())
        elif label == "The count":
            self.ui.showDialogue(self.game.scenes["galley"].sum())
        elif label == "The last page":
            self.ui.showDialogue(endings.text(state))
        else:
            return self.go("epilogue" if state.over else "bunks")
        return self.id

    def descriptor(self):
        state = self.state
        onTrail = sum(1 for f in facts.TRAIL if state.knows(f))
        return "Day %d. %d of %d things known; %d of %d on the trail of the count." % (
            state.day,
            len(state.facts),
            len(facts.FACTS),
            onTrail,
            len(facts.TRAIL),
        )

    def knownText(self):
        state = self.state
        if not state.facts:
            return "Nothing yet."
        lines = []
        for factId in facts.FACTS:  # registry order, not learning order
            if state.knows(factId):
                marker = "*" if factId in facts.TRAIL else "-"
                day = state.learnedOn(factId)
                when = "" if day is None else " - day %d" % day
                lines.append(
                    "%s %s%s\n  %s"
                    % (marker, facts.title(factId), when, facts.text(factId))
                )
        lines.append("\n(* marks the trail of the count.)")
        return "\n\n".join(lines)

    def leadsText(self):
        """The rumour web: under what you know, where it points that you
        haven't been. Never names the missing fact - says where to look."""
        state = self.state
        lines = []
        for factId in facts.FACTS:
            if not state.knows(factId):
                continue
            for target, text in facts.leads(factId):
                if not state.knows(target) and text not in lines:
                    lines.append(text)
        if not lines:
            return ""
        return "\n\nThere's more to learn:\n" + "\n".join("? " + line for line in lines)

    def calendarText(self):
        rows = [
            "Day %2d  %s" % (day, line) for day, line in winter.calendar(self.state)
        ]
        return "\n".join(rows)
