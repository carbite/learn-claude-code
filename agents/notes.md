# (LLM+工具)的循环 = agent

1. 核心机制：
```
    while stop_reason == "tool_use":
        response = LLM(messages, tools)
        execute tools
        append results
```
  - 循环退出条件：模型不再调用工具
  - 上下文列表：sp，用户输入->模型回复->工具结果->模型回复->工具结果...->模型回复->用户输入->...

2. 工具定义需符合json schema标准
```
{
  "type": "object",
  "properties": {
    "参数名1": {
      "type": "数据类型",
      "description": "对这个参数的详细描述"
    },
    "参数名2": {
      "type": "数据类型",
      "enum": ["选项A", "选项B"]
    }
  },
  "required": ["参数名1"] 
}
```

3. role一般定义system、user、assistant、tool几种。（openAI标准）
  - Anthropic（Claude），没有独立的tool角色，结果放在user里，但content里专门标记这是一个工具结果。
  - Google（Gemini），function角色

4. tool_call_id（OpenAI）
  - tool_use_id（Anthropic）
  - 作用：大模型要求执行工具时，自动生成的唯一流水号。核心作用是：对号入座。它的存在是为了应对“并发工具调用”的场景。
  - 完整生命周期：a. 大模型决定使用工具时随机生成tool_call_id。 b.解析参数，工具调用。 c. 封装工具结果为JSON，把刚才的id贴回去发给LLM。 d. LLM把结果的id和之前的问题匹配，给出回答。
  - 校验流程：当你把messages列表发给 OpenAI 或 Anthropic 的服务器时，在数据真正进入大模型（神经网络）进行推理之前，API 网关（拦截器）会先做一次“严格的语法和逻辑体检”。
    - 查“孤儿”：网关看到了最后一条是 role: "tool"，它要求携带 tool_call_id。于是网关会往回看你的聊天记录，寻找前面有没有哪个 assistant 曾经发起过这个 ID 的调用。如果没找到（比如你瞎编了一个 ID，或者漏传了第二回合的记录），网关直接打回：400 Bad Request: Invalid tool_call_id。
    - 查“烂尾”：如果网关看到聊天记录里，assistant 发起了两个 tool_calls（比如 call_A 和 call_B），但在后面的记录里只看到了 call_A 的结果，就开始要求模型生成下一步回复，网关也会报错，因为它认为你的逻辑没有闭环。
  - 大模型本身是无状态的，它通过阅读完整的、带有严密逻辑链的上下文回答问题。如果前后文对不上号，大模型厂商的API接口会拦截。
  - 自己编也可以，只要构造出逻辑严密不冲突的上下文即可。

=====================================================


# 工具分发


1. insight：新增工具只用加schema和handler，不用改核心循环（写if-else）
  - 多工具实现为dispatch map。


2. 安全目录
```
# 获取当前工作目录（命令执行的目录，不是文件目录）
WORKDIR = Path.cwd()
def safe_path(p: str) -> Path:
    # WORKDIR / p：利用 pathlib 把基础目录和传入的相对路径 p 拼接在一起。
    # .resolve()：计算出这个路径的最终真实绝对路径。自动处理./..
    path = (WORKDIR / p).resolve()
    # 判断path是否为WORKDIR的子目录
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path
```

3. bash vs read/write/edit工具
  - bash可以通过cat读文件，echo或cat <<EOF写文件，用sed或awk改文件。但实际表现不佳：
    - 模型用bash写文档，大概率会将引号，双引号，反斜杠搞乱。用专用write工具写，模型直接无脑调用，不需要考虑转义问题。
    - sed修改文件需要复杂正则，专用edit工具更安全。
    - bash读文件，很容易cat file.log，直接上下文塞满。专用read工具内置分页、行号过滤等。
    - 报错更友好，利于模型自己修复问题。
  - bash是万能大锤，适合执行系统命令、起停服务、安装依赖。
  - read..是精密手术刀，专门用来解决LLM处理文本时的智力短板和格式缺陷。

