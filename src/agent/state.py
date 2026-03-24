from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time

@dataclass
class AgentState:
    """智能代理状态管理类"""
    
    # 对话历史
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    
    # 当前任务信息
    current_task: Optional[str] = None
    task_id: Optional[str] = None
    task_start_time: Optional[float] = None
    
    # 执行轨迹
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    
    # 工具执行结果
    tool_results: Dict[str, Any] = field(default_factory=dict)
    
    # 错误信息
    error_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # 上下文信息
    context: Dict[str, Any] = field(default_factory=dict)
    
    # 对话状态
    is_active: bool = True
    last_activity_time: float = field(default_factory=time.time)
    
    def add_message(self, role: str, content: str) -> None:
        """
        添加对话消息
        
        Args:
            role: 角色 (user/assistant)
            content: 消息内容
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        self.last_activity_time = time.time()
    
    def add_execution_step(self, step_type: str, content: Any, **kwargs) -> None:
        """
        添加执行步骤
        
        Args:
            step_type: 步骤类型 (thought/action/observation/answer)
            content: 步骤内容
            **kwargs: 额外参数
        """
        step = {
            "type": step_type,
            "content": content,
            "timestamp": time.time(),
            **kwargs
        }
        self.execution_trace.append(step)
    
    def add_tool_result(self, tool_name: str, result: Any) -> None:
        """
        添加工具执行结果
        
        Args:
            tool_name: 工具名称
            result: 执行结果
        """
        self.tool_results[tool_name] = {
            "result": result,
            "timestamp": time.time()
        }
    
    def add_error(self, error_type: str, message: str, **kwargs) -> None:
        """
        添加错误信息
        
        Args:
            error_type: 错误类型
            message: 错误消息
            **kwargs: 额外参数
        """
        error = {
            "type": error_type,
            "message": message,
            "timestamp": time.time(),
            **kwargs
        }
        self.error_history.append(error)
    
    def set_current_task(self, task: str) -> None:
        """
        设置当前任务
        
        Args:
            task: 任务描述
        """
        self.current_task = task
        self.task_id = f"task_{int(time.time())}"
        self.task_start_time = time.time()
    
    def get_recent_history(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """
        获取最近的对话历史
        
        Args:
            max_messages: 最大消息数
            
        Returns:
            最近的对话历史
        """
        return self.conversation_history[-max_messages:]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        获取所有对话消息
        
        Returns:
            所有对话消息
        """
        return self.conversation_history
    
    def get_execution_summary(self) -> str:
        """
        获取执行摘要
        
        Returns:
            执行摘要字符串
        """
        summary = []
        for step in self.execution_trace:
            if step["type"] == "thought":
                summary.append(f"思考: {step['content']}")
            elif step["type"] == "action":
                summary.append(f"行动: {step['content']}")
            elif step["type"] == "observation":
                summary.append(f"观察: {step['content']}")
            elif step["type"] == "answer":
                summary.append(f"回答: {step['content']}")
        return "\n".join(summary)
    
    def clear(self) -> None:
        """
        清除状态
        """
        self.conversation_history.clear()
        self.current_task = None
        self.task_id = None
        self.task_start_time = None
        self.execution_trace.clear()
        self.tool_results.clear()
        self.error_history.clear()
        self.context.clear()
        self.last_activity_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            状态字典
        """
        return {
            "conversation_history": self.conversation_history,
            "current_task": self.current_task,
            "task_id": self.task_id,
            "task_start_time": self.task_start_time,
            "execution_trace": self.execution_trace,
            "tool_results": self.tool_results,
            "error_history": self.error_history,
            "context": self.context,
            "is_active": self.is_active,
            "last_activity_time": self.last_activity_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        """
        从字典创建状态
        
        Args:
            data: 状态字典
            
        Returns:
            AgentState实例
        """
        state = cls()
        state.conversation_history = data.get("conversation_history", [])
        state.current_task = data.get("current_task")
        state.task_id = data.get("task_id")
        state.task_start_time = data.get("task_start_time")
        state.execution_trace = data.get("execution_trace", [])
        state.tool_results = data.get("tool_results", {})
        state.error_history = data.get("error_history", [])
        state.context = data.get("context", {})
        state.is_active = data.get("is_active", True)
        state.last_activity_time = data.get("last_activity_time", time.time())
        return state
