# campnet-login

GUI automation CLI to log into BITS Campnet.

## Install
pip install campnet-login

### Required: Tkinter
PyAutoGUI (via mouseinfo) requires Tkinter. Install it for the Python you use to run campnet-login.

- Debian/Ubuntu: sudo apt install python3-tk
- Fedora: sudo dnf install python3-tkinter
- Arch: sudo pacman -S tk

If you use a virtual environment, ensure the base Python has Tkinter or recreate the venv from one that does. 
Verify:
python -c "import tkinter; print('tk OK', tkinter.TkVersion)"

### Optional system tool (Linux)
For desktop notifications, install notify-send (libnotify). If missing, the tool falls back to printing messages.

- Debian/Ubuntu: sudo apt install libnotify-bin
- Fedora: sudo dnf install libnotify
- Arch: sudo pacman -Sy libnotify

## Usage
campnet-login --help