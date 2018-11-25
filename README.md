# Keep model of add cards
## Rationale
For some reason, the note type in anki «add» window may suddenly
change. In the worst case, it may lead to losing data, if the new note
type has less fields than the old note type. It may also means you'll
submit the note in the wrong type if you didn't pay attention.

More precisely, this may occur in the following cases:
* In the browser, if you change the note type of a note already
  existing.
* If you use the importing window and change the note type.
* Using addon [Open multiple instances of the same
  window](https://ankiweb.net/shared/info/354407385), when you change
  the note type of a «add» window.
## Usage
This add-on ensure that the note type of a «add» window only change
when you choose a note type from the same window.

## Internal
* In module ```aqt.addcards```, ```AddCards.__init__``` is
  redefined. The new method call the former method and then change
  some hooks.
* On object ```o``` of type ```aqt.ModelChange```, the method
  ```onModelChange``` is changed when the object is called from the
  window ```addCard```. The only difference is that this instance call
  the method onModelChange in the addCard window.
## Advice

## Version 2.0

## Links, licence and credits

Key         |Value
------------|-------------------------------------------------------------------
Copyright   | Arthur Milchior <arthur@milchior.fr>
Based on    | Anki code by Damien Elmes <anki@ichi2.net>
License     | GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
Source in   | https://github.com/Arthur-Milchior/anki-
Addon number| [NNNNNNNNNNNN](https://ankiweb.net/shared/info/NNNNNNNNNNNN)
