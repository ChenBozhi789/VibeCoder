# Smolagents Token-Efficient Editing Tools Implementation Plan

*Created: August 21, 2025*

## Executive Summary

Based on analysis of gemini-cli's sophisticated editing tools, design and implement token-efficient file editing tools for smolagents that enable precise, surgical edits without reading entire files into context.

## Analysis of Gemini-CLI Editing Patterns

### Key Insights from gemini-cli Tools

#### 1. Sophisticated Edit Tool (`edit.ts`)
**Core Pattern**: Exact string replacement with extensive validation
```typescript
// Key features:
- Uses exact literal text matching (old_string → new_string)
- Requires 3+ lines of context for precise targeting
- Validates occurrence count (expected_replacements)
- Uses ensureCorrectEdit() for AI-assisted correction
- Provides detailed error messages for failed matches
```

**Token Efficiency Techniques**:
- Only reads file once during calculateEdit()
- Caches content for validation and execution
- Uses diff patches for minimal display output
- Normalizes line endings for consistent processing

#### 2. Read File Tool (`read-file.ts`)
**Core Pattern**: Supports pagination with offset/limit
```typescript
// Token-saving features:
- offset: Start reading from specific line number
- limit: Read only N lines at a time
- Automatic truncation warnings with next-offset suggestions
- MIME type detection for different file handling
```

#### 3. Write File Tool (`write-file.ts`)
**Core Pattern**: Intelligent content correction before writing
```typescript
// Efficiency features:
- getCorrectedFileContent() validates before write
- ensureCorrectFileContent() for new files
- Handles file existence checking efficiently
- Creates parent directories automatically
```

#### 4. Read Many Files Tool (`read-many-files.ts`)
**Core Pattern**: Batch file operations with glob patterns
```typescript
// Scalability features:
- Processes multiple files in single operation
- Uses glob patterns for file selection
- Filters by include/exclude patterns
- Returns structured results for multiple files
```

#### 5. Grep Tool (`grep.ts`)
**Core Pattern**: Content search without full file reads
```typescript
// Search efficiency:
- Uses native tools (ripgrep) when available
- Supports regex patterns and file filtering
- Returns only matching lines with context
- Handles large codebases efficiently
```

## Token-Efficient Editing Strategy for Smolagents

### Problem Analysis
Current VibeCoder approach:
```python
# Token-heavy approach:
content = read_file("large_file.tsx")    # 500+ lines → many tokens
new_content = modify_content(content)    # Process entire file
write_file("large_file.tsx", new_content)  # Write entire file
```

### Solution: Surgical Editing Tools

#### A. Targeted String Replacement
```python
@tool
def replace_exact_text(file_path: str, old_text: str, new_text: str, occurrence_count: int = 1) -> str:
    """
    Replace exact text in file without reading entire file into context.
    
    Args:
        file_path: Absolute path to file
        old_text: Exact text to replace (include surrounding context)
        new_text: Replacement text
        occurrence_count: Expected number of replacements (default 1)
    
    Returns:
        Success message with replacement count
    """
    # Implementation uses file streaming to find/replace text
    # Only loads necessary parts into memory
    # Validates occurrence count matches expectation
```

#### B. Line-Based Editing
```python
@tool
def edit_lines(file_path: str, start_line: int, end_line: int, new_content: str) -> str:
    """
    Replace specific lines in file - ultra token efficient.
    
    Args:
        file_path: Absolute path to file
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (inclusive)
        new_content: New content for those lines
    
    Returns:
        Success message with line count
    """
    # Reads only the target line range
    # Preserves surrounding content
    # Minimal token usage
```

#### C. Section-Based Editing with Markers
```python
@tool
def edit_section(file_path: str, start_marker: str, end_marker: str, new_content: str) -> str:
    """
    Edit content between specific markers - perfect for React components.
    
    Args:
        file_path: Absolute path to file
        start_marker: Text that marks start of section to replace
        end_marker: Text that marks end of section to replace
        new_content: New content for the section
    
    Returns:
        Success message
    """
    # Example usage:
    # start_marker: "// BEGIN STATE SECTION"
    # end_marker: "// END STATE SECTION"
    # new_content: "const [todos, setTodos] = useState([]);"
```

