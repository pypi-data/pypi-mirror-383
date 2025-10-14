import unittest
from dataclasses import dataclass
from unittest.mock import patch, MagicMock
import sys
import os

from ai_six.object_model import Message

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from ai_six.llm_providers.openai_provider import OpenAIProvider


class TestOpenAIProvider(unittest.TestCase):

    def setUp(self):
        # Initialize OpenAIProvider with a mock API key
        self.provider = OpenAIProvider(api_key="mock-api-key")
        # Replace the client with a mock
        self.provider.client = MagicMock()

    def test_usage_extraction(self):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Mock content"
        mock_response.choices[0].message.role = "assistant"
        mock_response.choices[0].message.tool_calls = []
        mock_response.usage = MagicMock(prompt_tokens=12, completion_tokens=8)

        mock_message = Message('some message', 'user')

        self.provider.client.chat.completions.create.return_value = mock_response

        # Test sending messages
        response = self.provider.send(messages=[mock_message], tool_dict={})

        # Check the usage was set correctly
        self.assertEqual(response.usage.input_tokens, 12)
        self.assertEqual(response.usage.output_tokens, 8)


if __name__ == "__main__":
    unittest.main()
