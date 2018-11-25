# -*- coding: utf-8 -*-
# Github: https://github.com/Arthur-Milchior/anki-keep-model-in-add-cards
# Original code from Anki, copyright Damien Elmes <anki@ichi2.net>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Add-on number 
from aqt.qt import QPushButton
from aqt.utils import tooltip
from anki.sound import clearAudioQueue
from aqt.addcards import AddCards
from anki.hooks import remHook, addHook
from aqt.modelchooser import ModelChooser
from aqt.deckchooser import DeckChooser
from anki.notes import Note
oldInit = AddCards.__init__

def debug(t):
    print(t)
    pass


def newInit(self,mw):
    debug("Call newInit")
    oldInit(self,mw)
    remHook("currentModelChanged",self.onModelChange)
    remHook('reset', self.onReset)
    addHook("reset",self.onResetSameModel)
    
AddCards.__init__=newInit
def setupChoosers(self):
  class NewModelChooser(ModelChooser):
    def __init__(self, mw, widget, label=True):
        super().__init__( mw, widget, label=label)
        remHook('reset', self.onReset)
        
    def onModelChange(selfModel):
        """Open Choose Note Type window"""
        #Method called when we want to change the current model
        debug("Call newOnModelChange")
        from aqt.studydeck import StudyDeck
        current = selfModel.deck.models.current()['name']
        # edit button
        edit = QPushButton(_("Manage"), clicked=selfModel.onEdit)
        def nameFunc():
            return sorted(selfModel.deck.models.allNames())
        ret = StudyDeck(
            selfModel.mw, names=nameFunc,
            accept=_("Choose"), title=_("Choose Note Type"),
            help="_notes", current=current, parent=selfModel.widget,
            buttons=[edit], cancel=True, geomKey="selectModel")
        if not ret.name:
            return
        m = selfModel.deck.models.byName(ret.name)
        selfModel.deck.conf['curModel'] = m['id']
        cdeck = selfModel.deck.decks.current()
        cdeck['mid'] = m['id']
        selfModel.deck.decks.save(cdeck)
        #runHook("currentModelChanged")
        #selfModel.mw.reset()
        ### New line: 
        debug("Call AddCard.onModelChange")
        self.onModelChange() #this is onModelChange from card, and note from ModelChange
        selfModel.models.setText(ret.name)
  self.modelChooser = NewModelChooser(
        self.mw, self.form.modelArea)
  self.deckChooser = DeckChooser(
        self.mw, self.form.deckArea)
AddCards.setupChoosers = setupChoosers
# def setupChoosers(self):
#     pass
# AddCards.setupChoosers= setupChoosers
# import anki.hooks
# def remHook(hook, func):
#     "Remove a function if is on hook."
#     hook = anki.hooks._hooks.get(hook, [])
#     if func in hook:
#         hook.remove(func)
#         return True
#     else:
#         return False

def onReset(self, model=None, keep=False):
        """Create a new note and set it.

        keyword arguments
        model -- A model object. Used for the new note.
        keep -- whether to keep sticky values from old note
        """
        #Also called from __init__
        oldNote = self.editor.note
        if model is None:
            note = self.mw.col.newNote()
        else:#Difference is here. If model given as argument, it is used
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

AddCards.onReset=onReset
def onResetSameModel(self,keep=False):
    return onReset(self,model=self.editor.note._model,keep=keep)
AddCards.onResetSameModel= onResetSameModel #this is a new method
def _addCards(self):
        """Adding the content of the fields as a new note.

        Assume that the content of the GUI saved in the model."""
        self.editor.saveAddModeVars()
        note = self.editor.note
        note = self.addNote(note)
        if not note:
            return
        tooltip(_("Added"), period=500)
        # stop anything playing
        clearAudioQueue()
        self.onResetSameModel(keep=True)#Only difference is calling onResetSameModel instead of onReset
        self.mw.col.autosave()
AddCards._addCards= _addCards

old_reject = AddCards._reject
def _reject(self):
    remHook('reset', self.onResetSameModel)
    self.old_reject()
AddCards._reject=old_reject
