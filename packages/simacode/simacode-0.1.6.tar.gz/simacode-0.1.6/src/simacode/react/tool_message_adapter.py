"""
工具消息适配器 (Tool Message Adapter)

此模块负责将ToolResult转换为统一的ReAct消息格式，
实现工具执行信息与消息分类体系的无缝集成。
"""

import logging
import json

from typing import Dict, Any, Optional
from ..tools import ToolResult, ToolResultType
from .messages import ReActMessage, MessageType, MessageLevel, MessageCategory

logger = logging.getLogger(__name__)

class ToolMessageAdapter:
    """
    工具消息适配器

    将ToolResult转换为统一的ReAct消息格式，保持现有ToolResult系统不变
    的同时，提供统一的消息输出体验。
    """

    # ToolResultType到MessageType的映射
    TOOL_RESULT_TO_MESSAGE_TYPE = {
        ToolResultType.INFO: MessageType.TOOL_EXECUTION,
        ToolResultType.SUCCESS: MessageType.TOOL_EXECUTION,
        ToolResultType.ERROR: MessageType.ERROR,
        ToolResultType.WARNING: MessageType.TOOL_EXECUTION,
        ToolResultType.OUTPUT: MessageType.TOOL_EXECUTION,
    }

    # ToolResultType到MessageLevel的映射
    TOOL_RESULT_TO_MESSAGE_LEVEL = {
        ToolResultType.INFO: MessageLevel.INFO,
        ToolResultType.SUCCESS: MessageLevel.SUCCESS,
        ToolResultType.ERROR: MessageLevel.ERROR,
        ToolResultType.WARNING: MessageLevel.WARN,
        ToolResultType.OUTPUT: MessageLevel.SUCCESS,
    }

    # 需要过滤的技术性消息模式
    TECHNICAL_MESSAGE_PATTERNS = [
        "execution finished in",
        "Starting.*execution",
        "Writing to file:",
        "Successfully wrote file:",
        "Reading from file:",
        "File read completed",
    ]

    @staticmethod
    def convert_tool_result(
        tool_result: ToolResult,
        session_id: Optional[str] = None,
        filter_technical: bool = True
    ) -> Optional[ReActMessage]:
        """
        将ToolResult转换为ReActMessage

        Args:
            tool_result: 原始工具结果
            session_id: 会话ID
            filter_technical: 是否过滤技术性消息

        Returns:
            ReActMessage或None（如果消息被过滤）
        """

        # 过滤技术性消息
        if filter_technical and ToolMessageAdapter._should_filter_message(tool_result.content):
            return None

        # 获取消息类型和级别
        message_type = ToolMessageAdapter.TOOL_RESULT_TO_MESSAGE_TYPE.get(
            tool_result.type, MessageType.TOOL_EXECUTION
        )
        message_level = ToolMessageAdapter.TOOL_RESULT_TO_MESSAGE_LEVEL.get(
            tool_result.type, MessageLevel.INFO
        )

        # 优化消息内容
        content = ToolMessageAdapter._optimize_message_content(tool_result)

        # 创建ReAct消息
        return ReActMessage(
            type=message_type,
            content=content,
            category=MessageCategory.SYSTEM,
            level=message_level,
            metadata={
                "tool_name": tool_result.tool_name,
                "execution_id": tool_result.execution_id,
                "original_type": tool_result.type.value,
                "original_metadata": tool_result.metadata
            },
            session_id=session_id
        )

    @staticmethod
    def _should_filter_message(content: str) -> bool:
        """
        判断是否应该过滤技术性消息

        Args:
            content: 消息内容

        Returns:
            True如果应该过滤，False否则
        """
        import re

        for pattern in ToolMessageAdapter.TECHNICAL_MESSAGE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def _optimize_message_content(tool_result: ToolResult) -> str:
        """
        优化工具消息内容，使其更用户友好

        Args:
            tool_result: 工具结果

        Returns:
            优化后的消息内容
        """
        content = tool_result.content
        logger.debug(f"[DEBUG_OPTIMIZE] tool_name={tool_result.tool_name}, type={tool_result.type}, content_len={len(tool_result.content)}, preview={tool_result.content}, metadata={tool_result.metadata}")
        # 根据工具类型和结果类型进行内容优化
        if tool_result.type == ToolResultType.SUCCESS:
            # 成功消息简化
            if "file_write" in str(tool_result.tool_name):
                if "Successfully wrote file:" in content:
                    # 从路径中提取文件名
                    import os
                    path_start = content.find("Successfully wrote file:") + len("Successfully wrote file:")
                    file_path = path_start.strip() if path_start else content
                    if file_path and os.path.exists(file_path.strip()):
                        filename = os.path.basename(file_path.strip())
                        return f"✅ 文件创建成功: {filename}"
            elif "universal_ocr" in str(tool_result.tool_name):
                if "OCR processing completed" in content:
                    return "✅ 图像文字识别完成"
            elif "email_smtp" in str(tool_result.tool_name):
                if "Email sent successfully" in content:
                    return "✅ 邮件发送成功"

        elif tool_result.type == ToolResultType.INFO:
            # 信息消息优化
            if "file_write" in str(tool_result.tool_name):
                if "Writing to file:" in content:
                    return None  # 这类消息将被过滤
            elif "universal_ocr" in str(tool_result.tool_name):
                if "Starting OCR processing" in content:
                    return "🔍 开始识别图像文字..."

        elif tool_result.type == ToolResultType.OUTPUT:
            # 输出结果消息 - 通常包含重要内容，保持原样但添加标识
            try:
                parsed_content = json.loads(content.strip())
                result = parsed_content.get("isError", False) and "失败" or "成功"
                content_data = json.loads(parsed_content.get("content", "")[0]["text"])

                return f"工具 {tool_result.tool_name} 执行{result}\n 详情：{content_data["message"]}"
            except Exception as e:
                logger.warning(f"[DEBUG_OPTIMIZE] Failed to parse OUTPUT content: {e}")
                return f"{tool_result.tool_name}执行完成，详情请查看日志"

        # 默认返回原内容
        return content

    @staticmethod
    def convert_to_dict(
        tool_result: ToolResult,
        session_id: Optional[str] = None,
        filter_technical: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        将ToolResult直接转换为字典格式（用于流式输出）

        Args:
            tool_result: 原始工具结果
            session_id: 会话ID
            filter_technical: 是否过滤技术性消息

        Returns:
            消息字典或None（如果消息被过滤）
        """
        react_message = ToolMessageAdapter.convert_tool_result(
            tool_result, session_id, filter_technical
        )

        return react_message.to_dict() if react_message else None


class ToolProgressTracker:
    """
    工具执行进度跟踪器

    跟踪工具执行状态，提供更好的用户反馈
    """

    def __init__(self):
        self.active_tools: Dict[str, Dict[str, Any]] = {}

    def start_tool_execution(self, tool_name: str, execution_id: str, description: str = "") -> ReActMessage:
        """
        开始工具执行

        Args:
            tool_name: 工具名称
            execution_id: 执行ID
            description: 执行描述

        Returns:
            工具执行开始消息
        """
        import time

        self.active_tools[execution_id] = {
            "tool_name": tool_name,
            "start_time": time.time(),
            "description": description
        }

        # 友好的工具名称映射
        friendly_names = {
            "file_write": "文件写入",
            "file_read": "文件读取",
            "universal_ocr": "图像文字识别",
            "email_smtp": "邮件发送",
            "bash": "命令执行"
        }

        friendly_name = friendly_names.get(tool_name, tool_name)
        content = f"开始{friendly_name}" + (f": {description}" if description else "")

        return ReActMessage(
            type=MessageType.TOOL_EXECUTION,
            content=content,
            category=MessageCategory.SYSTEM,
            level=MessageLevel.INFO,
            metadata={
                "tool_name": tool_name,
                "execution_id": execution_id,
                "status": "started"
            }
        )

    def complete_tool_execution(self, execution_id: str, success: bool = True) -> Optional[ReActMessage]:
        """
        完成工具执行

        Args:
            execution_id: 执行ID
            success: 是否成功

        Returns:
            工具执行完成消息
        """
        import time

        if execution_id not in self.active_tools:
            return None

        tool_info = self.active_tools.pop(execution_id)
        execution_time = time.time() - tool_info["start_time"]

        status = "完成" if success else "失败"
        level = MessageLevel.SUCCESS if success else MessageLevel.ERROR

        return ReActMessage(
            type=MessageType.TOOL_EXECUTION,
            content=f"{tool_info['tool_name']}{status}",
            category=MessageCategory.SYSTEM,
            level=level,
            metadata={
                "tool_name": tool_info["tool_name"],
                "execution_id": execution_id,
                "execution_time": execution_time,
                "status": "completed" if success else "failed"
            }
        )