#### D. Append/Prepend Operations
```python
@tool
def append_to_file(file_path: str, content: str, position: str = "end") -> str:
    """
    Append content to file without reading existing content.
    
    Args:
        file_path: Absolute path to file
        content: Content to append
        position: "end", "start", or "after:marker_text"
    
    Returns:
        Success message
    """
    # Ultra-efficient for adding imports, exports, etc.
    # No need to read entire file
```

#### E. Smart Component Insertion
```python
@tool
def add_react_component(file_path: str, component_name: str, props: dict = None, position: str = "before_closing_tag") -> str:
    """
    Add React component to JSX without reading entire file.
    
    Args:
        file_path: Path to React component file
        component_name: Name of component to add
        props: Optional props dictionary
        position: Where to insert ("before_closing_tag", "after_opening_tag", "replace_content")
    
    Returns:
        Success message with insertion details
    """
    # Uses AST parsing or regex to find insertion point
    # Generates JSX with proper formatting
    # Handles imports automatically if needed
```

#### F. Import Management
```python
@tool
def add_import(file_path: str, import_statement: str, import_type: str = "named") -> str:
    """
    Add import statement to file without reading entire content.
    
    Args:
        file_path: Path to file
        import_statement: Import to add (e.g., "useState" or "react-router-dom")
        import_type: "named", "default", "namespace", or "side-effect"
    
    Returns:
        Success message
    """
    # Intelligently places imports in correct location
    # Handles merging with existing imports
    # Sorts imports according to conventions
```

#### G. Search and Context Tools
```python
@tool
def find_function_context(file_path: str, function_name: str, context_lines: int = 5) -> str:
    """
    Find function and return it with surrounding context - minimal tokens.
    
    Args:
        file_path: Path to file
        function_name: Name of function to find
        context_lines: Lines of context around function
    
    Returns:
        Function definition with context
    """
    # Returns only the relevant part of file
    # Perfect for understanding before making changes
```

@tool
def search_pattern_in_file(file_path: str, pattern: str, max_matches: int = 10) -> str:
    """
    Search for pattern in file, return matches with line numbers.
    
    Args:
        file_path: Path to file
        pattern: Regex pattern to search for
        max_matches: Maximum number of matches to return
    
    Returns:
        Matching lines with line numbers and context
    """
    # Similar to grep but file-specific
    # Returns structured results for precise editing
```
```

## Implementation Architecture

### Simple Function-Based Approach

All tools implemented as standalone functions - no unnecessary classes or complex abstractions.

#### 1. File Manipulation Functions
```python
# file_editing.py

def read_file_lines(file_path: str, start_line: int = None, end_line: int = None) -> list[str]:
    """Read specific line range from file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    if start_line is not None and end_line is not None:
        return lines[start_line-1:end_line]  # Convert to 0-indexed
    return lines

def write_file_lines(file_path: str, lines: list[str]) -> None:
    """Write lines to file."""
    with open(file_path, 'w') as f:
        f.writelines(lines)

def find_text_in_file(file_path: str, search_text: str) -> list[int]:
    """Find line numbers containing text."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    return [i + 1 for i, line in enumerate(lines) if search_text in line]

def replace_text_in_file(file_path: str, old_text: str, new_text: str, expected_count: int = 1) -> dict:
    """Replace exact text in file with validation."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    count = content.count(old_text)
    if count != expected_count:
        return {"success": False, "error": f"Expected {expected_count} occurrences, found {count}"}
    
    new_content = content.replace(old_text, new_text)
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    return {"success": True, "replacements": count}
```

#### 2. React-Specific Functions
```python
# react_editing.py

import re

def find_react_imports(file_path: str) -> list[str]:
    """Find all import statements in React file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    import_pattern = r'^import.*?;$'
    return re.findall(import_pattern, content, re.MULTILINE)

def add_import_to_file(file_path: str, import_statement: str) -> str:
    """Add import statement to top of file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Find where to insert (after existing imports or at top)
    insert_line = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('import'):
            insert_line = i + 1
        elif line.strip() and not line.strip().startswith('import'):
            break
    
    lines.insert(insert_line, f"{import_statement};\n")
    
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    return f"Added import: {import_statement}"

def find_jsx_elements(content: str) -> list[dict]:
    """Find JSX elements using regex."""
    pattern = r'<(\w+)(?:\s+[^>]*)?(?:/>|>.*?</\1>)'
    matches = []
    for match in re.finditer(pattern, content, re.DOTALL):
        matches.append({
            'tag': match.group(1),
            'start': match.start(),
            'end': match.end(),
            'content': match.group(0)
        })
    return matches
```

