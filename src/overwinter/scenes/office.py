# @author Daniel McCoy Stephenson
from overwinter import facts, people
from overwinter.scenes.base import Scene

# The station log, sixty years of it, on Marit's desk. Each entry the
# player can look up is a fact; reading one costs a watch, the way any
# afternoon with a ledger does.
LOG_ENTRIES = [
    (
        "1958 - the depot",
        facts.THE_DEPOT,
        "1958, October. 'Emergency depot laid this day in a stone cairn on "
        "the headland, one mile north of the strip: pemmican and hard bread "
        "in sealed tins, for twelve days at one man. To be inspected each "
        "season.' Below it, in eight different hands over fifty years: "
        "'Inspected. Cairn sound.' Nobody has written that they opened it.",
    ),
    (
        "1961 - the station moves",
        facts.THE_OLD_HUT,
        "1961, August. 'Station re-sited to the east shore of the bay for the "
        "strip. Old hut closed up against need: stove, two bunks, lamp and "
        "twenty days of fuel left in. Door wired, not locked.' A sketch map: "
        "the old hut is straight across the bay from the strip - an hour on "
        "the ice, or a day round the headland on foot.",
    ),
    (
        "1971 - December",
        facts.SEVENTY_ONE,
        "1971, December 3rd. 'Larsen fever 40.1, third day. Base informed. "
        "Base will attempt flight tomorrow in window.' December 4th: 'Otter "
        "struck the ridge on approach 10:40, in cloud. Pilot Haugen killed. "
        "Aircraft destroyed.' December 5th, and every day to the 22nd: "
        "Larsen's temperature, coming down. January 3rd: 'Larsen up and "
        "working.' And under it, in the leader's hand, nothing to do with "
        "the weather: 'We should have waited.'",
    ),
    (
        "The ice table",
        facts.THE_ICE,
        "Inside the back cover, in Marit's hand, eight winters of it: the "
        "date of the first hard frost and the date the bay would bear, each "
        "year three still nights after. This year's frost is entered. "
        "Three nights after it is the fifth day. Under the table: 'Never "
        "before. Not for anything.'",
    ),
]


class Office(Scene):
    id = "office"
    travelTo = ("galley", "radio", "shed", "bunks", "strip")

    def descriptor(self):
        return (
            "Marit's office: the barograph, the instruments, the station log "
            "open on the desk, and Marit, who does not look up until spoken to."
        )

    def run(self):
        options, actions, unavailable = [], [], {}
        options.append("Talk to Marit")
        actions.append(("marit", None))
        options.append("Read the station log")
        actions.append(("log", None))
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "marit":
            self.talk(people.marit(self.game))
            return self.after()
        return self.readLog()

    def readLog(self):
        """Pick an entry; reading it costs a watch. Closing the book is free."""
        options = []
        for label, factId, _ in LOG_ENTRIES:
            options.append(
                "%s%s" % (label, " (read)" if self.state.knows(factId) else "")
            )
        options.append("Close the log")
        choice = int(
            self.ui.showOptions(
                "The station log. Sixty years, one page a day, and an index "
                "of the years somebody thought worth finding again.",
                options,
            )
        )
        if choice == len(options):
            return self.id
        _, factId, entry = LOG_ENTRIES[choice - 1]
        self.game.learn(factId)
        self.ui.showDialogue(entry)
        return self.spend(1)
