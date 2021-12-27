from typing import List

from aqt.modelchooser import ModelChooser
from aqt.qt import QPushButton
from anki.lang import _
from aqt import gui_hooks
from aqt.utils import TR, tr, HelpPage

class ModelChooser(ModelChooser):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super().__init__(*args, **kwargs)

    def onModelChange(self):
        """Open Choose Note Type window"""
        from aqt.studydeck import StudyDeck

        current = self.deck.models.current()["name"]
        # edit button
        edit = QPushButton(tr(TR.QT_MISC_MANAGE), clicked=self.onEdit)  # type: ignore

        def nameFunc() -> List[str]:
            return sorted(self.deck.models.allNames())

        ret = StudyDeck(
            self.mw,
            names=nameFunc,
            accept=tr(TR.ACTIONS_CHOOSE),
            title=tr(TR.QT_MISC_CHOOSE_NOTE_TYPE),
            help=HelpPage.NOTE_TYPE,
            current=current,
            parent=self._widget,
            buttons=[edit],
            cancel=True,
            geomKey="selectModel",
        )
        if not ret.name:
            return
        m = self.deck.models.byName(ret.name)
        self.deck.conf["curModel"] = m["id"]
        cdeck = self.deck.decks.current()
        cdeck["mid"] = m["id"]
        # New line:
        self.deck.decks.save(cdeck)
        # Following code was in original method
        gui_hooks.current_note_type_did_change(current)
        self.parent.onModelChange()
        self.updateModels()
        self.parent.setAndFocusNote(self.parent.editor.note)
        # self.mw.reset()
