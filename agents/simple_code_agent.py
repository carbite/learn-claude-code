#!/usr/bin/env python3
"""
简单代码代理 - 遵循agent-builder的最小原则
一个极简但功能完整的代码问答代理
"""

import os
import glob
import subprocess
import sys

class SimpleCodeAgent:
    """简单代码代理 - 只有3个核心能力"""
    
    def __init__(self):
        self.context = []  # 简单的上下文跟踪
        
    # ========== 核心能力 ==========
    
    def read_code(self, filename: str) -> str:
        """能力1: 读取代码文件"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            self.context.append(f"读取: {filename}")
            return content
        except FileNotFoundError:
            return f"错误: 文件 {filename} 不存在"
    
    def explain_code(self, filename: str) -> str:
        """能力2: 解释代码"""
        code = self.read_code(filename)
        if "错误:" in code:
            return code
        
        # 简单分析
        lines = code.split('\n')
        functions = [line for line in lines if line.strip().startswith('def ')]
        classes = [line for line in lines if line.strip().startswith('class ')]
        imports = [line for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')]
        
        explanation = f"""
文件: {filename}
行数: {len(lines)}
函数: {len(functions)}
类: {len(classes)}
导入: {len(imports)}

主要函数:
{chr(10).join(functions[:3]) if functions else '无'}

主要类:
{chr(10).join(classes[:3]) if classes else '无'}
"""
        self.context.append(f"解释: {filename}")
        return explanation
    
    def fix_and_run(self, filename: str, issue: str = "") -> str:
        """能力3: 修复并运行代码"""
        if not os.path.exists(filename):
            return f"错误: 文件 {filename} 不存在"
        
        result = ""
        
        # 如果有问题描述，尝试修复
        if issue:
            code = self.read_code(filename)
            if "错误:" not in code:
                # 简单修复示例：添加缺失的导入
                if "导入" in issue or "import" in issue:
                    fixed_code = "import sys\nimport os\n" + code
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(fixed_code)
                    result += f"已修复导入问题\n"
        
        # 运行代码
        try:
            output = subprocess.run(
                [sys.executable, filename],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            result += f"""
运行结果:
退出代码: {output.returncode}

输出:
{output.stdout}

错误:
{output.stderr}
"""
            self.context.append(f"运行: {filename}")
            return result
            
        except subprocess.TimeoutExpired:
            return "错误: 运行超时"
    
    # ========== 代理循环 ==========
    
    def agent_loop(self):
        """代理主循环"""
        print("🤖 简单代码代理已启动")
        print("输入 '帮助' 查看可用命令")
        print("输入 '退出' 结束")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['退出', 'quit', 'exit']:
                    print("再见！")
                    break
                
                if user_input.lower() in ['帮助', 'help']:
                    print(self.get_help())
                    continue
                
                if user_input.lower() in ['上下文', 'context']:
                    print(self.get_context())
                    continue
                
                if user_input.lower() in ['文件', 'files']:
                    files = glob.glob("*.py")
                    print(f"Python文件: {', '.join(files)}")
                    continue
                
                # 解析命令
                response = self.process_input(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n代理已停止")
                break
            except Exception as e:
                print(f"错误: {e}")
    
    def process_input(self, user_input: str) -> str:
        """处理用户输入"""
        words = user_input.split()
        
        if len(words) < 2:
            return "请提供更多信息，例如: '解释 hello.py'"
        
        action = words[0].lower()
        target = words[1]
        
        # 确保目标文件存在
        if not target.endswith('.py'):
            target += '.py'
        
        if action in ['读取', 'read']:
            return self.read_code(target)
        
        elif action in ['解释', 'explain', '分析']:
            return self.explain_code(target)
        
        elif action in ['运行', 'run', '执行']:
            issue = ' '.join(words[2:]) if len(words) > 2 else ""
            return self.fix_and_run(target, issue)
        
        elif action in ['修复', 'fix']:
            issue = ' '.join(words[2:]) if len(words) > 2 else "未知问题"
            return self.fix_and_run(target, issue)
        
        else:
            return f"未知命令: {action}\n{self.get_help()}"
    
    def get_help(self) -> str:
        """获取帮助信息"""
        return """
可用命令:
1. 读取 [文件名]      - 读取代码文件内容
2. 解释 [文件名]      - 解释代码结构和功能
3. 运行 [文件名]      - 运行Python文件
4. 修复 [文件名] [问题] - 修复并运行代码
5. 文件              - 列出当前目录的Python文件
6. 上下文            - 查看操作历史
7. 帮助              - 显示此帮助
8. 退出              - 退出代理

示例:
  读取 hello.py
  解释 calculator.py
  运行 greet.py
  修复 buggy.py 导入错误
"""
    
    def get_context(self) -> str:
        """获取上下文"""
        if not self.context:
            return "还没有操作历史"
        return "最近操作:\n" + "\n".join(f"- {item}" for item in self.context[-5:])


def main():
    """启动代理"""
    agent = SimpleCodeAgent()
    agent.agent_loop()


if __name__ == "__main__":
    main()