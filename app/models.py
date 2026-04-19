from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict


class GameState(StrEnum):
    START = "start"
    BINGO_PLAYING = "bingo_playing"
    BINGO_WIN = "bingo_win"
    HUNT_PLAYING = "hunt_playing"
    HUNT_WIN = "hunt_win"
    CARD_PLAYING = "card_playing"
    CARD_WIN = "card_win"


class GameMode(StrEnum):
    BINGO = "bingo"
    SCAVENGER_HUNT = "scavenger_hunt"
    CARD_DECK = "card_deck"


class BingoSquareData(BaseModel):
    """A single square on the bingo board."""

    model_config = ConfigDict(frozen=True)

    id: int
    text: str
    is_marked: bool = False
    is_free_space: bool = False


class BingoLine(BaseModel):
    """A winning line (row, column, or diagonal) on the board."""

    model_config = ConfigDict(frozen=True)

    type: Literal["row", "column", "diagonal"] = "row"
    index: int = 0
    squares: list[int] = []


class HuntItemData(BaseModel):
    """A single item on the scavenger hunt list."""

    model_config = ConfigDict(frozen=True)

    id: int
    text: str
    is_found: bool = False


class CardData(BaseModel):
    """A single card in the card deck."""

    model_config = ConfigDict(frozen=True)

    id: int
    text: str
    hint: str = ""
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    is_found: bool = False
