"""AgentbayIntegration tools."""

from typing import Optional, Type

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class WriteFileInput(BaseModel):
    """Input schema for writing file to AgentBay session."""

    path: str = Field(..., description="Path where to write the file")
    content: str = Field(..., description="Content to write to the file")
    mode: str = Field(default="overwrite", description="Write mode ('overwrite' or 'append')")


class WriteFileTool(BaseTool):  # type: ignore[override]
    """Tool for writing files in AgentBay session.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install agentbay
            export AGENTBAY_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration.tools import WriteFileTool
            
            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            tool = WriteFileTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"path": "/tmp/test.txt", "content": "Hello World"})

        .. code-block:: python

            # Output: "File written successfully to /tmp/test.txt"

    """  # noqa: E501

    name: str = "write_file"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Write content to a file in the AgentBay session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = WriteFileInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AgentBay session object"""

    def _run(
        self, 
        path: str, 
        content: str, 
        mode: str = "overwrite",
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Write content to a file in the AgentBay session."""
        try:
            result = self.session.file_system.write_file(path, content, mode)
            if result.success:
                return f"File written successfully to {path} with mode '{mode}'"
            else:
                return f"Failed to write file: {result.error_message}"
        except Exception as e:
            return f"Error occurred while writing file: {str(e)}"


class ReadFileInput(BaseModel):
    """Input schema for reading file from AgentBay session."""

    path: str = Field(..., description="Path of the file to read")


class ReadFileTool(BaseTool):  # type: ignore[override]
    """Tool for reading files in AgentBay session.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install agentbay
            export AGENTBAY_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration.tools import ReadFileTool
            
            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            tool = ReadFileTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"path": "/tmp/test.txt"})

        .. code-block:: python

            # Output: "File content:\\n<file_content>"

    """  # noqa: E501

    name: str = "read_file"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Read content from a file in the AgentBay session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = ReadFileInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AgentBay session object"""

    def _run(
        self, 
        path: str, 
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Read content from a file in the AgentBay session."""
        try:
            result = self.session.file_system.read_file(path)
            if result.success:
                return f"File content:\n{result.content}"
            else:
                return f"Failed to read file: {result.error_message}"
        except Exception as e:
            return f"Error occurred while reading file: {str(e)}"


class RunCodeInput(BaseModel):
    """Input schema for running code in AgentBay session."""

    code: str = Field(..., description="The code to execute")
    language: str = Field(..., description="The programming language of the code. Supported languages are: 'python', 'javascript'")
    timeout_s: int = Field(default=300, description="The timeout for the code execution in seconds")


class RunCodeTool(BaseTool):  # type: ignore[override]
    """Tool for running code in AgentBay session.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install agentbay
            export AGENTBAY_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration.tools import RunCodeTool
            
            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            tool = RunCodeTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"code": "print('Hello World')", "language": "python"})

        .. code-block:: python

            # Output: "Code execution result:\\n<code_output>"

    """  # noqa: E501

    name: str = "run_code"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Execute code in the AgentBay session. Supported languages are: python, javascript"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = RunCodeInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AgentBay session object"""

    def _run(
        self, 
        code: str, 
        language: str,
        timeout_s: int = 300,
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute code in the AgentBay session."""
        try:
            # AgentBay SDK doesn't seem to have a direct run_code method
            # We'll write the code to a file and execute it as a command
            if language == "python":
                file_path = f"/tmp/temp_script_{hash(code)}.py"
                write_result = self.session.file_system.write_file(file_path, code)
                if not write_result.success:
                    return f"Failed to write code to file: {write_result.error_message}"
                
                execution_result = self.session.command.execute_command(f"python3 {file_path}")
                if execution_result.success:
                    return f"Code execution result:\n{execution_result.output}"
                else:
                    return f"Code execution failed with error: {execution_result.error_message}"
            elif language == "javascript":
                file_path = f"/tmp/temp_script_{hash(code)}.js"
                write_result = self.session.file_system.write_file(file_path, code)
                if not write_result.success:
                    return f"Failed to write code to file: {write_result.error_message}"
                
                execution_result = self.session.command.execute_command(f"node {file_path}")
                if execution_result.success:
                    return f"Code execution result:\n{execution_result.output}"
                else:
                    return f"Code execution failed with error: {execution_result.error_message}"
            else:
                return f"Unsupported language: {language}. Supported languages are: python, javascript"
        except Exception as e:
            return f"Error occurred while executing code: {str(e)}"


class ExecuteCommandInput(BaseModel):
    """Input schema for executing command in AgentBay session."""

    command: str = Field(..., description="Shell command to execute")
    timeout_ms: int = Field(default=1000, description="Timeout for command execution in milliseconds")


class ExecuteCommandTool(BaseTool):  # type: ignore[override]
    """Tool for executing shell commands in AgentBay session.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install agentbay
            export AGENTBAY_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration.tools import ExecuteCommandTool
            
            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            tool = ExecuteCommandTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"command": "ls -la", "timeout_ms": 1000})

        .. code-block:: python

            # Output: "Command output:\n<command_output>"

    """  # noqa: E501

    name: str = "execute_command"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Execute a shell command in the AgentBay session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = ExecuteCommandInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AgentBay session object"""

    def _run(
        self, 
        command: str, 
        timeout_ms: int = 1000,
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute a shell command in the AgentBay session."""
        try:
            result = self.session.command.execute_command(command, timeout_ms)
            if result.success:
                return f"Command output:\n{result.output}"
            else:
                return f"Command failed with error: {result.error_message}"
        except Exception as e:
            return f"Error occurred while executing command: {str(e)}"