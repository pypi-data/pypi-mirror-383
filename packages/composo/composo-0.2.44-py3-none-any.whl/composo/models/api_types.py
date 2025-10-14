import math
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .common_types import (
    ModelCore,
    reward_starts,
    binary_starts,
    criteria_starts,
    EvaluationType,
)


class LLMToolResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the tool call.")
    response: str = Field(..., description="Tool response")

    name: Optional[str] = Field(default=None, description="Tool name")

    model_config = ConfigDict(
        extra="allow",
    )


class LLMToolCall(BaseModel):
    id: str = Field(..., description="Unique identifier for the tool call.")
    name: str = Field(..., description="Tool name")
    parameters: str = Field(..., description="Tool parameters.")

    model_config = ConfigDict(
        extra="allow",
    )


class LLMToolDefinition(BaseModel):
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: str = Field(..., description="Tool parameters.")

    model_config = ConfigDict(
        extra="allow",
    )


class LLMInput(BaseModel):
    role: str = Field(
        ...,
        description="Role of the message sender (e.g., user, system, assistant, tool)",
    )
    type: Optional[str] = Field(
        default=None,
        description="Type of message (e.g., text, thinking_tokens, tool_call). This can be arbitrary but should be consistent within a trace.",
    )
    content: Union[str, LLMToolCall, LLMToolResponse] = Field(
        ..., description="Content of the LLM Input."
    )


class LLMOutput(BaseModel):
    type: Optional[str] = Field(
        default=None,
        description="Type of message (e.g., text, thinking_tokens, tool_call). This can be arbitrary but should be consistent within a trace.",
    )
    content: Union[str, LLMToolCall] = Field(..., description="Content of the message")


class LLMInteraction(BaseModel):
    input_messages: List[LLMInput] = Field(
        ...,
        description="List of input messages to the LLM invocation.",
    )
    output_messages: List[LLMOutput] = Field(
        ...,
        description="List of output messages from the LLM invocation.",
    )
    tools_available: Optional[List[LLMToolDefinition]] = Field(
        default=None,
        description="List of tools available to the agent in this interaction.",
    )


class AgentInstance(BaseModel):
    id: str = Field(..., description="Unique identifier for the agent instance.")
    name: str = Field(..., description="User defined name of the agent invoked.")
    interactions: List[Union[str, LLMInteraction]] = Field(
        ...,
        description="List of ordered LLM interactions or agent instance ids for this agent instance.",
    )


class MultiAgentTrace(BaseModel):
    root_agent_instance_id: str = Field(
        ...,
        description="User invoked Agent Instance ID. This is the root of the trace.",
    )
    agent_instance_by_id: dict[str, AgentInstance] = Field(
        ..., description="Mapping of ID to Agent Instance objects."
    )


class RequestBase(BaseModel):
    messages: List[dict] = Field(
        ..., description="A list of chat messages", min_length=2
    )
    system: Optional[str] = Field(
        None,
        description="System message is separate for Anthropic-style LLM calls. Optional.",
    )
    tools: Optional[List[dict]] = Field(
        None,
        description="List of tools available for the assistant to call. Optional.",
    )
    model_core: ModelCore = Field(
        default=ModelCore.ALIGN_20250529,
        description="The model core for reward evaluation. Defaults to align-20250503 if not specified.",
    )

    @field_validator("messages")
    @classmethod
    def last_message_must_be_assistant(cls, messages) -> List[dict]:
        if not messages:
            raise ValueError("Conversation must contain at least one message")

        return messages


class RewardRequest(RequestBase):
    """
    Request model for reward score evaluation of LLM responses against specified criteria.
    """

    evaluation_criteria: str = Field(
        ...,
        description="Criteria used for evaluation. Begins with one of the following: "
        + ", ".join(reward_starts),
    )

    @field_validator("evaluation_criteria")
    @classmethod
    def check_evaluation_criteria_length(cls, evaluation_criteria):
        if len(evaluation_criteria) > 4096:
            raise ValueError("Evaluation criteria length cannot exceed 4k characters")
        return evaluation_criteria

    @field_validator("evaluation_criteria")
    @classmethod
    def evaluation_criteria_must_start_with_correct_prefix(cls, value):
        if not any(value.startswith(start) for start in reward_starts):
            raise ValueError(
                "Evaluation criteria must start with one of the following: "
                + ", ".join(reward_starts)
            )
        return value


class RewardGPURequest(RewardRequest):
    """
    Request model for reward score evaluation of LLM responses against specified criteria,
    specifically for GPU-based evaluation.
    """

    explanation: str = Field(
        description="Explanation of the evaluation criteria. Optional.",
    )


