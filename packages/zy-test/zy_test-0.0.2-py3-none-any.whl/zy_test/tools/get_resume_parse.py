import subprocess
from typing import Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun

from gptsre_tools.tools.register_tool import ToolRegistry


class CommandExecutorInput(BaseModel):
    command: str = Field(description="The command to execute")


@ToolRegistry.register_tool('zy-test', CommandExecutorInput)
class CommandExecutorTool(BaseTool):
    name: str = "command_executor"
    description: str = "Execute a command and return the result"

    def _run(
        self,
        command: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return f"stdout: {result.stdout}\nstderr: {result.stderr}\nreturn_code: {result.returncode}"
        except Exception as e:
            return f"Error executing command: {str(e)}"

    async def _arun(
        self,
        command: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async execution not supported")
