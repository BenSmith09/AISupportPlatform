
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from classify_ticket import classify_ticket


@patch("classify_ticket.client.messages.create")
def test_valid_classification(mock_create):
    mock_response = Mock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [
        Mock(
            type="text",
            text='{"category":"Networking",'
                 '"likely_cause":"IP conflict",'
                 '"recommended_action":"Check IP settings",'
                 '"confidence":0.9}'
        )
    ]

    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50
    mock_create.return_value = mock_response

    result = classify_ticket("NVR cameras offline")

    assert result["category"] == "Networking"
    assert result["confidence"] == 0.9


@patch("classify_ticket.client.messages.create")
def test_invalid_category(mock_create):
    mock_response = Mock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [
        Mock(
            type="text",
            text='{"category":"Incorrect",'
                 '"likely_cause":"Unknown",'
                 '"recommended_action":"Check device",'
                 '"confidence":0.5}'
        )
    ]

    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50
    mock_create.return_value = mock_response

    with pytest.raises(ValueError, match="Invalid category"):
        classify_ticket("Test ticket")
