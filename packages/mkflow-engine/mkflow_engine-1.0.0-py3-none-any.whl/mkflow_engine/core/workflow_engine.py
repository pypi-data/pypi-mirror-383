"""
IDE Agent工作流引擎核心类

基于六大原则设计：阶段→步骤→工作节点→反馈→结束+指针
"""

import json
import jsonschema
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class NodeType(Enum):
    """工作节点类型枚举"""
    ACTION = "action"
    DECISION = "decision"
    INPUT = "input"
    OUTPUT = "output"


class EndConditionType(Enum):
    """结束条件类型枚举"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    MANUAL = "manual"


@dataclass
class WorkNode:
    """工作节点数据类"""
    id: str
    name: str
    type: NodeType
    action: Optional[str] = None
    conditions: List[str] = None
    feedback_rules: Dict[str, str] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.feedback_rules is None:
            self.feedback_rules = {}


@dataclass
class Pointer:
    """指针数据类"""
    id: str
    name: str
    target: str
    condition: Optional[str] = None


@dataclass
class Step:
    """步骤数据类"""
    id: str
    name: str
    description: Optional[str] = None
    work_nodes: List[WorkNode] = None
    pointers: List[Pointer] = None
    
    def __post_init__(self):
        if self.work_nodes is None:
            self.work_nodes = []
        if self.pointers is None:
            self.pointers = []


@dataclass
class EndCondition:
    """结束条件数据类"""
    type: EndConditionType
    condition: str
    message: Optional[str] = None


@dataclass
class Stage:
    """阶段数据类"""
    id: str
    name: str
    description: Optional[str] = None
    steps: List[Step] = None
    end_conditions: List[EndCondition] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.end_conditions is None:
            self.end_conditions = []


@dataclass
class Workflow:
    """工作流数据类"""
    id: str
    name: str
    version: str
    description: Optional[str] = None
    stages: List[Stage] = None
    
    def __post_init__(self):
        if self.stages is None:
            self.stages = []


class WorkflowEngine:
    """工作流引擎主类"""
    
    def __init__(self, schema_file: str = None):
        """
        初始化工作流引擎
        
        Args:
            schema_file: JSON Schema文件路径
        """
        self.schema = None
        if schema_file:
            self.load_schema(schema_file)
        
        self.current_workflow: Optional[Workflow] = None
        self.current_stage: Optional[Stage] = None
        self.current_step: Optional[Step] = None
        self.current_node: Optional[WorkNode] = None
        self.pointer_position: Optional[str] = None
        
        # 状态跟踪
        self.execution_history: List[Dict[str, Any]] = []
        self.feedback_messages: List[str] = []
    
    def load_schema(self, schema_file: str) -> None:
        """
        加载JSON Schema
        
        Args:
            schema_file: Schema文件路径
        """
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            print(f"✅ Schema加载成功: {schema_file}")
        except Exception as e:
            print(f"❌ Schema加载失败: {e}")
            raise
    
    def validate_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """
        验证工作流数据是否符合Schema
        
        Args:
            workflow_data: 工作流数据字典
            
        Returns:
            bool: 验证是否通过
        """
        if not self.schema:
            print("⚠️ 未加载Schema，跳过验证")
            return True
        
        try:
            jsonschema.validate(workflow_data, self.schema)
            print("✅ 工作流数据验证通过")
            return True
        except jsonschema.ValidationError as e:
            print(f"❌ 工作流数据验证失败: {e}")
            return False
    
    def parse_workflow(self, workflow_data: Dict[str, Any]) -> Workflow:
        """
        解析工作流数据并创建Workflow对象
        
        Args:
            workflow_data: 工作流数据字典
            
        Returns:
            Workflow: 解析后的工作流对象
        """
        if not self.validate_workflow(workflow_data):
            raise ValueError("工作流数据验证失败")
        
        workflow_info = workflow_data['workflow']
        workflow = Workflow(
            id=workflow_info['id'],
            name=workflow_info['name'],
            version=workflow_info['version'],
            description=workflow_info.get('description')
        )
        
        # 解析阶段
        for stage_data in workflow_data['stages']:
            stage = Stage(
                id=stage_data['id'],
                name=stage_data['name'],
                description=stage_data.get('description')
            )
            
            # 解析步骤
            for step_data in stage_data.get('steps', []):
                step = Step(
                    id=step_data['id'],
                    name=step_data['name'],
                    description=step_data.get('description')
                )
                
                # 解析工作节点
                for node_data in step_data.get('work_nodes', []):
                    work_node = WorkNode(
                        id=node_data['id'],
                        name=node_data['name'],
                        type=NodeType(node_data['type']),
                        action=node_data.get('action'),
                        conditions=node_data.get('conditions', []),
                        feedback_rules=node_data.get('feedback_rules', {})
                    )
                    step.work_nodes.append(work_node)
                
                # 解析指针
                for pointer_data in step_data.get('pointers', []):
                    pointer = Pointer(
                        id=pointer_data['id'],
                        name=pointer_data['name'],
                        target=pointer_data['target'],
                        condition=pointer_data.get('condition')
                    )
                    step.pointers.append(pointer)
                
                stage.steps.append(step)
            
            # 解析结束条件
            for end_cond_data in stage_data.get('end_conditions', []):
                end_condition = EndCondition(
                    type=EndConditionType(end_cond_data['type']),
                    condition=end_cond_data['condition'],
                    message=end_cond_data.get('message')
                )
                stage.end_conditions.append(end_condition)
            
            workflow.stages.append(stage)
        
        self.current_workflow = workflow
        return workflow
    
    def start_stage(self, stage_id: str) -> bool:
        """
        开始执行特定阶段
        
        Args:
            stage_id: 阶段ID
            
        Returns:
            bool: 是否成功开始
        """
        if not self.current_workflow:
            print("❌ 未加载工作流")
            return False
        
        stage = next((s for s in self.current_workflow.stages if s.id == stage_id), None)
        if not stage:
            print(f"❌ 未找到阶段: {stage_id}")
            return False
        
        self.current_stage = stage
        self.current_step = None
        self.current_node = None
        self.pointer_position = None
        
        print(f"🚀 开始执行阶段: {stage.name}")
        self._add_feedback(f"开始执行阶段: {stage.name}")
        
        return True
    
    def execute_step(self, step_id: str) -> bool:
        """
        执行特定步骤
        
        Args:
            step_id: 步骤ID
            
        Returns:
            bool: 是否成功执行
        """
        if not self.current_stage:
            print("❌ 未开始任何阶段")
            return False
        
        step = next((s for s in self.current_stage.steps if s.id == step_id), None)
        if not step:
            print(f"❌ 未找到步骤: {step_id}")
            return False
        
        self.current_step = step
        self.current_node = None
        
        print(f"📋 执行步骤: {step.name}")
        self._add_feedback(f"执行步骤: {step.name}")
        
        # 记录执行历史
        self.execution_history.append({
            'type': 'step',
            'stage': self.current_stage.name,
            'step': step.name,
            'timestamp': self._get_timestamp()
        })
        
        return True
    
    def process_node(self, node_id: str, input_data: Any = None) -> Dict[str, Any]:
        """
        处理工作节点
        
        Args:
            node_id: 节点ID
            input_data: 输入数据
            
        Returns:
            Dict: 处理结果和反馈
        """
        if not self.current_step:
            return {'success': False, 'feedback': '未开始任何步骤'}
        
        node = next((n for n in self.current_step.work_nodes if n.id == node_id), None)
        if not node:
            return {'success': False, 'feedback': f'未找到节点: {node_id}'}
        
        self.current_node = node
        
        print(f"🔧 处理节点: {node.name} ({node.type.value})")
        
        result = {
            'success': True,
            'node_id': node.id,
            'node_name': node.name,
            'node_type': node.type.value,
            'feedback': self._get_node_feedback(node, 'success'),
            'output': None
        }
        
        # 根据节点类型执行相应操作
        if node.type == NodeType.ACTION and node.action:
            result['output'] = self._execute_action(node.action, input_data)
        elif node.type == NodeType.DECISION:
            result['output'] = self._make_decision(node.conditions, input_data)
        elif node.type == NodeType.INPUT:
            result['output'] = self._handle_input(input_data)
        elif node.type == NodeType.OUTPUT:
            result['output'] = self._handle_output(input_data)
        
        self._add_feedback(result['feedback'])
        
        # 记录执行历史
        self.execution_history.append({
            'type': 'node',
            'stage': self.current_stage.name,
            'step': self.current_step.name,
            'node': node.name,
            'result': result,
            'timestamp': self._get_timestamp()
        })
        
        return result
    
    def update_pointer(self, pointer_id: str) -> bool:
        """
        更新指针位置
        
        Args:
            pointer_id: 指针ID
            
        Returns:
            bool: 是否成功更新
        """
        if not self.current_step:
            print("❌ 未开始任何步骤")
            return False
        
        pointer = next((p for p in self.current_step.pointers if p.id == pointer_id), None)
        if not pointer:
            print(f"❌ 未找到指针: {pointer_id}")
            return False
        
        self.pointer_position = pointer.target
        
        print(f"📍 更新指针位置: {pointer.name} -> {pointer.target}")
        self._add_feedback(f"指针更新: {pointer.name}")
        
        return True
    
    def check_end_conditions(self) -> Optional[Dict[str, Any]]:
        """
        检查结束条件
        
        Returns:
            Optional[Dict]: 结束条件信息，如果未结束返回None
        """
        if not self.current_stage:
            return None
        
        for condition in self.current_stage.end_conditions:
            # 这里应该实现具体的条件检查逻辑
            # 简化实现：假设所有条件都满足
            if self._evaluate_condition(condition.condition):
                return {
                    'type': condition.type.value,
                    'message': condition.message or f"阶段 {self.current_stage.name} 结束",
                    'stage': self.current_stage.name
                }
        
        return None
    
    def get_feedback(self) -> List[str]:
        """
        获取所有反馈信息
        
        Returns:
            List[str]: 反馈信息列表
        """
        return self.feedback_messages.copy()
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        获取当前状态
        
        Returns:
            Dict: 当前状态信息
        """
        return {
            'workflow': self.current_workflow.name if self.current_workflow else None,
            'stage': self.current_stage.name if self.current_stage else None,
            'step': self.current_step.name if self.current_step else None,
            'node': self.current_node.name if self.current_node else None,
            'pointer': self.pointer_position,
            'feedback_count': len(self.feedback_messages),
            'execution_history_count': len(self.execution_history)
        }
    
    def _add_feedback(self, message: str) -> None:
        """添加反馈信息"""
        self.feedback_messages.append(f"[{self._get_timestamp()}] {message}")
    
    def _get_node_feedback(self, node: WorkNode, feedback_type: str) -> str:
        """获取节点反馈信息"""
        return node.feedback_rules.get(feedback_type, f"节点 {node.name} 执行{feedback_type}")
    
    def _execute_action(self, action: str, input_data: Any) -> Any:
        """执行动作"""
        # 这里应该实现具体的动作执行逻辑
        return f"执行动作: {action}"
    
    def _make_decision(self, conditions: List[str], input_data: Any) -> Any:
        """做出决策"""
        # 这里应该实现决策逻辑
        return f"基于条件做出决策: {conditions}"
    
    def _handle_input(self, input_data: Any) -> Any:
        """处理输入"""
        return f"处理输入: {input_data}"
    
    def _handle_output(self, output_data: Any) -> Any:
        """处理输出"""
        return f"输出结果: {output_data}"
    
    def _evaluate_condition(self, condition: str) -> bool:
        """评估条件"""
        # 这里应该实现条件评估逻辑
        # 简化实现：返回True
        return True
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 使用示例
def main():
    """工作流引擎使用示例"""
    # 创建引擎实例
    engine = WorkflowEngine()
    
    # 示例工作流数据
    sample_workflow = {
        "workflow": {
            "id": "dev_workflow_001",
            "name": "开发工作流示例",
            "version": "1.0.0",
            "description": "示例开发工作流"
        },
        "stages": [
            {
                "id": "planning",
                "name": "规划阶段",
                "description": "项目规划阶段",
                "steps": [
                    {
                        "id": "requirements",
                        "name": "需求分析",
                        "work_nodes": [
                            {
                                "id": "analyze_req",
                                "name": "分析需求",
                                "type": "action",
                                "action": "analyze_requirements",
                                "feedback_rules": {
                                    "success": "需求分析完成",
                                    "failure": "需求分析失败"
                                }
                            }
                        ]
                    }
                ],
                "end_conditions": [
                    {
                        "type": "success",
                        "condition": "requirements_completed",
                        "message": "规划阶段完成"
                    }
                ]
            }
        ]
    }
    
    # 解析工作流
    workflow = engine.parse_workflow(sample_workflow)
    
    # 执行工作流
    engine.start_stage("planning")
    engine.execute_step("requirements")
    result = engine.process_node("analyze_req", "用户需求文档")
    
    print(f"执行结果: {result}")
    print(f"当前状态: {engine.get_current_status()}")
    print(f"反馈信息: {engine.get_feedback()}")


if __name__ == "__main__":
    main()