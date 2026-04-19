import uuid
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.game_service import GameSession, get_session
from app.models import GameMode, GameState

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Soc Ops - Social Bingo")
app.add_middleware(SessionMiddleware, secret_key="soc-ops-secret-key")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Constants
DEFAULT_ITEM_COUNT = 24
DEFAULT_GAME_MODE = "bingo"


def _get_game_session(request: Request) -> GameSession:
    """Get or create a game session using cookie-based sessions."""
    if "session_id" not in request.session:
        request.session["session_id"] = uuid.uuid4().hex
    return get_session(request.session["session_id"])


def _parse_game_mode(mode_str: str) -> GameMode:
    """Parse and validate game mode from string."""
    try:
        return GameMode(mode_str)
    except ValueError:
        return GameMode.BINGO


def _parse_item_count(count_str: str, default: int = DEFAULT_ITEM_COUNT) -> int:
    """Parse and validate item count from string."""
    try:
        return int(count_str)
    except ValueError:
        return default


def _get_game_screen_template(session: GameSession) -> str:
    """Get appropriate screen template based on game mode."""
    if session.game_mode == GameMode.SCAVENGER_HUNT:
        return "components/hunt_screen.html"
    return "components/game_screen.html"


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    session = _get_game_session(request)
    return templates.TemplateResponse(
        request,
        "home.html",
        {"session": session, "GameState": GameState},
    )


@app.post("/start", response_class=HTMLResponse)
async def start_game(request: Request) -> Response:
    session = _get_game_session(request)
    session.game_mode = _parse_game_mode(
        request.query_params.get("mode", DEFAULT_GAME_MODE)
    )
    item_count = _parse_item_count(
        request.query_params.get("count", str(DEFAULT_ITEM_COUNT))
    )

    if session.game_mode == GameMode.SCAVENGER_HUNT:
        session.start_hunt(item_count)
    else:
        session.start_game()

    template = _get_game_screen_template(session)
    return templates.TemplateResponse(request, template, {"session": session})


@app.post("/toggle/{square_id}", response_class=HTMLResponse)
async def toggle_square(request: Request, square_id: int) -> Response:
    session = _get_game_session(request)
    session.handle_square_click(square_id)
    return templates.TemplateResponse(
        request, "components/game_screen.html", {"session": session}
    )


@app.post("/reset", response_class=HTMLResponse)
async def reset_game(request: Request) -> Response:
    session = _get_game_session(request)
    session.reset_game()
    return templates.TemplateResponse(
        request,
        "components/start_screen.html",
        {"session": session, "GameState": GameState},
    )


@app.post("/dismiss-modal", response_class=HTMLResponse)
async def dismiss_modal(request: Request) -> Response:
    session = _get_game_session(request)
    session.dismiss_modal()
    template = _get_game_screen_template(session)
    return templates.TemplateResponse(request, template, {"session": session})


@app.post("/hunt/collect/{item_id}", response_class=HTMLResponse)
async def hunt_collect_item(request: Request, item_id: int) -> Response:
    session = _get_game_session(request)
    session.mark_item_found(item_id)
    return templates.TemplateResponse(
        request, "components/hunt_screen.html", {"session": session}
    )


def run() -> None:
    """Entry point for the application."""
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
