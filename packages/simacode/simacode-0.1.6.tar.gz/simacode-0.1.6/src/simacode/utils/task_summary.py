"""
Task Summary Generation Utilities

This module provides utilities for generating task execution summaries
that can be used across different components of the system.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..react.engine import ReActSession

# 常量定义 - 使用国际化消息系统
DEFAULT_TASK_SUCCESS_MESSAGE = "🔍 执行摘要：\n\n📊 最终结果：\n🎉 任务执行完成"

def get_conversational_success_message(language: str = "zh") -> str:
    """获取对话成功完成消息"""
    from ..react.messages import MessageBuilder
    return MessageBuilder.conversational_completed(language).content


def generate_task_summary_content(session: "ReActSession") -> str:
    """
    Generate task execution summary content for completion messages.
    
    Args:
        session: ReAct session containing tasks and evaluations
        
    Returns:
        str: Task summary content
    """
    from ..react.engine import TaskStatus, ToolResultType
    
    successful_tasks = sum(1 for task in session.tasks if task.status == TaskStatus.COMPLETED)
    failed_tasks = sum(1 for task in session.tasks if task.status == TaskStatus.FAILED)
    total_tasks = len(session.tasks)
    
    # Handle conversational inputs with no tasks
    if total_tasks == 0:
        return get_conversational_success_message()
    
    # Generate detailed task breakdown
    content_lines = ["执行摘要：", ""]
    
    for i, task in enumerate(session.tasks, 1):
        # Get task status and evaluation
        evaluation = session.evaluations.get(task.id)
        status_emoji = "✅" if task.status == TaskStatus.COMPLETED else "❌"
        status_text = "成功" if task.status == TaskStatus.COMPLETED else "失败"
        
        # Get tools used
        tools_used = [task.tool_name] if task.tool_name else []
        tools_text = f"使用工具: {tools_used}" if tools_used else "无工具使用"
        
        # Add task summary
        task_line = f"{status_emoji} 任务 {i}: {task.description} - {status_text}"
        content_lines.append(task_line)
        content_lines.append(f"   {tools_text}")
        
        # Add evaluation details if available
        if evaluation:
            if evaluation.reasoning:
                # Truncate long reasoning for readability
                reasoning = evaluation.reasoning[:100] + "..." if len(evaluation.reasoning) > 100 else evaluation.reasoning
                content_lines.append(f"   评估: {reasoning}")

            # Show detailed error information for failed tasks
            if task.status == TaskStatus.FAILED and evaluation.evidence:
                for evidence in evaluation.evidence[:3]:  # Show up to 3 error messages
                    # Don't truncate error messages - they contain important debugging info
                    # Remove generic "MCP Error: Unknown MCP error" prefix if present
                    if "Unknown MCP error" in evidence and len(evaluation.evidence) > 1:
                        continue  # Skip generic error if we have more specific ones
                    content_lines.append(f"   错误: {evidence}")
            
            if evaluation.recommendations:
                # Show first recommendation if any
                first_rec = evaluation.recommendations[0] if evaluation.recommendations else ""
                if first_rec:
                    rec_text = first_rec[:80] + "..." if len(first_rec) > 80 else first_rec
                    content_lines.append(f"   建议: {rec_text}")
        
        # Fallback: Extract error info directly from task results if no evaluation available
        elif task.status == TaskStatus.FAILED and task.id in session.task_results:
            error_results = [r for r in session.task_results[task.id] if r.type == ToolResultType.ERROR]
            for error_result in error_results[:2]:  # Show up to 2 error messages
                error_text = error_result.content[:120] + "..." if len(error_result.content) > 120 else error_result.content
                content_lines.append(f"   错误: {error_text}")
        
        content_lines.append("")  # Empty line for spacing
    
    # Overall result
    overall_success = failed_tasks == 0 and successful_tasks > 0
    if overall_success:
        overall_emoji = "🎉"
        overall_text = f"所有任务执行成功！共完成 {successful_tasks} 个任务"
    elif successful_tasks > 0:
        overall_emoji = "⚠️"
        overall_text = f"部分任务完成：{successful_tasks} 个成功，{failed_tasks} 个失败"
    else:
        overall_emoji = "❌"
        overall_text = f"所有任务都失败了：共 {failed_tasks} 个任务失败"
    
    content_lines.extend([
        "最终结果：",
        f"{overall_emoji} {overall_text}"
        #f"⏱️ 总耗时: {(session.updated_at - session.created_at).total_seconds():.1f} 秒"
    ])
    
    return "\n".join(content_lines)