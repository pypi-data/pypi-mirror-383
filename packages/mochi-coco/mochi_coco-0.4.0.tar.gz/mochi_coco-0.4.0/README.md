# Mochi Coco 🍡

```bash
.-===-.
|[:::]|
`-----´
```

A beautiful, feature-rich CLI chat application for interacting with LLMs via Ollama with streaming responses, session persistence, markdown rendering and tool support.

## Installation

```bash
pip install mochi-coco
```

## Quick Start

1. Make sure you have [Ollama](https://ollama.com) running locally
2. Pull a model: `ollama pull gpt-oss:20b`
3. Start chatting:

```bash
mochi-coco
```

## Features

- 🚀 **Streaming responses** - Real-time chat with immediate feedback
- 💾 **Session persistence** - Your conversations are automatically saved in the terminal's directory and resumable
- 🎨 **Rich markdown rendering** - Beautiful formatting with syntax highlighting and toggle rendering mid session
- 🔄 **Model switching** - Change models mid-conversation
- ✏️ **Message editing** - Edit previous messages and start from there
- 🧠 **Thinking blocks** - Toggle display of model reasoning (when supported by model + only in markdown mode)
- 📋 **Session management** - Switch between different chat sessions
- 🎛️ **Interactive menus** - Easy-to-use command interface with clear instructions
- ⚡ **Background summarization** - Automatic conversation summaries
- 📝 **System Prompts** - Drop `*.md` or `*.txt` files into the `system_prompts` folder in the root directory of the terminal to use as system prompts.

## Commands

While chatting, you can use these commands:

- `/menu` - Open the main menu with all options OR type in the following shortcuts:
  - `/chats` - Switch between existing sessions or create new ones
  - `/models` - Change the current model
  - `/markdown` - Toggle markdown rendering on/off
  - `/thinking` - Toggle thinking blocks display (only when markdown rendering is enabled)
  - `/system` - Change system prompt during chat session
  - `/tools` - Enable/disable tools feature (only when `/tools` folder exists in the terminal's root directory)
- `/edit` - Edit a previous message and continue from there
- `/exit` or `/quit` - Exit the application

## Usage

### Basic Chat
```bash
mochi-coco
```

### Custom Ollama Host
```bash
mochi-coco --host http://localhost:11434
```

### Example Session
```bash
$ mochi-coco
╭──────────────────────────────────────── 🍡 Welcome to Mochi-Coco! ─────────────────────────────────────────╮
│                                                                                                            │
│  🤖 AI Chat with Style                                                                                     │
│                                                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─────────────────────────────────────────── 💬 Previous Sessions ───────────────────────────────────────────╮
│                                                                                                            │
│ ┏━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓             │
│ ┃ #   ┃ Session ID   ┃ Model                ┃ Preview                             ┃ Messages ┃             │
│ ┡━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩             │
│ │ 1   │ 241d72d985   │ gpt-oss:20b          │ Who was the first Avenger in the    │    2     │             │
│ │     │              │                      │ MCU?                                │          │             │
│ │ 2   │ c1def24fa7   │ gpt-oss:20b          │ Hi                                  │    2     │             │
│ └─────┴──────────────┴──────────────────────┴─────────────────────────────────────┴──────────┘             │
│                                                                                                            │
│ 💡 Options:                                                                                                │
│ • 📝 Select session (1-2)                                                                                  │
│ • 🆕 Type 'new' for new chat                                                                               │
│ • 🗑️ Type '/delete <number>' to delete session                                                             │
│ • 👋 Type 'q' to quit                                                                                      │
│                                                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice: new
╭─ 🤖 Available Models ──────────────────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬───────────────────────────┬──────────────┬─────────────────┬──────────┬───────╮                    │
│ │ #   │ Model Name                │    Size (MB) │ Family          │ Max. Cxt │ Tools │                    │
│ ├─────┼───────────────────────────┼──────────────┼─────────────────┼──────────┼───────┤                    │
│ │ 1   │ gpt-oss:20b               │      13141.8 │ gptoss          │   131072 │  Yes  │                    │
│ │ 2   │ qwen3:14b                 │       8846.5 │ qwen3           │    40960 │  Yes  │                    │
│ │ 3   │ qwen3:latest              │       4983.3 │ qwen3           │    40960 │  Yes  │                    │
│ │ 4   │ qwen3:30b                 │      17697.0 │ qwen3moe        │   262144 │  Yes  │                    │
│ │ 5   │ llama3.2:latest           │       1925.8 │ llama           │   131072 │  Yes  │                    │
│ │ 6   │ qwen3-coder:latest        │      17697.0 │ qwen3moe        │   262144 │  No   │                    │
│ │ 7   │ mistral-small3.2:latest   │      14474.3 │ mistral3        │   131072 │  Yes  │                    │
│ ╰─────┴───────────────────────────┴──────────────┴─────────────────┴──────────┴───────╯                    │
│                                                                                                            │
│ 💡 Options:                                                                                                │
│ • 🔢 Select model (1-7)                                                                                    │
│ • 👋 Type 'q' to quit                                                                                      │
│                                                                                                            │
│ ⚠️ ATTENTION: Max. Cxt. is only supported context length not set.                                          │
│ 💡 Open Ollama application to set default context length!                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice: 1
╭──────────────────────────────────────────── Markdown Rendering ────────────────────────────────────────────╮
│ 📝 Enable markdown formatting for responses?                                                               │
│ This will format code blocks, headers, tables, etc.                                                        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Enable markdown? [y/n] (y): y
╭────────────────────────────────────────── Thinking Block Display ──────────────────────────────────────────╮
│ 🤔 Show model's thinking process in responses?                                                             │
│ This will display thinking blocks as formatted quotes.                                                     │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Show thinking blocks? [y/n] (n): y
╭─ 🔧 System Prompts ────────────────────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬───────────────────┬────────────────────────────────────────┬────────────╮                          │
│ │ #   │ Filename          │ Preview                                │ Word Count │                          │
│ ├─────┼───────────────────┼────────────────────────────────────────┼────────────┤                          │
│ │ 1   │ AGENT.md          │ # Persona You are a 00-agent of the... │         58 │                          │
│ │ 2   │ system_prompt.txt │ You are a helpful assistant.           │          5 │                          │
│ ╰─────┴───────────────────┴────────────────────────────────────────┴────────────╯                          │
│                                                                                                            │
│ 💡 Options:                                                                                                │
│ • 📝 Select system prompt (1-2)                                                                            │
│ • 🆕 Type 'no' for no system prompt                                                                        │
│ • 🗑️ Type '/delete <number>' to delete a system prompt                                                     │
│ • 👋 Type 'q' to quit                                                                                      │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice: no
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 💡 Continuing without system prompt...                                                                     │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Info ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ The current model 'gpt-oss:20b' doesn't support structured summarization. Please select a compatible model │
│ to use for generating conversation summaries.                                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ 🤖 Available Models ──────────────────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬───────────────────────────┬──────────────┬─────────────────┬──────────┬───────╮                    │
│ │ #   │ Model Name                │    Size (MB) │ Family          │ Max. Cxt │ Tools │                    │
│ ├─────┼───────────────────────────┼──────────────┼─────────────────┼──────────┼───────┤                    │
│ │ 1   │ qwen3:latest              │       4983.3 │ qwen3           │    40960 │  Yes  │                    │
│ │ 2   │ llama3.2:latest           │       1925.8 │ llama           │   131072 │  Yes  │                    │
│ │ 3   │ qwen3-coder:latest        │      17697.0 │ qwen3moe        │   262144 │  No   │                    │
│ │ 4   │ mistral-small3.2:latest   │      14474.3 │ mistral3        │   131072 │  Yes  │                    │
│ ╰─────┴───────────────────────────┴──────────────┴─────────────────┴──────────┴───────╯                    │
│                                                                                                            │
│ 💡 Options:                                                                                                │
│ • 🔢 Select model (1-4)                                                                                    │
│ • 👋 Type 'q' to quit                                                                                      │
│                                                                                                            │
│ ⚠️ ATTENTION: Max. Cxt. is only supported context length not set.                                          │
│ 💡 Open Ollama application to set default context length!                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice: 2
╭─ Success ──────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Summary model set to 'llama3.2:latest' for this session                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ 💬 Chat Session ──────────────────────────────────────────────────────────────────────────────────────────╮
│ Session ID: b61cafc23e                                                                                     │
│ Model: gpt-oss:20b                                                                                         │
│ Summary Model: llama3.2:latest                                                                             │
│ Tools: None                                                                                                │
│ Tool Policy: Always confirm                                                                                │
│ Markdown: Enabled                                                                                          │
│ Thinking Blocks: Enabled                                                                                   │
│                                                                                                            │
│ 💡 Available Commands:                                                                                     │
│ • /menu - Open the main menu                                                                               │
│ • /edit - Edit a previous message                                                                          │
│ • /exit or /quit - Exit the application                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────╮
│ 🧑 You │
╰────────╯
```

### Chat Session Menu

During a chat session it is possible to open the chat menu with the command `/menu`. Select one of the options by typing the number (e.g. `1`).

> **Tip**:
>
> Each of the available options in this menu is also a command itself and can therefore be directly executed without opening the chat menu. For example, typing `/1` will switch to a different chat session. Or `/5` to toggle the tool feature and open the tool menu.

```bash
╭────────╮
│ 🧑 You │
╰────────╯
/menu
╭─ ⌨️ Available Commands ───────────────────────────────────────────────────────────────────────╮
│ ╭──────────────┬────────────────────────┬─────────────────────────────────────╮               │
│ │  /1          │  💬 Switch Sessions    │  Change to different chat session   │               │
│ │  /2          │  🤖 Change Model       │  Select a different AI model        │               │
│ │  /3          │  📝 Toggle Markdown    │  Enable/disable markdown rendering  │               │
│ │  /4          │  🤔 Toggle Thinking    │  Show/hide thinking blocks          │               │
│ │  /5          │  📂 Enable Tools       │  Select tools to use                │               │
│ │  /6          │  🔧 System Prompt      │  Select different system prompt     │               │
│ │  /help       │  📚 Help               │  Show all available commands        │               │
│ │  /quit       │  👋 Exit               │  Exit the application               │               │
│ ╰──────────────┴────────────────────────┴─────────────────────────────────────╯               │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice:
```

### System Prompts

System prompts have to be provided within the `/system_prompts` folder at the terminals root directory. Only `*.md` or `*.txt` files are supported.

Find more here: [User Guide System Prompts](docs/system_prompt/user_guide_system_prompt.md)

The system prompts can be selected when creating a new chat session:
```bash
╭─ 🔧 System Prompts ──────────────────────────────────────────────────────────────────────╮
│ ╭─────┬─────────────────┬─────────────────────────────────────┬────────────╮             │
│ │ #   │ Filename        │ Preview                             │ Word Count │             │
│ ├─────┼─────────────────┼─────────────────────────────────────┼────────────┤             │
│ │ 1   │ AGENTS.md       │ You are a helpful agent             │          5 │             │
│ ╰─────┴─────────────────┴─────────────────────────────────────┴────────────╯             │
│                                                                                          │
│ 💡 Options:                                                                              │
│ • 📝 Select system prompt (1-1)                                                          │
│ • 🆕 Type 'no' for no system prompt                                                      │
│ • 🗑️ Type '/delete <number>' to delete a system prompt                                   │
│ • 👋 Type 'q' to quit                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice:
```

... or by opening the chat session menu and selecting the corresponding option
```bash
╭────────╮
│ 🧑 You │
╰────────╯
/menu
╭─ ⌨️ Available Commands ──────────────────────────────────────────────────────────────────╮
│ ╭──────────────┬────────────────────────┬─────────────────────────────────────╮          │
│ │  /1          │  💬 Switch Sessions    │  Change to different chat session   │          │
│ │  /2          │  🤖 Change Model       │  Select a different AI model        │          │
│ │  /3          │  📝 Toggle Markdown    │  Enable/disable markdown rendering  │          │
│ │  /4          │  🤔 Toggle Thinking    │  Show/hide thinking blocks          │          │
│ │  /5          │  📂 Enable Tools       │  Select tools to use                │          │
│ │  /6          │  🔧 System Prompt      │  Select different system prompt     │          │
│ │  /quit /q    │  👋 Exit               │  Exit the menu                      │          │
│ ╰──────────────┴────────────────────────┴─────────────────────────────────────╯          │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice: 6
╭─ 🔧 System Prompts ──────────────────────────────────────────────────────────────────────╮
│ ╭─────┬─────────────────┬─────────────────────────────────────┬────────────╮             │
│ │ #   │ Filename        │ Preview                             │ Word Count │             │
│ ├─────┼─────────────────┼─────────────────────────────────────┼────────────┤             │
│ │ 1   │ AGENTS.md       │ You are a helpful agent             │          5 │             │
│ ╰─────┴─────────────────┴─────────────────────────────────────┴────────────╯             │
│                                                                                          │
│ 💡 Options:                                                                              │
│ • 📝 Select system prompt (1-1)                                                          │
│ • 🆕 Type 'no' for no system prompt                                                      │
│ • 🗑️ Type '/delete <number>' to delete a system prompt                                   │
│ • 👋 Type 'q' to quit                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice:
```

... or by typing the shortcut `/system` into the chat
```bash
╭────────╮
│ 🧑 You │
╰────────╯
/system
╭─ 🔧 System Prompts ──────────────────────────────────────────────────────────────────────╮
│ ╭─────┬─────────────────┬─────────────────────────────────────┬────────────╮             │
│ │ #   │ Filename        │ Preview                             │ Word Count │             │
│ ├─────┼─────────────────┼─────────────────────────────────────┼────────────┤             │
│ │ 1   │ AGENTS.md       │ You are a helpful agent             │          5 │             │
│ ╰─────┴─────────────────┴─────────────────────────────────────┴────────────╯             │
│                                                                                          │
│ 💡 Options:                                                                              │
│ • 📝 Select system prompt (1-1)                                                          │
│ • 🆕 Type 'no' for no system prompt                                                      │
│ • 🗑️ Type '/delete <number>' to delete a system prompt                                   │
│ • 👋 Type 'q' to quit                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice:
```

### Edit Menu

With the in-chat command `/edit` you can edit messages from the current chat history.

```bash
╭────────╮
│ 🧑 You │
╰────────╯
/edit