4. 工具定义
```
# -- The dispatch map: {tool_name: handler} --
# lambda **kw: 将传入的参数变为一个字典 kw，方便调用对应的工具函数；工具函数根据需要从 kw 中提取参数。
TOOL_HANDLERS = {
    "bash":       lambda **kw: run_bash(kw["command"]),
    "read_file":  lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":  lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
}

TOOLS = [
    {"name": "bash", "description": "Run a shell command.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "read_file", "description": "Read file contents.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write content to file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "edit_file", "description": "Replace exact text in file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}},
]
```
  - TOOLS是给LLM看的说明书（有哪些工具，参数是什么）
  - TOOL_HANDLERS是给Python代码用的路由表，把LLM输出的文本指令映射到本地真实函数上。
  - 如果没有TOOL_HANDLERS，就需要在“核心循环”里写很多if-else
  - `lambda **kw`接收大模型传来的字典，从中安全提取参数喂给工具函数。kw.get('limit')写法可处理非必传参数。
  - `**block.input`可以将LLM给出的参数（map）解包为若干参数。
  ```
  block.input = {"command": "ls", "timeout": 30}
  # 如果你直接解包给底层函数
  run_bash(**block.input) 
  # 等价于 run_bash(command="ls", timeout=30)
  ```


=====================================================


# Todo List


1. 背景：多步任务中，模型会丢失进度：重复做过的事，跳步，跑偏。对话越长越严重：工具结果不断填满上下文，System Prompt的注意力逐渐被稀释。
  - 一个10步重构可能做完1-3步就开始即兴发挥，因为4-10步已经被挤出注意力了。

2. 核心insight：通过`todo manager`让agent自己可以追踪进度，配合nag reminder注入提醒。
**"同时只能有一个 in_progress" 强制顺序聚焦。nag reminder 制造问责压力 -- 你不更新计划, 系统就追着你问。**
  - 限制todo个数、格式必须规范
  - 同一时间只允许一个in_progess。
  - todo工具也和其他一样作为工具加入dispatch map。
    - todo工具的核心价值在于“锚定目标”，强制LLM在复杂探索中保持理智和条理，如果是简单的短平快agent（2-3轮），直接prompt控制或思维链即可。
  - nag reminder：模型连续3轮以上不调用todo时注入提醒。


3. 要求LLM使用todo工具：
  - system prompt
  - 工具描述，写成行为触发条件
  - 在工具层硬拦截，调用工具前检查todo list是否为空。
  - 首轮：tool_choice，强制模型在这次请求中，必须调用add_todo工具。
  - 本case中，是通过nag reminder在循环中强制提醒。

4. todo工具的意义：
  - 抵抗长程任务，上下文失忆，找回全局视野。比如模型目标是搭网站，中间配置nginx时遇到报错，调用了15次工具去查日志，解问题，会由于注意力机制的便宜，忘记最初的任务，以为自己是修nginx的agent
  - 强制先规划，后执行。降低幻觉率
  - 斩断死循环，防止钻牛角尖，卡在一个todo多次后模型会反思是否应拆分步骤或者换个思路。
  - 破局黑盒效应，人类可观测

5. 踩坑：对于 Anthropic API 来说，它的底层校验有着极其严苛的顺序强迫症：当你回复上一轮的 tool_use（工具调用）时，在组装 user 消息的 content 数组时，所有的 tool_result 块必须放在数组的最前面！任何附加的 text 文本块，必须放在所有工具结果的后面。
  - 错：
  ```
  results.insert(0, {"type": "text", "text": "<reminder>Update your todos.</reminder>"})
  ```
  - 对：
  ```
  results.append({"type": "text", "text": "<reminder>Update your todos.</reminder>"})
  ```


=====================================================


# 子Agent

1. 背景：智能体工作越久, messages 数组越胖。每次读文件、跑命令的输出都永久留在上下文里。"这个项目用什么测试框架?" 可能要读 5 个文件, 但父智能体只需要一个词: "pytest。"

2. 核心insight：**"大任务拆小, 每个小任务干净的上下文" -- 子智能体用独立 messages[], 不污染主对话。**
  - 主agent拥有task工具和其他普通工具，子agent拥有除task外的其他工具。（防递归）
  - 子agent以空数组启动（只有主agent提供的1轮对话；限制调用工具次数-防止死机，丢掉过程的上下文，只返回最终结果的摘要。


3. 子agent的意义：
  - 物理隔离上下文。避免上下文爆炸污染主agent注意力。
  - 系统提示词纯度更高，防止人格分裂。
  - 工具权限可以通过子agent隔离，降低危险系数。
  - 防止死循环。主agent给子agent限制轮次。




