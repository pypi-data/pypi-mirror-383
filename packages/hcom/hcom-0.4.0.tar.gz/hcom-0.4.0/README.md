# hcom - Claude Hook Comms

[![PyPI - Version](https://img.shields.io/pypi/v/hcom)](https://pypi.org/project/hcom/)
 [![PyPI - License](https://img.shields.io/pypi/l/hcom)](https://opensource.org/license/MIT) [![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org) [![DeepWiki](https://img.shields.io/badge/DeepWiki-aannoo%2Fclaude--hook--comms-blue.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAyCAYAAAAnWDnqAAAAAXNSR0IArs4c6QAAA05JREFUaEPtmUtyEzEQhtWTQyQLHNak2AB7ZnyXZMEjXMGeK/AIi+QuHrMnbChYY7MIh8g01fJoopFb0uhhEqqcbWTp06/uv1saEDv4O3n3dV60RfP947Mm9/SQc0ICFQgzfc4CYZoTPAswgSJCCUJUnAAoRHOAUOcATwbmVLWdGoH//PB8mnKqScAhsD0kYP3j/Yt5LPQe2KvcXmGvRHcDnpxfL2zOYJ1mFwrryWTz0advv1Ut4CJgf5uhDuDj5eUcAUoahrdY/56ebRWeraTjMt/00Sh3UDtjgHtQNHwcRGOC98BJEAEymycmYcWwOprTgcB6VZ5JK5TAJ+fXGLBm3FDAmn6oPPjR4rKCAoJCal2eAiQp2x0vxTPB3ALO2CRkwmDy5WohzBDwSEFKRwPbknEggCPB/imwrycgxX2NzoMCHhPkDwqYMr9tRcP5qNrMZHkVnOjRMWwLCcr8ohBVb1OMjxLwGCvjTikrsBOiA6fNyCrm8V1rP93iVPpwaE+gO0SsWmPiXB+jikdf6SizrT5qKasx5j8ABbHpFTx+vFXp9EnYQmLx02h1QTTrl6eDqxLnGjporxl3NL3agEvXdT0WmEost648sQOYAeJS9Q7bfUVoMGnjo4AZdUMQku50McDcMWcBPvr0SzbTAFDfvJqwLzgxwATnCgnp4wDl6Aa+Ax283gghmj+vj7feE2KBBRMW3FzOpLOADl0Isb5587h/U4gGvkt5v60Z1VLG8BhYjbzRwyQZemwAd6cCR5/XFWLYZRIMpX39AR0tjaGGiGzLVyhse5C9RKC6ai42ppWPKiBagOvaYk8lO7DajerabOZP46Lby5wKjw1HCRx7p9sVMOWGzb/vA1hwiWc6jm3MvQDTogQkiqIhJV0nBQBTU+3okKCFDy9WwferkHjtxib7t3xIUQtHxnIwtx4mpg26/HfwVNVDb4oI9RHmx5WGelRVlrtiw43zboCLaxv46AZeB3IlTkwouebTr1y2NjSpHz68WNFjHvupy3q8TFn3Hos2IAk4Ju5dCo8B3wP7VPr/FGaKiG+T+v+TQqIrOqMTL1VdWV1DdmcbO8KXBz6esmYWYKPwDL5b5FA1a0hwapHiom0r/cKaoqr+27/XcrS5UwSMbQAAAABJRU5ErkJggg==)](https://deepwiki.com/aannoo/claude-hook-comms)

CLI tool for launching multiple Claude Code terminals with interactive [subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents), headless persistence, and real-time communication via [hooks](https://docs.anthropic.com/en/docs/claude-code/hooks). Works on Mac, Linux, Windows, and Android with zero dependencies.

![Claude Code Hook Comms Example](https://raw.githubusercontent.com/aannoo/claude-hook-comms/main/screencapture.gif)

## 🥦 Usage

**Run without installing** ([uv](https://docs.astral.sh/uv/#installation))
```bash
uvx hcom open 2
```

**Install**
```bash
pip install hcom
hcom open 2
```

| Commands |  |
|---------|-------------|
| `hcom open [n]` | Launch `n` instances or named agents |
| `hcom watch` | View live dashboard and messaging |
| `hcom stop` | Disable hcom chat for instance |
| `hcom start` | Enable hcom chat for instance |


## 🦆 What It Does

`hcom open` adds hooks to the `.claude/settings.local.json` file in the current folder and launches terminals with claude code that remain active, waiting to respond to messages in the shared chat. Normal Claude Code opened with `claude` remains unaffected by hcom, but can opt-in via `hcom start` and opt-out with `hcom stop`.


### Interactive subagents in their own terminal
```bash
# Launch subagents from your .claude/agents
hcom open -a planner -a code-writer -a reviewer
```

### Persistent headless instances
```bash
# Launch one headless instance (default 30min timeout)
hcom open -p
hcom stop # Stop it earlier than timeout
```

### Groups and direct messages
```bash
hcom open 2 -t cool  # Creates cool-hovoa7 & cool-homab8
hcom send '@cool hi, you are cool'
hcom send '@homab8 hi, you are cooler'
```

### Toggle HCOM in Claude Code
```bash
claude  # Start normal Claude Code
'run hcom start'  # Start HCOM for this instance to receive messages
'run hcom stop'  # Stop HCOM for this instance, continue as normal claude code
```

---


<details>
<summary><strong>🦷 Features</strong></summary>

- **Multi-Terminal Launch** - Launch Claude Code subagents in new terminals
- **Background Mode** - Run headless instances without terminal windows
- **Interactive subagents** - Run subagents in their own terminal window
- **Live Dashboard** - Real-time monitoring and messaging
- **Multi-Agent Communication** - Instances talk to each other via shared chat
- **@Mention Targeting** - Send messages to specific instances or teams
- **Session Persistence** - Resume previous conversations automatically
- **Zero Dependencies** - Pure Python stdlib, works everywhere
- **Cross-platform** - Native support for Windows, WSL, macOS, Linux, Android

</details>

<details>
<summary><strong>🥨 All Commands</strong></summary>

```bash
Usage:
  hcom open [count] [-a agent]... [-t prefix] [-p] [-- claude-args]
  hcom watch [--logs|--status|--wait [SEC]]
  hcom stop [target] [--force]
  hcom start [target]
  hcom send "msg"

Commands:
  open                 Launch Claude instances (default count: 1)
  watch                Monitor conversation dashboard
  stop                 Stop instances, clear conversation, or remove hooks
  start                Start stopped instances
  send                 Send message to instances

Open options:
  [count]              Number of instances per agent (default 1)
  -a, --agent AGENT    Agent to launch (repeatable)
  -t, --prefix PREFIX  Team prefix for names
  -p, --background     Launch in background

Stop targets:
  (no arg)             Stop HCOM for current instance (when inside)
  <alias>              Stop HCOM for specific instance
  all                  Stop all instances + clear & archive conversation
  hooking              Remove hooks from current directory
  hooking --all        Remove hooks from all tracked directories
  everything           Stop all + clear conversation + remove all hooks

Start targets:
  (no arg)             Start HCOM for current instance (when inside)
  <alias>              Start HCOM for specific instance
  hooking              Install hooks in current directory

Watch options:
  --logs               Show message history
  --status             Show instance status JSON
  --wait [SEC]         Wait for new messages (default 60s)

Stop flags:
  --force              Force stop (deny Bash tool use)
```

</details>



<details>
<summary><strong>🗿 Examples</strong></summary>

```bash
# Launch 3 headless instances that time out after 60 seconds of inactivity
HCOM_WAIT_TIMEOUT="60" hcom open 3 -p
# Stop all instances
hcom stop all

# Launch multiple of the same subagent
hcom open 3 -a reviewer

# Launch mixed agents with team prefix
hcom open -t api -a backend -a frontend

# Launch agent with specific prompt
HCOM_INITIAL_PROMPT='write tests' hcom open -a test-writer

# Resume instance (hcom chat will continue)
hcom open -- --resume session_id

# Text appended to all messages recieved by instance
HCOM_INSTANCE_HINTS="remember where you came from" hcom open

# Pass multiple Claude flags
hcom open -a orchestrator -- --model sonnet --resume session_id

</details>

<details>
<summary><strong>🦖 Configuration</strong></summary>

### Configuration

Settings can be changed two ways:

#### Method 1: Environment variable (temporary, per-command/instance)


```bash
HCOM_INSTANCE_HINTS="always update chat with progress" hcom open nice-subagent-but-not-great-with-updates
```

#### Method 2: Config file (persistent, affects all instances)

### Config File Location

`~/.hcom/config.json`

| Setting | Default | Environment Variable | Description |
|---------|---------|---------------------|-------------|
| `wait_timeout` | 1800 | `HCOM_WAIT_TIMEOUT` | How long instances wait for messages (seconds) |
| `max_message_size` | 1048576 | `HCOM_MAX_MESSAGE_SIZE` | Maximum message length (1MB) |
| `max_messages_per_delivery` | 50 | `HCOM_MAX_MESSAGES_PER_DELIVERY` | Messages delivered per batch |
| `sender_name` | "bigboss" | `HCOM_SENDER_NAME` | Your name in chat |
| `sender_emoji` | "🐳" | `HCOM_SENDER_EMOJI` | Your emoji icon |
| `initial_prompt` | "Say hi in chat" | `HCOM_INITIAL_PROMPT` | What new instances are told to do |
| `first_use_text` | "Essential, concise messages only" | `HCOM_FIRST_USE_TEXT` | Welcome message for instances |
| `terminal_mode` | "new_window" | `HCOM_TERMINAL_MODE` | How to launch terminals ("new_window", "same_terminal", "show_commands") |
| `terminal_command` | null | `HCOM_TERMINAL_COMMAND` | Custom terminal command (see Terminal Options) |
| `cli_hints` | "" | `HCOM_CLI_HINTS` | Extra text added to CLI outputs |
| `instance_hints` | "" | `HCOM_INSTANCE_HINTS` | Extra text added to instance messages |
| `auto_watch` | true | `HCOM_AUTO_WATCH` | Auto-launch watch dashboard after open |
| `env_overrides` | {} | - | Additional environment variables for Claude Code |

### Examples

```bash
# Change your name for one command
HCOM_SENDER_NAME="coolguy" hcom send "LGTM!"

# Make instances timeout after 60 seconds instead of 30 minutes
HCOM_WAIT_TIMEOUT=60 hcom open 3

# Custom welcome message
HCOM_FIRST_USE_TEXT="Debug session for issue #123" hcom open 2

# Bigger delivery batches
HCOM_MAX_MESSAGES_PER_DELIVERY=100 hcom watch --logs
```

**Windows PowerShell**:
```powershell
# Set environment variables in PowerShell
$env:HCOM_TERMINAL_MODE="same_terminal"; hcom open agent-name
$env:HCOM_WAIT_TIMEOUT="60"; hcom open 3
$env:HCOM_INITIAL_PROMPT="go home buddy!"; hcom open
```

### Status Indicators

When running `hcom watch`, each instance shows its current state:

- ▶ **active** (green) - Working (processing/executing)
- ▷ **delivered** (cyan) - Just received a message
- ◉ **waiting** (blue) - Waiting for messages
- ■ **blocked** (yellow) - Permission request pending
- ○ **inactive** (red) - Closed/timed out/ended
- ○ **unknown** (gray) - No status data or stale
- **(bg)** suffix - Instance running in background headless mode

</details>

<details>
<summary><strong>🎲 How It Works</strong></summary>

### Hooks!

hcom adds hooks to your project directory's `.claude/settings.local.json`:

1. **Sending**: Claude uses `hcom send "message"` to communicate
2. **Receiving**: Other Claudes get notified via Stop hook or immediate delivery after sending
3. **Waiting**: Stop hook keeps Claude in a waiting state for new messages

- **Identity**: Each instance gets a unique name based on session ID (e.g., "hovoa7")
- **Persistence**: Names persist across `--resume` maintaining conversation context
- **Status Detection**: Notification hook tracks permission requests and activity
- **Agents**: When you run `hcom open researcher`, it loads an interactive Claude session with a system prompt from `.claude/agents/researcher.md` (local) or `~/.claude/agents/researcher.md` (global). Specified `model:` and `tools:` are carried over

### Architecture
- **Single conversation** - All instances share one global conversation
- **Opt-in participation** - Only Claude code instances launched with `hcom open` join automatically, normal instances can use `hcom start`/`stop`
- **@-mention filtering** - Target messages to specific instances or teams

### File Structure
```plaintext
~/.hcom/                             
├── hcom.log       # Conversation log
├── instances/     # Instance tracking
├── logs/          # Background process logs
├── config.json    # Configuration
└── archive/       # Archived sessions

your-project/  
└── .claude/
    └── settings.local.json  # hcom hooks
```

</details>


<details>
<summary><strong>🥔 Terminal Options</strong></summary>

### Terminal Mode

Configure terminal behavior in `~/.hcom/config.json`:
- `"terminal_mode": "new_window"` - Opens new terminal window(s) (default)
- `"terminal_mode": "same_terminal"` - Opens in current terminal

#### Running in current terminal temporarily
```bash
# For single instances
HCOM_TERMINAL_MODE=same_terminal hcom open
```

### Default Terminals

- **macOS**: Terminal.app
- **Linux**: gnome-terminal, konsole, or xterm
- **Windows & WSL**: Windows Terminal / Git Bash
- **Android**: Termux


### Custom Terminals

Configure `terminal_command` in `~/.hcom/config.json` (permanent) or environment variables (temporary).

#### How to use this

The `{script}` placeholder is replaced by HCOM with the path to a temporary bash script that launches Claude Code.

Your custom command just needs to:
1. Accept `{script}` as a placeholder that will be replaced with a script path
2. Execute that script with bash

Example template: `your_terminal_command --execute "bash {script}"`

### Custom Terminal Examples

#### iTerm2
```json
"terminal_command": "open -a iTerm {script}"
```

#### [ttab](https://github.com/mklement0/ttab) (new tab instead of new window in Terminal.app)
```json
"terminal_command": "ttab {script}"
```

#### [wttab](https://github.com/lalilaloe/wttab) (new tab in Windows Terminal)
```json
"terminal_command": "wttab {script}"
```

#### More
```json
# WezTerm Linux/Windows
"terminal_command": "wezterm start -- bash {script}"

# Tabs from within WezTerm
"terminal_command": "wezterm cli spawn -- bash {script}"

# WezTerm macOS:
"terminal_command": "open -n -a WezTerm.app --args start -- bash {script}"

# Tabs from within WezTerm macOS
"terminal_command": "/Applications/WezTerm.app/Contents/MacOS/wezterm cli spawn -- bash {script}"

# Wave Terminal Mac/Linux/Windows. From within Wave Terminal:
"terminal_command": "wsh run -- bash {script}"

# Alacritty macOS:
"terminal_command": "open -n -a Alacritty.app --args -e bash {script}"

# Alacritty Linux:
"terminal_command": "alacritty -e bash {script}"

# Kitty macOS:
"terminal_command": "open -n -a kitty.app --args {script}"

# Kitty Linux
"terminal_command": "kitty {script}"
```

#### tmux
```json
"terminal_command": "tmux new-window -n hcom {script}"
```
```bash
# tmux commands work inside tmux, start a session with:
tmux new-session 'hcom open 3' # each instance opens in new tmux window

# Or one time split-panes:
# Start tmux with split panes and 3 claude instances in hcom chat
HCOM_TERMINAL_COMMAND="tmux split-window -h {script}" hcom open 3
```

### Android (Termux)

1. Install [Termux](https://f-droid.org/packages/com.termux/) from F-Droid (not Google Play)
2. Setup:
   ```bash
   pkg install python nodejs
   npm install -g @anthropic-ai/claude-cli
   pip install hcom
   ```
3. Enable:
   ```bash
   echo "allow-external-apps=true" >> ~/.termux/termux.properties
   termux-reload-settings
   ```
4. Enable: "Display over other apps" permission for visible terminals

5. Run: `hcom open`

---

</details>


<details>
<summary><strong>⚗️ Remove</strong></summary>


### Archive Conversation / Start New
```bash
hcom stop all
```

### Stop Running Instances
```bash
# Stop specific instance
hcom stop hovoa7

# Stop all and archive
hcom stop all
```

### Start Stopped Instances
```bash
# Start specific instance
hcom start hovoa7
```

### Remove HCOM hooks
```bash
# Current directory
hcom stop hooking

# All directories
hcom stop hooking --all
```

### Remove hcom Completely
1. Remove hcom: `rm /usr/local/bin/hcom` (or wherever you installed hcom)
2. Remove all data: `rm -rf ~/.hcom`

</details>

## 🦐 Requirements

- Python 3.10+
- [Claude Code](https://claude.ai/code)



## 🌮 License

- MIT License

---