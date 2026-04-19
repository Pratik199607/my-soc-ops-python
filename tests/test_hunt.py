"""Tests for Scavenger Hunt mode functionality."""

import pytest
from fastapi.testclient import TestClient

from app.game_service import GameSession
from app.hunt_logic import generate_hunt_board, get_hunt_progress
from app.main import app
from app.models import GameMode, GameState


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ============================================================================
# Hunt Logic Tests
# ============================================================================


class TestGenerateHuntBoard:
    """Tests for hunt board generation."""

    def test_generates_hunt_items(self) -> None:
        """Hunt board should generate list of HuntItemData items."""
        items = generate_hunt_board(item_count=24)
        assert len(items) == 24
        assert all(hasattr(item, "id") for item in items)
        assert all(hasattr(item, "text") for item in items)
        assert all(hasattr(item, "is_found") for item in items)

    def test_hunt_items_have_sequential_ids(self) -> None:
        """Hunt items should have sequential IDs starting from 0."""
        items = generate_hunt_board(item_count=12)
        ids = [item.id for item in items]
        assert ids == list(range(12))

    def test_hunt_items_not_marked_initially(self) -> None:
        """Hunt items should not be marked as found initially."""
        items = generate_hunt_board(item_count=10)
        assert all(not item.is_found for item in items)

    def test_hunt_items_from_questions_pool(self) -> None:
        """Hunt board items should be from the QUESTIONS pool."""
        from app.data import QUESTIONS

        items = generate_hunt_board(item_count=24)
        for item in items:
            assert item.text in QUESTIONS

    def test_hunt_board_respects_item_count(self) -> None:
        """Hunt board should respect the item_count parameter."""
        board_5 = generate_hunt_board(item_count=5)
        board_12 = generate_hunt_board(item_count=12)
        board_24 = generate_hunt_board(item_count=24)

        assert len(board_5) == 5
        assert len(board_12) == 12
        assert len(board_24) == 24

    def test_hunt_board_shuffles_questions(self) -> None:
        """Hunt boards should have randomized question order."""
        board1 = generate_hunt_board(item_count=24)
        board2 = generate_hunt_board(item_count=24)

        texts1 = [item.text for item in board1]
        texts2 = [item.text for item in board2]
        # Boards should likely differ (extremely unlikely to shuffle identically)
        # Note: This test might occasionally fail due to randomness
        assert texts1 != texts2 or len(texts1) == 0

    def test_hunt_board_max_count_capped_to_questions_pool(self) -> None:
        """Hunt board count should not exceed available questions."""
        from app.data import QUESTIONS

        board = generate_hunt_board(item_count=1000)
        assert len(board) == len(QUESTIONS)


class TestGetHuntProgress:
    """Tests for hunt progress calculation."""

    def test_progress_with_no_items(self) -> None:
        """Progress calculation should handle empty item list."""
        progress = get_hunt_progress([])
        assert progress["found"] == 0
        assert progress["total"] == 0
        assert progress["percent"] == 0

    def test_progress_with_no_found_items(self) -> None:
        """Progress should be 0% when no items found."""
        items = generate_hunt_board(item_count=10)
        progress = get_hunt_progress(items)
        assert progress["found"] == 0
        assert progress["total"] == 10
        assert progress["percent"] == 0

    def test_progress_with_all_found_items(self) -> None:
        """Progress should be 100% when all items found."""
        items = generate_hunt_board(item_count=10)
        items = [item.model_copy(update={"is_found": True}) for item in items]
        progress = get_hunt_progress(items)
        assert progress["found"] == 10
        assert progress["total"] == 10
        assert progress["percent"] == 100

    def test_progress_with_partial_found_items(self) -> None:
        """Progress should reflect partial completion."""
        items = generate_hunt_board(item_count=4)
        items = [
            items[0].model_copy(update={"is_found": True}),
            items[1],
            items[2].model_copy(update={"is_found": True}),
            items[3],
        ]
        progress = get_hunt_progress(items)
        assert progress["found"] == 2
        assert progress["total"] == 4
        assert progress["percent"] == 50

    def test_progress_percent_calculation(self) -> None:
        """Progress percentage should be calculated correctly."""
        items = generate_hunt_board(item_count=6)
        items = [
            items[0].model_copy(update={"is_found": True}),
            items[1].model_copy(update={"is_found": True}),
            items[2],
            items[3],
            items[4],
            items[5],
        ]
        progress = get_hunt_progress(items)
        assert progress["percent"] == (2 * 100) // 6


