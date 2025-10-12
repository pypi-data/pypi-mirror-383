"""
Mermaid流程图解析器

将Mermaid流程图解析为工作流JSON结构
"""

import re
from typing import Dict, List, Any, Tuple
from pathlib import Path


class MermaidParser:
    """Mermaid流程图解析器类"""
    
    def __init__(self):
        self.stages = []
        self.steps = []
        self.nodes = []
        self.pointers = []
        self.end_conditions = []
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析Mermaid文件
        
        Args:
            file_path: Mermaid文件路径
            
        Returns:
            Dict: 解析后的工作流数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_content(content, Path(file_path).stem)
        except Exception as e:
            raise ValueError(f"解析Mermaid文件失败: {e}")
    
    def parse_content(self, content: str, workflow_name: str = "unnamed") -> Dict[str, Any]:
        """
        解析Mermaid内容
        
        Args:
            content: Mermaid流程图内容
            workflow_name: 工作流名称
            
        Returns:
            Dict: 解析后的工作流数据
        """
        # 清理内容
        content = self._clean_content(content)
        
        # 重置解析状态
        self.stages = []
        self.steps = []
        self.nodes = []
        self.pointers = []
        self.end_conditions = []
        
        # 解析流程图类型
        if "graph" in content.lower() or "flowchart" in content.lower():
            return self._parse_flowchart(content, workflow_name)
        elif "sequenceDiagram" in content:
            return self._parse_sequence_diagram(content, workflow_name)
        else:
            raise ValueError("不支持的Mermaid图表类型")
    
    def _clean_content(self, content: str) -> str:
        """清理Mermaid内容"""
        # 移除注释
        content = re.sub(r'%%[^\n]*\n', '', content)
        # 移除多余的空行
        content = re.sub(r'\n\s*\n', '\n', content)
        return content.strip()
    
    def _parse_flowchart(self, content: str, workflow_name: str) -> Dict[str, Any]:
        """解析流程图类型的Mermaid"""
        lines = content.split('\n')
        
        # 提取流程图定义
        flowchart_def = None
        for i, line in enumerate(lines):
            if line.strip().startswith('graph') or line.strip().startswith('flowchart'):
                flowchart_def = line.strip()
                # 获取方向
                direction = 'TD'  # 默认从上到下
                if 'LR' in line:
                    direction = 'LR'
                elif 'RL' in line:
                    direction = 'RL'
                elif 'BT' in line:
                    direction = 'BT'
                break
        
        if not flowchart_def:
            raise ValueError("未找到流程图定义")
        
        # 解析节点和连接
        nodes = {}
        connections = []
        
        for line in lines[i+1:]:
            line = line.strip()
            if not line or line.startswith('end') or line.startswith('}'):
                continue
            
            # 解析节点定义
            node_match = re.match(r'(\w+)\[([^\]]+)\]', line)
            if node_match:
                node_id, node_label = node_match.groups()
                nodes[node_id] = {
                    'id': node_id,
                    'label': node_label,
                    'type': self._classify_node(node_label)
                }
                continue
            
            # 解析简单节点
            simple_match = re.match(r'(\w+)(\(([^)]+)\))?', line)
            if simple_match:
                node_id, _, node_label = simple_match.groups()
                nodes[node_id] = {
                    'id': node_id,
                    'label': node_label or node_id,
                    'type': self._classify_node(node_label or node_id)
                }
                continue
            
            # 解析连接
            connection_match = re.match(r'(\w+)\s*([->]+)\s*(\w+)(\s*\|([^|]+)\|)?', line)
            if connection_match:
                from_node, arrows, to_node, _, label = connection_match.groups()
                connections.append({
                    'from': from_node,
                    'to': to_node,
                    'arrows': arrows,
                    'label': label.strip() if label else None
                })
        
        # 构建工作流结构
        return self._build_workflow_from_nodes(nodes, connections, workflow_name)
    
    def _parse_sequence_diagram(self, content: str, workflow_name: str) -> Dict[str, Any]:
        """解析序列图类型的Mermaid"""
        # 这里实现序列图解析逻辑
        # 由于时间关系，先返回一个基础结构
        return {
            "workflow": {
                "id": f"seq_{workflow_name}",
                "name": workflow_name,
                "version": "1.0.0",
                "description": "从序列图解析的工作流"
            },
            "stages": [
                {
                    "id": "main_stage",
                    "name": "主阶段",
                    "description": "主要执行阶段",
                    "steps": [
                        {
                            "id": "main_step",
                            "name": "主要步骤",
                            "work_nodes": [
                                {
                                    "id": "start_node",
                                    "name": "开始",
                                    "type": "action"
                                }
                            ]
                        }
                    ],
                    "end_conditions": [
                        {
                            "type": "success",
                            "condition": "completed",
                            "message": "序列图工作流执行完成"
                        }
                    ]
                }
            ]
        }
    
    def _classify_node(self, label: str) -> str:
        """根据标签分类节点类型"""
        label_lower = label.lower()
        
        if any(word in label_lower for word in ['开始', 'start', 'init']):
            return 'start'
        elif any(word in label_lower for word in ['结束', 'end', 'finish']):
            return 'end'
        elif any(word in label_lower for word in ['阶段', 'stage', 'phase']):
            return 'stage'
        elif any(word in label_lower for word in ['步骤', 'step', 'task']):
            return 'step'
        elif any(word in label_lower for word in ['决策', 'decision', '判断']):
            return 'decision'
        elif any(word in label_lower for word in ['输入', 'input']):
            return 'input'
        elif any(word in label_lower for word in ['输出', 'output']):
            return 'output'
        else:
            return 'action'
    
    def _build_workflow_from_nodes(self, nodes: Dict, connections: List, workflow_name: str) -> Dict[str, Any]:
        """从节点和连接构建工作流结构"""
        
        # 识别阶段和步骤
        stages = self._identify_stages(nodes, connections)
        
        # 构建工作流JSON
        workflow_data = {
            "workflow": {
                "id": f"flow_{workflow_name}",
                "name": workflow_name,
                "version": "1.0.0",
                "description": "从流程图解析的工作流"
            },
            "stages": stages
        }
        
        return workflow_data
    
    def _identify_stages(self, nodes: Dict, connections: List) -> List[Dict]:
        """识别阶段结构"""
        stages = []
        
        # 找到开始节点
        start_nodes = [node_id for node_id, node in nodes.items() 
                      if node['type'] == 'start']
        
        if not start_nodes:
            # 如果没有明确的开始节点，使用第一个节点
            start_nodes = [list(nodes.keys())[0]] if nodes else []
        
        for start_node in start_nodes:
            stage = self._build_stage_from_start(start_node, nodes, connections)
            if stage:
                stages.append(stage)
        
        return stages
    
    def _build_stage_from_start(self, start_node: str, nodes: Dict, connections: List) -> Dict:
        """从开始节点构建阶段"""
        # 跟踪访问过的节点
        visited = set()
        stage_nodes = self._traverse_from_node(start_node, nodes, connections, visited)
        
        # 将节点组织成阶段结构
        stage_steps = self._organize_nodes_into_steps(stage_nodes, connections)
        
        return {
            "id": f"stage_{start_node}",
            "name": nodes[start_node]['label'],
            "description": f"从节点 {start_node} 开始的阶段",
            "steps": stage_steps,
            "end_conditions": self._identify_end_conditions(stage_nodes, connections)
        }
    
    def _traverse_from_node(self, current_node: str, nodes: Dict, connections: List, visited: set) -> List:
        """从节点开始遍历连接"""
        if current_node in visited:
            return []
        
        visited.add(current_node)
        result = [current_node]
        
        # 找到所有从当前节点出发的连接
        outgoing = [conn for conn in connections if conn['from'] == current_node]
        
        for conn in outgoing:
            next_nodes = self._traverse_from_node(conn['to'], nodes, connections, visited)
            result.extend(next_nodes)
        
        return result
    
    def _organize_nodes_into_steps(self, node_ids: List[str], connections: List) -> List[Dict]:
        """将节点组织成步骤结构"""
        steps = []
        current_step_nodes = []
        
        for node_id in node_ids:
            # 这里实现节点到步骤的映射逻辑
            # 简化实现：每个节点作为一个步骤
            step = {
                "id": f"step_{node_id}",
                "name": f"步骤 {node_id}",
                "work_nodes": [
                    {
                        "id": f"node_{node_id}",
                        "name": f"节点 {node_id}",
                        "type": "action"
                    }
                ]
            }
            
            # 添加指针
            outgoing = [conn for conn in connections if conn['from'] == node_id]
            if outgoing:
                step["pointers"] = []
                for conn in outgoing:
                    pointer = {
                        "id": f"pointer_{node_id}_to_{conn['to']}",
                        "name": f"指向 {conn['to']}",
                        "target": conn['to']
                    }
                    if conn.get('label'):
                        pointer["condition"] = conn['label']
                    step["pointers"].append(pointer)
            
            steps.append(step)
        
        return steps
    
    def _identify_end_conditions(self, stage_nodes: List[str], connections: List) -> List[Dict]:
        """识别结束条件"""
        end_conditions = []
        
        for node_id in stage_nodes:
            # 检查是否是结束节点（没有出度）
            outgoing = [conn for conn in connections if conn['from'] == node_id]
            if not outgoing:
                end_conditions.append({
                    "type": "success",
                    "condition": f"node_{node_id}_completed",
                    "message": f"节点 {node_id} 执行完成"
                })
        
        return end_conditions


