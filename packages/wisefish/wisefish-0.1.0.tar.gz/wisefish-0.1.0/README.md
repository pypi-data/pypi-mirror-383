# Wisefish 🐟

**Wisefish** is a command-line tool that displays fun ASCII fish art along with a configurable text box. It allows users to personalize greetings, toggle display options, and manage preferences stored in a user-specific configuration file.

---

## Features
- Display ASCII fish art in the terminal.
- Create decorative, centered text boxes using customizable width and padding.
- Manage user configuration (name, silent mode, time display) through commands.
- Automatically saves user preferences in the platform’s standard configuration directory.

---

## Installation

Clone this repository and install dependencies:

```

git clone https://github.com/yourusername/wisefish.git
cd wisefish
pip install -r requirements.txt

```

If you are using it as a module:

```

pip install .

```

---

## Usage

Run the main script using Python:

```

python -m wisefish --text "Your custom message"

```

Or, simply:

```

python -m wisefish

```

This will read your configuration and display a greeting inside the ASCII box with the fish art below it.



### Example Output

```text
  .-------------------------------------------.
 /                                             \
 |                                             |
 |                 Hello, Alex!                |
 |                                             |
 |             2025-10-12 19:38:26             |
 |                                             |
 \                                             /
  '-------------------------------------------' 
          ()                     ---
             O     ___======____=---=)
               o /T            \_--===)
                 [ \ (0)   \~    \_-==)
                  \      / )J~~    \-=)
                   \\___/  )JJ~~~   \)
                    \_____/JJJ~~~~    \
                    / \  , \J~~~~~     \
                   (-\)\=|\\\~~~~       L__
                   (\\)  (\\\)_           \==__
                    \V    \\\) ===_____   \\\\\\
                           \V)     \_) \\\\JJ\J\)
                                       /J\JT\JJJJ)
                                       (JJJ| \UUU)
                                        (UU) 
```
---

## Configuration

Wisefish saves user preferences in a configuration file located under the standard platform-specific configuration directory (using `platformdirs`).

Run the following to view or update configuration:

```
python -m wisefish config
```


### Configuration Options

| Option | Description | Example |
| :-- | :-- | :-- |
| `--name` | Set default user name | `python -m wisefish config --name Alice` |
| `--silent` | Toggle ASCII box display | `python -m wisefish config --silent/--no-silent` |
| `--time` | Enable/disable current time | `python -m wisefish config --time/--no-time` |

Example:

```
python -m wisefish config --name Bob --time --no-silent 
```


---


## Dependencies

- Python ≥ 3.8
- `platformdirs`

Install dependencies manually if required:

```
pip install platformdirs
```


---

## Author

Developed by **Yousef Miryousefi**. Contributions, issues, and feature requests are welcome!

---
