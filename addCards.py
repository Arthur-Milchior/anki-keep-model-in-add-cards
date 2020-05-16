from .modelChooser import ModelChooser
from aqt.addcards import AddCards
from aqt import dialogs
from anki.hooks import addHook, remHook
from anki.lang import _
from anki.notes import Note
from anki.sound import clearAudioQueue
from aqt.deckchooser import DeckChooser
from aqt.utils import tooltip
from aqt import gui_hooks
from aqt.sound import av_player


def init_add_card(addCards):
    gui_hooks.current_note_type_did_change.remove(addCards.onModelChange)
    gui_hooks.state_did_reset.remove(addCards.onReset)
    gui_hooks.state_did_reset.append(addCards.onResetSameModel)

gui_hooks.add_cards_did_init.append(init_add_card)



def setupChoosers(self):
    # only differenc: use our ModelChooser
    self.modelChooser = ModelChooser(self, self.mw,
                                     self.form.modelArea)
    self.deckChooser = DeckChooser(
        self.mw, self.form.deckArea)

AddCards.setupChoosers = setupChoosers

def onReset(self, model: None = None, keep: bool = False) -> None:
    """Create a new note and set it.

    keyword arguments
    model -- A model object. Used for the new note.
    keep -- whether to keep sticky values from old note
    """
    # Also called from __init__
    oldNote = self.editor.note
    if model is None:
        note = self.mw.col.newNote()
    else:  # Difference is here. If model given as argument, it is used
        note = Note(self.mw.col, model=model)
    flds = note.model()['flds']
    # copy fields from old note
    if oldNote:
        if not keep:
            self.removeTempNote(oldNote)
        for index in range(min(len(note.fields), len(oldNote.fields))):
            if not keep or flds[index]["sticky"]:
                note.fields[index] = oldNote.fields[index]
    if self.editor.web:
        # don't set and focus the window is cleaned up
        self.setAndFocusNote(note)

AddCards.onReset = onReset

def onResetSameModel(self, keep=False):  # this is a new method
    return self.onReset(model=self.editor.note.model() if self.editor.note else None, keep=keep)
AddCards.onResetSameModel = onResetSameModel

def _addCards(self):
    """Adding the content of the fields as a new note.

    Assume that the content of the GUI saved in the model."""
    self.editor.saveAddModeVars()
    if not self.addNote(self.editor.note):
        return
    tooltip(_("Added"), period=500)
    av_player.stop_and_clear_queue()
    # only diff is using onResetSameModel
    self.onResetSameModel(keep=True)
    self.mw.col.autosave()
AddCards._addCards = _addCards

_old_reject = AddCards._reject
def _reject(self):
    gui_hooks.state_did_reset.remove(self.onResetSameModel)
    # onReset will also be removed from the hook by super. It's not a
    # problem, as `remove` detect the method is not here
    _old_reject(self)
AddCards._reject = _reject

# The window opener contains information about the class, and not its adress. Thus it must be updated.
dialogs._dialogs["AddCards"][0] = AddCards

def onModelChange(self, unused=None) -> None:
    oldNote = self.editor.note
    note = self.mw.col.newNote()
    self.previousNote = None
    if oldNote:
        oldFields = list(oldNote.keys())
        newFields = list(note.keys())
        for index, fldType in enumerate(note.model()["flds"]):
            fieldName = fldType["name"]
            # copy identical fields
            if fieldName in oldFields:
                note[fieldName] = oldNote[fieldName]
            elif index < len(oldNote.model()["flds"]):
                # set non-identical fields by field index
                oldFieldName = oldNote.model()["flds"][index]["name"]
                if oldFieldName not in newFields:
                    note.fields[index] = oldNote.fields[index]
        self.removeTempNote(oldNote)
    # put back this missing code: next line
    self.editor.note = note
AddCards.onModelChange = onModelChange