✏️ Edit Message
╭─ ✏️  Edit Messages ────────────────────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬──────────────┬───────────────────────────────────────────────────────────────────────────╮         │
│ │ #   │ Role         │ Preview                                                                   │         │
│ ├─────┼──────────────┼───────────────────────────────────────────────────────────────────────────┤         │
│ │ 1   │ 🧑 User      │ Who was the first Avenger in the MCU?                                     │         │
│ │ -   │ 🤖 Assistant │ **Captain America (Steve Rogers)** is widely considered the first Aven... │         │
│ ╰─────┴──────────────┴───────────────────────────────────────────────────────────────────────────╯         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Select a user message (1-1) or 'q' to cancel                                                               │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

> **Disclaimer**
>
> Editing a message will continue the chat from this point. All previously trailing messages - whether user or assistant - will be deleted.

### Tool Menu

The tool feature depends on the existence of a `/tools` folder in the terminal's root directory and python functions. Tools are not enabled by default.

Get more information how to use the tool feature here: [User Guide: Tools](docs/tools/user_guide_tools.md)

```bash
╭────────╮
│ 🧑 You │
╰────────╯
/5
No tools currently selected

╭─ 🛠️ Tool Selection ──────────────────────────────────────────────────────────────────────╮
│ Individual Tools                                                                         │
│ ╭───────┬───────────────────────────┬──────────────────────────────────────────────────╮ │
│ │ #     │ Tool Name                 │ Description                                      │ │
│ ├───────┼───────────────────────────┼──────────────────────────────────────────────────┤ │
│ │ 1     │ add_numbers               │ Add two numbers together.                        │ │
│ │ 2     │ subtract_numbers          │ Subtract the second number from the first        │ │
│ │       │                           │ number.                                          │ │
│ │ 3     │ multiply_numbers          │ Multiply two numbers together.                   │ │
│ │ 4     │ divide_numbers            │ Divide the first number by the second number.    │ │
│ │ 5     │ power_calculation         │ Calculate base raised to the power of exponent.  │ │
│ │ 6     │ square_root               │ Calculate the square root of a number.           │ │
│ │ 7     │ calculate_percentage      │ Calculate what percentage one number is of       │ │
│ │       │                           │ another.                                         │ │
│ │ 8     │ get_current_time          │ Get the current date and time.                   │ │
│ │ 9     │ generate_random_number    │ Generate a random number between two values.     │ │
│ │ 10    │ flip_coin                 │ Flip a virtual coin.                             │ │
│ │ 11    │ count_words               │ Count the number of words in a text.             │ │
│ │ 12    │ reverse_text              │ Reverse the given text.                          │ │
│ │ 13    │ roll_dice                 │ Roll one or more dice with specified number of   │ │
│ │       │                           │ sides.                                           │ │
│ ╰───────┴───────────────────────────┴──────────────────────────────────────────────────╯ │
│                                                                                          │
│ Tool Groups                                                                              │
│ ╭──────────┬───────────────────────────┬───────────────────────────────────────────────╮ │
│ │ Letter   │ Group Name                │ Tools Included                                │ │
│ ├──────────┼───────────────────────────┼───────────────────────────────────────────────┤ │
│ │ a        │ basic_calculator          │ add_numbers, subtract_numbers,                │ │
│ │          │                           │ multiply_numbers...                           │ │
│ │ b        │ fun_tools                 │ flip_coin, roll_dice, reverse_text,           │ │
│ │          │                           │ generate_ra...                                │ │
│ │ c        │ math                      │ add_numbers, subtract_numbers,                │ │
│ │          │                           │ multiply_numbers...                           │ │
│ │ d        │ utilities                 │ get_current_time, generate_random_number,     │ │
│ │          │                           │ flip_...                                      │ │
│ ╰──────────┴───────────────────────────┴───────────────────────────────────────────────╯ │
│                                                                                          │
│ 💡 Options:                                                                              │
│ • 🔢 Select tools by numbers (e.g., 1,3,4 or 1-3)                                        │
│ • 📂 Select a group by letter (e.g., a)                                                  │
│ • ❌ Type 'none' to clear selection                                                       │
│ • 🔄 Type 'reload' to refresh tools                                                      │
│ • ↩️  Press Enter to keep current selection                                              │
│ • 👋 Type 'q' to cancel                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice:
```
