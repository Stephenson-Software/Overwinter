# @author Daniel McCoy Stephenson
from overwinter import endings
from overwinter.scenes.base import Scene


class Epilogue(Scene):
    """After the ending. The last page can be read again, the journal is
    still there, and there is nothing else to do but leave."""

    id = "epilogue"
    travelTo = ()

    def run(self):
        options = ["Read the last page again", "Open your journal", "Quit"]
        choice = int(
            self.ui.showOptions(
                "The winter is over: %s. The plane is a sound going away over "
                "the ridge, or you are on it." % endings.name(self.state),
                options,
            )
        )
        if choice == 1:
            self.ui.showDialogue(endings.text(self.state))
            return self.id
        if choice == 2:
            return self.go("journal")
        return "quit"
