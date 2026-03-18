# 代码问答代理

基于agent-builder技能设计的代码问答代理，能够读取、解释、修复和实现代码。

## 设计原则

遵循agent-builder技能的核心原则：
1. **模型即代理** - 保持代码简单，让AI模型发挥智能
2. **最小能力集** - 只实现3-5个核心能力
3. **按需知识** - 知识在需要时加载
4. **简单循环** - 清晰的代理决策循环

## 文件结构

```
.
├── code_qa_agent.py      # 完整版代码代理
├── simple_code_agent.py  # 极简版代码代理
├── test_buggy_code.py    # 测试文件1
├── buggy_example.py      # 测试文件2（有bug）
└── README_代码代理.md     # 说明文档
```

## 快速开始

### 使用完整版代理
```bash
python code_qa_agent.py
```

### 使用极简版代理（推荐）
```bash
python simple_code_agent.py
```

## 代理能力

### 1. 读取代码
```
读取 hello.py
读取 calculator.py
```

### 2. 解释代码
```
解释 hello.py
解释 calculator.py
```

### 3. 运行代码
```
运行 hello.py
运行 test_buggy_code.py
```

### 4. 修复代码
```
修复 buggy_example.py 除零错误
修复 buggy_example.py 可变默认参数
```

### 5. 其他命令
```
文件      # 列出所有Python文件
上下文    # 查看操作历史
帮助      # 显示帮助信息
退出      # 退出代理
```

## 示例对话

```
🤖 简单代码代理已启动
输入 '帮助' 查看可用命令
输入 '退出' 结束

> 文件
Python文件: hello.py, calculator.py, test_buggy_code.py, buggy_example.py

> 解释 buggy_example.py

文件: buggy_example.py
行数: 30
函数: 4
类: 0
导入: 0

主要函数:
def divide_numbers(a, b):
def process_list(items=[]):  # Bug: 可变默认参数
def read_file(filename):

> 运行 buggy_example.py

运行结果:
退出代码: 0

输出:
测试1: 5.0
测试2: ['processed']
测试3: ['processed', 'processed']

错误:

> 修复 buggy_example.py 可变默认参数
已修复导入问题

运行结果:
退出代码: 0
...
```

## 设计亮点

### 1. 遵循agent-builder原则
- 只有3个核心能力（读取、解释、修复运行）
- 简单的上下文管理
- 清晰的用户交互

### 2. 实际可用的bug检测
- 检测可变默认参数
- 检测除零错误风险
- 检测文件关闭问题

### 3. 渐进式复杂度
- `simple_code_agent.py` - 基础版本（推荐开始）
- `code_qa_agent.py` - 完整版本（更多功能）

## 扩展建议

根据agent-builder技能的渐进复杂度模型：

### Level 1: 基础（已完成）
- 3个核心能力
- 简单上下文

### Level 2: 增加规划能力
- 多步骤代码重构
- 测试生成
- 代码质量报告

### Level 3: 增加子代理
- 专门的bug检测代理
- 代码风格检查代理
- 性能优化代理

### Level 4: 增加技能系统
- 按需加载代码模式
- 框架特定知识（Django、Flask等）
- 算法优化知识

## 学习要点

1. **信任模型** - 代理不需要复杂的规则，AI模型会自己推理
2. **能力优先** - 先实现能做什么，再优化怎么做
3. **上下文是关键** - 保持上下文清晰，代理才能连贯工作
4. **从简单开始** - 大多数应用只需要基础能力

## 下一步

尝试运行代理并与它交互：
```bash
python simple_code_agent.py
```

然后尝试：
1. 列出文件
2. 解释一个文件
3. 运行测试文件
4. 尝试修复bug

体验agent-builder技能中强调的"简单循环"和"模型即代理"哲学。