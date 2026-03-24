from typing import Dict, List, Optional, Any
import json
import os

class AstronomyKnowledgeBase:
    """天文领域知识库（基于JSON）"""
    
    def __init__(self, knowledge_file: str = None):
        """初始化知识库"""
        # 默认知识库文件路径
        if knowledge_file is None:
            knowledge_file = os.path.join(os.path.dirname(__file__), "astronomy_knowledge.json")
        
        self.knowledge_file = knowledge_file
        self.knowledge_data = self._load_knowledge()
        self.rules = self.knowledge_data.get('rules', [])
        # 按优先级排序
        self.rules.sort(key=lambda x: x.get('priority', 1))
    
    def _load_knowledge(self) -> Dict[str, Any]:
        """加载知识库JSON文件"""
        if not os.path.exists(self.knowledge_file):
            # 如果文件不存在，返回空知识库
            return {
                "version": "1.0.0",
                "last_updated": "2026-03-18",
                "rules": []
            }
        
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载知识库失败: {e}")
            # 加载失败时返回空知识库
            return {
                "version": "1.0.0",
                "last_updated": "2026-03-18",
                "rules": []
            }
    
    def _save_knowledge(self, knowledge: Dict[str, Any]):
        """保存知识库到JSON文件"""
        try:
            os.makedirs(os.path.dirname(self.knowledge_file), exist_ok=True)
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存知识库失败: {e}")
    
    def keyword_match(self, query: str, keywords: List[str]) -> bool:
        """基础关键词匹配"""
        query_lower = query.lower()
        for keyword in keywords:
            if keyword.lower() in query_lower:
                return True
        return False
    
    def advanced_match(self, query: str, rule: Dict[str, Any]) -> tuple:
        """高级匹配，返回是否匹配和匹配分数"""
        query_lower = query.lower()
        keywords = rule.get('keywords', [])
        exclude = rule.get('exclude_keywords', [])
        
        # 先检查排除词
        for excl in exclude:
            if excl.lower() in query_lower:
                return False, 0
        
        # 计算匹配分数
        matched_keywords = []
        for kw in keywords:
            if kw.lower() in query_lower:
                matched_keywords.append(kw)
        
        if matched_keywords:
            # 计算匹配率
            score = len(matched_keywords) / len(keywords) if keywords else 0
            return True, score
        else:
            return False, 0
    
    def match_rule(self, query: str) -> List[Dict[str, Any]]:
        """匹配所有相关规则"""
        matched_rules = []
        
        for rule in self.rules:
            if not rule.get('enabled', True):
                continue
                
            is_match, score = self.advanced_match(query, rule)
            if is_match:
                rule_copy = rule.copy()
                rule_copy['match_score'] = score
                matched_rules.append(rule_copy)
        
        # 按匹配分数和优先级排序
        matched_rules.sort(
            key=lambda x: (x['match_score'], -x['priority']), 
            reverse=True
        )
        
        return matched_rules
    
    def get_action_plan(self, query: str) -> List[Dict[str, Any]]:
        """生成执行计划"""
        matched_rules = self.match_rule(query)
        
        if not matched_rules:
            return [{
                "action": "fallback",
                "message": "未找到匹配的数据源，建议使用通用搜索或咨询管理员"
            }]
        
        # 去重，同一领域只保留最高分规则
        seen_domains = set()
        unique_rules = []
        for rule in matched_rules:
            if rule['domain'] not in seen_domains:
                seen_domains.add(rule['domain'])
                unique_rules.append(rule)
        
        # 构建执行计划
        action_plan = []
        for rule in unique_rules[:3]:  # 最多执行3个任务
            action_plan.append({
                "domain": rule['domain'],
                "action": rule['action'],
                "source": rule['primary_source'],
                "params": rule.get('action_params', {}),
                "match_score": rule['match_score'],
                "description": rule.get('description', '')
            })
        
        return action_plan
    
    def format_for_prompt(self, query: str) -> str:
        """生成供LLM使用的提示词上下文"""
        action_plan = self.get_action_plan(query)
        
        if not action_plan or action_plan[0]['action'] == 'fallback':
            return "未找到匹配的知识库规则，请根据你的通用知识回答。"
        
        context = "根据知识库规则，请按照以下计划执行：\n\n"
        for i, plan in enumerate(action_plan, 1):
            context += f"{i}. 【{plan['domain']}】\n"
            context += f"   - 数据源：{plan['source']}\n"
            context += f"   - 执行动作：{plan['action']}\n"
            context += f"   - 说明：{plan['description']}\n"
            if plan.get('params'):
                context += f"   - 参数：{json.dumps(plan['params'], ensure_ascii=False)}\n"
            context += "\n"
        
        return context
    
    

# 创建全局知识库实例
knowledge_base = AstronomyKnowledgeBase()

if __name__ == "__main__":
    # 测试知识库
    kb = AstronomyKnowledgeBase()
    
    print("=== 交互式知识库测试 ===")
    print("输入查询语句，输入 'exit' 退出测试")
    print("示例查询: '查询M1', '执行ADQL查询获取太阳附近的恒星', '分析恒星温度的分布'")
    print("=" * 50)
    
    while True:
        try:
            query = input("\n请输入查询: ")
            if query.lower() == "exit":
                print("测试结束！")
                break
            if not query.strip():
                print("查询不能为空，请重新输入")
                continue
            
            # 测试规则匹配
            action_plan = kb.get_action_plan(query)
            prompt_context = kb.format_for_prompt(query)
            print("\n执行计划:")
            print(prompt_context)
        except KeyboardInterrupt:
            print("\n测试被中断！")
            break
        except Exception as e:
            print(f"错误: {e}")
            continue