class BinaryEvaluationRequest(RequestBase):
    """
    Request model for binary evaluation of LLM responses against specified criteria.
    """

    evaluation_criteria: str = Field(
        ...,
        description="Criteria used for evaluation. Begins with one of the following: "
        + ", ".join(binary_starts),
    )

    @field_validator("evaluation_criteria")
    @classmethod
    def check_evaluation_criteria_length(cls, evaluation_criteria):
        if len(evaluation_criteria) > 4096:
            raise ValueError("Evaluation criteria length cannot exceed 4k characters")
        return evaluation_criteria

    @field_validator("evaluation_criteria")
    @classmethod
    def evaluation_criteria_must_start_with_correct_prefix(cls, value):
        if not any(value.startswith(start) for start in binary_starts):
            raise ValueError(
                "Evaluation criteria must start with one of the following: "
                + ", ".join(binary_starts)
            )
        return value


class TraceRewardRequest(BaseModel):
    """
    Request model for a trace based evaluation of LLM responses against specified criteria.
    """

    trace: MultiAgentTrace = Field(
        ...,
        description="A Multi Agent Trace object representing the full trace of agent interactions.",
    )
    model_core: ModelCore = Field(
        default=ModelCore.ALIGN_20250529,
        description="The model core for reward evaluation. Defaults to align-20250503 if not specified.",
    )

    evaluation_criteria: str = Field(
        ...,
        description="Criteria used for evaluation. Begins with one of the following: "
        + ", ".join(
            criteria_starts["reward"][EvaluationType.AGENT_EVALUATION]
            + criteria_starts["binary"][EvaluationType.AGENT_EVALUATION]
        ),
    )

    @field_validator("evaluation_criteria")
    @classmethod
    def check_evaluation_criteria_length(cls, evaluation_criteria):
        if len(evaluation_criteria) > 4096:
            raise ValueError("Evaluation criteria length cannot exceed 4k characters")
        return evaluation_criteria

    @field_validator("evaluation_criteria")
    @classmethod
    def evaluation_criteria_must_start_with_correct_prefix(cls, value):
        agent_evaluation_starts = (
            criteria_starts["reward"][EvaluationType.AGENT_EVALUATION]
            + criteria_starts["binary"][EvaluationType.AGENT_EVALUATION]
        )
        if not any(value.startswith(start) for start in agent_evaluation_starts):
            raise ValueError(
                "Evaluation criteria must start with one of the following: "
                + ", ".join(agent_evaluation_starts)
            )
        return value


class ScoreResponse(BaseModel):
    """
    Response model for evaluation scores.
    """

    score: Optional[float] = Field(
        None,
        description="Evaluation score between 0 and 1. If null, the criteria was deemed not applicable.",
    )
    explanation: str = Field(description="Explanation of the evaluation score")

    @field_validator("score")
    def validate_score(cls, value):
        if value is None:
            return value
        if math.isnan(value):
            return None
        if not 0 <= value <= 1:
            raise ValueError("Score must be between 0 and 1.")
        return value


class BinaryEvaluationResponse(BaseModel):
    """
    Response model for binary evaluation results.
    """

    passed: Optional[bool] = Field(
        default=None,
        description="Whether the evaluation passed. If null, the criteria was deemed not applicable.",
    )
    explanation: str = Field(description="Explanation of the evaluation score")


class SummaryStatistics(BaseModel):
    median: Optional[float] = Field(default=None, description="Median score.")
    min: Optional[float] = Field(default=None, description="Minimum score.")
    max: Optional[float] = Field(default=None, description="Maximum score.")
    std: Optional[float] = Field(
        default=None, description="Standard deviation of scores."
    )


class AgentTraceResult(BaseModel):
    agent_name: str = Field(..., description="Name of the agent evaluated.")
    results_by_agent_instance_id: dict[
        str, Union[ScoreResponse, BinaryEvaluationResponse, None]
    ] = Field(
        ...,
        description="Mapping of Agent Instance ID to their respective Score Response, Binary Evaluation Response, or None depending on criteria.",
    )
    summary_statistics: Optional[SummaryStatistics] = Field(
        default=None,
        description="Summary statistics for the agent's evaluations. Only applicable for reward evaluations.",
    )


class MultiAgentTraceResponse(BaseModel):
    """
    Response model for multi-agent trace evaluations.
    """

    request_id: str = Field(
        ..., description="Unique identifier for the evaluation request."
    )
    results_by_agent_name: dict[str, AgentTraceResult] = Field(
        ..., description="Mapping of Agent Name to their respective trace results."
    )

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)
