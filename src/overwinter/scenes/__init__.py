# @author Daniel McCoy Stephenson
"""One class per place. Each has run(), which shows the place's menu once,
acts on the choice, and returns the id of the place to show next - the same
one, usually - or "quit"."""

from overwinter.scenes.galley import Galley
from overwinter.scenes.office import Office
from overwinter.scenes.radio import Radio
from overwinter.scenes.shed import Shed
from overwinter.scenes.bunks import Bunks
from overwinter.scenes.strip import Strip
from overwinter.scenes.hut import Hut
from overwinter.scenes.journal import Journal
from overwinter.scenes.epilogue import Epilogue

QUIT = "quit"


def build(game):
    return {
        "galley": Galley(game),
        "office": Office(game),
        "radio": Radio(game),
        "shed": Shed(game),
        "bunks": Bunks(game),
        "strip": Strip(game),
        "hut": Hut(game),
        "journal": Journal(game),
        "epilogue": Epilogue(game),
    }
