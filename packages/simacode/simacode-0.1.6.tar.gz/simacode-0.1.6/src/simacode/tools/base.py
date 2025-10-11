"""
Base tool framework for SimaCode.

This module defines the core abstractions and interfaces for all tools in the
SimaCode system, providing a consistent framework for tool development,
validation, execution, and monitoring.
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolStatus(Enum):
    """Tool execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolResultType(Enum):
    """Tool result type enumeration."""
    PROGRESS = "progress"
    OUTPUT = "output"
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"
    INFO = "info"


@dataclass
class ToolResult:
    """
    Represents the result of a tool execution.
    
    This class encapsulates all information about a tool's execution result,
    including status, output, errors, and metadata.
    """
    type: ToolResultType
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    tool_name: str = ""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "tool_name": self.tool_name,
            "execution_id": self.execution_id
        }
    
    def to_json(self) -> str:
        """Convert result to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class ToolInput(BaseModel):
    """
    Base input model for all tools.
    
    This Pydantic model provides input validation and serialization
    for tool parameters.
    """
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = Field(None, description="Associated session ID for context access")
    session_context: Optional[Dict[str, Any]] = Field(None, description="Session context information")
    
    class Config:
        extra = "allow"  # Allow additional fields for tool-specific inputs


class Tool(ABC):
    """
    Abstract base class for all SimaCode tools.
    
    This class defines the interface that all tools must implement,
    providing a consistent framework for tool development and execution.
    """
    
    def __init__(self, name: str, description: str, version: str = "1.0.0", session_manager=None):
        """
        Initialize the tool with basic metadata.
        
        Args:
            name: Tool name
            description: Tool description
            version: Tool version
            session_manager: Optional SessionManager instance for session access
        """
        self.name = name
        self.description = description
        self.version = version
        self.session_manager = session_manager
        self.created_at = datetime.now()
        self._execution_count = 0
        self._total_execution_time = 0.0
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get tool metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "execution_count": self._execution_count,
            "average_execution_time": (
                self._total_execution_time / self._execution_count
                if self._execution_count > 0 else 0.0
            )
        }
    
    async def get_session(self, input_data: ToolInput):
        """
        Get session object if session_manager and session_id are available.
        
        Args:
            input_data: Tool input containing session_id
            
        Returns:
            ReActSession or None: Session object if available
        """
        if self.session_manager and input_data.session_id:
            try:
                return await self.session_manager.get_session(input_data.session_id)
            except Exception as e:
                # Log error but don't fail the tool execution
                logger.warning(f"Failed to get session {input_data.session_id}: {str(e)}")
        return None
    
    @abstractmethod
    def get_input_schema(self) -> Type[ToolInput]:
        """
        Return the Pydantic model class for validating tool inputs.
        
        Returns:
            Type[ToolInput]: The input schema class for this tool
        """
        pass
    
    @abstractmethod
    async def validate_input(self, input_data: Dict[str, Any]) -> ToolInput:
        """
        Validate and parse tool input data.
        
        Args:
            input_data: Raw input data dictionary
            
        Returns:
            ToolInput: Validated input object
            
        Raises:
            ValidationError: If input validation fails
        """
        pass
    
    @abstractmethod
    async def check_permissions(self, input_data: ToolInput) -> bool:
        """
        Check if the tool has permission to execute with given input.
        
        Args:
            input_data: Validated tool input
            
        Returns:
            bool: True if permission granted, False otherwise
        """
        pass
    
    @abstractmethod
    async def execute(self, input_data: ToolInput) -> AsyncGenerator[ToolResult, None]:
        """
        Execute the tool with validated input.
        
        Args:
            input_data: Validated tool input
            
        Yields:
            ToolResult: Execution results (progress, output, errors, etc.)
        """
        pass
    
    async def run(self, input_data: Dict[str, Any]) -> AsyncGenerator[ToolResult, None]:
        """
        Main execution method that orchestrates the tool execution pipeline.
        
        This method handles the complete execution flow including validation,
        permission checking, execution, and monitoring.
        
        Args:
            input_data: Raw input data dictionary
            
        Yields:
            ToolResult: Execution results
        """
        start_time = time.time()
        execution_id = str(uuid.uuid4())
        
        try:
            # Update execution count
            self._execution_count += 1
            
            # Yield start notification
            yield ToolResult(
                type=ToolResultType.INFO,
                content=f"Starting {self.name} execution",
                tool_name=self.name,
                execution_id=execution_id,
                metadata={"start_time": start_time}
            )
            
            # Validate input
            try:
                validated_input = await self.validate_input(input_data)
                validated_input.execution_id = execution_id
            except Exception as e:
                yield ToolResult(
                    type=ToolResultType.ERROR,
                    content=f"Input validation failed: {str(e)}",
                    tool_name=self.name,
                    execution_id=execution_id
                )
                return
            
            # Check permissions
            try:
                has_permission = await self.check_permissions(validated_input)
                if not has_permission:
                    yield ToolResult(
                        type=ToolResultType.ERROR,
                        content="Permission denied for this operation",
                        tool_name=self.name,
                        execution_id=execution_id
                    )
                    return
            except Exception as e:
                yield ToolResult(
                    type=ToolResultType.ERROR,
                    content=f"Permission check failed: {str(e)}",
                    tool_name=self.name,
                    execution_id=execution_id
                )
                return
            
            # Execute tool
            execution_successful = False
            has_error = False
            has_mcp_error = False
            async for result in self.execute(validated_input):
                result.tool_name = self.name
                result.execution_id = execution_id
                yield result

                # Track if execution was successful or had errors
                if result.type == ToolResultType.SUCCESS:
                    execution_successful = True
                elif result.type == ToolResultType.ERROR:
                    has_error = True
                elif result.type == ToolResultType.OUTPUT:
                    # 🔧 检查MCP工具输出中的错误信息
                    has_mcp_error = self._check_mcp_error_in_result(result)

            # Yield completion notification if no explicit success was reported and no errors occurred
            if not execution_successful and not has_error and not has_mcp_error:
                yield ToolResult(
                    type=ToolResultType.SUCCESS,
                    content=f"工具 {self.name} 执行成功",
                    tool_name=self.name,
                    execution_id=execution_id
                )
                
        except asyncio.CancelledError:
            yield ToolResult(
                type=ToolResultType.WARNING,
                content=f"工具 {self.name} 执行取消",
                tool_name=self.name,
                execution_id=execution_id
            )
            raise
            
        except Exception as e:
            yield ToolResult(
                type=ToolResultType.ERROR,
                content=f"Unexpected error in {self.name}: {str(e)}",
                tool_name=self.name,
                execution_id=execution_id,
                metadata={"error_type": type(e).__name__}
            )
            
        finally:
            # Update execution time statistics
            execution_time = time.time() - start_time
            self._total_execution_time += execution_time
            
            yield ToolResult(
                type=ToolResultType.INFO,
                content=f"{self.name} execution finished in {execution_time:.2f}s",
                tool_name=self.name,
                execution_id=execution_id,
                metadata={
                    "execution_time": execution_time,
                    "end_time": time.time()
                }
            )
    
    def __str__(self) -> str:
        """String representation of the tool."""
        return f"{self.name} v{self.version}: {self.description}"
    
    def __repr__(self) -> str:
        """Detailed representation of the tool."""
        return (
            f"Tool(name='{self.name}', version='{self.version}', "
            f"executions={self._execution_count})"
        )

    def _check_mcp_error_in_result(self, result: ToolResult) -> bool:
        """
        检查单个ToolResult中是否包含MCP错误信息。

        Args:
            result: 工具执行结果

        Returns:
            bool: 如果发现MCP错误则返回True
        """
        if result.type != ToolResultType.OUTPUT:
            return False

        try:
            import json
            content = result.content.strip()

            # 如果内容看起来像JSON，尝试解析
            if content.startswith('{') and content.endswith('}'):
                parsed_content = json.loads(content)

                # 检查是否包含MCP错误标识
                if isinstance(parsed_content, dict):
                    # 检查 success: false 或 isError: true
                    if (parsed_content.get('success') is False or
                            parsed_content.get('isError') is True):
                        return True

                    # 检查嵌套的错误信息
                    if 'result' in parsed_content:
                        nested_result = parsed_content['result']
                        if isinstance(nested_result, dict):
                            if (nested_result.get('success') is False or
                                    nested_result.get('isError') is True):
                                return True

        except (json.JSONDecodeError, TypeError, AttributeError):
            # 如果不是有效的JSON，返回False
            pass

        return False


class ToolRegistry:
    """
    Global registry for managing tool instances and discovery.
    
    This singleton class maintains a registry of all available tools
    and provides methods for tool discovery, registration, and management.
    """
    
    _instance: Optional["ToolRegistry"] = None
    _tools: Dict[str, Tool] = {}
    
    def __new__(cls) -> "ToolRegistry":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, tool: Tool) -> None:
        """
        Register a tool in the global registry.
        
        Args:
            tool: Tool instance to register
            
        Raises:
            ValueError: If tool name already exists
        """
        if tool.name in cls._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        
        cls._tools[tool.name] = tool
    
    @classmethod
    def unregister(cls, tool_name: str) -> bool:
        """
        Unregister a tool from the registry.
        
        Args:
            tool_name: Name of the tool to unregister
            
        Returns:
            bool: True if tool was removed, False if not found
        """
        if tool_name in cls._tools:
            del cls._tools[tool_name]
            return True
        return False
    
    @classmethod
    def get_tool(cls, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            Optional[Tool]: Tool instance or None if not found
        """
        return cls._tools.get(tool_name)
    
    @classmethod
    def list_tools(cls) -> List[str]:
        """
        Get list of all registered tool names.
        
        Returns:
            List[str]: List of tool names
        """
        return list(cls._tools.keys())
    
    @classmethod
    def get_all_tools(cls) -> Dict[str, Tool]:
        """
        Get all registered tools.
        
        Returns:
            Dict[str, Tool]: Dictionary mapping tool names to tool instances
        """
        return cls._tools.copy()
    
    @classmethod
    def get_tool_metadata(cls, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Optional[Dict[str, Any]]: Tool metadata or None if not found
        """
        tool = cls.get_tool(tool_name)
        return tool.metadata if tool else None
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered tools (mainly for testing)."""
        cls._tools.clear()
    
    @classmethod
    def get_registry_stats(cls) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dict[str, Any]: Registry statistics
        """
        total_executions = sum(tool._execution_count for tool in cls._tools.values())
        total_time = sum(tool._total_execution_time for tool in cls._tools.values())
        
        return {
            "total_tools": len(cls._tools),
            "tool_names": list(cls._tools.keys()),
            "total_executions": total_executions,
            "total_execution_time": total_time,
            "average_execution_time": (
                total_time / total_executions if total_executions > 0 else 0.0
            )
        }


# Auto-register core tools when module is imported
def _register_core_tools() -> None:
    """Register core tools automatically."""
    # This will be called when other tool modules are imported
    pass


# Helper function for tool discovery
async def discover_tools() -> List[Tool]:
    """
    Discover and return all available tools.
    
    Returns:
        List[Tool]: List of all registered tool instances
    """
    return list(ToolRegistry.get_all_tools().values())


# Helper function for executing tools by name
async def execute_tool(
    tool_name: str, 
    input_data: Dict[str, Any],
    session_id: Optional[str] = None,
    session_context: Optional[Dict[str, Any]] = None
) -> AsyncGenerator[ToolResult, None]:
    """
    Execute a tool by name with given input data.
    
    Args:
        tool_name: Name of the tool to execute
        input_data: Input data for the tool
        session_id: Optional session ID for context
        session_context: Optional session context information
        
    Yields:
        ToolResult: Execution results
        
    Raises:
        ValueError: If tool is not found
    """
    tool = ToolRegistry.get_tool(tool_name)
    if not tool:
        raise ValueError(f"Tool '{tool_name}' not found in registry")
    
    # Add session information to input data if provided
    if session_id or session_context:
        input_data = input_data.copy()  # Don't modify original
        if session_id:
            input_data['session_id'] = session_id
        if session_context:
            input_data['session_context'] = session_context
    
    async for result in tool.run(input_data):
        yield result


def _analyze_and_enhance_tool_result(result: ToolResult) -> ToolResult:
    """
    分析并增强工具结果，特别检测MCP工具的错误输出格式。

    Args:
        result: 原始工具结果

    Returns:
        ToolResult: 增强后的工具结果（如果检测到错误，类型可能被修改为ERROR）
    """
    # 只处理OUTPUT类型的结果
    if result.type != ToolResultType.OUTPUT:
        return result

    try:
        import json
        content = result.content.strip()

        # 检查是否是JSON格式
        if not (content.startswith('{') and content.endswith('}')):
            return result

        parsed_content = json.loads(content)
        if not isinstance(parsed_content, dict):
            return result

        # 检测MCP工具错误格式: 顶层有isError字段
        if parsed_content.get("isError") is True:
            # 提取错误信息
            error_message = "MCP tool reported error"

            # 从content数组中提取详细错误信息
            content_array = parsed_content.get("content", [])
            if isinstance(content_array, list) and len(content_array) > 0:
                first_content = content_array[0]
                if isinstance(first_content, dict) and "text" in first_content:
                    try:
                        error_json = json.loads(first_content["text"])
                        if isinstance(error_json, dict):
                            error_message = (error_json.get("message") or
                                           error_json.get("error") or
                                           error_message)
                    except (json.JSONDecodeError, TypeError):
                        # 如果解析失败，使用原始文本
                        error_message = first_content["text"][:200] + "..." if len(first_content["text"]) > 200 else first_content["text"]

            logger.warning(f"Detected MCP tool error in OUTPUT: {error_message}")

            # 创建新的ERROR类型结果
            return ToolResult(
                type=ToolResultType.ERROR,
                content=f"MCP tool error: {error_message}",
                metadata=result.metadata.copy() if result.metadata else {},
                timestamp=result.timestamp,
                tool_name=result.tool_name,
                execution_id=result.execution_id
            )

        # 检测内容中的success: false（嵌套格式）
        content_array = parsed_content.get("content", [])
        if isinstance(content_array, list) and len(content_array) > 0:
            first_content = content_array[0]
            if isinstance(first_content, dict) and "text" in first_content:
                try:
                    nested_json = json.loads(first_content["text"])
                    if (isinstance(nested_json, dict) and
                        nested_json.get("success") is False):

                        error_message = (nested_json.get("message") or
                                       nested_json.get("error") or
                                       "Tool execution failed")

                        logger.warning(f"Detected nested MCP tool error: {error_message}")

                        # 创建新的ERROR类型结果
                        return ToolResult(
                            type=ToolResultType.ERROR,
                            content=f"MCP tool error: {error_message}",
                            metadata=result.metadata.copy() if result.metadata else {},
                            timestamp=result.timestamp,
                            tool_name=result.tool_name,
                            execution_id=result.execution_id
                        )
                except (json.JSONDecodeError, TypeError):
                    # 解析失败，继续正常流程
                    pass

    except (json.JSONDecodeError, TypeError, AttributeError):
        # 如果不是有效的JSON或解析失败，返回原结果
        pass

    return result