=====================================================


# Skill

1. 背景：希望智能体遵循特定领域的工作流: git 约定、测试模式、代码审查清单。全塞进系统提示太浪费 -- 10 个技能, 每个 2000 token, 就是 20,000 token, 大部分跟当前任务毫无关系。

2. 核心insight：**"用到什么知识, 临时加载什么知识" -- 通过 tool_result 注入, 不塞 system prompt。**
  - 第一层: 系统提示中放技能名称 (低成本)。第二层: tool_result 中按需放完整内容。
  - 每个技能是一个目录, 包含 SKILL.md 文件和 YAML frontmatter。
  - SkillLoader 递归扫描 SKILL.md 文件, 用目录名作为技能标识。
  - 第一层写入系统提示。第二层不过是 dispatch map 中的又一个工具。
  - 模型知道有哪些技能 (便宜), 需要时再加载完整内容 (贵)。

3. skill的实现：
  - 一般一个skill对应一个文件夹，包含SKILL.md，以及一些脚本，代码等。
  - SKILL.md，一般在最开头通过---包括一段配置信息，称为YAML Frontmatter。在加载时，递归查找skill目录下的所有SKILL.md，解析其开头的yaml（meta）获取skill name和desc，其余部分作为skill的body。
  - layer 1:获取所有skill的desc，拼接后直接塞入sp
  - 加载技能body实现为一个tool
  - layer 2:LLM在需要时会调用工具，将skill body作为tool result塞入注入上下文。

4. skill的意义：
  - 突破预训练边界，能力无限扩展。
  - 上下文管理。渐进式加载
  - 封装人类的最佳实践，SOP固化
  - 架构解耦，模型能力和业务逻辑剥离开。

5. 怎么写skill
  a. 界定边界和依赖，它能做什么？依赖什么tool;（脚本需要bash tool）
  b. 编写YAML头部，写成“触发声明”。
  c. 正文SOP，<skill>...</skill>中的内容。包括“角色和目标”，“标准操作流”，“输出规范”，“防御性规则”
  d. 注入Few-shot
一个模板：
```
---
name: github_pr_reviewer
description: 当用户要求 "review code" 或 "检查 PR" 时必须触发此技能。包含代码审查的严谨流程。
tags: code, github, review
---
# GitHub PR 审查指南

你是一个以苛刻著称的高级架构师。你需要对用户的代码进行极其严格的审查。

## 核心流程
1. **理解意图**：如果代码没有注释说明目的，要求用户先补充。
2. **执行检索**：请使用你的 `bash` 工具，运行 `grep` 或 `cat` 查看相关依赖文件，不要只看被修改的几行。
3. **安全性扫描**：重点排查 SQL 注入、硬编码密钥。
4. **性能评估**：检查是否有 O(n^2) 的不合理嵌套循环。

## 严格禁忌
- 绝对不要只回复 "LGTM" 或 "代码看起来不错"。
- 如果发现严重安全漏洞，必须用 `<CRITICAL_WARNING>` 标签包裹你的警告。

## 输出格式
请使用以下格式返回审查结果：
### 🐛 发现的问题
- [严重程度] 描述

### 💡 修改建议
(给出具体的代码片段)
```


=====================================================


# 上下文压缩


1. 背景：上下文窗口是有限的。读一个 1000 行的文件就吃掉 ~4000 token; 读 30 个文件、跑 20 条命令, 轻松突破 100k token。不压缩, 智能体根本没法在大项目里干活。

2. 核心insight：**"上下文总会满, 要有办法腾地方" -- 三层压缩策略, 换来无限会话。**

3. 第一层：micro_compact:每次LLM调用前，将旧的tool result替换为占位符。
> 不能直接删除历史记录里的工具返回，不然会报错，也会上下文对不齐
  - 触发条件是，每一轮都跑，反正成本低，还快。
  - 收集所有工具结果，记录位置
  - 如果工具结果个数小于特定阈值（3，5），说明还在短期记忆，跳过不处理。
  - 根据tool_use_id找到assistant消息里，对应的tool_name，建立tool_use_id 2 tool_name的map
  - 将那些3轮以前的，长度大于100的工具结果，直接替换掉其content，替换为[Previous: used tool_name]

