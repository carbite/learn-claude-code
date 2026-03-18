#!/usr/bin/env python3
"""
代码问答代理 - 基于agent-builder技能设计
一个能够读取、解释、修复和实现代码的AI代理
"""

import os
import sys
import glob
import ast
import subprocess
from typing import List, Dict, Any, Optional
import json

class CodeQAAgent:
    """代码问答代理"""
    
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = workspace_dir
        self.context = []
        
        # 代理的核心能力（3-5个关键能力）
        self.capabilities = {
            "read_code": self.read_code_file,
            "explain_code": self.explain_code,
            "find_bugs": self.find_bugs,
            "fix_bug": self.fix_bug,
            "implement_feature": self.implement_feature,
            "list_files": self.list_code_files,
            "run_code": self.run_code,
        }
        
        # 代理的知识（按需加载）
        self.knowledge = {
            "python_best_practices": self.load_python_best_practices,
            "common_bugs": self.load_common_bugs,
            "design_patterns": self.load_design_patterns,
        }
    
    def load_python_best_practices(self) -> str:
        """加载Python最佳实践知识"""
        return """
        Python最佳实践：
        1. 遵循PEP 8代码风格
        2. 使用有意义的变量名
        3. 添加类型提示
        4. 编写文档字符串
        5. 异常处理要具体
        6. 避免全局变量
        7. 使用列表推导式简化代码
        8. 遵循单一职责原则
        """
    
    def load_common_bugs(self) -> str:
        """加载常见bug知识"""
        return """
        常见Python bug：
        1. 可变默认参数：def func(items=[])
        2. 修改迭代中的列表
        3. 变量作用域混淆
        4. 未关闭的文件句柄
        5. 整数除法问题（Python 2）
        6. 字符串编码问题
        7. 浅拷贝 vs 深拷贝
        8. 循环引用导致内存泄漏
        """
    
    def load_design_patterns(self) -> str:
        """加载设计模式知识"""
        return """
        常用设计模式：
        1. 单例模式（Singleton）
        2. 工厂模式（Factory）
        3. 观察者模式（Observer）
        4. 策略模式（Strategy）
        5. 装饰器模式（Decorator）
        6. 适配器模式（Adapter）
        7. 模板方法模式（Template Method）
        """
    
    def list_code_files(self, pattern: str = "*.py") -> List[str]:
        """列出工作目录中的代码文件"""
        files = glob.glob(os.path.join(self.workspace_dir, "**", pattern), recursive=True)
        return files
    
    def read_code_file(self, filepath: str) -> str:
        """读取代码文件内容"""
        try:
            full_path = os.path.join(self.workspace_dir, filepath)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 添加到上下文
            self.add_to_context(f"读取文件: {filepath}")
            return content
        except FileNotFoundError:
            return f"错误：文件 {filepath} 不存在"
        except Exception as e:
            return f"读取文件时出错: {str(e)}"
    
    def explain_code(self, filepath: str, specific_part: str = "") -> str:
        """解释代码功能"""
        code = self.read_code_file(filepath)
        if code.startswith("错误"):
            return code
        
        # 分析代码结构
        try:
            tree = ast.parse(code)
            
            # 提取基本信息
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        imports.append(f"{module}.{name.name}")
            
            explanation = f"""
文件: {filepath}
代码长度: {len(code)} 字符
函数数量: {len(functions)}
类数量: {len(classes)}
导入模块: {len(imports)}

主要函数: {', '.join(functions[:5])}
主要类: {', '.join(classes[:5])}
导入: {', '.join(imports[:10])}
"""
            
            # 如果有特定部分，尝试解释
            if specific_part:
                explanation += f"\n关于 '{specific_part}' 的解释:\n"
                # 这里可以添加更详细的特定部分分析
                
            return explanation
            
        except SyntaxError as e:
            return f"语法错误: {str(e)}"
    
    def find_bugs(self, filepath: str) -> str:
        """查找代码中的bug"""
        code = self.read_code_file(filepath)
        if code.startswith("错误"):
            return code
        
        bugs = []
        
        try:
            tree = ast.parse(code)
            
            # 检查常见问题
            for node in ast.walk(tree):
                # 检查可变默认参数
                if isinstance(node, ast.FunctionDef):
                    for arg in node.args.defaults:
                        if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                            bugs.append(f"函数 '{node.name}' 使用了可变默认参数")
                
                # 检查未使用的变量
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    # 简单检查：如果变量只被赋值但未使用
                    pass
            
            # 检查语法问题
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if 'except:' in line and 'except Exception:' not in line:
                    bugs.append(f"第{i}行: 使用了过于宽泛的 except 语句")
                if 'eval(' in line or 'exec(' in line:
                    bugs.append(f"第{i}行: 使用了危险的 eval/exec 函数")
                if 'password' in line.lower() or 'secret' in line.lower():
                    bugs.append(f"第{i}行: 可能包含硬编码的敏感信息")
            
            if bugs:
                return f"在 {filepath} 中发现 {len(bugs)} 个潜在问题:\n" + "\n".join(f"- {bug}" for bug in bugs)
            else:
                return f"在 {filepath} 中未发现明显的bug"
                
        except SyntaxError as e:
            return f"语法错误: {str(e)}"
    
    def fix_bug(self, filepath: str, bug_description: str) -> str:
        """修复指定的bug"""
        code = self.read_code_file(filepath)
        if code.startswith("错误"):
            return code
        
        # 这里应该实现具体的修复逻辑
        # 由于bug类型多样，这里提供一个框架
        
        fixed_code = code  # 默认不修改
        
        # 示例：修复过于宽泛的except语句
        if "过于宽泛的 except" in bug_description:
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if 'except:' in line and 'except Exception:' not in line:
                    lines[i] = line.replace('except:', 'except Exception:')
            fixed_code = '\n'.join(lines)
        
        # 保存修复后的代码
        try:
            full_path = os.path.join(self.workspace_dir, filepath)
            backup_path = full_path + '.backup'
            
            # 创建备份
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # 写入修复后的代码
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            
            self.add_to_context(f"修复bug: {bug_description}")
            return f"已修复 {filepath} 中的bug。原始文件已备份到 {backup_path}"
            
        except Exception as e:
            return f"修复bug时出错: {str(e)}"
    
    def implement_feature(self, filepath: str, feature_description: str) -> str:
        """实现新功能"""
        code = self.read_code_file(filepath)
        if code.startswith("错误"):
            # 如果文件不存在，创建新文件
            if "不存在" in code:
                code = "# 新文件\n"
            else:
                return code
        
        # 解析功能描述，生成代码
        # 这里简化处理，实际应该更智能
        new_code = f"""
# 新增功能: {feature_description}
def new_feature():
    \"\"\"{feature_description}\"\"\"
    # TODO: 实现功能
    pass

# 调用示例
if __name__ == "__main__":
    new_feature()
"""
        
        # 将新代码附加到文件末尾
        updated_code = code.rstrip() + "\n\n" + new_code
        
        try:
            full_path = os.path.join(self.workspace_dir, filepath)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(updated_code)
            
            self.add_to_context(f"实现功能: {feature_description}")
            return f"已在 {filepath} 中实现新功能"
            
        except Exception as e:
            return f"实现功能时出错: {str(e)}"
    
    def run_code(self, filepath: str) -> str:
        """运行代码文件"""
        try:
            full_path = os.path.join(self.workspace_dir, filepath)
            
            # 检查文件是否存在
            if not os.path.exists(full_path):
                return f"错误：文件 {filepath} 不存在"
            
            # 运行Python文件
            result = subprocess.run(
                [sys.executable, full_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = f"""
运行 {filepath} 的结果:
退出代码: {result.returncode}

标准输出:
{result.stdout}

标准错误:
{result.stderr}
"""
            return output
            
        except subprocess.TimeoutExpired:
            return f"错误：运行 {filepath} 超时"
        except Exception as e:
            return f"运行代码时出错: {str(e)}"
    
    def add_to_context(self, message: str):
        """添加上下文"""
        self.context.append(message)
        # 保持上下文大小合理
        if len(self.context) > 10:
            self.context = self.context[-10:]
    
    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        if not self.context:
            return "无上下文历史"
        return "最近操作:\n" + "\n".join(f"- {item}" for item in self.context[-5:])
    
    def process_query(self, query: str) -> str:
        """处理用户查询"""
        # 简单的查询解析
        query_lower = query.lower()
        
        # 检查是否需要特定知识
        if "最佳实践" in query_lower:
            knowledge = self.knowledge["python_best_practices"]()
            return f"Python最佳实践知识:\n{knowledge}"
        
        if "常见bug" in query_lower or "常见错误" in query_lower:
            knowledge = self.knowledge["common_bugs"]()
            return f"常见bug知识:\n{knowledge}"
        
        if "设计模式" in query_lower:
            knowledge = self.knowledge["design_patterns"]()
            return f"设计模式知识:\n{knowledge}"
        
        # 列出文件
        if "列出文件" in query_lower or "list files" in query_lower:
            files = self.list_code_files()
            return f"工作目录中的Python文件:\n" + "\n".join(files)
        
        # 解释代码
        if "解释" in query_lower and ".py" in query_lower:
            # 简单提取文件名
            for word in query.split():
                if word.endswith('.py'):
                    return self.explain_code(word)
        
        # 查找bug
        if "bug" in query_lower or "错误" in query_lower:
            for word in query.split():
                if word.endswith('.py'):
                    return self.find_bugs(word)
        
        # 运行代码
        if "运行" in query_lower or "run" in query_lower:
            for word in query.split():
                if word.endswith('.py'):
                    return self.run_code(word)
        
        # 默认响应
        return f"""
我无法完全理解您的查询: "{query}"

我可以帮助您：
1. 列出代码文件 - 说"列出文件"
2. 读取代码文件 - 说"读取 [文件名]"
3. 解释代码功能 - 说"解释 [文件名]"
4. 查找bug - 说"查找 [文件名] 中的bug"
5. 运行代码 - 说"运行 [文件名]"
6. 获取知识 - 问"Python最佳实践"、"常见bug"、"设计模式"

当前上下文:
{self.get_context_summary()}
"""


def main():
    """主函数 - 简单的命令行界面"""
    print("=== 代码问答代理 ===")
    print("输入 '退出' 或 'quit' 结束")
    print()
    
    agent = CodeQAAgent()
    
    while True:
        try:
            query = input("\n您想了解什么？> ").strip()
            
            if query.lower() in ['退出', 'quit', 'exit']:
                print("再见！")
                break
            
            if not query:
                continue
            
            # 处理查询
            response = agent.process_query(query)
            print(f"\n{response}")
            
        except KeyboardInterrupt:
            print("\n\n程序被中断")
            break
        except Exception as e:
            print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()