#### 3. Simple Validation Functions
```python
# validation.py

import subprocess
import json

def create_backup(file_path: str) -> str:
    """Create backup file."""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    return backup_path

def restore_backup(backup_path: str, original_path: str) -> None:
    """Restore file from backup."""
    import shutil
    shutil.copy2(backup_path, original_path)
```

### Error Handling Strategy

#### Detailed Error Types
```python
class EditError(Exception):
    """Base class for edit errors."""
    pass

class TextNotFoundError(EditError):
    """Exact text not found for replacement."""
    def __init__(self, file_path: str, search_text: str):
        self.suggestions = self._generate_suggestions(search_text)
        super().__init__(f"Text not found in {file_path}. Suggestions: {self.suggestions}")

class OccurrenceCountMismatchError(EditError):
    """Wrong number of occurrences found."""
    def __init__(self, expected: int, found: int):
        super().__init__(f"Expected {expected} occurrences, found {found}")

class SyntaxValidationError(EditError):
    """Generated code has syntax errors."""
    def __init__(self, errors: list[str]):
        super().__init__(f"Syntax errors: {', '.join(errors)}")
```

#### Simple Recovery Functions
```python
# error_handling.py

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for fuzzy matching."""
    import re
    # Replace multiple whitespace with single space
    return re.sub(r'\s+', ' ', text.strip())

def suggest_similar_text(file_path: str, search_text: str, max_suggestions: int = 3) -> list[str]:
    """Find similar text in file for suggestions."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    suggestions = []
    
    # Simple similarity: lines that contain any word from search_text
    search_words = search_text.split()
    for line in lines:
        if any(word in line for word in search_words):
            suggestions.append(line.strip())
            if len(suggestions) >= max_suggestions:
                break
    
    return suggestions
```

## Smolagents Tool Definitions

### Core Editing Tools
```python
# editing_tools.py

from smolagents import tool

@tool
def replace_exact_text(file_path: str, old_text: str, new_text: str, expected_count: int = 1) -> str:
    """
    Replace exact text in file with occurrence validation.
    
    Args:
        file_path: Absolute path to file
        old_text: Exact text to replace (include context for precision)
        new_text: Replacement text
        expected_count: Expected number of replacements
    
    Returns:
        Success message with replacement count
    """
    result = replace_text_in_file(file_path, old_text, new_text, expected_count)
    if result["success"]:
        return f"Successfully replaced {result['replacements']} occurrences in {file_path}"
    else:
        return f"Failed to replace text: {result['error']}"

@tool
def edit_file_lines(file_path: str, start_line: int, end_line: int, new_content: str) -> str:
    """
    Replace specific line range in file.
    
    Args:
        file_path: Absolute path to file
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (inclusive)
        new_content: New content for those lines
    
    Returns:
        Success message
    """
    lines = read_file_lines(file_path)
    
    # Replace the specified range
    lines[start_line-1:end_line] = [new_content + '\n']
    
    write_file_lines(file_path, lines)
    return f"Replaced lines {start_line}-{end_line} in {file_path}"

@tool
def add_import_statement(file_path: str, import_statement: str) -> str:
    """
    Add import statement to React/TypeScript file.
    
    Args:
        file_path: Path to React component file
        import_statement: Import to add (e.g., "import { useState } from 'react'")
    
    Returns:
        Success message
    """
    return add_import_to_file(file_path, import_statement)

@tool
def find_text_locations(file_path: str, search_text: str) -> str:
    """
    Find line numbers containing specific text.
    
    Args:
        file_path: Path to file
        search_text: Text to search for
    
    Returns:
        Line numbers where text is found
    """
    line_numbers = find_text_in_file(file_path, search_text)
    if line_numbers:
        return f"Found text on lines: {', '.join(map(str, line_numbers))}"
    else:
        return f"Text not found in {file_path}"

@tool
def read_file_section(file_path: str, start_line: int, end_line: int) -> str:
    """
    Read specific lines from file for context.
    
    Args:
        file_path: Path to file
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (inclusive)
    
    Returns:
        Content of specified lines
    """
    lines = read_file_lines(file_path, start_line, end_line)
    return ''.join(lines)
```

