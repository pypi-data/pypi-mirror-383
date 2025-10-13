import os
import json
import textwrap
import argparse
from platformdirs import user_config_dir
import importlib.resources as resources

APP_NAME = "wisefish"

fish_art ="""
          ()                     ---
             O     ___======____=---=)
               o /T            \\_--===)
                 [ \\ (0)   \\~    \\_-==)
                  \\      / )J~~    \\-=)
                   \\\\___/  )JJ~~~   \\)
                    \\_____/JJJ~~~~    \\
                    / \\  , \\J~~~~~     \\
                   (-\\)\\=|\\\\\\~~~~       L__
                   (\\\\)  (\\\\\\)_           \\==__
                    \\V    \\\\\\) ===_____   \\\\\\\\\\\\
                           \\V)     \\_) \\\\\\\\JJ\\J\\)
                                       /J\\JT\\JJJJ)
                                       (JJJ| \\UUU)
                                        (UU) 
"""


def load_user_config():
    """Load user config from standard location, create if missing."""
    config_dir = user_config_dir(APP_NAME)
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.json")

    if not os.path.exists(config_path):
        # Copy defaults from package
        with resources.open_text("wisefish", "default_config.json") as f:
            default_config = json.load(f)
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)
        return default_config
    else:
        with open(config_path) as f:
            return json.load(f)


def save_user_config(config):
    config_dir = user_config_dir(APP_NAME)
    config_path = os.path.join(config_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def wrap_preserve_linebreaks(text, width):
    wrapped_lines = []
    for line in text.splitlines():  # Split by existing '\n'
        # Wrap each line individually
        wrapped_lines.extend(textwrap.wrap(line, width=width) or [""])
    return wrapped_lines


def make_box(text: str, width: int = 41, padding=2):
    """
    Creates a simple ASCII box with centered text inside.
    `width` = number of spaces inside the box (not counting borders)
    `height` = number of empty lines inside the box
    """
    # Wrap text to fit inside box width
    lines = wrap_preserve_linebreaks(text, width)
    
    # Limit the number of lines to box height
    height = len(lines) + padding 
    
    # Calculate vertical centering
    top_padding = (height - len(lines)) // 2
    
    # Top and slanted borders
    box = []
    box.append("  ." + "-" * (width + padding * 2 - 2) + ".")
    box.append(" /" + " " * (width + padding * 2) + "\\")
    
    # Box content (centered text)
    for i in range(height):
        if top_padding <= i < top_padding + len(lines):
            line = lines[i - top_padding].center(width)
        else:
            line = " " * width
        box.append(f" |{' ' * padding}{line}{' ' * padding}|")
    
    # Bottom borders
    box.append(" \\" + " " * (width + padding * 2) + "/")
    box.append("  '" + "-" * (width + padding * 2 - 2) + "' ")
    
    return "\n".join(box)


def main():
    parser = argparse.ArgumentParser(description="Wisefish ASCII box CLI tool.")
    parser.add_argument("--text", help="Text to display in the box")
    subparsers = parser.add_subparsers(dest="command")

    # Config subcommand
    config_parser = subparsers.add_parser("config", help="View or update configuration")
    config_parser.add_argument("--name", help="Set default name")
    config_parser.add_argument("--silent", action=argparse.BooleanOptionalAction, help="Enable or disable silent mode")
    config_parser.add_argument("--time", action=argparse.BooleanOptionalAction, help="Enable or disable Time")

    args = parser.parse_args()
    config = load_user_config()

    if args.command == "config":
        updated = False
        if args.name:
            config["name"] = args.name
            updated = True

        if args.silent is not None:
            config["silent"] = args.silent
            updated = True

        if args.time is not None:
            config["time"] = args.time
            updated = True
        

        if updated:
            save_user_config(config)
            print("Configuration updated successfully.")
        else:
            print("Current configuration:")
            print(json.dumps(config, indent=2))
    else:
        # Just print the box
        def default_text():   
            out = f"Hello, {config.get('name', 'World')}!"
            if config.get("time", False):
                from datetime import datetime
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                out += f"\n\n{current_time}"
            return out
    
        text = args.text or default_text()
        
        box = make_box(text) if not config.get("silent") else ""
        print(box + fish_art)
    

if __name__ == "__main__":
    main()

