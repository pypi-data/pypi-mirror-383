import webbrowser
import pyautogui
import time
import csv
import sys
import random
import argparse
import json
from pathlib import Path

class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

def _dist_version() -> str:
    try:
        from importlib.metadata import version
        return version("campnet-login")
    except Exception:
        return "unknown"

_NOTIFY_WARNED = False
# Use a portable default rather than a personal path
DEFAULT_CSV = str(Path.home() / ".config/campnet-login/login_details.csv")
DEFAULT_CONFIG_PATH = Path.home() / ".config/campnet-login/config.json"
DEFAULT_POSITIONS = {
    "user": {"x": 1037, "y": 337},
    "pass": {"x": 1044, "y": 402},
}

def count_rows(csv_path):
    with open(csv_path, newline='') as csvfile:
        return sum(1 for row in csv.reader(csvfile) if row)

def get_login_details(csv_path, line_num):
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for idx, row in enumerate(reader, start=1):
            if idx == line_num:
                return row[0], row[1]
    raise ValueError("Line number out of range in login_details.csv")

def load_positions(config_path: Path):
    pos = {k: v.copy() for k, v in DEFAULT_POSITIONS.items()}
    try:
        if config_path and config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
            for key in ("user", "pass"):
                if key in data:
                    if "x" in data[key]: pos[key]["x"] = int(data[key]["x"])
                    if "y" in data[key]: pos[key]["y"] = int(data[key]["y"])
    except Exception:
        pass
    return pos

def save_positions(config_path: Path, positions: dict):
    config = {}
    try:
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
    except Exception:
        config = {}
    for key in ("user", "pass"):
        if key in positions:
            config[key] = {"x": int(positions[key]["x"]), "y": int(positions[key]["y"])}
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Saved positions to {config_path}")

def load_csv_from_config(config_path: Path):
    try:
        if config_path and config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
            if "csv" in data and data["csv"]:
                return str(data["csv"])
    except Exception:
        pass
    return None

def save_csv_to_config(config_path: Path, csv_path: str):
    cfg = {}
    try:
        if config_path.exists():
            with open(config_path) as f:
                cfg = json.load(f)
    except Exception:
        cfg = {}
    cfg["csv"] = str(csv_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"Saved csv path to {config_path}")

def notify(message: str, timeout_ms: int = 4000, title: str = "Campnet Login"):
    global _NOTIFY_WARNED
    try:
        import shutil, subprocess
        if shutil.which("notify-send"):
            subprocess.run(
                ["notify-send", "-a", "campnet-login", "-t", str(timeout_ms), title, message],
                check=False
            )
        else:
            if not _NOTIFY_WARNED:
                print("Tip: install 'notify-send' (libnotify) for desktop notifications. Falling back to stdout.")
                _NOTIFY_WARNED = True
            print(message)
    except Exception:
        print(message)

def calibrate_positions():
    print("Calibration starting. You will have 3 seconds to hover over each field.")
    positions = {}

    url = 'https://campnet.bits-goa.ac.in:8090/'
    webbrowser.open(url)
    time.sleep(1)

    notify("Hover mouse over the USERNAME field...")
    time.sleep(3)
    p = pyautogui.position()
    positions["user"] = {"x": p.x, "y": p.y}
    notify(f"Captured username at ({p.x}, {p.y})")
    print(f"Captured username at ({p.x}, {p.y})")

    notify("Hover mouse over the PASSWORD field...")
    time.sleep(3)
    p = pyautogui.position()
    positions["pass"] = {"x": p.x, "y": p.y}
    notify(f"Captured password at ({p.x}, {p.y})")
    print(f"Captured password at ({p.x}, {p.y})")
    pyautogui.hotkey('ctrl','w')
    pyautogui.hotkey('alt','tab')
    return positions

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="campnet-login",
        description="Login to Campnet via GUI automation.",
        formatter_class=HelpFormatter,
        epilog=(
            "Examples:\n"
            "  campnet-login --calibrate\n"
            "  campnet-login --csv ~/.config/campnet-login/login_details.csv\n"
            "  campnet-login -l 2\n"
        ),
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {_dist_version()}")
    parser.add_argument("-l", "--line", type=int, help="CSV line number to use (1-based). If omitted, a random line is used.")
    parser.add_argument("--csv", type=Path, default=None, help="Path to login_details.csv (overrides config for this run)")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to JSON config for field coordinates")
    parser.add_argument("--user-x", type=int, help="Override username field X coordinate")
    parser.add_argument("--user-y", type=int, help="Override username field Y coordinate")
    parser.add_argument("--pass-x", type=int, help="Override password field X coordinate")
    parser.add_argument("--pass-y", type=int, help="Override password field Y coordinate")
    parser.add_argument("--calibrate", action="store_true", help="Interactively capture coordinates and save to --config")
    parser.add_argument("--save-overrides", action="store_true", help="Persist any --user-*/--pass-* and --csv to --config")

    args = parser.parse_args(argv)

    if args.calibrate:
        positions = calibrate_positions()
        save_positions(args.config, positions)
        return 0

    config_csv = load_csv_from_config(args.config)
    csv_path = str(args.csv) if args.csv is not None else (config_csv if config_csv else DEFAULT_CSV)

    if args.line is None:
        total = count_rows(csv_path)
        if total == 0:
            raise ValueError("login_details.csv is empty")
        line_number = random.randint(1, total)
        print(f"No line number provided. Using random line: {line_number} of {total}")
    else:
        line_number = args.line

    positions = load_positions(args.config)
    if args.user_x is not None: positions["user"]["x"] = args.user_x
    if args.user_y is not None: positions["user"]["y"] = args.user_y
    if args.pass_x is not None: positions["pass"]["x"] = args.pass_x
    if args.pass_y is not None: positions["pass"]["y"] = args.pass_y

    if args.save_overrides:
        save_positions(args.config, positions)
        if args.csv is not None:
            save_csv_to_config(args.config, str(args.csv))

    username, password = get_login_details(csv_path, line_number)

    url = 'https://campnet.bits-goa.ac.in:8090/'
    webbrowser.open(url)
    time.sleep(1)

    pyautogui.click(x=positions["user"]["x"], y=positions["user"]["y"])
    pyautogui.write(username)

    pyautogui.click(x=positions["pass"]["x"], y=positions["pass"]["y"])
    pyautogui.write(password)

    pyautogui.press('enter')
    time.sleep(0.7)
    pyautogui.hotkey('ctrl','w')
    pyautogui.hotkey('alt','tab')
    pyautogui.hotkey('alt','f4')
    pyautogui.press('enter')

if __name__ == "__main__":
    raise SystemExit(main())