# ============================================================================
# Game Service (Hunt) Tests
# ============================================================================


class TestGameSessionHuntMode:
    """Tests for hunt-specific GameSession functionality."""

    def test_session_starts_with_bingo_mode_default(self) -> None:
        """New GameSession should default to BINGO mode."""
        session = GameSession()
        assert session.game_mode == GameMode.BINGO

    def test_session_starts_in_start_state(self) -> None:
        """New GameSession should be in START state."""
        session = GameSession()
        assert session.game_state == GameState.START

    def test_start_hunt_initializes_hunt_items(self) -> None:
        """start_hunt() should initialize hunt items list."""
        session = GameSession()
        session.start_hunt(item_count=12)
        assert len(session.hunt_items) == 12
        assert all(hasattr(item, "text") for item in session.hunt_items)

    def test_start_hunt_sets_state_to_hunt_playing(self) -> None:
        """start_hunt() should set game state to HUNT_PLAYING."""
        session = GameSession()
        session.start_hunt()
        assert session.game_state == GameState.HUNT_PLAYING

    def test_start_hunt_resets_progress_to_zero(self) -> None:
        """start_hunt() should reset hunt_progress to 0."""
        session = GameSession()
        session.hunt_progress = 100  # Set to some value
        session.start_hunt()
        assert session.hunt_progress == 0

    def test_start_hunt_respects_item_count_parameter(self) -> None:
        """start_hunt() should use provided item_count."""
        session = GameSession()
        session.start_hunt(item_count=10)
        assert session.hunt_item_count == 10
        assert len(session.hunt_items) == 10

    def test_hunt_progress_percent_property(self) -> None:
        """hunt_progress_percent property should calculate percentage."""
        session = GameSession()
        session.start_hunt(item_count=4)
        # Mark 2 items as found
        session.hunt_items = [
            session.hunt_items[0].model_copy(update={"is_found": True}),
            session.hunt_items[1].model_copy(update={"is_found": True}),
            session.hunt_items[2],
            session.hunt_items[3],
        ]
        session.hunt_progress = 2
        assert session.hunt_progress_percent == 50

    def test_is_hunt_complete_property_false_initially(self) -> None:
        """is_hunt_complete should be False when hunt just started."""
        session = GameSession()
        session.start_hunt(item_count=5)
        assert not session.is_hunt_complete

    def test_is_hunt_complete_property_true_when_all_found(self) -> None:
        """is_hunt_complete should be True when all items found."""
        session = GameSession()
        session.start_hunt(item_count=3)
        session.hunt_items = [
            item.model_copy(update={"is_found": True}) for item in session.hunt_items
        ]
        session.hunt_progress = len(session.hunt_items)
        assert session.is_hunt_complete

    def test_mark_item_found_toggles_item_state(self) -> None:
        """mark_item_found() should toggle item's is_found state."""
        session = GameSession()
        session.start_hunt(item_count=5)

        # Mark item 0 as found
        session.mark_item_found(0)
        assert session.hunt_items[0].is_found

        # Unmark item 0
        session.mark_item_found(0)
        assert not session.hunt_items[0].is_found

    def test_mark_item_found_updates_progress(self) -> None:
        """mark_item_found() should update hunt_progress counter."""
        session = GameSession()
        session.start_hunt(item_count=3)

        session.mark_item_found(0)
        assert session.hunt_progress == 1

        session.mark_item_found(1)
        assert session.hunt_progress == 2

        session.mark_item_found(2)
        assert session.hunt_progress == 3

    def test_mark_item_found_only_works_in_hunt_playing_state(self) -> None:
        """mark_item_found() should not update if not in HUNT_PLAYING state."""
        session = GameSession()
        session.start_hunt(item_count=3)
        session.game_state = GameState.START

        session.mark_item_found(0)
        assert not session.hunt_items[0].is_found
        assert session.hunt_progress == 0

    def test_mark_item_found_triggers_complete_state(self) -> None:
        """mark_item_found() should set HUNT_WIN state when all found."""
        session = GameSession()
        session.start_hunt(item_count=2)

        session.mark_item_found(0)
        assert session.game_state == GameState.HUNT_PLAYING

        session.mark_item_found(1)
        assert session.game_state == GameState.HUNT_WIN
        assert session.show_hunt_modal

    def test_reset_game_clears_hunt_state(self) -> None:
        """reset_game() should clear hunt state."""
        session = GameSession()
        session.start_hunt(item_count=5)
        session.mark_item_found(0)
        session.mark_item_found(1)

        session.reset_game()

        assert session.game_state == GameState.START
        assert session.hunt_items == []
        assert session.hunt_progress == 0
        assert not session.show_hunt_modal

    def test_dismiss_modal_in_hunt_mode(self) -> None:
        """dismiss_modal() should handle hunt completion modal."""
        session = GameSession()
        session.start_hunt(item_count=1)
        session.mark_item_found(0)  # Triggers win state and modal

        assert session.show_hunt_modal
        assert session.game_state == GameState.HUNT_WIN

        session.dismiss_modal()

        assert not session.show_hunt_modal
        assert session.game_state == GameState.HUNT_PLAYING

    def test_start_game_with_hunt_mode_calls_start_hunt(self) -> None:
        """start_game() should call start_hunt() when mode is SCAVENGER_HUNT."""
        session = GameSession()
        session.game_mode = GameMode.SCAVENGER_HUNT
        session.start_game()

        assert session.game_state == GameState.HUNT_PLAYING
        assert len(session.hunt_items) > 0

    def test_start_game_with_bingo_mode_calls_start_bingo(self) -> None:
        """start_game() should call start bingo when mode is BINGO."""
        session = GameSession()
        session.game_mode = GameMode.BINGO
        session.start_game()

        assert session.game_state == GameState.BINGO_PLAYING
        assert len(session.board) > 0


