#!/usr/bin/env python3
"""
代理哲学演示 - 完全遵循agent-builder技能的核心思想

"模型就是代理。代码只是运行循环。"
"""

import os

class AgentPhilosophyDemo:
    """
    这个演示展示agent-builder技能的核心哲学：
    1. 模型已经知道如何成为代理
    2. 你的工作是不要挡路
    3. 代码只是提供机会
    """
    
    def __init__(self):
        # 极简的能力集（3个核心能力）
        self.capabilities = {
            "read": self.read_file,
            "analyze": self.analyze_code,
            "suggest": self.suggest_fix,
        }
        
        # 极简的上下文
        self.context = []
        
        print("=" * 60)
        print("代理哲学演示")
        print("=" * 60)
        print()
        print("核心思想: 模型已经知道如何成为代理")
        print("我们的工作: 提供能力，然后让模型发挥")
        print()
    
    def read_file(self, filename: str) -> str:
        """能力1: 读取文件"""
        try:
            with open(filename, 'r') as f:
                return f.read()
        except:
            return f"无法读取文件: {filename}"
    
    def analyze_code(self, filename: str) -> str:
        """能力2: 分析代码"""
        code = self.read_file(filename)
        
        # 极简分析 - 模型会做真正的分析
        lines = len(code.split('\n'))
        has_functions = 'def ' in code
        has_classes = 'class ' in code
        
        return f"""
文件分析: {filename}
基本统计: {lines} 行代码
代码特征: {'有函数' if has_functions else '无函数'}, {'有类' if has_classes else '无类'}

提示: 模型可以根据这些基本信息进行深入分析
"""
    
    def suggest_fix(self, filename: str, issue: str) -> str:
        """能力3: 建议修复"""
        code = self.read_file(filename)
        
        return f"""
针对问题: {issue}
在文件: {filename}

建议框架:
1. 理解问题: {issue}
2. 分析代码: {len(code.split('\n'))} 行代码需要检查
3. 定位问题: 模型会找到具体位置
4. 提供修复: 模型会生成具体修复方案

提示: 模型知道如何修复代码，我们只需要提供上下文
"""
    
    def agent_loop(self):
        """极简的代理循环"""
        print("🤖 代理循环开始")
        print("输入 '能力' 查看可用能力")
        print("输入 '退出' 结束")
        print()
        
        while True:
            try:
                user_input = input("用户: ").strip()
                
                if user_input == '退出':
                    print("代理: 再见！")
                    break
                
                if user_input == '能力':
                    print("代理: 我有3个能力:")
                    print("  1. 读取 [文件名] - 读取文件内容")
                    print("  2. 分析 [文件名] - 分析代码结构")
                    print("  3. 建议 [文件名] [问题] - 建议修复方案")
                    continue
                
                # 让模型决定做什么（这里简化处理）
                if user_input.startswith('读取 '):
                    filename = user_input[3:].strip()
                    result = self.capabilities['read'](filename)
                    print(f"代理: 读取结果:\n{result}")
                
                elif user_input.startswith('分析 '):
                    filename = user_input[3:].strip()
                    result = self.capabilities['analyze'](filename)
                    print(f"代理: 分析结果:\n{result}")
                
                elif user_input.startswith('建议 '):
                    parts = user_input[3:].split(' ', 1)
                    if len(parts) == 2:
                        filename, issue = parts
                        result = self.capabilities['suggest'](filename, issue)
                        print(f"代理: 建议:\n{result}")
                    else:
                        print("代理: 请提供文件名和问题描述")
                
                else:
                    # 关键部分：信任模型
                    print("代理: 我不确定您的具体需求，但让我尝试理解...")
                    print("作为代码代理，我可以：")
                    print("1. 帮助您理解代码")
                    print("2. 分析代码问题")
                    print("3. 建议改进方案")
                    print("请尝试更具体的命令，如 '分析 hello.py'")
                
                # 添加上下文
                self.context.append(f"用户: {user_input}")
                if len(self.context) > 5:
                    self.context = self.context[-5:]
                    
            except KeyboardInterrupt:
                print("\n代理: 循环被中断")
                break
    
    def demonstrate_philosophy(self):
        """演示agent-builder哲学"""
        print("\n" + "=" * 60)
        print("AGENT-BUILDER 哲学演示")
        print("=" * 60)
        
        print("\n1. 模型就是代理")
        print("   - 我们不需要教AI如何分析代码")
        print("   - AI已经知道如何阅读、理解、修复代码")
        print("   - 我们只需要提供访问代码的能力")
        
        print("\n2. 能力赋能")
        print("   - 读取能力: 让AI看到代码")
        print("   - 分析能力: 让AI理解结构")
        print("   - 建议能力: 让AI提供方案")
        print("   - 只有3个能力，但AI可以做无数事情")
        
        print("\n3. 简单循环")
        print("   - 用户输入 → 代理处理 → 返回结果")
        print("   - 没有复杂的状态机")
        print("   - 没有预设的工作流")
        print("   - AI在每次交互中重新推理")
        
        print("\n4. 信任模型")
        print("   - 不要过度指定'如何做'")
        print("   - 专注于'能做什么'")
        print("   - AI会找到最佳路径")
        
        print("\n" + "=" * 60)
        print("实际演示")
        print("=" * 60)


def main():
    """主函数"""
    demo = AgentPhilosophyDemo()
    demo.demonstrate_philosophy()
    demo.agent_loop()


if __name__ == "__main__":
    main()