4. 第二层：auto_compact:token 超过阈值时, 保存完整对话到磁盘, 让 LLM 做摘要。
  - 触发条件是：上下文长度达到阈值时，保命情况。
  - 持久化完整msg到磁盘
  - 大模型摘要-整个msg历史的前80000
  - 构造假的对话记录，抛弃了所有msg，只保留以下两轮
    - User假装说：前面的对话已经压缩存盘了，这个是摘要：【摘要】
    - Assistant假装回答：“明白，我已经掌握了上下文，咱们继续吧”
  - 保命

5. 第三层：第三层 -- manual compact: compact 工具按需触发同样的摘要机制。
  - 模型来调用auto_compact
  - 给模型一种高级的能力，让它自己决定什么时候应该收拾上下文。


6. 更多insight：
  - 平时每一轮：micro_compact，低成本，快速；日常垃圾回收
  - 极限情况或有必要时：auto_compact，成本高，慢；


=====================================================


# 任务系统

1. 背景：TodoManager 只是内存中的扁平清单: 没有顺序、没有依赖、状态只有做完没做完。真实目标是有结构的 -- 任务 B 依赖任务 A, 任务 C 和 D 可以并行, 任务 E 要等 C 和 D 都完成。没有显式的关系, 智能体分不清什么能做、什么被卡住、什么能同时跑。而且清单只活在内存里, 上下文压缩一跑就没了。


2. insight: **存入磁盘持久化，避免丢失，为多agent协作打基础；任务之间补充依赖关系，更加符合真实情况。**
  - task manager，支持create,get,update,list_all
  - 存储结构：每一个任务存储一个JSON文件。多个任务可以拼成一个DAG。
  - 任务定义：
  ```
  task = {
    "id": self._next_id, 
    "subject": subject, 
    "description": description,
    "status": "pending", 
    "blockedBy": [], 
    "blocks": [], 
    "owner": "", # <- 这个 owner 字段非常有野心！
}
  ```
  - id保持自增。
  - 自动补全双向的依赖关系；任务完成后自动清理依赖；这些工作通过代码逻辑完成。
  - 每次只生成/修改一个task，让模型直接生成一个复杂任务系统的DAG，可能会出错，陷入幻觉死锁。单独整可以增量更新。
  - 应该补充循环依赖、依赖缺失/冗余的检查。


3. todo manager VS task manager
  - todo manager本质上记录的是文本文档；task manager记录、维护的是状态机、DAG这种要求100%确定性的东西，不适合LLM这个文科生。
  - todo时，LLM拥有上次视角，但当任务数量变大有100个时，每一次更新任务都会消耗大量token，且容易出错；task时，LLM只触碰图中的一个节点，工程侧负责完成其余级连触发的责任。
  - 认知卸载，把LLM当傻子用，LLM的脑容量（注意力机制）极其宝贵，不要让它分心在任务图更新这种后勤逻辑上。


4. 汇总一下可优化项：
  - 双边依赖关系维护，不完整；
  - 既然维护了DAG，缺少循环依赖检测，只有add_block方法；
  - 存在上下文过载问题，任务数量过大时，list_all会占用大量token。可动态view



=====================================================


# 后台任务

1. 背景：有些命令要跑好几分钟: npm install、pytest、docker build。阻塞式循环下模型只能干等。用户说 "装依赖, 顺便建个配置文件", 智能体却只能一个一个来。

2. insight:**"慢操作丢后台, agent 继续想下一步" -- 后台线程跑命令, 完成后注入通知。**
  - BackgroundManager：支持run()跑异步任务；check()检查任务执行状态；drain_notifications()任务跑完之后中断通知队列。
  - tasks:全局状态表；`_notification_queue`消息信箱；`_lock`锁，防止同时读写消息信箱。
  - run方法极速返回，任务异步执行（`_execute`）：执行、更新任务状态、更新通知队列。

3. 实现异步任务的关键：
  - 任务异步执行，直接返回；
  - 通知方式1:给模型检查任务的工具。
  - 通知方式2:任务执行完成时，加入消息队列，主agent每一轮loop消费信件，如果已经完成，则构造messages.
  ```
    messages.append({"role": "user", "content": f"<background-results>\n{notif_text}\n</background-results>"})
    messages.append({"role": "assistant", "content": "Noted background results."})
  ```

























=====================================================


# 