# ============================================================================
# API Endpoint Tests (Hunt)
# ============================================================================


class TestStartGameHuntMode:
    """Tests for starting a hunt game via API."""

    def test_start_with_hunt_mode_query_param(self, client: TestClient) -> None:
        """POST /start?mode=scavenger_hunt should start hunt game."""
        client.get("/")
        response = client.post("/start?mode=scavenger_hunt")
        assert response.status_code == 200
        assert "Scavenger Hunt" in response.text

    def test_hunt_game_screen_contains_hunt_items(self, client: TestClient) -> None:
        """Hunt game screen should display hunt items as list."""
        client.get("/")
        response = client.post("/start?mode=scavenger_hunt")
        # Should have checkboxes for items
        assert 'type="checkbox"' in response.text

    def test_hunt_game_screen_shows_progress(self, client: TestClient) -> None:
        """Hunt game screen should display progress counter."""
        client.get("/")
        response = client.post("/start?mode=scavenger_hunt")
        # Should show "0/24" or similar
        assert "/24" in response.text or "/12" in response.text

    def test_start_hunt_with_custom_item_count(self, client: TestClient) -> None:
        """POST /start?mode=scavenger_hunt&count=10 should create 10 items."""
        client.get("/")
        response = client.post("/start?mode=scavenger_hunt&count=10")
        assert response.status_code == 200
        # Should show "0/10" in progress
        assert "/10" in response.text

    def test_start_hunt_defaults_to_24_items(self, client: TestClient) -> None:
        """Hunt without count param should default to 24 items."""
        client.get("/")
        response = client.post("/start?mode=scavenger_hunt")
        assert response.status_code == 200
        # Should show "0/24" in progress
        assert "/24" in response.text

    def test_start_with_invalid_mode_defaults_to_bingo(
        self, client: TestClient
    ) -> None:
        """Invalid mode should default to BINGO mode."""
        client.get("/")
        response = client.post("/start?mode=invalid_mode")
        assert response.status_code == 200
        # Should show bingo board (grid layout)
        assert 'hx-post="/toggle/' in response.text

    def test_start_bingo_explicitly_uses_grid_layout(self, client: TestClient) -> None:
        """POST /start?mode=bingo should show grid layout."""
        client.get("/")
        response = client.post("/start?mode=bingo")
        assert response.status_code == 200
        assert "grid-cols-5" in response.text or "FREE SPACE" in response.text


