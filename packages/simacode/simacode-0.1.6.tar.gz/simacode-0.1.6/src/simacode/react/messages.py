"""
Message type system for ReAct engine output formatting.

This module provides a structured approach to message categorization, formatting,
and display for the ReAct engine's status updates and user communications.
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass


class MessageType(Enum):
    """消息类型枚举"""
    SYSTEM_INIT = "system_init"        # 系统初始化
    TASK_ACCEPTED = "task_accepted"     # 任务接受
    REASONING = "reasoning"             # 推理阶段
    PLANNING = "planning"               # 规划阶段
    EXECUTION = "execution"             # 执行阶段
    EVALUATION = "evaluation"           # 评估阶段
    CONVERSATION = "conversation"       # 对话回复
    RESULT = "result"                  # 最终结果
    ERROR = "error"                    # 错误信息
    PROGRESS = "progress"              # 进度更新
    PROCESSING = "processing"          # 处理状态
    AI_RESPONSE = "ai_response"        # AI回复
    SUMMARY = "summary"                # 结果摘要
    CONFIRMATION = "confirmation"      # 确认流程
    CONFIRMATION_COMPLETED = "confirmation_completed"  # 确认完成
    TOOL_EXECUTION = "tool_execution"  # 工具执行
    USER_INPUT = "user_input"          # 用户输入
    TASK_INIT = "task_init"            # 任务初始化


class MessageLevel(Enum):
    """消息级别"""
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    SUCCESS = "success"


class MessageCategory(Enum):
    """消息分类"""
    ENGINE = "engine"        # 引擎状态
    TASK = "task"           # 任务相关
    USER = "user"           # 用户交互
    SYSTEM = "system"       # 系统信息
    TOOL = "tool"           # 工具执行


@dataclass
class MessageConfig:
    """消息配置"""
    show_timestamp: bool = False
    show_category: bool = True
    show_level: bool = True
    language: str = "zh"  # zh/en
    use_emoji: bool = True
    color_enabled: bool = True
    # 默认使用简洁的状态图标模式
    only_status_emoji: bool = True


class MessageFormatter:
    """消息格式化器"""

    # 图标映射
    EMOJI_MAP = {
        MessageType.SYSTEM_INIT: "🚀",
        MessageType.TASK_ACCEPTED: "📝",
        MessageType.REASONING: "🔍",
        MessageType.PLANNING: "🔄",
        MessageType.EXECUTION: "⚡",
        MessageType.EVALUATION: "📊",
        MessageType.CONVERSATION: "💬",
        MessageType.RESULT: "✅",
        MessageType.ERROR: "❌",
        MessageType.PROGRESS: "🔄",
        MessageType.PROCESSING: "🔄",
        MessageType.AI_RESPONSE: "👤",
        MessageType.SUMMARY: "📋",
        MessageType.CONFIRMATION: "❓",  # 等待用户选择
        MessageType.CONFIRMATION_COMPLETED: "🎯",  # 确认完成
        MessageType.TOOL_EXECUTION: "🔧",
        MessageType.USER_INPUT: "👤",
        MessageType.TASK_INIT: "🎯",
    }

    # 级别颜色映射（Rich markup）
    LEVEL_COLORS = {
        MessageLevel.DEBUG: "[dim]",
        MessageLevel.INFO: "[blue]",
        MessageLevel.WARN: "[yellow]",
        MessageLevel.ERROR: "[red]",
        MessageLevel.SUCCESS: "[green]",
    }

    # 分类颜色映射
    CATEGORY_COLORS = {
        MessageCategory.ENGINE: "[bold blue]",
        MessageCategory.TASK: "[bold green]",
        MessageCategory.USER: "[bold magenta]",
        MessageCategory.SYSTEM: "[bold cyan]",
    }

    # 多语言文本
    TRANSLATIONS = {
        "zh": {
            MessageType.SYSTEM_INIT: "引擎已启动",
            MessageType.TASK_ACCEPTED: "任务已接收",
            MessageType.REASONING: "推理分析中",
            MessageType.PLANNING: "任务规划中",
            MessageType.EXECUTION: "执行中",
            MessageType.EVALUATION: "评估中",
            MessageType.CONVERSATION: "对话回复",
            MessageType.RESULT: "执行完成",
            MessageType.ERROR: "错误",
            MessageType.PROGRESS: "进度更新",
            MessageType.PROCESSING: "处理中",
            MessageType.AI_RESPONSE: "AI回复",
            MessageType.SUMMARY: "执行摘要",
            MessageType.CONFIRMATION: "确认流程",
            MessageType.CONFIRMATION_COMPLETED: "确认完成",
            MessageType.TOOL_EXECUTION: "工具执行",
            MessageType.USER_INPUT: "用户输入",
            MessageType.TASK_INIT: "任务初始化",
            MessageCategory.ENGINE: "引擎",
            MessageCategory.TASK: "任务",
            MessageCategory.USER: "用户",
            MessageCategory.SYSTEM: "系统",
            # 常用消息内容
            "conversational_interaction_completed": "对话完成",
            "task_completed_successfully": "任务执行成功完成",
            "no_tasks_executed": "未执行任何任务",
            "processing_user_input": "处理中",
        },
        "en": {
            MessageType.SYSTEM_INIT: "Engine Started",
            MessageType.TASK_ACCEPTED: "Task Accepted",
            MessageType.REASONING: "Reasoning",
            MessageType.PLANNING: "Planning",
            MessageType.EXECUTION: "Executing",
            MessageType.EVALUATION: "Evaluating",
            MessageType.CONVERSATION: "Conversation",
            MessageType.RESULT: "Result",
            MessageType.ERROR: "Error",
            MessageType.PROGRESS: "Progress",
            MessageType.PROCESSING: "Processing",
            MessageType.AI_RESPONSE: "AI Response",
            MessageType.SUMMARY: "Summary",
            MessageType.CONFIRMATION: "Confirmation",
            MessageType.CONFIRMATION_COMPLETED: "Confirmed",
            MessageType.TOOL_EXECUTION: "Tool Execution",
            MessageType.USER_INPUT: "User Input",
            MessageType.TASK_INIT: "Task Initialization",
            MessageCategory.ENGINE: "ENGINE",
            MessageCategory.TASK: "TASK",
            MessageCategory.USER: "USER",
            MessageCategory.SYSTEM: "SYSTEM",
            # 常用消息内容
            "conversational_interaction_completed": "Conversation completed",
            "task_completed_successfully": "Task completed successfully",
            "no_tasks_executed": "No tasks were executed",
            "processing_user_input": "Processing",
        }
    }

    def __init__(self, config: Optional[MessageConfig] = None):
        self.config = config or MessageConfig()

    def translate(self, key: Union[str, MessageType, MessageCategory]) -> str:
        """翻译消息键值"""
        return self.TRANSLATIONS[self.config.language].get(key, str(key))

    def format_message(
        self,
        message_type: MessageType,
        content: str,
        category: MessageCategory = MessageCategory.ENGINE,
        level: MessageLevel = MessageLevel.INFO,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """格式化消息"""
        parts = []

        # 时间戳
        if self.config.show_timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
            parts.append(f"[{timestamp}]")

        # 分类和级别标签
        if self.config.show_category or self.config.show_level:
            label_parts = []
            if self.config.show_category:
                cat_text = self.translate(category)
                if self.config.color_enabled:
                    cat_text = f"{self.CATEGORY_COLORS[category]}{cat_text}[/]"
                label_parts.append(cat_text)

            if self.config.show_level:
                level_text = level.value.upper()
                if self.config.color_enabled:
                    level_text = f"{self.LEVEL_COLORS[level]}{level_text}[/]"
                label_parts.append(level_text)

            parts.append(f"[{':'.join(label_parts)}]")

        # 图标
        if self.config.use_emoji:
            emoji = self.EMOJI_MAP.get(message_type, "")

            # 如果启用了仅状态图标模式，只显示重要的状态图标
            if self.config.only_status_emoji:
                # 重要的状态图标：成功、错误、警告、用户确认、用户输入、报告
                important_emojis = {"✅", "❌", "⚠️", "❓", "👤", "📋"}
                if emoji in important_emojis:
                    parts.append(emoji)
            elif emoji:
                parts.append(emoji)

        # 内容
        parts.append(content)

        # 元数据
        if metadata:
            meta_info = []
            if "attempt" in metadata:
                meta_info.append(f"尝试 {metadata['attempt']}")
            if "progress" in metadata:
                meta_info.append(f"{metadata['progress']}")
            # 移除不必要的步数显示，对用户没有价值
            # if "step_count" in metadata:
            #     meta_info.append(f"{metadata['step_count']}步")

            if meta_info:
                parts.append(f"({', '.join(meta_info)})")

        return " ".join(parts)


@dataclass
class ReActMessage:
    """ReAct引擎消息"""
    type: MessageType
    content: str
    category: MessageCategory = MessageCategory.ENGINE
    level: MessageLevel = MessageLevel.INFO
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    session_id: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "type": self.type.value,
            "content": self.content,
            "category": self.category.value,
            "level": self.level.value,
            "metadata": self.metadata or {},
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
        }

    def format(self, formatter: Optional[MessageFormatter] = None) -> str:
        """格式化消息"""
        if formatter is None:
            formatter = MessageFormatter()

        return formatter.format_message(
            self.type,
            self.content,
            self.category,
            self.level,
            self.metadata
        )


class MessageBuilder:
    """消息构建器"""

    @staticmethod
    def _get_formatter(language: str = "zh") -> MessageFormatter:
        """获取格式化器实例"""
        config = MessageConfig(language=language)
        return MessageFormatter(config)

    @staticmethod
    def system_init(mode: str = "ReAct", language: str = "zh") -> ReActMessage:
        """系统初始化消息"""
        return ReActMessage(
            type=MessageType.SYSTEM_INIT,
            content=f"{mode}引擎已启动 - 智能任务编排模式",
            category=MessageCategory.ENGINE,
            level=MessageLevel.SUCCESS
        )

    @staticmethod
    def task_accepted(user_input: str) -> ReActMessage:
        """任务接受消息"""
        return ReActMessage(
            type=MessageType.TASK_ACCEPTED,
            content=f"任务已接收: \"{user_input}\"",
            category=MessageCategory.TASK,
            level=MessageLevel.INFO
        )

    @staticmethod
    def reasoning(content: str) -> ReActMessage:
        """推理阶段消息"""
        return ReActMessage(
            type=MessageType.REASONING,
            content=content,
            category=MessageCategory.ENGINE,
            level=MessageLevel.DEBUG
        )

    @staticmethod
    def planning(content: str, attempt: int = 1, max_attempts: int = 3) -> ReActMessage:
        """规划阶段消息"""
        return ReActMessage(
            type=MessageType.PLANNING,
            content=content,
            category=MessageCategory.ENGINE,
            level=MessageLevel.DEBUG,
            metadata={"attempt": f"{attempt}/{max_attempts}"}
        )

    @staticmethod
    def execution(task_description: str, current: int = 1, total: int = 1) -> ReActMessage:
        """执行阶段消息"""
        return ReActMessage(
            type=MessageType.EXECUTION,
            content=task_description,
            category=MessageCategory.TASK,
            level=MessageLevel.INFO,
            metadata={"progress": f"{current}/{total}"}
        )

    @staticmethod
    def conversation(content: str) -> ReActMessage:
        """对话回复消息"""
        return ReActMessage(
            type=MessageType.CONVERSATION,
            content=content,
            category=MessageCategory.USER,
            level=MessageLevel.SUCCESS
        )

    @staticmethod
    def result(content: str, task_count: int = 0, step_count: int = 0) -> ReActMessage:
        """结果消息"""
        return ReActMessage(
            type=MessageType.RESULT,
            content=content,
            category=MessageCategory.ENGINE,
            level=MessageLevel.SUCCESS,
            metadata={"task_count": task_count, "step_count": step_count}
        )

    @staticmethod
    def error(content: str, error_type: Optional[str] = None) -> ReActMessage:
        """错误消息"""
        metadata = {"error_type": error_type} if error_type else None
        return ReActMessage(
            type=MessageType.ERROR,
            content=content,
            category=MessageCategory.SYSTEM,
            level=MessageLevel.ERROR,
            metadata=metadata
        )

    @staticmethod
    def progress(content: str, percentage: Optional[int] = None) -> ReActMessage:
        """进度更新消息"""
        metadata = {"percentage": percentage} if percentage is not None else None
        return ReActMessage(
            type=MessageType.PROGRESS,
            content=content,
            category=MessageCategory.ENGINE,
            level=MessageLevel.INFO,
            metadata=metadata
        )

    @staticmethod
    def processing(content: str) -> ReActMessage:
        """处理状态消息"""
        return ReActMessage(
            type=MessageType.PROCESSING,
            content=content,
            category=MessageCategory.SYSTEM,
            level=MessageLevel.INFO
        )

    @staticmethod
    def ai_response(content: str) -> ReActMessage:
        """AI回复消息"""
        return ReActMessage(
            type=MessageType.AI_RESPONSE,
            content=content,
            category=MessageCategory.USER,
            level=MessageLevel.SUCCESS
        )

    @staticmethod
    def summary(content: str, step_count: Optional[int] = None) -> ReActMessage:
        """执行摘要消息"""
        metadata = {"step_count": step_count} if step_count is not None else None
        return ReActMessage(
            type=MessageType.SUMMARY,
            content=content,
            category=MessageCategory.SYSTEM,
            level=MessageLevel.INFO,
            metadata=metadata
        )

    @staticmethod
    def conversational_completed(language: str = "zh") -> ReActMessage:
        """对话完成消息"""
        formatter = MessageBuilder._get_formatter(language)
        content = formatter.translate("conversational_interaction_completed")
        return ReActMessage(
            type=MessageType.RESULT,
            content=content,
            category=MessageCategory.ENGINE,
            level=MessageLevel.SUCCESS
        )

    @staticmethod
    def confirmation_request(content: str) -> ReActMessage:
        """确认请求消息"""
        return ReActMessage(
            type=MessageType.CONFIRMATION,
            content=content,
            category=MessageCategory.SYSTEM,
            level=MessageLevel.INFO
        )

    @staticmethod
    def confirmation_completed(content: str) -> ReActMessage:
        """确认完成消息"""
        return ReActMessage(
            type=MessageType.CONFIRMATION_COMPLETED,
            content=content,
            category=MessageCategory.SYSTEM,
            level=MessageLevel.SUCCESS
        )

    @staticmethod
    def user_input_echo(content: str) -> ReActMessage:
        """用户输入回显消息"""
        return ReActMessage(
            type=MessageType.USER_INPUT,
            content=content,
            category=MessageCategory.USER,
            level=MessageLevel.INFO
        )

    @staticmethod
    def tool_execution(content: str, tool_name: Optional[str] = None) -> ReActMessage:
        """工具执行消息"""
        metadata = {"tool_name": tool_name} if tool_name else None
        return ReActMessage(
            type=MessageType.TOOL_EXECUTION,
            content=content,
            category=MessageCategory.SYSTEM,
            level=MessageLevel.DEBUG,
            metadata=metadata
        )

    @staticmethod
    def task_initialization(content: str) -> ReActMessage:
        """任务初始化消息"""
        return ReActMessage(
            type=MessageType.TASK_INIT,
            content=content,
            category=MessageCategory.TASK,
            level=MessageLevel.INFO
        )