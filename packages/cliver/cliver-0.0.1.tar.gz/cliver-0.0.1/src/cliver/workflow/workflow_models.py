"""
Workflow models for Cliver Workflow Engine.

This module defines the Pydantic models for workflow definitions, steps, and execution context.
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class StepType(str, Enum):
    """Enumeration of step types."""
    FUNCTION = "function"
    LLM = "llm"
    WORKFLOW = "workflow"
    HUMAN = "human"


class RetryPolicy(BaseModel):
    """Retry policy for steps."""
    max_attempts: int = Field(3, description="Maximum number of retry attempts")
    backoff_factor: float = Field(1.0, description="Backoff factor for exponential retry")
    max_backoff: float = Field(60.0, description="Maximum delay between retries in seconds")


class OnErrorAction(str, Enum):
    """Actions to take when a step fails."""
    FAIL = "fail"
    CONTINUE = "continue"


class BaseStep(BaseModel):
    """Base step model."""
    id: str = Field(..., description="Unique identifier for the step")
    name: str = Field(..., description="Descriptive name of the step")
    type: StepType = Field(..., description="Type of the step")
    description: Optional[str] = Field(None, description="Description of the step")
    inputs: Optional[Dict[str, Any]] = Field(None, description="Input variables for the step")
    # define the output variable name that can be used to access the execution results.
    outputs: Optional[List[str]] = Field(None, description="Output variable names from the step")
    retry: Optional[RetryPolicy] = Field(None, description="Retry policy configuration")
    timeout: Optional[int] = Field(None, description="Timeout in seconds")
    on_error: Optional[OnErrorAction] = Field(None, description="Action to take on error")
    condition: Optional[str] = Field(None, description="Condition expression for step execution")
    skipped: bool = Field(False, description="Whether the step is skipped")
    # Fields for execution context (set during workflow execution)
    workflow_name: Optional[str] = Field(None, description="Name of the workflow this step belongs to")
    execution_id: Optional[str] = Field(None, description="Execution ID for this workflow execution")


class FunctionStep(BaseStep):
    """Function step model."""
    type: StepType = StepType.FUNCTION
    function: str = Field(..., description="Module path to the function to execute")


class LLMStep(BaseStep):
    """LLM step model."""
    type: StepType = StepType.LLM
    prompt: str = Field(..., description="Prompt for the LLM")
    model: Optional[str] = Field(None, description="LLM model to use")
    stream: bool = Field(False, description="Whether to stream the response")
    images: Optional[List[str]] = Field(None, description="Image files to send with the message")
    audio_files: Optional[List[str]] = Field(None, description="Audio files to send with the message")
    video_files: Optional[List[str]] = Field(None, description="Video files to send with the message")
    files: Optional[List[str]] = Field(None, description="General files to upload for tools")
    skill_sets: Optional[List[str]] = Field(None, description="Skill sets to apply")
    template: Optional[str] = Field(None, description="Template to use for the prompt")
    params: Optional[Dict[str, Any]] = Field(None, description="Parameters for skill sets and templates")


class WorkflowStep(BaseStep):
    """Workflow step model."""
    type: StepType = StepType.WORKFLOW
    workflow: str = Field(..., description="Workflow name or path to the workflow file to execute")
    workflow_inputs: Optional[Dict[str, Any]] = Field(None, description="Inputs for the sub-workflow")


class HumanStep(BaseStep):
    """Human step model."""
    type: StepType = StepType.HUMAN
    prompt: str = Field(..., description="Prompt to show to the user")
    auto_confirm: bool = Field(False, description="Automatically confirm without user input")


# Union type for all step types
Step = Union[FunctionStep, LLMStep, WorkflowStep, HumanStep]


class Workflow(BaseModel):
    """Workflow definition model."""
    name: str = Field(..., description="Name of the workflow.(Global unique so that it can be used for search by name)")
    description: Optional[str] = Field(None, description="Description of the workflow")
    version: Optional[str] = Field(None, description="Version of the workflow")
    author: Optional[str] = Field(None, description="Author of the workflow")
    # we define the input variable names in the workflow definition, and pass the value on execution.
    inputs: Optional[List[str]] = Field(None, description="Input variable names for the workflow")
    steps: List[Step] = Field(default_factory=list, description="Steps in the workflow")


class ExecutionContext(BaseModel):
    """Execution context for workflow execution."""
    workflow_name: str = Field(..., description="Name of the workflow being executed")
    execution_id: str = Field(None, description="Unique execution identifier")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input variables")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Output variables from steps")
    step_outputs: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Nested output variables from steps by step ID")
    variables: Dict[str, Any] = Field(default_factory=dict, description="All variables in execution context")
    current_step: Optional[str] = Field(None, description="Currently executing step ID")


class ExecutionResult(BaseModel):
    """Result of a step execution."""
    step_id: str = Field(..., description="ID of the executed step")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Output variables from the step")
    success: bool = Field(True, description="Whether the step execution was successful")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")


class WorkflowExecutionState(BaseModel):
    """State of a workflow execution."""
    workflow_name: str = Field(..., description="Name of the workflow")
    execution_id: str = Field(..., description="Unique execution identifier")
    current_step_index: int = Field(0, description="Index of the current step")
    completed_steps: List[str] = Field(default_factory=list, description="List of completed step IDs")
    status: str = Field("running", description="Execution status: running, paused, completed, failed")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    context: ExecutionContext = Field(..., description="Execution context")