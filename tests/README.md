🌐 [Português (BR)](README.pt_BR.md) | [Español](README.es.md)

<div align="center">

# 🎯 Soc Ops

### **Break the ice. Find your people. Win bingo.**

*A real-time social bingo game that transforms ordinary mixers into unforgettable connections.*

[🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [📖 Documentation](#-documentation) • [🤝 Contribute](#-contribute)

</div>

---

## What is Soc Ops?

Soc Ops is an interactive **social bingo game** designed for in-person events, conferences, and mixers. Players receive a randomized 5×5 bingo card with prompts like:

> *"Find someone who has lived on 3+ continents"*  
> *"Find someone who speaks 4 languages"*  
> *"Find someone who coded their first app at 10"*

Players mingle around the room, find people who match the prompts, and **mark squares**. First person to get **5 in a row** wins! 🎉

### Why It's Awesome

✅ **Naturally encourages networking** – People have to talk to strangers  
✅ **Inclusive & flexible** – Works for any group, any topic  
✅ **Real-time gameplay** – Built with FastAPI + HTMX for smooth interactions  
✅ **Fully customizable** – Control the questions, themes, and rules  
✅ **Zero dependencies** – No external CDNs; works offline  

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🎰 **Dynamic Board Generation** | Random 5×5 bingo cards with a free center square |
| 🎮 **Real-time Interactions** | HTMX-powered instant feedback without page reloads |
| 📱 **Responsive Design** | Works on phones, tablets, and desktops |
| 🏆 **Win Detection** | Automatic detection of 5-in-a-row (row, column, diagonal) |
| 🎨 **Customizable Questions** | Easy to edit the question bank for your event |
| 🔒 **Session Management** | Persistent game state with secure cookie-based sessions |
| ⚡ **Lightweight** | Custom CSS utilities (Tailwind-like) with zero JS frameworks |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+**
- **uv** package manager ([install here](https://docs.astral.sh/uv/getting-started/))

### Installation & Running

```bash
# Clone the repository
git clone https://github.com/Pratik199607/my-soc-ops-python.git
cd my-soc-ops-python

# Install dependencies
uv sync

# Start the dev server
uv run uvicorn app.main:app --reload --port 8000
```

Then open your browser to **http://localhost:8000** and start playing! 🎯

### Quick Commands

```bash
# Run tests
uv run pytest

# Check code quality (lint)
uv run ruff check .

# Format code
uv run ruff format .
```

---

## 📚 Lab Guide & Learning Path

This project is also an interactive **coding workshop** for learning modern AI-assisted development patterns.

| Part | Title | Learn |
|------|-------|-------|
| [**00**](https://copilot-dev-days.github.io/agent-lab-python/docs/step.html?step=00-overview) | Overview & Checklist | Project setup & requirements |
| [**01**](https://copilot-dev-days.github.io/agent-lab-python/docs/step.html?step=01-setup) | Setup & Context Engineering | AI-powered development workflow |
| [**02**](https://copilot-dev-days.github.io/agent-lab-python/docs/step.html?step=02-design) | Design-First Frontend | Building delightful UIs with Jinja2 |
| [**03**](https://copilot-dev-days.github.io/agent-lab-python/docs/step.html?step=03-quiz-master) | Custom Quiz Master | Multi-agent AI orchestration |
| [**04**](https://copilot-dev-days.github.io/agent-lab-python/docs/step.html?step=04-multi-agent) | Multi-Agent Development | Advanced AI patterns & techniques |

📝 **Offline?** Lab guides are also in the [`workshop/`](workshop/) folder.

---

## 🏗️ Architecture

```
app/
├── templates/          # Jinja2 HTML templates
├── static/            # CSS & JavaScript
├── models.py          # Pydantic models (GameState, BingoSquare)
├── game_logic.py      # Board generation & bingo detection
├── game_service.py    # Session management
├── data.py            # Question bank
└── main.py            # FastAPI routes & HTMX endpoints
tests/                 # Unit tests
```

**Tech Stack:**
- **FastAPI** – Lightning-fast Python web framework
- **Jinja2** – Powerful template engine
- **HTMX** – Interactivity without bloated JS
- **Custom CSS** – Utilities for consistent styling
- **Pydantic** – Data validation & serialization

---

## 🎨 Customization

### Add Your Own Questions

Edit `app/data.py` to customize the bingo prompts:

```python
QUESTIONS = [
    "Find someone who has backpacked through Europe",
    "Find someone who speaks more than 3 languages",
    "Find someone who has met a celebrity",
    # Add more questions...
]
```

### Customize the Theme

Styling lives in `app/static/css/app.css`. It uses custom utility classes:

```html
<div class="flex flex-col items-center justify-center min-h-full bg-accent">
    <h1 class="text-4xl font-bold text-white">Soc Ops</h1>
</div>
```

---

## 🤝 Contribute

We love contributions! Whether it's:
- 🐛 **Bug fixes**
- ✨ **New features**
- 📚 **Better documentation**
- 🎨 **UI/UX improvements**
- ❓ **Questions or ideas**

**Please check out [CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines.

---

## 📄 License

Soc Ops is released under the [MIT License](LICENSE).

---

## 🎓 Credits

Built as part of the **Copilot Dev Days Agent Lab** – an interactive workshop for modern AI-assisted development.

<div align="center">

**[🌐 Official Site](https://copilot-dev-days.github.io/agent-lab-python/) • [💬 Discussions](https://github.com/Pratik199607/my-soc-ops-python/discussions) • [🐛 Issues](https://github.com/Pratik199607/my-soc-ops-python/issues)**

</div>
