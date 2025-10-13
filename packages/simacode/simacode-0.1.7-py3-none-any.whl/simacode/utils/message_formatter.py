"""
Enhanced message formatting utilities for SimaCode CLI and API output.

This module provides utilities to format and display ReAct engine messages
in a consistent, configurable way across CLI and API interfaces.
"""

from typing import Optional, Dict, Any, Union
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from ..react.messages import (
    ReActMessage, MessageFormatter, MessageConfig,
    MessageType, MessageLevel, MessageCategory
)


class RichMessageFormatter(MessageFormatter):
    """Rich-enhanced message formatter for CLI output"""

    def __init__(self, console: Console, config: Optional[MessageConfig] = None):
        super().__init__(config)
        self.console = console

    def format_for_console(self, message: ReActMessage) -> str:
        """Format message for Rich console output"""
        formatted = self.format_message(
            message.type,
            message.content,
            message.category,
            message.level,
            message.metadata
        )
        return formatted

    def print_message(self, message: ReActMessage, end: str = "\n"):
        """Print message to console with Rich formatting"""
        formatted = self.format_for_console(message)
        self.console.print(formatted, end=end)

    def create_status_panel(self, message: ReActMessage) -> Panel:
        """Create a Rich panel for important status messages"""
        title = self.TRANSLATIONS[self.config.language].get(
            message.type, message.type.value
        )

        style = "green" if message.level == MessageLevel.SUCCESS else "blue"

        return Panel(
            message.content,
            title=f"{self.EMOJI_MAP.get(message.type, '')} {title}",
            style=style,
            padding=(0, 1)
        )

    def create_progress_table(self, messages: list[ReActMessage]) -> Table:
        """Create a progress table from multiple messages"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("阶段", style="dim", width=12)
        table.add_column("状态", justify="center")
        table.add_column("描述", style="cyan")

        for msg in messages:
            stage = self.TRANSLATIONS[self.config.language].get(msg.type, msg.type.value)
            status = self.EMOJI_MAP.get(msg.type, "")
            table.add_row(stage, status, msg.content)

        return table


class APIMessageFormatter:
    """Message formatter for API responses"""

    @staticmethod
    def format_for_api(message: ReActMessage) -> Dict[str, Any]:
        """Format message for API JSON response"""
        return message.to_dict()

    @staticmethod
    def format_stream_chunk(message: ReActMessage) -> str:
        """Format message as SSE stream chunk"""
        import json
        data = APIMessageFormatter.format_for_api(message)
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    @staticmethod
    def format_websocket_message(message: ReActMessage) -> Dict[str, Any]:
        """Format message for WebSocket transmission"""
        return {
            "event": "react_message",
            "data": message.to_dict()
        }


class MessageQueue:
    """Message queue for batch processing and display"""

    def __init__(self, max_size: int = 100):
        self.messages: list[ReActMessage] = []
        self.max_size = max_size

    def add(self, message: ReActMessage):
        """Add message to queue"""
        self.messages.append(message)
        if len(self.messages) > self.max_size:
            self.messages.pop(0)

    def get_by_type(self, message_type: MessageType) -> list[ReActMessage]:
        """Get messages by type"""
        return [msg for msg in self.messages if msg.type == message_type]

    def get_by_level(self, level: MessageLevel) -> list[ReActMessage]:
        """Get messages by level"""
        return [msg for msg in self.messages if msg.level == level]

    def get_recent(self, count: int = 10) -> list[ReActMessage]:
        """Get recent messages"""
        return self.messages[-count:]

    def clear(self):
        """Clear all messages"""
        self.messages.clear()

    def to_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        type_counts = {}
        level_counts = {}

        for msg in self.messages:
            type_counts[msg.type.value] = type_counts.get(msg.type.value, 0) + 1
            level_counts[msg.level.value] = level_counts.get(msg.level.value, 0) + 1

        return {
            "total_messages": len(self.messages),
            "by_type": type_counts,
            "by_level": level_counts,
            "latest_timestamp": self.messages[-1].timestamp.isoformat() if self.messages else None
        }


def create_default_formatter(console: Optional[Console] = None) -> RichMessageFormatter:
    """Create default message formatter with optimal settings"""
    if console is None:
        console = Console()

    config = MessageConfig(
        show_timestamp=False,
        show_category=True,
        show_level=False,  # Simplify for better readability
        language="zh",
        use_emoji=True,
        color_enabled=True
    )

    return RichMessageFormatter(console, config)


def create_debug_formatter(console: Optional[Console] = None) -> RichMessageFormatter:
    """Create debug message formatter with detailed output"""
    if console is None:
        console = Console()

    config = MessageConfig(
        show_timestamp=True,
        show_category=True,
        show_level=True,
        language="zh",
        use_emoji=True,
        color_enabled=True
    )

    return RichMessageFormatter(console, config)