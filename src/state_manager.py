# -*- coding: utf-8 -*-
"""状态管理模块"""

from typing import Literal, Optional
from dataclasses import dataclass, field


ModeType = Literal["roast", "survival"]
ChoiceType = Literal["A", "B", "C"]


@dataclass
class ConversationMessage:
    """对话消息"""
    role: str  # "user" or "assistant"
    content: str
    choice: Optional[ChoiceType] = None  # 用户选择的选项（仅用户消息）


@dataclass 
class ModeRequest:
    """模式切换请求结果"""
    accepted: bool          # 请求是否被接受
    new_mode: ModeType      # 当前/新模式
    reason: str             # 原因说明


@dataclass
class StateManager:
    """应用状态管理器"""
    
    # 当前模式
    current_mode: ModeType = "roast"
    
    # 用户期望模式（手动开关设置）
    desired_mode: ModeType | None = None
    
    # 连续选择计数器
    happy_choice_count: int = 0   # 连续选择 A 的次数
    angry_choice_count: int = 0   # 连续选择 C 的次数
    
    # 模式切换阈值
    mode_switch_threshold: int = 3
    
    # 对话历史（用于 UI 显示）
    conversation_history: list[ConversationMessage] = field(default_factory=list)
    
    def record_choice(self, choice: ChoiceType) -> Optional[str]:
        """记录用户选择，返回模式变化
        
        综合考虑情绪选择和用户期望模式：
        - 情绪驱动的自动切换优先级最高
        - 期望模式在情绪条件满足时辅助决策
        
        Args:
            choice: 用户选择的选项 "A", "B", "C"
        
        Returns:
            模式变化: "to_survival" / "to_roast" / None
        """
        if self.current_mode == "roast":
            return self._handle_roast_mode(choice)
        else:
            return self._handle_survival_mode(choice)
    
    def _handle_roast_mode(self, choice: ChoiceType) -> Optional[str]:
        """处理作死模式下的选择
        
        规则：
        - 连续 3 次 C 进入求生模式
        - 如果用户期望 survival 且选择了 C，计数加倍（更快切换）
        - 选择 A 或 B 重置计数器
        """
        if choice == "C":
            # 如果用户期望进入求生模式，加速切换
            increment = 2 if self.desired_mode == "survival" else 1
            self.angry_choice_count += increment
            
            if self.angry_choice_count >= self.mode_switch_threshold:
                self.current_mode = "survival"
                self.angry_choice_count = 0
                self.happy_choice_count = 0
                self.desired_mode = None  # 清除期望，已达成
                return "to_survival"
        else:
            # A 或 B 重置计数器
            self.angry_choice_count = 0
            # 如果用户期望求生但选了开心/中立，可能是反悔
            if self.desired_mode == "survival" and choice == "A":
                self.desired_mode = None
        
        return None
    
    def _handle_survival_mode(self, choice: ChoiceType) -> Optional[str]:
        """处理求生模式下的选择
        
        规则：
        - 连续 3 次 A 恢复作死模式
        - 如果用户期望 roast 且选择了 A，计数加倍（更快切换）
        - 选择 B 或 C 重置计数器
        """
        if choice == "A":
            # 如果用户期望进入作死模式，加速切换
            increment = 2 if self.desired_mode == "roast" else 1
            self.happy_choice_count += increment
            
            if self.happy_choice_count >= self.mode_switch_threshold:
                self.current_mode = "roast"
                self.happy_choice_count = 0
                self.angry_choice_count = 0
                self.desired_mode = None  # 清除期望，已达成
                return "to_roast"
        else:
            # B 或 C 重置计数器
            self.happy_choice_count = 0
            # 如果用户期望作死但选了愤怒，可能是反悔
            if self.desired_mode == "roast" and choice == "C":
                self.desired_mode = None
        
        return None
    
    def request_mode_change(self, target_mode: ModeType) -> ModeRequest:
        """请求模式切换（手动开关）
        
        手动开关不直接切换模式，而是设置期望模式。
        根据当前情绪计数决定是否立即切换或等待情绪确认。
        
        Args:
            target_mode: 期望切换到的模式
        
        Returns:
            ModeRequest: 包含是否接受、新模式、原因
        """
        if target_mode == self.current_mode:
            return ModeRequest(
                accepted=True,
                new_mode=self.current_mode,
                reason="already_in_mode"
            )
        
        # 检查情绪计数是否支持切换
        if target_mode == "survival":
            # 想进入求生模式：需要有一定的愤怒情绪基础
            if self.angry_choice_count >= 1:
                # 有愤怒情绪基础，立即切换
                self.current_mode = "survival"
                self.angry_choice_count = 0
                self.happy_choice_count = 0
                self.desired_mode = None
                return ModeRequest(
                    accepted=True,
                    new_mode="survival",
                    reason="emotion_supported"
                )
            else:
                # 没有情绪基础，设置期望，等待确认
                self.desired_mode = "survival"
                return ModeRequest(
                    accepted=False,
                    new_mode=self.current_mode,
                    reason="pending_emotion_confirm"
                )
        else:
            # 想进入作死模式：需要有一定的开心情绪基础
            if self.happy_choice_count >= 1:
                # 有开心情绪基础，立即切换
                self.current_mode = "roast"
                self.angry_choice_count = 0
                self.happy_choice_count = 0
                self.desired_mode = None
                return ModeRequest(
                    accepted=True,
                    new_mode="roast",
                    reason="emotion_supported"
                )
            else:
                # 没有情绪基础，设置期望，等待确认
                self.desired_mode = "roast"
                return ModeRequest(
                    accepted=False,
                    new_mode=self.current_mode,
                    reason="pending_emotion_confirm"
                )
    
    def toggle_mode(self) -> ModeType:
        """手动切换模式（直接切换，用于向后兼容）
        
        Returns:
            切换后的模式
        """
        if self.current_mode == "roast":
            self.current_mode = "survival"
        else:
            self.current_mode = "roast"
        
        # 重置计数器
        self.happy_choice_count = 0
        self.angry_choice_count = 0
        self.desired_mode = None
        
        return self.current_mode
    
    def set_mode(self, mode: ModeType):
        """设置模式
        
        Args:
            mode: 目标模式
        """
        self.current_mode = mode
        self.happy_choice_count = 0
        self.angry_choice_count = 0
        self.desired_mode = None
    
    def reset(self):
        """重置状态"""
        self.current_mode = "roast"
        self.desired_mode = None
        self.happy_choice_count = 0
        self.angry_choice_count = 0
        self.conversation_history.clear()
    
    def get_desired_mode(self) -> ModeType | None:
        """获取用户期望模式"""
        return self.desired_mode
    
    def clear_desired_mode(self):
        """清除期望模式"""
        self.desired_mode = None
    
    def add_user_message(self, content: str, choice: Optional[ChoiceType] = None):
        """添加用户消息到历史
        
        Args:
            content: 消息内容
            choice: 选项类型（如果是点击建议卡片）
        """
        self.conversation_history.append(
            ConversationMessage(role="user", content=content, choice=choice)
        )
    
    def add_assistant_message(self, content: str):
        """添加助手消息到历史
        
        Args:
            content: 消息内容
        """
        self.conversation_history.append(
            ConversationMessage(role="assistant", content=content)
        )
    
    def get_conversation_history(self) -> list[ConversationMessage]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
