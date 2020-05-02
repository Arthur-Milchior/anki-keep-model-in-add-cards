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
    gui_hooks.current_note_type_did_change.append(addCards.onModelChange)
    gui_hooks.state_did_reset.append(addCards.onReset)
    gui_hooks.state_did_reset.append(addCards.onResetSameModel)

gui_hooks.add_cards_did_init.append(init_add_card)



def setupChoosers(self):
    self.modelChooser = ModelChooser(self, self.mw,
                                     self.form.modelArea)
    self.deckChooser = DeckChooser(
        self.mw, self.form.deckArea)

AddCards.setupChoosers = setupChoosers

def onReset(self, model=None, keep=False):
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
        for n in range(len(note.fields)):
            try:
                if not keep or flds[n]['sticky']:
                    note.fields[n] = oldNote.fields[n]
                else:
                    note.fields[n] = ""
            except IndexError:
                break
    self.setAndFocusNote(note)

AddCards.onReset = onReset

def onResetSameModel(self, keep=False):  # this is a new method
    return self.onReset(model=self.editor.note._model, keep=keep)
AddCards.onResetSameModel = onResetSameModel

def _addCards(self):
    """Adding the content of the fields as a new note.

    Assume that the content of the GUI saved in the model."""
    self.editor.saveAddModeVars()
    if not self.addNote(self.editor.note):
        return
    tooltip(_("Added"), period=500)
    av_player.stop_and_clear_queue()
    self.onResetSameModel(keep=True)
    self.mw.col.autosave()

    def _reject(self):
        remHook('reset', self.onResetSameModel)
        super()._reject()


AddCards._addCards = _addCards
# The window opener contains information about the class, and not its adress. Thus it must be updated.
dialogs._dialogs["AddCards"] = [AddCards, None]

def onModelChange(self, unused=None) -> None:
    oldNote = self.editor.note
    note = self.mw.col.newNote()
    self.previousNote = None
    if oldNote:
        oldFields = list(oldNote.keys())
        newFields = list(note.keys())
        for n, f in enumerate(note.model()["flds"]):
            fieldName = f["name"]
            try:
                oldFieldName = oldNote.model()["flds"][n]["name"]
            except IndexError:
                oldFieldName = None
            # copy identical fields
            if fieldName in oldFields:
                note[fieldName] = oldNote[fieldName]
            # set non-identical fields by field index
            elif oldFieldName and oldFieldName not in newFields:
                try:
                    note.fields[n] = oldNote.fields[n]
                except IndexError:
                    pass
        self.removeTempNote(oldNote)
    # put back this missing code: next line
    self.note = note
AddCards.onModelChange = onModelChange

