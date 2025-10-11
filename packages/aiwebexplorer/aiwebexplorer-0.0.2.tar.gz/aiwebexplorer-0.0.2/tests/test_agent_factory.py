"""Tests for agent factory and model provider logic."""

import os
from unittest.mock import Mock, patch

import pytest

from aiwebexplorer.agent_factory import _get_api_key, _get_model, get_agent


class TestGetApiKey:
    """Test API key retrieval functionality."""

    @patch.dict(os.environ, {"OPENAI_APIKEY": "test-openai-key"}, clear=True)
    def test_get_api_key_openai_available(self):
        """Test getting OpenAI API key when available."""
        api_key, provider = _get_api_key()
        assert api_key == "test-openai-key"
        assert provider == "openai"

    @patch("dotenv.load_dotenv")
    @patch.dict(os.environ, {"TOGETHERAI_APIKEY": "test-together-key"}, clear=True)
    def test_get_api_key_togetherai_available(self, mock_load_dotenv):
        """Test getting TogetherAI API key when available."""
        api_key, provider = _get_api_key()
        assert api_key == "test-together-key"
        assert provider == "togetherai"

    @patch("dotenv.load_dotenv")
    @patch.dict(os.environ, {"DEEPSEEK_APIKEY": "test-deepseek-key"}, clear=True)
    def test_get_api_key_deepseek_available(self, mock_load_dotenv):
        """Test getting DeepSeek API key when available."""
        api_key, provider = _get_api_key()
        assert api_key == "test-deepseek-key"
        assert provider == "deepseek"

    @patch("dotenv.load_dotenv")
    @patch.dict(
        os.environ,
        {
            "OPENAI_APIKEY": "test-openai-key",
            "TOGETHERAI_APIKEY": "test-together-key",
            "DEEPSEEK_APIKEY": "test-deepseek-key",
        },
        clear=True,
    )
    def test_get_api_key_priority_order(self, mock_load_dotenv):
        """Test API key priority order (OpenAI > TogetherAI > DeepSeek)."""
        api_key, provider = _get_api_key()
        assert api_key == "test-openai-key"
        assert provider == "openai"

    @patch("dotenv.load_dotenv")
    @patch.dict(os.environ, {"DEEPSEEK_APIKEY": "test-deepseek-key"}, clear=True)
    def test_get_api_key_specific_provider(self, mock_load_dotenv):
        """Test getting API key for specific provider."""
        api_key, provider = _get_api_key("deepseek")
        assert api_key == "test-deepseek-key"
        assert provider == "deepseek"

    @patch("dotenv.load_dotenv")
    @patch.dict(os.environ, {"OPENAI_APIKEY": "test-openai-key"}, clear=True)
    def test_get_api_key_specific_provider_missing(self, mock_load_dotenv):
        """Test getting API key for specific provider when key is missing."""
        with pytest.raises(ValueError, match="Expected DEEPSEEK_APIKEY to be set when requesting provider deepseek"):
            _get_api_key("deepseek")

    @patch("dotenv.load_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_no_keys_available(self, mock_load_dotenv):
        """Test getting API key when no keys are available."""
        with pytest.raises(ValueError, match="No api key found for any provider"):
            _get_api_key()


class TestGetModel:
    """Test model creation functionality."""

    @patch("aiwebexplorer.agent_factory.OpenAIChat")
    def test_get_model_openai(self, mock_openai):
        """Test creating OpenAI model."""
        mock_model = Mock()
        mock_openai.return_value = mock_model

        result = _get_model(model_id="gpt-4", provider="openai", api_key="test-key")

        mock_openai.assert_called_once_with(id="gpt-4", api_key="test-key")
        assert result == mock_model

    @patch("aiwebexplorer.agent_factory.Together")
    def test_get_model_togetherai(self, mock_together):
        """Test creating TogetherAI model."""
        mock_model = Mock()
        mock_together.return_value = mock_model

        result = _get_model(model_id="openai/gpt-oss-20b", provider="togetherai", api_key="test-key")

        mock_together.assert_called_once_with(id="openai/gpt-oss-20b", api_key="test-key")
        assert result == mock_model

    @patch("aiwebexplorer.agent_factory.DeepSeek")
    def test_get_model_deepseek(self, mock_deepseek):
        """Test creating DeepSeek model."""
        mock_model = Mock()
        mock_deepseek.return_value = mock_model

        result = _get_model(model_id="chat", provider="deepseek", api_key="test-key")

        mock_deepseek.assert_called_once_with(id="chat", api_key="test-key")
        assert result == mock_model

    def test_get_model_invalid_provider(self):
        """Test creating model with invalid provider."""
        with pytest.raises(ValueError, match="Invalid provider: invalid"):
            _get_model(model_id="test-model", provider="invalid", api_key="test-key")

    @patch("aiwebexplorer.agent_factory._get_api_key")
    @patch("aiwebexplorer.agent_factory.OpenAIChat")
    def test_get_model_auto_api_key(self, mock_openai, mock_get_api_key):
        """Test model creation with automatic API key retrieval."""
        mock_get_api_key.return_value = ("test-key", "openai")
        mock_model = Mock()
        mock_openai.return_value = mock_model

        result = _get_model(model_id="gpt-4")

        mock_get_api_key.assert_called_once_with(None)
        mock_openai.assert_called_once_with(id="gpt-4", api_key="test-key")
        assert result == mock_model

    @patch("aiwebexplorer.agent_factory._get_api_key")
    @patch("aiwebexplorer.agent_factory.OpenAIChat")
    def test_get_model_with_model_id_map(self, mock_openai, mock_get_api_key):
        """Test model creation with model ID map."""
        mock_get_api_key.return_value = ("test-key", "openai")
        mock_model = Mock()
        mock_openai.return_value = mock_model

        model_id_map = {"openai": "gpt-4"}
        result = _get_model(model_id_map=model_id_map)

        mock_openai.assert_called_once_with(id="gpt-4", api_key="test-key")
        assert result == mock_model

    @patch.dict(os.environ, {"OPENAI_APIKEY": "test-key"}, clear=True)
    def test_get_model_missing_model_id_map(self):
        """Test model creation without model ID map."""
        with pytest.raises(ValueError, match="You didn't provide a model id or a model id map"):
            _get_model()


class TestGetAgent:
    """Test agent creation functionality."""

    @patch("aiwebexplorer.agent_factory._get_model")
    @patch("aiwebexplorer.agent_factory.Agent")
    def test_get_agent_basic(self, mock_agent_class, mock_get_model):
        """Test basic agent creation."""
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        instructions = ["Test instruction"]
        result = get_agent("test-agent", instructions)

        mock_get_model.assert_called_once()
        mock_agent_class.assert_called_once_with(name="test-agent", instructions=instructions, model=mock_model)
        assert result == mock_agent

    @patch("aiwebexplorer.agent_factory._get_model")
    @patch("aiwebexplorer.agent_factory.Agent")
    def test_get_agent_with_model_id_map(self, mock_agent_class, mock_get_model):
        """Test agent creation with model ID map."""
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        instructions = ["Test instruction"]
        model_id_map = {"openai": "gpt-4"}
        result = get_agent("test-agent", instructions, model_id_map=model_id_map)

        mock_get_model.assert_called_once_with(None, None, None, model_id_map)
        assert result == mock_agent

    @patch("aiwebexplorer.agent_factory._get_model")
    @patch("aiwebexplorer.agent_factory.Agent")
    def test_get_agent_with_specific_provider(self, mock_agent_class, mock_get_model):
        """Test agent creation with specific provider."""
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        instructions = ["Test instruction"]
        result = get_agent("test-agent", instructions, provider="openai", api_key="test-key")

        mock_get_model.assert_called_once_with(None, "openai", "test-key", None)
        assert result == mock_agent

    @patch("aiwebexplorer.agent_factory._get_model")
    @patch("aiwebexplorer.agent_factory.Agent")
    def test_get_agent_with_kwargs(self, mock_agent_class, mock_get_model):
        """Test agent creation with additional kwargs."""
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        instructions = ["Test instruction"]
        result = get_agent("test-agent", instructions, temperature=0.7, max_tokens=100)

        mock_agent_class.assert_called_once_with(
            name="test-agent", instructions=instructions, model=mock_model, temperature=0.7, max_tokens=100
        )
        assert result == mock_agent

    def test_get_agent_interface_compliance(self):
        """Test that created agent implements IAgent interface."""
        with (
            patch("aiwebexplorer.agent_factory._get_model") as mock_get_model,
            patch("aiwebexplorer.agent_factory.Agent") as mock_agent_class,
        ):
            mock_model = Mock()
            mock_get_model.return_value = mock_model
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            instructions = ["Test instruction"]
            result = get_agent("test-agent", instructions)

            # Verify the agent has the required interface
            assert hasattr(result, "arun")
            assert callable(result.arun)