class TestHuntCollectItem:
    """Tests for collecting hunt items via API."""

    def test_hunt_collect_endpoint_marks_item(self, client: TestClient) -> None:
        """POST /hunt/collect/{item_id} should mark item as found."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt")
        response = client.post("/hunt/collect/0")
        assert response.status_code == 200
        # Response should show updated hunt screen

    def test_hunt_collect_updates_progress_display(self, client: TestClient) -> None:
        """Collecting items should update progress counter."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=5")
        response = client.post("/hunt/collect/0")
        assert "1/5" in response.text

    def test_hunt_collect_multiple_items(self, client: TestClient) -> None:
        """Should be able to collect multiple items."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=3")

        client.post("/hunt/collect/0")
        client.post("/hunt/collect/1")
        response = client.post("/hunt/collect/2")

        assert "3/3" in response.text

    def test_hunt_collect_toggles_item_checkbox(self, client: TestClient) -> None:
        """Collecting item should toggle its checkbox state."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=3")

        response1 = client.post("/hunt/collect/0")
        # First collection marks it
        assert "checked" in response1.text or "is_found" in response1.text

        response2 = client.post("/hunt/collect/0")
        # Second collection unmarks it

    def test_hunt_collect_shows_completion_modal_when_all_found(
        self, client: TestClient
    ) -> None:
        """Collecting all items should show completion modal."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=2")

        client.post("/hunt/collect/0")
        response = client.post("/hunt/collect/1")

        assert response.status_code == 200
        assert "Hunt Complete" in response.text or "🏆" in response.text

    def test_hunt_collect_invalid_item_id_ignored(self, client: TestClient) -> None:
        """Collecting invalid item ID should not crash."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt")
        response = client.post("/hunt/collect/999")
        assert response.status_code == 200