### Quality Check Tools
```python
# quality_tools.py

@tool
def check_typescript_syntax(file_path: str) -> str:
    """
    Check TypeScript syntax using tsc compiler.
    
    Args:
        file_path: Path to TypeScript file
    
    Returns:
        Syntax check results
    """
    import subprocess
    
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit", file_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(file_path)
        )
        
        if result.returncode == 0:
            return f"✅ TypeScript syntax valid for {file_path}"
        else:
            return f"❌ TypeScript errors in {file_path}:\n{result.stderr}"
    
    except FileNotFoundError:
        return "❌ TypeScript compiler (tsc) not found. Run 'npm install -g typescript'"

@tool
def run_eslint_check(file_path: str) -> str:
    """
    Run ESLint on specific file.
    
    Args:
        file_path: Path to file to lint
    
    Returns:
        Linting results
    """
    import subprocess
    
    try:
        result = subprocess.run(
            ["npx", "eslint", file_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(file_path)
        )
        
        if result.returncode == 0:
            return f"✅ ESLint passed for {file_path}"
        else:
            return f"❌ ESLint errors in {file_path}:\n{result.stdout}"
    
    except FileNotFoundError:
        return "❌ ESLint not found. Install with 'npm install eslint'"

@tool
def build_react_app(app_directory: str) -> str:
    """
    Build React app to check for errors.
    
    Args:
        app_directory: Path to React app directory
    
    Returns:
        Build results
    """
    import subprocess
    import os
    
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            capture_output=True,
            text=True,
            cwd=app_directory
        )
        
        if result.returncode == 0:
            return f"✅ Build successful for {app_directory}"
        else:
            return f"❌ Build failed for {app_directory}:\n{result.stderr}"
    
    except Exception as e:
        return f"❌ Build error: {e}"
```

### Simple Agent Setup
```python
# agent_setup.py

from smolagents import CodeAgent, OpenAIServerModel

# Import all editing tools
from editing_tools import (
    replace_exact_text,
    edit_file_lines, 
    add_import_statement,
    find_text_locations,
    read_file_section
)

from quality_tools import (
    check_typescript_syntax,
    run_eslint_check,
    build_react_app
)

# Create agent with all tools
editing_agent = CodeAgent(
    tools=[
        # File editing
        replace_exact_text,
        edit_file_lines,
        add_import_statement,
        find_text_locations,
        read_file_section,
        
        # Quality checks  
        check_typescript_syntax,
        run_eslint_check,
        build_react_app,
        
        # File system tools from am_tools.py
        read_file,
        write_file,
        list_files,
        mkdir
    ],
    model=OpenAIServerModel("gpt-5"),
    additional_authorized_imports=["subprocess", "re", "os", "shutil"]
)
```

## Example Usage Workflow

### Typical Agent Workflow
```python
# Example: Add a new feature to React component

# 1. First, understand the current file
context = read_file_section("src/App.tsx", 1, 20)
print(f"Current App.tsx content:\n{context}")

# 2. Find where to add new import
import_locations = find_text_locations("src/App.tsx", "import")
print(f"Imports found on lines: {import_locations}")

# 3. Add required import
add_import_statement("src/App.tsx", "import { useState } from 'react'")

# 4. Find where to add new state
state_location = find_text_locations("src/App.tsx", "function App")
print(f"App function on lines: {state_location}")

# 5. Add state using exact text replacement
old_text = """function App() {
  return ("""

new_text = """function App() {
  const [count, setCount] = useState(0);
  return ("""

replace_exact_text("src/App.tsx", old_text, new_text)

# 6. Validate the changes
check_typescript_syntax("src/App.tsx")
run_eslint_check("src/App.tsx")

# 7. Test build
build_react_app(".")
```

### Simple Error Recovery
```python
# If replacement fails, get suggestions
try:
    replace_exact_text("src/App.tsx", old_text, new_text)
except Exception as e:
    print(f"Edit failed: {e}")
    
    # Get context to understand what's wrong
    context = read_file_section("src/App.tsx", 1, 50)
    print(f"Current file content:\n{context}")
    
    # Find similar text for suggestions
    suggestions = suggest_similar_text("src/App.tsx", "function App")
    print(f"Similar text found: {suggestions}")
```

## Simple Quality Check Pattern

