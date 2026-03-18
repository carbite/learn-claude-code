# Example Usage with Claude

Once you have your MCP servers configured and running with Claude, here are examples of how to use them:

## General Purpose Tools (`my_mcp_server.py`)

### File Operations
```
"Read the contents of my README.md file"
"List all files in the current directory"
"Write 'Hello World' to test.txt"
"Get information about the config.json file"
```

### System Information
```
"Show me system information"
"Check disk usage for the current directory"
```

### Web Tools
```
"Fetch the latest news from example.com"
"Check if google.com is reachable"
```

### Data Processing
```
"Format this JSON string: {'name': 'test', 'value': 123}"
"Analyze the statistics of this text"
"Wrap this long text to 80 characters"
```

## Code Analysis (`code_analysis_server.py`)

### Code Review
```
"Analyze the structure of main.py"
"Find all functions in utils.py"
"Check the syntax of my script.py"
```

### Project Analysis
```
"Count lines of code in the src directory"
"Search for 'TODO' comments in all Python files"
"Show me the directory tree structure"
```

### Specific Queries
```
"How many functions are in the models module?"
"Are there any syntax errors in my code?"
"What's the total lines of code in this project?"
```

## Weather Information (`weather_server.py`)

### Current Weather
```
"Get current weather in Tokyo"
"What's the weather like in Paris today?"
"Show me weather for New York, US"
```

### Forecasts
```
"Get 3-day forecast for London"
"What's the weather forecast for Berlin?"
```

### Utilities
```
"Convert 25°C to Fahrenheit"
"Compare weather between Sydney and Melbourne"
"Check air quality in Beijing"
```

## Combined Usage Examples

### Project Setup Assistant
```
"I'm starting a new Python project. Can you:
1. Create a directory structure for me
2. Set up a basic README.md
3. Create a requirements.txt file
4. Initialize a git repository"
```

### Code Review Workflow
```
"Please review my codebase:
1. Analyze all Python files for structure
2. Check for syntax errors
3. Count total lines of code
4. Find any TODO or FIXME comments"
```

### Weather Planning
```
"I'm planning a trip. Can you:
1. Compare weather between London and Paris
2. Get 5-day forecast for both cities
3. Check air quality
4. Suggest which city has better weather?"
```

## Advanced Prompt Patterns

### Sequential Tool Use
```
"First, read the project structure. Then, analyze the main.py file. Finally, check for any syntax issues."
```

### Conditional Tool Use
```
"If there are more than 1000 lines of code, analyze the largest file. Otherwise, check all files for functions."
```

### Data Processing Pipeline
```
"Read data.json, format it nicely, analyze the text statistics, and save the analysis to report.txt"
```

## Tips for Effective Use

1. **Be Specific**: Instead of "check files", say "check Python files in src/ directory"
2. **Use Natural Language**: Claude understands "what's in this folder?" as well as "list directory"
3. **Chain Operations**: Ask for multiple related operations in one request
4. **Provide Context**: Mention file paths or parameters when relevant
5. **Verify Results**: Ask Claude to explain what it found or show summaries

## Example Conversation

**User**: "I'm working on a Python project. Can you analyze the code quality?"

**Claude**: "I'll help you analyze your Python project. Let me start by examining the directory structure and then analyze the Python files."

*Claude uses `list_directory` to see files, then `analyze_python_file` on each .py file*

**Claude**: "I found 3 Python files with a total of 450 lines. main.py has 2 functions and good documentation. There's one TODO comment in utils.py. Would you like me to show you the specific findings or check for syntax errors?"

**User**: "Yes, check for syntax errors and show me the TODO comment"

*Claude uses `check_python_syntax` and `search_in_files`*

**Claude**: "All files have valid syntax. The TODO comment is in utils.py line 45: '# TODO: Add error handling for edge cases'"

This shows how Claude can intelligently combine multiple MCP tools to provide comprehensive assistance!