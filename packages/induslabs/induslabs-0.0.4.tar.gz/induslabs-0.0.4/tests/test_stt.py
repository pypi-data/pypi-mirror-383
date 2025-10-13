"""
Unit tests for STT functionality
"""

import pytest
import asyncio
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock, mock_open
from induslabs import Client, STTResponse


@pytest.fixture
def client():
    """Create a test client"""
    return Client(api_key="test_key")


@pytest.fixture
def mock_stt_response():
    """Create a mock STT response"""
    return {
        "request_id": "stt-test-123",
        "text": "यह एक परीक्षण है",
        "language_detected": "hi",
        "audio_duration_seconds": 5.5,
        "processing_time_seconds": 1.2,
        "first_token_time_seconds": 0.05,
        "credits_used": 0.2,
    }


class TestSTTBasic:
    """Test basic STT functionality"""

    @patch("requests.post")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_audio")
    def test_basic_stt_from_file(self, mock_file, mock_post, client, mock_stt_response):
        """Test basic STT from file path"""
        mock_response = Mock()
        mock_response.json.return_value = mock_stt_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = client.stt.transcribe(file="test.wav", language="hi")

        assert isinstance(result, STTResponse)
        assert result.text == "यह एक परीक्षण है"
        assert result.language_detected == "hi"
        assert result.request_id == "stt-test-123"
        assert result.audio_duration_seconds == 5.5
        assert result.processing_time_seconds == 1.2
        assert result.credits_used == 0.2

        # Verify API call
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert "files" in call_kwargs
        assert "data" in call_kwargs
        assert call_kwargs["data"]["language"] == "hi"

    @patch("requests.post")
    def test_stt_from_file_object(self, mock_post, client, mock_stt_response):
        """Test STT from file-like object"""
        mock_response = Mock()
        mock_response.json.return_value = mock_stt_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        file_obj = BytesIO(b"fake_audio_data")
        result = client.stt.transcribe(file=file_obj, language="hi")

        assert isinstance(result, STTResponse)
        assert result.text == "यह एक परीक्षण है"

    @patch("requests.post")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_audio")
    def test_stt_default_parameters(self, mock_file, mock_post, client, mock_stt_response):
        """Test STT with default parameters"""
        mock_response = Mock()
        mock_response.json.return_value = mock_stt_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = client.stt.transcribe(file="test.wav")

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["data"]["chunk_length_s"] == 6
        assert call_kwargs["data"]["stride_s"] == 5.9
        assert call_kwargs["data"]["overlap_words"] == 7

    @patch("requests.post")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_audio")
    def test_stt_custom_parameters(self, mock_file, mock_post, client, mock_stt_response):
        """Test STT with custom parameters"""
        mock_response = Mock()
        mock_response.json.return_value = mock_stt_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = client.stt.transcribe(
            file="test.wav", language="en", chunk_length_s=10, stride_s=9.5, overlap_words=5
        )

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["data"]["language"] == "en"
        assert call_kwargs["data"]["chunk_length_s"] == 10
        assert call_kwargs["data"]["stride_s"] == 9.5
        assert call_kwargs["data"]["overlap_words"] == 5


class TestSTTResponse:
    """Test STTResponse object"""

    def test_response_properties(self, mock_stt_response):
        """Test response properties"""
        result = STTResponse(mock_stt_response)

        assert result.request_id == "stt-test-123"
        assert result.text == "यह एक परीक्षण है"
        assert result.language_detected == "hi"
        assert result.audio_duration_seconds == 5.5
        assert result.processing_time_seconds == 1.2
        assert result.first_token_time_seconds == 0.05
        assert result.credits_used == 0.2

    def test_str_representation(self, mock_stt_response):
        """Test string representation"""
        result = STTResponse(mock_stt_response)
        assert str(result) == "यह एक परीक्षण है"

    def test_repr_representation(self, mock_stt_response):
        """Test repr representation"""
        result = STTResponse(mock_stt_response)
        repr_str = repr(result)
        assert "STTResponse" in repr_str
        assert "hi" in repr_str

    def test_to_dict(self, mock_stt_response):
        """Test converting to dictionary"""
        result = STTResponse(mock_stt_response)
        result_dict = result.to_dict()

        assert result_dict == mock_stt_response
        assert result_dict["text"] == "यह एक परीक्षण है"


class TestSTTAsync:
    """Test async STT functionality"""

    @pytest.mark.asyncio
    async def test_async_stt(self, client, mock_stt_response):
        """Test async STT"""
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = MagicMock()

            async def mock_json():
                return mock_stt_response

            mock_response.json = mock_json
            mock_response.raise_for_status = Mock()

            mock_post.return_value.__aenter__.return_value = mock_response

            with patch("builtins.open", mock_open(read_data=b"fake_audio")):
                result = await client.stt.transcribe_async(file="test.wav", language="hi")

            assert isinstance(result, STTResponse)
            assert result.text == "यह एक परीक्षण है"

            await client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
