import json
import os
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from openinference.semconv.trace import OpenInferenceSpanKindValues

from grafi.assistants.assistant import Assistant
from grafi.common.events.topic_events.consume_from_topic_event import (
    ConsumeFromTopicEvent,
)
from grafi.common.events.topic_events.publish_to_topic_event import PublishToTopicEvent
from grafi.common.models.invoke_context import InvokeContext
from grafi.common.models.message import Message
from grafi.topics.topic_types import TopicType
from grafi.workflows.workflow import Workflow


class TestAssistant:
    @pytest.fixture
    def invoke_context(self):
        """Fixture providing a mock InvokeContext."""
        return InvokeContext(
            conversation_id="test_conversation",
            invoke_id="test_invoke",
            assistant_request_id="test_request",
        )

    @pytest.fixture
    def mock_workflow(self, invoke_context):
        """Create a mock Workflow instance."""
        mock_workflow = Mock(spec=Workflow)

        async def mock_invoke(*args, **kwargs):
            yield ConsumeFromTopicEvent(
                invoke_context=invoke_context,
                name="agent_output",
                type=TopicType.AGENT_OUTPUT_TOPIC_TYPE,
                consumer_name="test_consumer",
                consumed_type="Workflow",
                offset=0,
                data=[Message(content="async workflow response", role="assistant")],
            )

        mock_workflow.invoke.return_value = mock_invoke()
        mock_workflow.to_dict.return_value = {"workflow": "data"}
        return mock_workflow

    @pytest.fixture
    def mock_assistant(self, mock_workflow):
        """Create a mock Assistant instance."""
        with patch.object(Assistant, "_construct_workflow"):
            assistant = Assistant(
                assistant_id="test_id",
                name="test_assistant",
                type="test_type",
                oi_span_type=OpenInferenceSpanKindValues.AGENT,
                workflow=mock_workflow,
            )
            return assistant

    @pytest.fixture
    def input_messages(self):
        """Fixture providing sample input messages."""
        return [Message(content="test message", role="user")]

    # Test Assistant Creation and Initialization
    def test_assistant_creation_with_defaults(self):
        """Test Assistant creation with default values."""
        with patch.object(Assistant, "_construct_workflow"):
            assistant = Assistant()

            assert assistant.name == "Assistant"
            assert assistant.type == "assistant"
            assert assistant.oi_span_type == OpenInferenceSpanKindValues.AGENT
            assert assistant.workflow is not None
            assert len(assistant.assistant_id) > 0

    def test_assistant_creation_with_custom_values(self, mock_workflow):
        """Test Assistant creation with custom values."""
        custom_id = "custom_assistant_id"

        with patch.object(Assistant, "_construct_workflow"):
            assistant = Assistant(
                assistant_id=custom_id,
                name="custom_assistant",
                type="custom_type",
                oi_span_type=OpenInferenceSpanKindValues.CHAIN,
                workflow=mock_workflow,
            )

            assert assistant.assistant_id == custom_id
            assert assistant.name == "custom_assistant"
            assert assistant.type == "custom_type"
            assert assistant.oi_span_type == OpenInferenceSpanKindValues.CHAIN
            assert assistant.workflow == mock_workflow

    def test_model_post_init_calls_construct_workflow(self):
        """Test that model_post_init calls _construct_workflow."""
        with patch.object(Assistant, "_construct_workflow") as mock_construct:
            Assistant()
            mock_construct.assert_called_once()

    # Test Async Invoke Method
    @pytest.mark.asyncio
    @patch("grafi.assistants.assistant.record_assistant_invoke")
    async def test_invoke_success(
        self, mock_decorator, mock_assistant, invoke_context, input_messages
    ):
        """Test successful async invoke method."""
        # Setup the decorator to call the original function
        mock_decorator.side_effect = lambda func: func

        input_data = PublishToTopicEvent(
            invoke_context=invoke_context, data=input_messages
        )

        # Invoke
        result_events = []
        async for event in mock_assistant.invoke(input_data):
            result_events.append(event)

        # Verify
        mock_assistant.workflow.invoke.assert_called_once_with(input_data, False)
        assert len(result_events) == 1
        assert result_events[0].data[0].content == "async workflow response"
        assert result_events[0].data[0].role == "assistant"

    @pytest.mark.asyncio
    @patch("grafi.assistants.assistant.record_assistant_invoke")
    async def test_invoke_with_empty_messages(
        self, mock_decorator, mock_assistant, invoke_context
    ):
        """Test async invoke with empty messages."""
        mock_decorator.side_effect = lambda func: func
        empty_messages = []

        input_data = PublishToTopicEvent(
            invoke_context=invoke_context, data=empty_messages
        )

        result_events = []
        async for event in mock_assistant.invoke(input_data):
            result_events.append(event)

        mock_assistant.workflow.invoke.assert_called_once_with(input_data, False)
        assert len(result_events) == 1

    @pytest.mark.asyncio
    @patch("grafi.assistants.assistant.record_assistant_invoke")
    async def test_invoke_multiple_yields(
        self, mock_decorator, mock_assistant, invoke_context, input_messages
    ):
        """Test async invoke with multiple yields."""
        mock_decorator.side_effect = lambda func: func

        # Setup mock to yield multiple times
        async def mock_multi_yield(*args, **kwargs):
            yield ConsumeFromTopicEvent(
                invoke_context=invoke_context,
                name="agent_output",
                type=TopicType.AGENT_OUTPUT_TOPIC_TYPE,
                consumer_name="test_consumer",
                consumed_type="Workflow",
                offset=0,
                data=[Message(content="first response", role="assistant")],
            )
            yield ConsumeFromTopicEvent(
                invoke_context=invoke_context,
                name="agent_output",
                type=TopicType.AGENT_OUTPUT_TOPIC_TYPE,
                consumer_name="test_consumer",
                consumed_type="Workflow",
                offset=0,
                data=[Message(content="second response", role="assistant")],
            )

        mock_assistant.workflow.invoke.return_value = mock_multi_yield()

        input_data = PublishToTopicEvent(
            invoke_context=invoke_context, data=input_messages
        )

        result_events = []
        async for event in mock_assistant.invoke(input_data):
            result_events.append(event)

        assert len(result_events) == 2
        assert result_events[0].data[0].content == "first response"
        assert result_events[1].data[0].content == "second response"

    @pytest.mark.asyncio
    @patch("grafi.assistants.assistant.record_assistant_invoke")
    async def test_invoke_workflow_exception_propagated(
        self, mock_decorator, mock_assistant, invoke_context, input_messages
    ):
        """Test that async workflow exceptions are propagated."""
        mock_decorator.side_effect = lambda func: func

        async def mock_error_generator(*args, **kwargs):
            raise ValueError("Async workflow error")
            yield  # This line won't be reached, but needed for generator syntax

        mock_assistant.workflow.invoke.return_value = mock_error_generator()

        input_data = PublishToTopicEvent(
            invoke_context=invoke_context, data=input_messages
        )

        with pytest.raises(ValueError, match="Async workflow error"):
            async for _ in mock_assistant.invoke(input_data):
                pass

    # Test to_dict Method
    def test_to_dict_success(self, mock_assistant):
        """Test successful to_dict method."""
        result = mock_assistant.to_dict()

        assert result == {
            "assistant_id": "test_id",
            "name": "test_assistant",
            "oi_span_type": "AGENT",
            "type": "test_type",
            "workflow": {
                "workflow": "data",
            },
        }
        mock_assistant.workflow.to_dict.assert_called_once()

    def test_to_dict_workflow_exception_propagated(self, mock_assistant):
        """Test that workflow to_dict exceptions are propagated."""
        mock_assistant.workflow.to_dict.side_effect = RuntimeError(
            "Serialization error"
        )

        with pytest.raises(RuntimeError, match="Serialization error"):
            mock_assistant.to_dict()

    # Test generate_manifest Method
    def test_generate_manifest_success(self, mock_assistant, tmp_path):
        """Test successful manifest generation."""
        output_dir = str(tmp_path)

        result_path = mock_assistant.generate_manifest(output_dir)

        # Verify the method returns correct path
        expected_path = os.path.join(output_dir, "test_assistant_manifest.json")
        assert (
            result_path is None
        )  # Method doesn't return path, but we can check file exists

        # Verify file was created and contains correct data
        assert os.path.exists(expected_path)

        with open(expected_path, "r") as f:
            manifest_data = json.load(f)

        assert manifest_data == {
            "assistant_id": "test_id",
            "name": "test_assistant",
            "oi_span_type": "AGENT",
            "type": "test_type",
            "workflow": {
                "workflow": "data",
            },
        }
        mock_assistant.workflow.to_dict.assert_called()

    def test_generate_manifest_with_default_directory(self, mock_assistant):
        """Test manifest generation with default directory."""
        with patch("builtins.open", create=True) as mock_open:
            with patch("json.dumps", return_value='{"workflow": "data"}') as mock_dumps:
                mock_assistant.generate_manifest()

                # Verify file was opened with correct path
                expected_path = os.path.join(".", "test_assistant_manifest.json")
                mock_open.assert_called_once_with(expected_path, "w")

                # Verify JSON serialization
                mock_dumps.assert_called_once_with(
                    {
                        "assistant_id": "test_id",
                        "name": "test_assistant",
                        "oi_span_type": "AGENT",
                        "type": "test_type",
                        "workflow": {
                            "workflow": "data",
                        },
                    },
                    indent=4,
                )

    def test_generate_manifest_custom_directory(self, mock_assistant, tmp_path):
        """Test manifest generation with custom directory."""
        custom_dir = tmp_path / "custom"
        custom_dir.mkdir()

        mock_assistant.generate_manifest(str(custom_dir))

        expected_path = custom_dir / "test_assistant_manifest.json"
        assert expected_path.exists()

        with open(expected_path, "r") as f:
            manifest_data = json.load(f)

        assert manifest_data == {
            "assistant_id": "test_id",
            "name": "test_assistant",
            "oi_span_type": "AGENT",
            "type": "test_type",
            "workflow": {
                "workflow": "data",
            },
        }

    def test_generate_manifest_file_write_error(self, mock_assistant):
        """Test manifest generation with file write error."""
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            with pytest.raises(IOError, match="Permission denied"):
                mock_assistant.generate_manifest()

    def test_generate_manifest_json_serialization_error(self, mock_assistant):
        """Test manifest generation with JSON serialization error."""
        # Make to_dict return something that can't be serialized
        mock_assistant.workflow.to_dict.return_value = {"key": object()}

        with pytest.raises(TypeError):
            mock_assistant.generate_manifest()

    @pytest.mark.asyncio
    async def test_full_async_workflow_integration(
        self, mock_workflow, invoke_context, input_messages
    ):
        """Test full async integration with real workflow calls."""
        with patch.object(Assistant, "_construct_workflow"):
            assistant = Assistant(name="async_integration_test", workflow=mock_workflow)

            input_data = PublishToTopicEvent(
                invoke_context=invoke_context, data=input_messages
            )

            # Test asynchronous invoke
            async_results = []
            async for event in assistant.invoke(input_data):
                async_results.append(event)

            assert len(async_results) == 1
            assert async_results[0].data[0].content == "async workflow response"

    # Test Edge Cases
    def test_assistant_with_none_workflow(self):
        """Test Assistant behavior with None workflow."""
        with patch.object(Assistant, "_construct_workflow"):
            with pytest.raises(Exception):  # This should fail during validation
                Assistant(workflow=None)

    def test_assistant_name_affects_manifest_filename(self, mock_workflow, tmp_path):
        """Test that assistant name affects manifest filename."""
        with patch.object(Assistant, "_construct_workflow"):
            assistant = Assistant(name="special_assistant_name", workflow=mock_workflow)

            assistant.generate_manifest(str(tmp_path))

            expected_file = tmp_path / "special_assistant_name_manifest.json"
            assert expected_file.exists()
