# @author Daniel McCoy Stephenson
"""The game: a save slot, the state, the scenes, and the loop that runs
them. Front-end agnostic - see tak.ui."""

import json
import os
import shutil
from datetime import datetime

from jsonschema.exceptions import ValidationError

from tak import Prompt
from tak.saves import (
    SaveFileManager,
    chooseSlot,
    syncBrowserSaves,
    validateAgainstSchema,
)
from tak.ui import UIType, createUserInterface

from overwinter import endings, premise, progression, scenes, usageReporting
from overwinter.config import Config
from overwinter.header import buildHeader
from overwinter.state import SAVE_FILENAME, SCHEMA_PATH, State
from overwinter.trace_client import TraceClient

TITLE = "Overwinter"
TAGLINE = "four people, one station, twenty days until a plane"
ENV_PREFIX = "OVERWINTER"
OPENING_PROMPT = (
    "The plane is a sound going away over the ridge. What would you like to do?"
)

# Which front-end the game runs. The rest of the game is front-end agnostic.
INTERFACE_TYPE = UIType.CONSOLE


def describeSlot(metadata):
    """The save menu's summary of a slot: "Day 7, 4 known"."""
    if metadata.get("ending"):
        return "over - %s, %d known" % (metadata["ending"], metadata.get("known", 0))
    return "Day %s, %d known" % (metadata.get("day", 1), metadata.get("known", 0))


def slotMetadata(slotPath, data):
    """The save menu's fields for a slot. The manager only calls this once
    the file has parsed as JSON; a file that parses but is not a save (a
    day of "seven") is described as damaged rather than raising here, and
    load() will refuse it properly against the schema."""
    try:
        state = State.fromDict(data)
        if not isinstance(state.day, int):
            raise TypeError("day is not a number")
        return {
            "day": state.day,
            "known": len(state.facts),
            "ending": endings.name(state) if state.over else None,
        }
    except (KeyError, TypeError, ValueError, AttributeError):
        return {"day": "?", "known": 0, "ending": None}


# @author Daniel McCoy Stephenson
class Overwinter:
    def __init__(self, interfaceType=INTERFACE_TYPE):
        self.running = True
        self.usageReporting = TraceClient.disabled()
        self.config = Config()
        self.usageReporting = usageReporting.start(self.config)
        self.saveFileManager = SaveFileManager(
            self.config.dataDirectory,
            primaryFile=SAVE_FILENAME,
            readMetadata=slotMetadata,
        )
        self.failedLoad = None

        self.state = State()
        self.prompt = Prompt(OPENING_PROMPT)
        self.ui = createUserInterface(
            interfaceType,
            self.prompt,
            lambda: buildHeader(self),
            title=TITLE,
            tagline=TAGLINE,
            envPrefix=ENV_PREFIX,
        )

        chosen = chooseSlot(
            self.ui, self.saveFileManager, TITLE + " - Save Files", describeSlot
        )
        if chosen is None:
            # Ending the run rather than the process, so the front-end still
            # gets its cleanup() - play() does nothing but that.
            self.running = False
            return

        self.usageReporting.report("save-loaded", tags=usageReporting.versionTags())

        kind, _ = chosen
        savePath = self.saveFileManager.get_save_path(SAVE_FILENAME)
        if kind == "load" and os.path.exists(savePath):
            self.load(savePath)
            if self.failedLoad:
                self._preserveDamagedSave(savePath)
            elif self.state.day > 1 or self.state.facts:
                self.prompt.text = "Day %d. What would you like to do?" % self.state.day
        # A loaded save may predate an unlock, or have earned one since.
        progression.catchUp(self.state)
        self.scenes = scenes.build(self)
        # A brand-new game opens on where you are and who is here, once.
        self.showOpening = kind == "new" or (
            self.state.day == 1 and not self.state.facts and self.state.watch == 0
        )

    # --- the scenes' hooks ------------------------------------------------
    def learn(self, factId):
        """Promote something to knowledge. Returns True if it was new."""
        return self.state.learn(factId)

    # --- play -------------------------------------------------------------
    def play(self):
        try:
            if self.running:
                self._runGameLoop()
        finally:
            self.ui.cleanup()
            self.usageReporting.close()

    def _runGameLoop(self):
        if self.showOpening:
            self.ui.showDialogue(premise.OPENING)
            self.showOpening = False
        while self.running:
            unlock = progression.getNextUnlock(self.state)
            if unlock is not None:
                self.ui.showDialogue("[%s]" % unlock["announcement"])
            current = self.state.location
            if current not in self.scenes:
                current = self.state.location = "galley"
            nextScene = self.scenes[current].run()
            self.save()
            if nextScene == scenes.QUIT:
                self.running = False

    # --- persistence ------------------------------------------------------
    def save(self):
        data = self.state.toDict()
        validateAgainstSchema(data, SCHEMA_PATH)
        path = self.saveFileManager.get_save_path(SAVE_FILENAME)
        with open(path, "w", encoding="utf-8") as saveFile:
            json.dump(data, saveFile, indent=2)
        syncBrowserSaves()

    def load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as saveFile:
                data = json.load(saveFile)
            validateAgainstSchema(data, SCHEMA_PATH)
            self.state = State.fromDict(data)
        except (ValueError, ValidationError, OSError, KeyError, TypeError) as error:
            # A failed load leaves a fresh state in place of the player's run,
            # and save() writes it back after the very next action - so the
            # bytes that failed are copied aside before play() is reached.
            self.failedLoad = "%s: %s" % (os.path.basename(path), error)
            self.state = State()

    def _preserveDamagedSave(self, path):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = "%s.damaged-%s" % (path, stamp)
        try:
            shutil.copy2(path, backup)
            where = "A copy was kept at %s." % backup
        except OSError:
            where = "It could not be copied aside."
        self.ui.showDialogue(
            "This save could not be read (%s). You'll start a fresh game in "
            "this slot. %s" % (self.failedLoad, where)
        )
