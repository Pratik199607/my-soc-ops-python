import random
from typing import TypedDict

from app.data import QUESTIONS
from app.models import HuntItemData


class HuntProgress(TypedDict):
    """Hunt progress tracking data."""

    found: int
    total: int
    percent: int


def generate_hunt_board(item_count: int = 24) -> list[HuntItemData]:
    """Generate a new scavenger hunt board with shuffled questions.

    Args:
        item_count: Number of items to generate (capped to available questions)

    Returns:
        List of HuntItemData items with shuffled questions
    """
    count = min(item_count, len(QUESTIONS))
    selected_questions = random.sample(QUESTIONS, count)
    return [
        HuntItemData(id=i, text=question, is_found=False)
        for i, question in enumerate(selected_questions)
    ]


def get_hunt_progress(items: list[HuntItemData]) -> HuntProgress:
    """Calculate hunt progress as percentage and count.

    Args:
        items: List of hunt items

    Returns:
        Dict with found count, total count, and percentage completion
    """
    if not items:
        return HuntProgress(found=0, total=0, percent=0)

    found = sum(1 for item in items if item.is_found)
    total = len(items)
    percent = (found * 100) // total if total > 0 else 0

    return HuntProgress(found=found, total=total, percent=percent)
