from __future__ import annotations

from pydantic import BaseModel
from typing_extensions import deprecated

from .run_workflow_request_file import RunWorkflowRequestFile


class RunWorkflowRequestBody(BaseModel):
    inputs: dict | None = None
    response_mode: str | None = None
    user: str | None = None
    files: list[RunWorkflowRequestFile] | None = None

    @staticmethod
    def builder() -> RunWorkflowRequestBodyBuilder:
        return RunWorkflowRequestBodyBuilder()


class RunWorkflowRequestBodyBuilder:
    def __init__(self):
        self._run_workflow_body = RunWorkflowRequestBody()

    def build(self):
        return self._run_workflow_body

    def inputs(self, inputs: dict) -> RunWorkflowRequestBodyBuilder:
        self._run_workflow_body.inputs = inputs
        return self

    @deprecated(
        """
        This method is deprecated and will be removed in a future release. 
        The response_mode is now automatically determined based on whether 
        streaming or blocking execution is requested. 
        You no longer need to set it manually.
        """
    )
    def response_mode(self, response_mode: str) -> RunWorkflowRequestBodyBuilder:
        if response_mode not in ["streaming", "blocking"]:
            raise ValueError('response_mode must be either "streaming" or "blocking"')
        self._run_workflow_body.response_mode = response_mode
        return self

    def user(self, user: str) -> RunWorkflowRequestBodyBuilder:
        self._run_workflow_body.user = user
        return self

    def files(self, files: list[RunWorkflowRequestFile]) -> RunWorkflowRequestBodyBuilder:
        self._run_workflow_body.files = files
        return self
