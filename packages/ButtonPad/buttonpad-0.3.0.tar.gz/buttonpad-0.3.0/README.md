# ButtonPad

ButtonPad lets you create a GUI of a grid of buttons, labels, text boxes, and images using a compact, CSV-like layout string and control it with simple Python callbacks. It’s built on the Tkinter standard library and works on Windows, macOS, and Linux. (On macOS, it optionally uses tkmacosx for better button color support.)

For example, this layout string is for a calculator app:

```
LAYOUT = """
'','','',''
C,(,),⌫
7,8,9,÷
4,5,6,x
1,2,3,-
0,.,=,+
"""
```

Key features:

* Pure-Python code that only depends on the standard library, built on top of tkinter. (Pillow is optional.)
* A CSV-like layout configuration string generates the grid of widgets.
* Callback functions handle click, enter, and exit events.
* Each widget can be assigned tool tip text, hotkey mappings, and custom font and colors.
* Optional status bar with custom colors.
* Optional menubar configuration.
* Adjustable per-column/row sizing, margins, borders, and resizable windows
* PyMsgBox dialog boxes: `alert()`, `confirm()`, `prompt()`, `password()`


## Quick Start with the Launcher

Run `python -m buttonpad` to run the launcher program to view several demo programs and games made with Buttonpad.