def generate_mermaid_template(workflow_type: str = "flowchart") -> str:
    """
    生成Mermaid模板
    
    Args:
        workflow_type: 工作流类型（flowchart/sequence）
        
    Returns:
        str: Mermaid模板内容
    """
    if workflow_type == "flowchart":
        return """flowchart TD
    A[开始] --> B{决策节点}
    B -->|条件1| C[动作1]
    B -->|条件2| D[动作2]
    C --> E[结束]
    D --> E
"""
    elif workflow_type == "sequence":
        return """sequenceDiagram
    participant A as 用户
    participant B as 系统
    A->>B: 请求
    B->>A: 响应
"""
    else:
        return """graph TD
    Start[开始] --> Process[处理过程]
    Process --> End[结束]
"""


# 使用示例
def main():
    """Mermaid解析器使用示例"""
    parser = MermaidParser()
    
    # 示例Mermaid内容
    mermaid_content = """flowchart TD
    A[需求分析] --> B[技术设计]
    B --> C[编码实现]
    C --> D[测试验证]
    D --> E[部署上线]
"""
    
    # 解析Mermaid
    workflow_data = parser.parse_content(mermaid_content, "开发工作流")
    
    # 输出解析结果
    import json
    print("解析结果:")
    print(json.dumps(workflow_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()