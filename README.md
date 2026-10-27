# DOT - Desktop Operations Terminal

> A modular, deterministic, text-based Windows desktop assistant.
> Fully offline, deterministic regex-based command parsing with native Windows automation.

---

## Overview

**DOT** is a lightweight, fully offline Windows desktop assistant designed to run directly in your terminal. It understands plain-English commands for system monitoring, file management, app control, media playback, productivity, reminders, calculations, and general utilities — with zero AI or cloud dependency.

```text
DOT > time
🕐 22:31:04  —  Thursday, October 27, 2026

DOT > system info
SYSTEM INFORMATION
----------------------------------------
  CPU Usage   : 12.3%
  RAM Usage   : 58.1%  (9.3 / 16.0 GB)
  Disk Usage  : 74.2%  (371.0 / 500.0 GB)
  Battery     : 88%  Plugged in

DOT > remind me take a break in 30 minutes
✓ Reminder set: "take a break" in 30 minutes

DOT > calc (45 * 2) + 10
Result: 100
```

---

## Project Structure

```text
VoiceAssistant/
├── main.py                     # Primary entry point — boots the interactive REPL
├── config.py                   # Central settings loader and saver (data/settings.json)
├── dot_config.example.json     # Configuration template
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation
├── LICENSE                     # MIT License
│
├── core/                       # Architecture framework
│   ├── assistant.py            # Assistant orchestrator: REPL, banner, TTS, built-ins
│   ├── parser.py               # Text -> ParsedCommand regex intent mapper
│   ├── dispatcher.py           # Command dispatcher with permission enforcement
│   ├── command_registry.py     # Command registration, aliases, and category indexing
│   ├── context.py              # Session state (working directory, history)
│   ├── permissions.py          # SAFE / CONFIRM / DANGEROUS permission gates
│   ├── scheduler.py            # Background thread worker for timed reminders
│   └── logger.py               # Rotating file logging to logs/dot.log
│
├── modules/                    # Feature modules
│   ├── system.py               # CPU, RAM, disk, battery, power, sleep, lock
│   ├── files.py                # Create, read, edit, copy, move, delete, search files
│   ├── apps.py                 # Launch, close, list, force terminate applications
│   ├── media.py                # Volume, music, video, Spotify, YouTube search
│   ├── browser.py              # Web search, URL navigation
│   ├── clipboard.py            # Clipboard read, write, clear
│   ├── screenshots.py          # Capture screen and open latest screenshot
│   ├── reminders.py            # Schedule timed reminders with desktop notifications
│   ├── productivity.py         # Command history, personal notes, to-do list manager
│   ├── information.py          # Weather, dictionary, calculator, units, trivia, jokes
│   └── automation.py           # Shell execution gated by DANGEROUS permission
│
├── services/                   # Shared singleton services
│   └── notifications.py        # Windows desktop toast notifications (plyer fallback)
│
├── legacy/                     # Historical monolithic archive
│   ├── DotAssistant.py         # Original prototype script (superseded)
│   └── README.md               # Legacy archive notes
│
├── data/                       # Runtime storage (auto-created, gitignored)
│   ├── settings.json           # User configuration
│   ├── reminders.json          # Persistent reminders
│   ├── todos.json              # Persistent to-do items
│   └── notes.txt               # Personal notes storage
│
├── logs/                       # Application logs (gitignored)
│   └── dot.log
│
└── tests/                      # Automated test suite
    ├── test_parser.py          # Intent parsing & regex tests
    ├── test_dispatcher.py      # Dispatch & execution tests
    └── test_assistant.py       # Orchestrator & TTS confirmation tests
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/I71gs/Dot-Assisstant.git
cd Dot-Assisstant
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Customize Configuration

DOT creates default settings automatically on its first run at `data/settings.json`. If you wish to pre-configure directories or API keys:

```bash
copy dot_config.example.json data\settings.json
```

### 5. Launch DOT

```bash
python main.py
```

---

## Command Reference

### Time & Date
| Command | Aliases / Examples | Description |
|---|---|---|
| `time` | `what is the time`, `current time` | Show current system time and day |
| `date` | `today`, `what is the date` | Show today's full date |

### System & Power
| Command | Example / Aliases | Description |
|---|---|---|
| `system info` | `sysinfo`, `sys info` | Comprehensive system stats (CPU, RAM, Disk, Battery) |
| `cpu` | `cpu usage`, `cpu load` | Real-time CPU utilization percentage |
| `ram` | `memory`, `ram usage` | Current memory consumption and total available |
| `disk [path]` | `disk C:\`, `storage` | Disk capacity, used, and free space |
| `battery` | `battery status` | Battery percentage and charging status |
| `network info` | `net info`, `netinfo` | Network adapters and connection statistics |
| `processes` | `ps`, `running processes` | List top active system processes |
| `lock` | `lock computer`, `lock screen` | Immediately lock the Windows workstation |
| `sleep` | `hibernate`, `suspend` | Put system into sleep/standby mode *(Requires confirmation)* |
| `brightness <0-100>` | `brightness 75` | Adjust monitor brightness level |
| `shutdown [in N]` | `shutdown in 60` | Schedule system shutdown *(Dangerous: requires full confirmation)* |
| `restart [in N]` | `reboot` | Schedule system restart *(Dangerous: requires full confirmation)* |
| `cancel shutdown` | `cancel reboot` | Abort a pending shutdown or restart timer |

### File Operations
| Command | Example | Description |
|---|---|---|
| `create file <name>` | `new file project.txt` | Create an empty file or write initial content |
| `read file <name>` | `open file notes.txt` | View file contents in the console |
| `update file <name>` | `edit file config.ini` | Interactive multi-line file content editor |
| `append file <name> <text>` | `append file log.txt done` | Append a line of text directly to a file |
| `rename file <src> to <dst>` | `rename file old.txt to new.txt` | Rename a file |
| `copy file <src> to <dst>` | `copy file a.txt to backup\a.txt` | Copy a file to another location |
| `move file <src> to <dst>` | `move file a.txt to archive\` | Move a file to another directory |
| `delete file <name>` | `delete file temp.log` | Delete a file *(Requires confirmation)* |
| `list files [path]` | `ls`, `dir` | List files and folders with size and modified dates |
| `recent files [path]` | `recent files` | List recently modified files |
| `search files <pattern>` | `find files *.py` | Search files matching pattern recursively |
| `file info <path>` | `file info notes.txt` | Inspect file metadata, permissions, and timestamps |
| `create folder <path>` | `new folder backups` | Create a new directory |
| `delete folder <path>` | `delete folder temp` | Remove a directory *(Requires confirmation)* |
| `open folder <path>` | `open dir downloads` | Reveal directory in Windows File Explorer |

### Applications
| Command | Example | Description |
|---|---|---|
| `open <app>` | `open chrome`, `launch notepad` | Open an application or executable |
| `close app <name>` | `close app notepad` | Close an active application gracefully |
| `terminate <app>` | `force kill chrome` | Force terminate a process |
| `minimize all` | `minimize windows` | Minimize all open application windows |
| `show desktop` | `desktop` | Toggle the Windows desktop view |
| `running apps` | `list applications` | List active user window applications |

*Executable shortcuts can be customized in `data/settings.json` under `app_paths`.*

### Media & Audio
| Command | Example | Description |
|---|---|---|
| `volume <0-100>` | `volume 50` | Set master volume to an exact percentage |
| `volume up [step]` | `vol up 15` | Increase volume by specified increment |
| `volume down [step]` | `vol down 10` | Decrease volume by specified increment |
| `mute` / `unmute` | `silence` | Mute or restore audio |
| `play music [path]` | `play music` | Play audio file or random music from configured directory |
| `play video [path]` | `play video` | Play video file from configured directory |
| `spotify` | `open spotify` | Launch Spotify application |
| `youtube <query>` | `yt lofi hip hop` | Search YouTube directly in browser |
| `radio` | `play radio` | Open curated streaming radio |

### Productivity
| Command | Example | Description |
|---|---|---|
| `history [count]` | `history 10` | Display recent command execution history |
| `note <text>` | `note call client at 3 PM` | Quickly save a timestamped note |
| `notes [count]` | `read notes 5` | View recent entries from your notes file |
| `add todo <task>` | `add todo submit project report` | Add a new task to your to-do list |
| `todos` / `tasks` | `list todos` | Display all active and completed to-do items |
| `done todo <id>` | `complete todo 1` | Mark a to-do item as completed |
| `remove todo <id>` | `delete todo 1` | Delete a task from the to-do list |

### Information & Utilities
| Command | Example | Description |
|---|---|---|
| `weather [city]` | `weather Tokyo` | Current weather and temperature (OpenWeatherMap) |
| `define <word>` | `define algorithm` | Word definition, phonetics, and speech part |
| `calc <expression>` | `calculate 144 / 12 + 7` | Safe mathematical calculator |
| `convert <val> <from> to <to>` | `convert 10 km to miles` | Unit converter (length, weight, temperature, data) |
| `trivia` | `fun fact` | Interesting facts and trivia |
| `joke` | `tell me a joke` | Clean and dark comedy jokes (toggleable in settings) |

### Automation
| Command | Example | Description |
|---|---|---|
| `run command <cmd>` | `cmd dir /w` | Run raw shell commands *(Dangerous: requires explicit confirmation)* |

### Reminders & Notifications
| Command | Example | Description |
|---|---|---|
| `remind me <msg> in <N> minutes` | `remind me drink water in 20 minutes` | Set reminder with Windows desktop notification |
| `remind me in <N> hours <msg>` | `remind me in 1 hour stand up` | Schedule hourly reminder |
| `list reminders` | `my reminders` | List active background reminders |
| `delete reminder <index>` | `delete reminder 1` | Cancel a scheduled reminder |

### Browser & Clipboard
| Command | Example | Description |
|---|---|---|
| `search <query>` | `search Python threading` | Perform Google search in default browser |
| `open website <url>` | `visit github.com` | Navigate to web address |
| `clipboard` | `get clipboard` | Read current text in Windows clipboard |
| `copy <text>` | `copy hello world` | Set text into Windows clipboard |
| `clear clipboard` | `clear clipboard` | Wipe clipboard contents |
| `screenshot` | `snap` | Take full screenshot and save to `screenshots/` |
| `open last screenshot` | `latest screenshot` | Open the most recent screenshot in default viewer |

### Settings & Terminal Control
| Command | Description |
|---|---|
| `settings` | Display table of active configuration values |
| `settings menu` | Interactive configuration editor in terminal |
| `toggle tts` | Turn text-to-speech feedback on or off |
| `toggle genz` | Enable/disable playful Gen Z conversational flair |
| `toggle dark jokes` | Enable/disable dark humor in jokes |
| `help` / `commands` | Show full command index table |
| `help <category>` | View commands filtered by category (e.g. `help Files`) |
| `exit` / `quit` | Exit DOT assistant cleanly |

---

## Architecture & Design Principles

```text
User Input (text)
      │
      ▼
  core/parser.py       ◄── Regex intent rules ──► ParsedCommand { intent, arguments, raw }
      │
      ▼
  core/dispatcher.py   ◄── Checks permissions ──► PermissionLevel (SAFE / CONFIRM / DANGEROUS)
      │
      ▼
  modules/*.py         ◄── Executes handler ────► Structured result string
      │
      ▼
  core/assistant.py    ◄── Renders UI (Rich) ───► Prints formatted output / Optional TTS
```

- **Deterministic Execution**: Every command follows strict regex grammar and dedicated handler dispatch. No unpredictable hallucinations, external LLM calls, or latency.
- **Strict Permission Gating**: Destructive actions (deletions, system reboot/shutdown, shell automation) require explicit interactive user confirmations (`y/N` or typing `yes`).
- **Zero Cloud Requirement**: Functions completely offline on any modern Windows system without requiring external internet access (except for optional online weather and definition lookups).
- **Graceful Fallbacks**: Audio, notifications, and clipboard gracefully degrade to terminal fallbacks if system libraries or services are unavailable.

---

## Running the Automated Test Suite

DOT includes an automated unit test suite covering intent parsing, permission handling, registry dispatch, and assistant orchestration.

```bash
pytest tests/ -v
```

---

## Author & Maintainer

Created, designed, and maintained by **Shubham Salunke**.

---

## License

MIT - see [LICENSE](LICENSE).

---

## Project Status & Concluding Note

This repository represents the **completed and finalized** release of the **DOT Desktop Operations Terminal**. The codebase has been fully refactored from its initial monolithic prototype into a clean, modular, and maintainable architecture with robust error handling, automated testing, and comprehensive Windows desktop management capabilities.

Thank you for exploring DOT!
