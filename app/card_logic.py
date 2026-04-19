import random
from typing import Literal

from app.data import QUESTIONS
from app.models import CardData


def generate_card_deck(deck_size: int = 24) -> list[CardData]:
    """Generate a shuffled card deck with difficulty levels.
    
    Args:
        deck_size: Number of cards in the deck (max = len(QUESTIONS))
    
    Returns:
        List of CardData objects with random questions and difficulties.
    """
    size = min(deck_size, len(QUESTIONS))
    selected_questions = random.sample(QUESTIONS, size)
    difficulties: list[Literal["easy", "medium", "hard"]] = ["easy", "medium", "hard"]

    return [
        CardData(
            id=i,
            text=question,
            difficulty=random.choice(difficulties),
            is_found=False,
        )
        for i, question in enumerate(selected_questions)
    ]


def get_card_by_index(cards: list[CardData], index: int) -> CardData | None:
    """Get a card by its index in the deck.
    
    Args:
        cards: List of CardData objects
        index: Index of the card (0-based)
    
    Returns:
        CardData if index is valid, None otherwise.
    """
    if 0 <= index < len(cards):
        return cards[index]
    return None


def mark_card_found(cards: list[CardData], card_id: int) -> list[CardData]:
    """Mark a card as found by updating the list.
    
    Args:
        cards: List of CardData objects
        card_id: ID of the card to mark
    
    Returns:
        New list with the card marked/unmarked.
    """
    return [
        card.model_copy(update={"is_found": not card.is_found})
        if card.id == card_id
        else card
        for card in cards
    ]


def get_cards_found_count(cards: list[CardData]) -> int:
    """Count how many cards have been found.
    
    Args:
        cards: List of CardData objects
    
    Returns:
        Number of cards marked as found.
    """
    return sum(1 for card in cards if card.is_found)


def get_card_progress(cards: list[CardData], target: int = 10) -> dict:
    """Calculate card collection progress.
    
    Args:
        cards: List of CardData objects
        target: Target number of cards to find
    
    Returns:
        Dict with found, target, and percent.
    """
    found = get_cards_found_count(cards)
    return {
        "found": found,
        "target": target,
        "percent": (found * 100) // target if target > 0 else 0,
    }


def get_difficulty_color(difficulty: str) -> str:
    """Get CSS color class for difficulty level.
    
    Args:
        difficulty: Difficulty level (easy, medium, hard)
    
    Returns:
        CSS class name for styling.
    """
    colors = {
        "easy": "text-green-600",
        "medium": "text-yellow-600",
        "hard": "text-red-600",
    }
    return colors.get(difficulty, "text-gray-600")
