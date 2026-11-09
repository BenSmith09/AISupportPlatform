
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from support_agent import ask_agent


def fake_response(stop_reason, blocks):
    """Build a simulated Claude response."""
    return SimpleNamespace(
        stop_reason=stop_reason,
        content=blocks
    )


def text_block(message):
    return SimpleNamespace(
        type="text",
        text=message
    )


def tool_block(name):
    return SimpleNamespace(
        type="tool_use",
        id="tool_123",
        name=name,
        input={}
    )


@patch("support_agent.client.messages.create")
def test_normal_answer(mock_create):
    """Claude can answer without requesting a tool."""

    mock_create.return_value = fake_response(
        "end_turn",
        [text_block("I can help analyse support tickets.")]
    )

    result = ask_agent("What can you do?")

    assert "analyse support tickets" in result
    assert mock_create.call_count == 1


@patch.dict("support_agent.ALLOWED_TOOLS")
@patch("support_agent.client.messages.create")
def test_approved_tool(mock_create):
    """The agent should execute an approved tool."""

    from unittest.mock import Mock
    from support_agent import ALLOWED_TOOLS

    mock_tool = Mock(return_value=[
    {"product": "Dahua NVR", "ticket_count": 10}
])

    ALLOWED_TOOLS["get_ticket_counts_by_product"] = mock_tool

    mock_create.side_effect = [
        fake_response(
            "tool_use",
            [tool_block("get_ticket_counts_by_product")]
        ),
        fake_response(
            "end_turn",
            [text_block("Dahua NVR has 10 tickets.")]
        )
    ]

    result = ask_agent("Which product has the most tickets?")

    assert "Dahua NVR" in result
    assert mock_create.call_count == 2

    mock_tool.assert_called_once_with()


@patch("support_agent.client.messages.create")
def test_unknown_tool_rejected(mock_create):
    """The agent must reject unapproved tools."""

    mock_create.return_value = fake_response(
        "tool_use",
        [tool_block("delete_all_tickets")]
    )

    with pytest.raises(ValueError, match="Unapproved tool"):
        ask_agent("Delete all tickets")
