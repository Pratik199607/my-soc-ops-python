from dataclasses import dataclass, field

from app.game_logic import (
    check_bingo,
    generate_board,
    get_winning_square_ids,
    toggle_square,
)
from app.hunt_logic import generate_hunt_board
from app.models import (
    BingoLine,
    BingoSquareData,
    CardData,
    GameMode,
    GameState,
    HuntItemData,
)

DEFAULT_HUNT_ITEM_COUNT = 24


@dataclass
class GameSession:
    """Holds the state for a single game session."""

    game_state: GameState = GameState.START
    game_mode: GameMode = GameMode.BINGO
    board: list[BingoSquareData] = field(default_factory=list)
    winning_line: BingoLine | None = None
    show_bingo_modal: bool = False
    hunt_items: list[HuntItemData] = field(default_factory=list)
    hunt_progress: int = 0
    hunt_item_count: int = DEFAULT_HUNT_ITEM_COUNT
    show_hunt_modal: bool = False
    cards: list[CardData] = field(default_factory=list)
    current_card_index: int = 0
    cards_found: int = 0
    cards_target: int = 10
    show_card_modal: bool = False
    shared_cards: bool = False  # If False, each player gets unique cards

    @property
    def winning_square_ids(self) -> set[int]:
        return get_winning_square_ids(self.winning_line)

    @property
    def has_bingo(self) -> bool:
        return self.game_state == GameState.BINGO_WIN

    @property
    def hunt_progress_percent(self) -> int:
        if not self.hunt_items:
            return 0
        return (self.hunt_progress * 100) // len(self.hunt_items)

    @property
    def is_hunt_complete(self) -> bool:
        return self.hunt_progress == len(self.hunt_items) and len(self.hunt_items) > 0

    def start_game(self) -> None:
        """Start a bingo game."""
        if self.game_mode == GameMode.SCAVENGER_HUNT:
            self.start_hunt()
        else:
            self.board = generate_board()
            self.winning_line = None
            self.game_state = GameState.BINGO_PLAYING
            self.show_bingo_modal = False

    def handle_square_click(self, square_id: int) -> None:
        if self.game_state != GameState.BINGO_PLAYING:
            return
        self.board = toggle_square(self.board, square_id)

        if self.winning_line is None:
            bingo = check_bingo(self.board)
            if bingo is not None:
                self.winning_line = bingo
                self.game_state = GameState.BINGO_WIN
                self.show_bingo_modal = True

    def start_hunt(self, item_count: int = DEFAULT_HUNT_ITEM_COUNT) -> None:
        """Start a scavenger hunt game."""
        self.hunt_item_count = item_count
        self.hunt_items = generate_hunt_board(item_count)
        self.hunt_progress = 0
        self.game_state = GameState.HUNT_PLAYING
        self.show_hunt_modal = False

    def mark_item_found(self, item_id: int) -> None:
        """Mark a hunt item as found and update progress."""
        if self.game_state != GameState.HUNT_PLAYING:
            return
        self.hunt_items = self._toggle_item(self.hunt_items, item_id)
        self.hunt_progress = sum(1 for item in self.hunt_items if item.is_found)
        if self.is_hunt_complete:
            self.game_state = GameState.HUNT_WIN
            self.show_hunt_modal = True

    @staticmethod
    def _toggle_item(items: list[HuntItemData], item_id: int) -> list[HuntItemData]:
        """Toggle an item's found state. Returns new list."""
        return [
            item.model_copy(update={"is_found": not item.is_found})
            if item.id == item_id
            else item
            for item in items
        ]

    def reset_game(self) -> None:
        self.game_state = GameState.START
        self.board = []
        self.winning_line = None
        self.show_bingo_modal = False
        self.hunt_items = []
        self.hunt_progress = 0
        self.show_hunt_modal = False

    def dismiss_modal(self) -> None:
        """Dismiss active modal and return to active game state."""
        if self.show_bingo_modal:
            self.show_bingo_modal = False
            self.game_state = GameState.BINGO_PLAYING
        elif self.show_hunt_modal:
            self.show_hunt_modal = False
            self.game_state = GameState.HUNT_PLAYING


# In-memory session store keyed by session ID
_sessions: dict[str, GameSession] = {}


def get_session(session_id: str) -> GameSession:
    """Get or create a game session for the given session ID."""
    if session_id not in _sessions:
        _sessions[session_id] = GameSession()
    return _sessions[session_id]