![Screenshot](https://raw.githubusercontent.com/asweigart/buttonpad/main/screenshot-2048.webp)
![Screenshot](https://raw.githubusercontent.com/asweigart/buttonpad/main/screenshot-calc.webp)
![Screenshot](https://raw.githubusercontent.com/asweigart/buttonpad/main/screenshot-conway.webp)
![Screenshot](https://raw.githubusercontent.com/asweigart/buttonpad/main/screenshot-eightqueens.webp)
![Screenshot](https://raw.githubusercontent.com/asweigart/buttonpad/main/screenshot-emoji.webp)
![Screenshot](https://raw.githubusercontent.com/asweigart/buttonpad/main/screenshot-lightsout.webp)
![Screenshot](https://raw.githubusercontent.com/asweigart/buttonpad/main/screenshot-magic8ball.webp)
![Screenshot](https://raw.githubusercontent.com/asweigart/buttonpad/main/screenshot-samegame.webp)
![Screenshot](https://raw.githubusercontent.com/asweigart/buttonpad/main/screenshot-slide.webp)
![Screenshot](https://raw.githubusercontent.com/asweigart/buttonpad/main/screenshot-stopwatch.webp)












## Example Code

```python
# Phone keypad example
import buttonpad

# Multi-line string defines 4 rows of 3 cells each (a 3x4 grid).
bp = buttonpad.ButtonPad(
    """[],[],[]
    1,2,3
    4,5,6
    7,8,9
    *,0,#
    Call,Call,Cancel""",
)

bp.run()
```

The bottom row has a single "Call" button that is double-wide. The default click callback function prints the label of the button. Here's an expanded version:

```python
# Phone keypad example
import buttonpad

# Multi-line string defines 4 rows of 3 cells each (a 3x4 grid).
bp = buttonpad.ButtonPad(
	"""[],[],[]
    1,2,3
	4,5,6
	7,8,9
	*,0,#
	Call,Call,Cancel""",
	cell_width=100,
	cell_height=60,
	padx=10,
	pady=5,
	border=20,
	#default_bg_color='lightblue',
	#default_text_color='darkblue',
	#window_bg_color='whitesmoke',	
	title="Telephone Keypad Demo",
)

# Create callback functions for the buttons:
def cancel_call(widget, x, y):
    bp[0,0].text = ''  # Clear the display

def call_number(widget, x, y):
    buttonpad.alert("Simulate calling " + bp[0,0].text)  # Show an alert with the number being called

def add_button_label_to_display(widget, x, y):
    bp[0, 0].text += widget.text  # Append the pressed key to the display

# Assign callbacks to buttons:
for x in range(3):
    for y in range(1, 5):  # rows 1-4 contain keys 1..9,*,0,#
        bp[x,y].on_click = add_button_label_to_display

bp[2, 5].on_click = cancel_call  # Cancel button

bp[0, 5].on_click = call_number  # Call button

bp[0, 0].font_size = 24  # Make the display text larger

# Run the app:
bp.run()
```


## Layout string reference

The grid is described by a CSV-like string: commas separate columns, newlines separate rows.

Token types:
- Button (default): any unquoted text, e.g. `A`, `Click`, `7` (or prefix with `BUTTON:`)
- Label: text wrapped in single or double quotes, e.g. `'Hello'` or `"Ready"` (or prefix with `LABEL:`)
- Text box (multiline and editable): text wrapped in square brackets, e.g. `[Name]` (or prefix with `TEXTBOX:`)
- Image: Prefix with `IMAGE:` followed by the image filename.
- No-merge: prefix a token with a backtick to prevent merging, e.g. `` `X``
- Empty token: an empty cell becomes an empty button

Merging rules:
- Adjacent identical tokens merge into one larger element (row/column spanning).
- Merging is rectangular: a block of identical tokens forms a single widget.
- Prefixing a token with a backtick ` prevents merging for that cell only.

Examples:

This creates a top row with three buttons (labelled "A", "B", and "C"). The second row is a single wide, 3x1 cell button labelled "Play". The third row has two text labels that say "Status" and "Enabled", next to a text box with the placeholder text, "Name". The bottom row has three separate buttons, each labelled "Start":

```
A,B,C
Play,Play,Play
"Status","Enabled",[Name]
`Start,`Start,`Start
```

## API

### ButtonPad

Constructor:

```python
    def __init__(
        self,
        layout: str,  # """Button, 'Label 1', "Label 2", [Text Box], IMAGE:~/monalisa.png"""
        cell_width: Union[int, Sequence[int]] = 60,  # width of each grid cell in pixels; int for all cells or list of ints for per-column widths
        cell_height: Union[int, Sequence[int]] = 60,  # height of each grid cell in pixels; int for all cells or list of ints for per-row heights
        padx: int = 0,  # horizontal gap/padding between cells in pixels
        pady: int = 0,  # vertical gap/padding between cells in pixels
        window_bg_color: str = '#f0f0f0',  # background color of the window
        default_bg_color: str = '#f0f0f0',  # default background color for widgets
        default_text_color: str = 'black',  # default text color for widgets
        title: str = 'ButtonPad App',  # window title
        resizable: bool = True,  # whether the window is resizable
        border: int = 0,  # padding between the grid and the window edge
        status_bar: Optional[str] = None,  # initial status bar text; None means no status bar
        menu: Optional[Dict[str, Any]] = None,  # menu definition dict; see menu property for details
    ):
```

Notes:
- `cell_width`/`cell_height` can be a single int (uniform) or a list matching the number of columns/rows.
- `padx`/`pady` set the internal spacing between cells; `border` is outer margin.
- The window is resizable by default.

Instance methods and properties:
- `run()` — start the Tkinter event loop.
- `quit()` — close the window (idempotent).
- `update(new_layout: str)` — rebuild the grid from a new layout string.
- `[x, y]` — index into the grid to get an element wrapper at column x, row y.
- Status bar: `status_bar` (string or None) plus `status_bar_background_color`, `status_bar_text_color`.
- Menu: assign a nested dict to `menu` to build a menubar with optional accelerators.
- Global hooks: `on_pre_click(element)`, `on_post_click(element)` called around every click.

Re-exported dialogs from pymsgbox: 
- `alert(text: str = "", title: str = "PyMsgBox", button: str = "OK")` - Displays a message.
- `confirm(text: str = "", title: str = "PyMsgBox", buttons: Union[str, Sequence[str]] = ("OK", "Cancel"))` - Displays OK/Cancel box and returns selection.
- `prompt(text: str = "", title: str = "PyMsgBox", default: str = "")` - Lets user type a resonse and returns it.
- `password(text: str = "", title: str = "PyMsgBox", default: str = "", mask: str = "*")` - Like `prompt()` but hides the typed characters.


### Widgets

All wrappers expose:
- `text: str` — get/set the visible text.
- `background_color: str` — get/set background color.
- `text_color: str` — get/set text/foreground color.
- `font_name: str` and `font_size: int` — change font.
- `tooltip: Optional[str]` — small hover tooltip; set to a string to enable, `None`/`""` to disable.
- `on_click: Callable[[element, x, y], None] | None` — click handler.
- `on_enter` / `on_exit` — hover handlers with the same signature.
- `widget` — the underlying Tk widget, for advanced customization.
Specific additions:
- `BPButton.hotkey` / `BPLabel.hotkey` properties: assign a string (keysym) or tuple of strings to create independent hotkeys (case-insensitive). Reassigning replaces prior hotkeys.

Specifics:
- `BPButton` — click-focused element; created for unquoted tokens.
- `BPLabel` — static text; has `anchor` property (e.g., `"w"`, `"center"`, `"e"`) and optional `hotkey` like buttons.
- `BPTextBox` — editable single-line entry; `text` reflects its content.


## Keyboard mapping

Map keys to cells with `map_key`. Keys are Tk keysyms (case-insensitive): `"1"`, `"a"`, `"space"`, `"Return"`, `"Escape"`, etc.

```python
pad.map_key("1", 0, 0)
pad.map_key("space", 1, 0)
```


## Merging and no-merge cells

Adjacent identical tokens automatically merge into a single widget, spanning a rectangular area. To opt out for a specific cell, prefix it with a backtick to mark it as “no-merge”:

```
Play,Play,Play  # this row is merged into a single button
`Play,`Play,`Play   # this row is three separate buttons
```


## Platform notes

- macOS: For fully colorable buttons, install `tkmacosx`. When unavailable, ButtonPad falls back to the system `tk.Button` (colors may not update on some macOS builds). You’ll see a console message suggesting: `pip install tkmacosx`.
- Dialog helpers use `pymsgbox` and are re-exported for convenience.