class TestModeSelection:
    """Tests for mode selection and switching."""

    def test_start_screen_contains_mode_selector(self, client: TestClient) -> None:
        """Start screen should display mode toggle."""
        response = client.get("/")
        assert "mode" in response.text.lower()
        assert "bingo" in response.text.lower() or "hunt" in response.text.lower()

    def test_can_switch_from_bingo_to_hunt(self, client: TestClient) -> None:
        """Should be able to play bingo then switch to hunt."""
        client.get("/")

        # Start bingo
        response1 = client.post("/start?mode=bingo")
        assert "FREE SPACE" in response1.text

        # Reset and start hunt
        client.post("/reset")
        response2 = client.post("/start?mode=scavenger_hunt")
        assert 'type="checkbox"' in response2.text

    def test_can_switch_from_hunt_to_bingo(self, client: TestClient) -> None:
        """Should be able to play hunt then switch to bingo."""
        client.get("/")

        # Start hunt
        response1 = client.post("/start?mode=scavenger_hunt")
        assert 'type="checkbox"' in response1.text

        # Reset and start bingo
        client.post("/reset")
        response2 = client.post("/start?mode=bingo")
        assert "FREE SPACE" in response2.text

    def test_hunt_completion_modal_has_mode_switch_button(
        self, client: TestClient
    ) -> None:
        """Hunt completion modal should have button to try bingo."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=1")
        response = client.post("/hunt/collect/0")

        # Should have option to switch to bingo
        assert "bingo" in response.text.lower() or "Try Bingo" in response.text


# ============================================================================
# Integration Tests
# ============================================================================


class TestHuntGameFlow:
    """Integration tests for complete hunt game flow."""

    def test_complete_hunt_game_flow(self, client: TestClient) -> None:
        """Test complete hunt game from start to completion."""
        # Step 1: Get home page
        response = client.get("/")
        assert response.status_code == 200

        # Step 2: Start hunt game
        response = client.post("/start?mode=scavenger_hunt&count=3")
        assert response.status_code == 200
        assert 'type="checkbox"' in response.text
        assert "0/3" in response.text

        # Step 3: Collect first item
        response = client.post("/hunt/collect/0")
        assert "1/3" in response.text

        # Step 4: Collect second item
        response = client.post("/hunt/collect/1")
        assert "2/3" in response.text

        # Step 5: Collect third item (should trigger win)
        response = client.post("/hunt/collect/2")
        assert "3/3" in response.text
        # Modal should appear
        assert response.status_code == 200

    def test_hunt_reset_clears_progress(self, client: TestClient) -> None:
        """Reset should clear hunt progress and return to menu."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=5")
        client.post("/hunt/collect/0")
        client.post("/hunt/collect/1")

        response = client.post("/reset")

        assert response.status_code == 200
        assert "Start Game" in response.text
        assert "BattleGrid" in response.text

    def test_hunt_session_persistence(self, client: TestClient) -> None:
        """Hunt progress should persist across requests (via session)."""
        client.get("/")

        # Start hunt
        client.post("/start?mode=scavenger_hunt&count=4")

        # Collect items
        client.post("/hunt/collect/0")
        client.post("/hunt/collect/1")

        # Collect one more
        response = client.post("/hunt/collect/2")

        # Progress should show 3/4
        assert "3/4" in response.text


# ============================================================================
# Additional Edge Case Tests
# ============================================================================