### Agent Self-Checking Workflow
```python
# Agent workflow: Make edit, then check quality
# No compound tools - agent decides when to check

# 1. Make the edit
result = replace_exact_text("src/App.tsx", old_text, new_text)
print(result)

# 2. Agent chooses to check syntax
syntax_check = check_typescript_syntax("src/App.tsx")
print(syntax_check)

# 3. If syntax fails, agent can investigate and fix
if "❌" in syntax_check:
    # Agent reads the file to understand the issue
    content = read_file_section("src/App.tsx", 1, 30)
    print(f"Checking content: {content}")
    
    # Agent makes corrective edit
    # ... additional edit operations

# 4. Agent checks linting
lint_check = run_eslint_check("src/App.tsx")
print(lint_check)

# 5. Agent tests build
build_result = build_react_app(".")
print(build_result)
```

### Manual Backup Pattern
```python
# Agent can create backups when needed
backup_path = create_backup("src/App.tsx")
print(f"Created backup: {backup_path}")

# Make potentially risky edits
try:
    replace_exact_text("src/App.tsx", complex_old_text, complex_new_text)
    
    # Check if edit was successful
    if check_typescript_syntax("src/App.tsx").startswith("❌"):
        restore_backup(backup_path, "src/App.tsx")
        print("Restored from backup due to syntax errors")
        
except Exception as e:
    restore_backup(backup_path, "src/App.tsx") 
    print(f"Restored from backup due to error: {e}")
```

## Implementation Timeline

### Phase 1: Core File Operations (Week 1)
- ✅ Implement `replace_exact_text` with validation
- ✅ Implement `edit_file_lines` for line-based editing
- ✅ Implement `find_text_locations` for search
- ✅ Implement `read_file_section` for context
- ✅ Basic error handling and backup functions

### Phase 2: React Tools & Quality Checks (Week 2)
- ⚠️ Implement `add_import_statement` with smart insertion
- ⚠️ Implement `check_typescript_syntax` tool
- ⚠️ Implement `run_eslint_check` tool
- ⚠️ Implement `build_react_app` tool
- ⚠️ React import parsing and JSX utilities

### Phase 3: Integration & Testing (Week 3)
- ⚠️ Integrate with existing am_tools.py
- ⚠️ Create comprehensive test suite
- ⚠️ Error recovery and suggestion functions
- ⚠️ Agent workflow examples and documentation
- ⚠️ Performance testing with real files

### Phase 4: Polish & Optimization (Week 4)
- ⚠️ Optimize regex patterns for better matching
- ⚠️ Improve error messages and suggestions
- ⚠️ Add more React-specific patterns
- ⚠️ Complete documentation and examples
- ⚠️ Integration with template generator

## Success Metrics

### Token Efficiency
- **Target**: 90% reduction in tokens for typical edits
- **Baseline**: Full file read (500+ tokens) → Surgical edit (50 tokens)
- **Method**: Use `read_file_section()` and targeted replacements

### Accuracy
- **Target**: 95% success rate for exact text replacement
- **Validation**: TypeScript syntax and ESLint checks prevent broken code
- **Recovery**: Simple suggestion system for failed matches

### Performance  
- **Target**: <100ms for typical file edits
- **Simplicity**: Regex-based operations, no complex parsing
- **Memory**: Read only needed portions, no file caching

### Quality
- **Build Success**: 100% of edits must not break TypeScript compilation
- **Lint Compliance**: Tools available for agents to self-check
- **Backup Safety**: Simple backup/restore for risky operations

## Future Enhancements

### Enhanced React Patterns
```python
@tool
def add_react_hook(file_path: str, hook_type: str, hook_name: str, initial_value: str) -> str:
    """Add React hook with proper positioning."""

@tool  
def add_jsx_component(file_path: str, component_jsx: str, target_element: str) -> str:
    """Add JSX component inside target element."""
```

### Smarter Text Matching
```python
@tool
def fuzzy_replace_text(file_path: str, approximate_text: str, new_text: str) -> str:
    """Replace text with fuzzy matching for whitespace differences."""
```

### Project-Wide Operations
```python
@tool
def add_import_to_project(import_statement: str, file_pattern: str) -> str:
    """Add import to multiple files matching pattern."""
```

---

**Legend:**
- ✅ Completed
- ⚠️ In Progress/Planned
- 🔮 Future Enhancement

This implementation plan provides a comprehensive approach to building token-efficient, surgical editing tools for smolagents, inspired by the sophisticated patterns found in gemini-cli but adapted for the smolagents architecture and React development workflow.