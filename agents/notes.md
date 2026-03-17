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
















=====================================================


# 