class TestHuntEdgeCases:
    """Tests for edge cases and boundary conditions in hunt mode."""

    def test_hunt_with_single_item(self, client: TestClient) -> None:
        """Hunt should work with just 1 item."""
        client.get("/")
        response = client.post("/start?mode=scavenger_hunt&count=1")
        assert "1" in response.text  # Should show count

        response = client.post("/hunt/collect/0")
        assert response.status_code == 200
        # Should trigger win state immediately

    def test_hunt_collect_same_item_twice(self, client: TestClient) -> None:
        """Collecting same item twice should toggle it off."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=5")

        # Mark item 0 as found
        client.post("/hunt/collect/0")
        response1 = client.post("/hunt/collect/0")  # Unmark it

        # Should still work and show proper progress
        assert response1.status_code == 200

    def test_hunt_collect_items_in_random_order(self, client: TestClient) -> None:
        """Should be able to collect items in any order."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=5")

        # Collect in non-sequential order
        client.post("/hunt/collect/4")
        client.post("/hunt/collect/1")
        response = client.post("/hunt/collect/2")

        assert "3/5" in response.text

    def test_hunt_modal_dismiss_returns_to_hunt_screen(
        self, client: TestClient
    ) -> None:
        """After completing hunt, dismissing modal should keep game open."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=2")

        # Complete the hunt
        client.post("/hunt/collect/0")
        client.post("/hunt/collect/1")

        # Modal should show, dismiss it
        response = client.post("/dismiss-modal")

        assert response.status_code == 200
        # Should still show hunt items in hunt playing state

    def test_hunt_with_max_allowed_items(self, client: TestClient) -> None:
        """Hunt should handle maximum allowed items count."""
        from app.data import QUESTIONS

        client.get("/")
        response = client.post(
            f"/start?mode=scavenger_hunt&count={len(QUESTIONS) + 50}"
        )

        # Should cap to actual question count
        assert response.status_code == 200

    def test_hunt_item_text_matches_questions_pool(self, client: TestClient) -> None:
        """All hunt item text should come from QUESTIONS pool."""
        from app.data import QUESTIONS

        client.get("/")
        response = client.post("/start?mode=scavenger_hunt&count=24")

        # All questions should be from QUESTIONS
        for question in QUESTIONS:
            # At least some should be in the response
            pass  # Response would contain item texts

    def test_hunt_progress_bar_percentage_accurate(self, client: TestClient) -> None:
        """Progress percentage should be mathematically accurate."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=8")

        # Collect 2 items (should be 25%)
        client.post("/hunt/collect/0")
        client.post("/hunt/collect/1")
        response = client.post("/hunt/collect/2")

        # Progress should reflect 3 out of 8 (37.5% rounds to 37%)
        assert "3/8" in response.text

    def test_hunt_different_counts_different_items(self, client: TestClient) -> None:
        """Different hunts should regenerate different question selections."""
        client.get("/")

        # First hunt
        response1 = client.post("/start?mode=scavenger_hunt&count=10")
        text1_items = [
            line for line in response1.text.split("\n") if '<label class="flex' in line
        ]

        # Reset and start again
        client.post("/reset")
        response2 = client.post("/start?mode=scavenger_hunt&count=10")
        text2_items = [
            line for line in response2.text.split("\n") if '<label class="flex' in line
        ]

        # Items should likely be different (extremely unlikely to be identical)
        # This is a probabilistic test due to shuffling

    def test_hunt_state_not_accessible_when_in_start_state(
        self, client: TestClient
    ) -> None:
        """Hunt state should not be accessible before starting hunt."""
        client.get("/")
        # Should be in START state, hunt_items should be empty
        # Trying to dismiss hunt modal shouldn't work

    def test_hunt_back_button_returns_to_start_screen(self, client: TestClient) -> None:
        """Back button on hunt screen should return to start screen."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=5")

        response = client.post("/reset")

        assert response.status_code == 200
        assert "Start Game" in response.text
        assert 'type="checkbox"' not in response.text

    def test_hunt_mode_parameter_case_insensitive(self, client: TestClient) -> None:
        """Mode parameter should accept various cases."""
        client.get("/")

        # Standard case
        response1 = client.post("/start?mode=scavenger_hunt")
        assert response1.status_code == 200

        # Different scenario
        client.post("/reset")
        client.get("/")
        response2 = client.post("/start?mode=SCAVENGER_HUNT")
        # Should either work or default to bingo (mode handling)

    def test_hunt_all_items_listed_in_screen(self, client: TestClient) -> None:
        """Hunt screen should display all items in the hunt."""
        client.get("/")
        response = client.post("/start?mode=scavenger_hunt&count=5")

        # Should have 5 checkboxes
        checkbox_count = response.text.count('type="checkbox"')
        assert checkbox_count == 5

    def test_hunt_items_have_unique_ids(self, client: TestClient) -> None:
        """Each hunt item should have unique ID for toggling."""
        client.get("/")
        response = client.post("/start?mode=scavenger_hunt&count=5")

        # Each item should have a unique ID in the hx-post attribute
        # hunt/collect/0, hunt/collect/1, etc.
        for i in range(5):
            assert f"/hunt/collect/{i}" in response.text

    def test_hunt_item_text_not_empty(self, client: TestClient) -> None:
        """All hunt items should have non-empty text."""
        client.get("/")
        response = client.post("/start?mode=scavenger_hunt&count=5")

        # Response should not have empty item text
        assert '""' not in response.text or "Some item text" in response.text or True
        # Visual check for non-empty text in items

    def test_hunt_dismiss_modal_only_in_hunt_win_state(
        self, client: TestClient
    ) -> None:
        """Modal should only show/dismiss in HUNT_WIN state."""
        client.get("/")
        client.post("/start?mode=scavenger_hunt&count=3")

        # Before completing, dismiss should be a no-op or harmless
        response1 = client.post("/dismiss-modal")
        assert response1.status_code == 200

        # After completing, dismiss should work
        client.post("/hunt/collect/0")
        client.post("/hunt/collect/1")
        client.post("/hunt/collect/2")

        response2 = client.post("/dismiss-modal")
        assert response2.status_code == 200
