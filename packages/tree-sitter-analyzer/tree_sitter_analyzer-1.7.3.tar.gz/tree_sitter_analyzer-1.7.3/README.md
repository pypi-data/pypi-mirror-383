# 🌳 Tree-sitter Analyzer

**English** | **[日本語](README_ja.md)** | **[简体中文](README_zh.md)**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-2831%20passed-brightgreen.svg)](#quality-assurance)
[![Coverage](https://img.shields.io/badge/coverage-79.19%25-green.svg)](#quality-assurance)
[![Quality](https://img.shields.io/badge/quality-enterprise%20grade-blue.svg)](#quality-assurance)
[![PyPI](https://img.shields.io/pypi/v/tree-sitter-analyzer.svg)](https://pypi.org/project/tree-sitter-analyzer/)
[![Version](https://img.shields.io/badge/version-1.7.3-blue.svg)](https://github.com/aimasteracc/tree-sitter-analyzer/releases)
[![GitHub Stars](https://img.shields.io/github/stars/aimasteracc/tree-sitter-analyzer.svg?style=social)](https://github.com/aimasteracc/tree-sitter-analyzer)

## 🚀 Enterprise-Grade Code Analysis Tool for the AI Era

> **Deep AI Integration · Powerful File Search · Multilingual Support · Intelligent Code Analysis**

## 📋 Table of Contents

- [1. 💡 Project Features](#1--project-features)
- [2. 📋 Prerequisites (Required for All Users)](#2--prerequisites-required-for-all-users)
- [3. 🚀 Quick Start](#3--quick-start)
  - [3.1 🤖 AI Users (Claude Desktop, Cursor, etc.)](#31--ai-users-claude-desktop-cursor-etc)
  - [3.2 💻 CLI Users (Command Line Tools)](#32--cli-users-command-line-tools)
  - [3.3 👨‍💻 Developers (Source Code Development)](#33--developers-source-code-development)
- [4. 📖 Usage Workflow & Examples](#4--usage-workflow--examples)
  - [4.1 🔄 AI Assistant SMART Workflow](#41--ai-assistant-smart-workflow)
- [5. 🤖 Complete MCP Tool List](#5--complete-mcp-tool-list)
- [6. ⚡ Complete CLI Commands](#6--complete-cli-commands)
- [7. 🛠️ Core Features](#7-️-core-features)
- [8. 🏆 Quality Assurance](#8--quality-assurance)
- [9. 📚 Documentation & Support](#9--documentation--support)
- [10. 🤝 Contributing & License](#10--contributing--license)

---

## 1. 💡 Project Features

Tree-sitter Analyzer is an enterprise-grade code analysis tool designed for the AI era, providing:

| Feature Category | Key Capabilities | Core Benefits |
|------------------|------------------|---------------|
| **🤖 Deep AI Integration** | • MCP Protocol Support<br>• SMART Workflow<br>• Token Limitation Breaking<br>• Natural Language Interaction | Native support for Claude Desktop, Cursor, Roo Code<br>Systematic AI-assisted methodology<br>Handle code files of any size<br>Complex analysis via natural language |
| **🔍 Powerful Search** | • Intelligent File Discovery<br>• Precise Content Search<br>• Two-Stage Search<br>• Project Boundary Protection | fd-based high-performance search<br>ripgrep regex content search<br>Combined file + content workflow<br>Automatic security boundaries |
| **📊 Intelligent Analysis** | • Fast Structure Analysis<br>• Precise Code Extraction<br>• Complexity Analysis<br>• Unified Element System | Architecture understanding without full read<br>Line-range code snippet extraction<br>Cyclomatic complexity metrics<br>Revolutionary element management |

### 🌍 Enterprise Multi-language Support

| Programming Language | Support Level | Key Features |
|---------------------|---------------|--------------|
| **Java** | Complete Support | Spring framework, JPA, enterprise features |
| **Python** | Complete Support | Type annotations, decorators, modern Python features |
| **JavaScript** | Complete Support | ES6+, React/Vue/Angular, JSX |
| **TypeScript** | Complete Support | Interfaces, types, decorators, TSX/JSX, framework detection |
| **Markdown** | 🆕 Complete Support | Headers, code blocks, links, images, tables, task lists, blockquotes |
| **C/C++** | Basic Support | Basic syntax parsing |
| **Rust** | Basic Support | Basic syntax parsing |
| **Go** | Basic Support | Basic syntax parsing |

### 🏆 Production Ready
- **2,831 Tests** - 100% pass rate, enterprise-grade quality assurance
- **79.19% Coverage** - Comprehensive test coverage
- **Cross-platform Support** - Compatible with Windows, macOS, Linux
- **Continuous Maintenance** - Active development and community support

---

## 2. 📋 Prerequisites (Required for All Users)

Regardless of whether you are an AI user, CLI user, or developer, you need to install the following tools first:

### 1️⃣ Install uv (Required - for running tools)

**uv** is a fast Python package manager used to run tree-sitter-analyzer.

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```bash
uv --version
```

### 2️⃣ Install fd and ripgrep (Required for search functionality)

**fd** and **ripgrep** are high-performance file search and content search tools used for advanced MCP functionality.

| Operating System | Package Manager | Installation Command | Notes |
|-----------------|----------------|---------------------|-------|
| **macOS** | Homebrew | `brew install fd ripgrep` | Recommended |
| **Windows** | winget | `winget install sharkdp.fd BurntSushi.ripgrep.MSVC` | Recommended |
| | Chocolatey | `choco install fd ripgrep` | Alternative |
| | Scoop | `scoop install fd ripgrep` | Alternative |
| **Ubuntu/Debian** | apt | `sudo apt install fd-find ripgrep` | Official repository |
| **CentOS/RHEL/Fedora** | dnf | `sudo dnf install fd-find ripgrep` | Official repository |
| **Arch Linux** | pacman | `sudo pacman -S fd ripgrep` | Official repository |

**Verify installation:**
```bash
fd --version
rg --version
```

> **⚠️ Important Note:** 
> - **uv** is required for running all functionality
> - **fd** and **ripgrep** are required for using advanced file search and content analysis features
> - If fd and ripgrep are not installed, basic code analysis functionality will still be available, but file search features will not work

---

## 3. 🚀 Quick Start

### 3.1 🤖 AI Users (Claude Desktop, Cursor, etc.)

**For:** Users who use AI assistants (such as Claude Desktop, Cursor) for code analysis

#### ⚙️ Configuration Steps

**Claude Desktop Configuration:**

1. Find the configuration file location:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

2. Add the following configuration:

**Basic Configuration (Recommended - auto-detect project path):**
```json
{
  "mcpServers": {
    "tree-sitter-analyzer": {
      "command": "uv",
      "args": [
        "run", "--with", "tree-sitter-analyzer[mcp]",
        "python", "-m", "tree_sitter_analyzer.mcp.server"
      ]
    }
  }
}
```

**Advanced Configuration (manually specify project path):**
```json
{
  "mcpServers": {
    "tree-sitter-analyzer": {
      "command": "uv",
      "args": [
        "run", "--with", "tree-sitter-analyzer[mcp]",
        "python", "-m", "tree_sitter_analyzer.mcp.server"
      ],
      "env": {
        "TREE_SITTER_PROJECT_ROOT": "/absolute/path/to/your/project",
        "TREE_SITTER_OUTPUT_PATH": "/absolute/path/to/output/directory"
      }
    }
  }
}
```

3. Restart AI client

4. Start using! Tell the AI:
   ```
   Please set the project root directory to: /path/to/your/project
   ```

**Other AI Clients:**
- **Cursor**: Built-in MCP support, refer to Cursor documentation for configuration
- **Roo Code**: Supports MCP protocol, use the same configuration format
- **Other MCP-compatible clients**: Use the same server configuration

---

### 3.2 💻 CLI Users (Command Line Tools)

**For:** Developers who prefer using command line tools

#### 📦 Installation

```bash
# Basic installation
uv add tree-sitter-analyzer

# Popular language packages (recommended)
uv add "tree-sitter-analyzer[popular]"

# Complete installation (including MCP support)
uv add "tree-sitter-analyzer[all,mcp]"
```

#### ⚡ Quick Experience

```bash
# View help
uv run python -m tree_sitter_analyzer --help

# Analyze large file scale (1419 lines completed instantly)
uv run python -m tree_sitter_analyzer examples/BigService.java --advanced --output-format=text

# Generate detailed structure table for code files
uv run python -m tree_sitter_analyzer examples/BigService.java --table=full

# Precise code extraction
uv run python -m tree_sitter_analyzer examples/BigService.java --partial-read --start-line 93 --end-line 106
```

---

### 3.3 👨‍💻 Developers (Source Code Development)

**For:** Developers who need to modify source code or contribute code

#### 🛠️ Development Environment Setup

```bash
# Clone repository
git clone https://github.com/aimasteracc/tree-sitter-analyzer.git
cd tree-sitter-analyzer

# Install dependencies
uv sync --extra all --extra mcp

# Run tests
uv run pytest tests/ -v

# Generate coverage report
uv run pytest tests/ --cov=tree_sitter_analyzer --cov-report=html
```

#### 🔍 Code Quality Checks

```bash
# AI-generated code checks
uv run python llm_code_checker.py --check-all

# Quality checks
uv run python check_quality.py --new-code-only
```

---

## 4. 📖 Usage Workflow & Examples

### 4.1 🔄 AI Assistant SMART Workflow

The SMART workflow is the recommended process for analyzing code using AI assistants. The following demonstrates the complete process using `examples/BigService.java` (a large service class with 1419 lines):

- **S** (Set): Set project root directory
- **M** (Map): Precisely map target files
- **A** (Analyze): Analyze core structure
- **R** (Retrieve): Retrieve key code
- **T** (Trace): Trace dependencies

---

#### **S - Set Project (First Step)**

**Tell the AI:**
```
Please set the project root directory to: C:\git-public\tree-sitter-analyzer
```

**AI will automatically call** the `set_project_path` tool.

> 💡 **Tip**: You can also pre-set this through the environment variable `TREE_SITTER_PROJECT_ROOT` in MCP configuration.

---

#### **M - Map Target Files (Find files to analyze)**

**Scenario 1: Don't know where the file is, search first**

```
Find all Java files containing "BigService" in the project
```

**AI will call** the `find_and_grep` tool and return showing 8 matches in BigService.java.

**Scenario 2: Known file path, use directly**
```
I want to analyze the file examples/BigService.java
```

---

#### **A - Analyze Core Structure (Understand file scale and organization)**

**Tell the AI:**
```
Please analyze the structure of examples/BigService.java, I want to know how big this file is and what main components it contains
```

**AI will call** the `analyze_code_structure` tool and return:
```json
{
  "file_path": "examples/BigService.java",
  "language": "java",
  "metrics": {
    "lines_total": 1419,
    "lines_code": 906,
    "lines_comment": 246,
    "lines_blank": 267,
    "elements": {
      "classes": 1,
      "methods": 66,
      "fields": 9,
      "imports": 8,
      "packages": 1,
      "total": 85
    },
    "complexity": {
      "total": 348,
      "average": 5.27,
      "max": 15
    }
  }
}
```

**Key Information:**

- File has **1419 lines** total
- Contains **1 class**, **66 methods**, **9 fields**, **1 package**, **total 85 elements**

---

#### **R - Retrieve Key Code (Deep understanding of specific implementations)**

**Scenario 1: View complete structure table**
```
Please generate a detailed structure table for examples/BigService.java, I want to see a list of all methods
```

**AI will generate a Markdown table containing:**

- Class information: package name, type, visibility, line range
- Field list: 9 fields (DEFAULT_ENCODING, MAX_RETRY_COUNT, etc.)
- Constructor: BigService()
- Public methods: 19 (authenticateUser, createSession, generateReport, etc.)
- Private methods: 47 (initializeService, checkMemoryUsage, etc.)

**Scenario 2: Extract specific code snippet**
```
Please extract lines 93-106 from examples/BigService.java, I want to see the specific implementation of memory checking
```

**AI will call** the `extract_code_section` tool and return the code for the checkMemoryUsage method.

---

#### **T - Trace Dependencies (Understand code relationships)**

**Scenario 1: Find all authentication-related methods**
```
Find all methods related to authentication (auth) in examples/BigService.java
```

**AI will call query filtering** and return the authenticateUser method code (lines 141-172).

**Scenario 2: Find entry points**
```
Where is the main method in this file? What does it do?
```

**AI will locate:**

- **Location**: Lines 1385-1418
- **Function**: Demonstrates various features of BigService (authentication, sessions, customer management, report generation, performance monitoring, security checks)

**Scenario 3: Understand method call relationships**
```
Which methods call the authenticateUser method?
```

**AI will search the code** and find the call in the `main` method:
```java
service.authenticateUser("testuser", "password123");
```

---

### 💡 SMART Workflow Best Practices

1. **Natural language first**: Describe your needs in natural language, and AI will automatically select appropriate tools
2. **Step-by-step approach**: First understand the overall structure (A), then dive into specific code (R)
3. **Use tracking when needed**: Only use tracking (T) when you need to understand complex relationships
4. **Combined usage**: You can combine multiple steps in one conversation

**Complete example conversation:**
```
I want to understand the large file examples/BigService.java:
1. How big is it? What main features does it contain?
2. How is the authentication feature implemented?
3. What public API methods are available?
```

AI will automatically:
1. Analyze file structure (1419 lines, 66 methods)
2. Locate and extract the `authenticateUser` method (lines 141-172)
3. Generate list of public methods (19 public methods)

---

## 5. 🤖 Complete MCP Tool List

Tree-sitter Analyzer provides a rich set of MCP tools designed for AI assistants:

| Tool Category | Tool Name | Main Function | Core Features |
|-------------|---------|---------|---------|
| **📊 Code Analysis** | `check_code_scale` | Fast code file scale analysis | File size statistics, line count statistics, complexity analysis, performance metrics |
| | `analyze_code_structure` | Code structure analysis and table generation | 🆕 suppress_output parameter, multiple formats (full/compact/csv/json), automatic language detection |
| | `extract_code_section` | Precise code section extraction | Specified line range extraction, large file efficient processing, original format preservation |
| **🔍 Intelligent Search** | `list_files` | High-performance file discovery | fd-based, glob patterns, file type filters, time range control |
| | `search_content` | Regex content search | ripgrep-based, multiple output formats, context control, encoding handling |
| | `find_and_grep` | Two-stage search | File discovery → content search, fd+ripgrep combination, intelligent cache optimization |
| **🔧 Advanced Queries** | `query_code` | tree-sitter queries | Predefined query keys, custom query strings, filter expression support |
| **⚙️ System Management** | `set_project_path` | Project root path setting | Security boundary control, automatic path validation |
| **📁 Resource Access** | Code file resources | URI code file access | File content access via URI identification |
| | Project statistics resources | Project statistics data access | Project analysis data and statistical information |

### 🆕 v1.7.3 New Feature: Complete Markdown Support

Brand new Markdown language support provides powerful capabilities for document analysis and AI assistants:

- **📝 Complete Markdown Parsing**: Support for all major elements including ATX headers, Setext headers, code blocks, links, images, tables
- **🔍 Intelligent Element Extraction**: Automatically recognize and extract header levels, code languages, link URLs, image information
- **📊 Structured Analysis**: Convert Markdown documents to structured data for easy AI understanding and processing
- **🎯 Task List Support**: Complete support for GitHub-style task lists (checkboxes)
- **🔧 Query System Integration**: Support for all existing query and filtering functionality
- **📁 Multiple Extension Support**: Support for .md, .markdown, .mdown, .mkd, .mkdn, .mdx formats

### 🆕 v1.7.2 Feature: File Output Optimization

MCP search tools' newly added file output optimization feature is a revolutionary token-saving solution:

- **🎯 File Output Optimization**: `find_and_grep`, `list_files`, and `search_content` tools now include `suppress_output` and `output_file` parameters
- **🔄 Automatic Format Detection**: Smart file format selection (JSON/Markdown) based on content type
- **💾 Massive Token Savings**: Response size reduced by up to 99% when saving large search results to files
- **📚 ROO Rules Documentation**: Added comprehensive tree-sitter-analyzer MCP optimization usage guide
- **🔧 Backward Compatibility**: Optional feature that doesn't affect existing functionality

### 🆕 v1.7.0 Feature: suppress_output Function

The `suppress_output` parameter in the `analyze_code_structure` tool:

- **Problem solved**: When analysis results are too large, traditional methods return complete table data, consuming massive tokens
- **Intelligent optimization**: When `suppress_output=true` and `output_file` specified, only basic metadata is returned
- **Significant effect**: Response size reduced by up to 99%, dramatically saving AI dialog token consumption
- **Use cases**: Particularly suitable for large code file structure analysis and batch processing scenarios

---

## 6. ⚡ Complete CLI Commands

#### 📊 Code Structure Analysis Commands

```bash
# Quick analysis (show summary information)
uv run python -m tree_sitter_analyzer examples/BigService.java --summary

# Detailed analysis (show complete structure)
uv run python -m tree_sitter_analyzer examples/BigService.java --structure

# Advanced analysis (including complexity metrics)
uv run python -m tree_sitter_analyzer examples/BigService.java --advanced

# Generate complete structure table
uv run python -m tree_sitter_analyzer examples/BigService.java --table=full

# Specify output format
uv run python -m tree_sitter_analyzer examples/BigService.java --advanced --output-format=json
uv run python -m tree_sitter_analyzer examples/BigService.java --advanced --output-format=text

# Precise code extraction
uv run python -m tree_sitter_analyzer examples/BigService.java --partial-read --start-line 93 --end-line 106

# Specify programming language
uv run python -m tree_sitter_analyzer script.py --language python --table=full
```

#### 🔍 Query and Filter Commands

```bash
# Query specific elements
uv run python -m tree_sitter_analyzer examples/BigService.java --query-key methods
uv run python -m tree_sitter_analyzer examples/BigService.java --query-key classes

# Filter query results
# Find specific methods
uv run python -m tree_sitter_analyzer examples/BigService.java --query-key methods --filter "name=main"

# Find authentication-related methods (pattern matching)
uv run python -m tree_sitter_analyzer examples/BigService.java --query-key methods --filter "name=~auth*"

# Find public methods with no parameters (compound conditions)
uv run python -m tree_sitter_analyzer examples/BigService.java --query-key methods --filter "params=0,public=true"

# Find static methods
uv run python -m tree_sitter_analyzer examples/BigService.java --query-key methods --filter "static=true"

# View filter syntax help
uv run python -m tree_sitter_analyzer --filter-help
```

#### 📁 File System Operation Commands

```bash
# List files
uv run list-files . --extensions java
uv run list-files . --pattern "test_*" --extensions java --types f
uv run list-files . --types f --size "+1k" --changed-within "1week"

# Search content
uv run search-content --roots . --query "class.*extends" --include-globs "*.java"
uv run search-content --roots tests --query "TODO|FIXME" --context-before 2 --context-after 2
uv run search-content --files examples/BigService.java examples/Sample.java --query "public.*method" --case insensitive

# Two-stage search (first find files, then search content)
uv run find-and-grep --roots . --query "@SpringBootApplication" --extensions java
uv run find-and-grep --roots examples --query "import.*SQLException" --extensions java --file-limit 10 --max-count 5
uv run find-and-grep --roots . --query "public.*static.*void" --extensions java --types f --size "+1k" --output-format json
```

#### ℹ️ Information Query Commands

```bash
# Show help
uv run python -m tree_sitter_analyzer --help

# List supported query keys
uv run python -m tree_sitter_analyzer --list-queries

# Show supported languages
uv run python -m tree_sitter_analyzer --show-supported-languages

# Show supported extensions
uv run python -m tree_sitter_analyzer --show-supported-extensions

# Show common queries
uv run python -m tree_sitter_analyzer --show-common-queries

# Show query language support
uv run python -m tree_sitter_analyzer --show-query-languages
```

---

## 7. 🛠️ Core Features

| Feature Category | Feature Name | Core Capabilities | Technical Advantages |
|------------------|--------------|-------------------|---------------------|
| **📊 Code Structure Analysis** | Intelligent Parsing Engine | Class, method, and field statistics<br>Package information and import dependencies<br>Complexity metrics (cyclomatic complexity)<br>Precise line number positioning | Tree-sitter based high-precision parsing<br>Large enterprise codebase support<br>Real-time performance optimization |
| **✂️ Intelligent Code Extraction** | Precision Extraction Tool | Precise extraction by line range<br>Preserves original formatting and indentation<br>Includes position metadata<br>Efficient processing of large files | Zero-loss format preservation<br>Memory-optimized algorithms<br>Streaming processing support |
| **🔍 Advanced Query Filtering** | Multi-dimensional Filters | **Exact match**: `--filter "name=main"`<br>**Pattern match**: `--filter "name=~auth*"`<br>**Parameter filter**: `--filter "params=2"`<br>**Modifier filter**: `--filter "static=true,public=true"`<br>**Compound conditions**: Combine multiple conditions for precise queries | Flexible query syntax<br>High-performance indexing<br>Intelligent caching mechanisms |
| **🔗 AI Assistant Integration** | MCP Protocol Support | **Claude Desktop** - Full MCP support<br>**Cursor IDE** - Built-in MCP integration<br>**Roo Code** - MCP protocol support<br>**Other MCP-compatible tools** - Universal MCP server | Standard MCP protocol<br>Plug-and-play design<br>Cross-platform compatibility |
| **🌍 Multi-language Support** | Enterprise Language Engine | **Java** - Complete support, including Spring, JPA frameworks<br>**Python** - Complete support, including type annotations, decorators<br>**JavaScript** - Enterprise-grade support, including ES6+, React/Vue/Angular, JSX<br>**TypeScript** - **Complete support**, including interfaces, types, decorators, TSX/JSX, framework detection<br>**Markdown** - **🆕 Complete support**, including headers, code blocks, links, images, tables, task lists, blockquotes<br>**C/C++, Rust, Go** - Basic support | Framework-aware parsing<br>Syntax extension support<br>Continuous language updates |
| **📁 Advanced File Search** | fd+ripgrep Integration | **ListFilesTool** - Intelligent file discovery with multiple filtering conditions<br>**SearchContentTool** - Intelligent content search using regular expressions<br>**FindAndGrepTool** - Combined discovery and search, two-stage workflow | Rust-based high-performance tools<br>Parallel processing capabilities<br>Intelligent cache optimization |
| **🏗️ Unified Element System** | Revolutionary Architecture Design | **Single element list** - Unified management of all code elements (classes, methods, fields, imports, packages)<br>**Consistent element types** - Each element has an `element_type` attribute<br>**Simplified API** - Clearer interfaces and reduced complexity<br>**Better maintainability** - Single source of truth for all code elements | Unified data model<br>Type safety guarantees<br>Extensible design |

---

## 8. 🏆 Quality Assurance

### 📊 Quality Metrics
- **2,831 tests** - 100% pass rate ✅
- **79.19% code coverage** - Comprehensive test suite
- **Zero test failures** - Production ready
- **Cross-platform support** - Windows, macOS, Linux

### ⚡ Latest Quality Achievements (v1.7.3)
- ✅ **🆕 Complete Markdown Support** - Added new complete Markdown language plugin supporting all major Markdown elements
- ✅ **📝 Enhanced Document Analysis** - Support for intelligent extraction of headers, code blocks, links, images, tables, task lists
- ✅ **🔍 Markdown Query System** - 17 predefined query types with alias and custom query support
- ✅ **🧪 Comprehensive Test Validation** - Added extensive Markdown test cases ensuring feature stability
- ✅ **📊 Structured Output** - Convert Markdown documents to structured data for easy AI processing
- ✅ **🔧 Test Stability Improvement** - Fixed 28 test errors, all 2831 tests now passing 100%
- ✅ **File output optimization** - MCP search tools now include `suppress_output` and `output_file` parameters for massive token savings
- ✅ **Intelligent format detection** - Automatic selection of optimal file formats (JSON/Markdown) for storage and reading optimization
- ✅ **ROO rules documentation** - Added comprehensive tree-sitter-analyzer MCP optimization usage guide
- ✅ **Enhanced token management** - Response size reduced by up to 99% when outputting search results to files
- ✅ **Enterprise-grade test coverage** - Comprehensive test suite including complete validation of file output optimization features
- ✅ **Complete MCP tools** - Complete MCP server tool set supporting advanced file search and content analysis
- ✅ **Cross-platform path compatibility** - Fixed differences between Windows short path names and macOS symbolic links
- ✅ **GitFlow implementation** - Professional development/release branch strategy

### ⚙️ Running Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Generate coverage report
uv run pytest tests/ --cov=tree_sitter_analyzer --cov-report=html --cov-report=term-missing

# Run specific tests
uv run pytest tests/test_mcp_server_initialization.py -v
```

### 📈 Test Coverage Details

| Module Category | Module Name | Coverage | Quality Level | Main Features |
|------------------|-------------|-----------|---------------|---------------|
| **🔧 Core Modules** | Language Detector | 98.41% | Excellent | Automatic programming language recognition |
| | CLI Main Entry | 94.36% | Excellent | Command line interface |
| | Query Filter System | 96.06% | Excellent | Code querying and filtering |
| | Query Service | 86.25% | Good | Query execution engine |
| | MCP Error Handling | 82.76% | Good | AI assistant integration error handling |
| **🌍 Language Plugins** | Java Plugin | 80.30% | Excellent | Complete enterprise-grade support |
| | JavaScript Plugin | 76.74% | Good | Modern ES6+ feature support |
| | Python Plugin | 82.84% | Excellent | Complete type annotation support |
| **🤖 MCP Tools** | File Search Tool | 88.77% | Excellent | fd/ripgrep integration |
| | Content Search Tool | 92.70% | Excellent | Regular expression search |
| | Combined Search Tool | 91.57% | Excellent | Two-stage search |

### ✅ Documentation Verification Status

**All content in this README has been verified:**
- ✅ **All commands tested** - All CLI commands have been executed and verified in real environments
- ✅ **All data is real** - Data such as coverage rates and test counts are directly obtained from test reports
- ✅ **SMART flow is real** - Demonstrated based on actual BigService.java (1419 lines)
- ✅ **Cross-platform verified** - Tested on Windows, macOS, Linux environments

**Verification environment:**
- Operating systems: Windows 10, macOS, Linux
- Python version: 3.10+
- Project version: tree-sitter-analyzer v1.7.2
- Test files: BigService.java (1419 lines), sample.py (256 lines), MultiClass.java (54 lines)

---

## 9. 📚 Documentation & Support

### 📖 Complete Documentation
- **[User MCP Setup Guide](MCP_SETUP_USERS.md)** - Simple setup guide
- **[Developer MCP Setup Guide](MCP_SETUP_DEVELOPERS.md)** - Local development setup
- **[Project Root Configuration](PROJECT_ROOT_CONFIG.md)** - Complete configuration reference
- **[API Documentation](docs/api.md)** - Detailed API reference
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute code
- **[Onboarding & Training Guide](training/README.md)** - System onboarding materials for new members/maintainers

### 🤖 AI Collaboration Support
This project supports AI-assisted development with professional quality control:

```bash
# AI system pre-generation checks
uv run python check_quality.py --new-code-only
uv run python llm_code_checker.py --check-all
```

📖 **Detailed guides**:
- [AI Collaboration Guide](AI_COLLABORATION_GUIDE.md)
- [LLM Coding Guidelines](LLM_CODING_GUIDELINES.md)

### 💝 Sponsors & Acknowledgments

**[@o93](https://github.com/o93)** - *Lead Sponsor & Supporter*
- 🚀 **MCP Tool Enhancement**: Sponsored comprehensive MCP fd/ripgrep tool development
- 🧪 **Test Infrastructure**: Implemented enterprise-grade test coverage (50+ comprehensive test cases)
- 🔧 **Quality Assurance**: Supported bug fixes and performance improvements
- 💡 **Innovation Support**: Enabled early release of advanced file search and content analysis features

**[💖 Sponsor this project](https://github.com/sponsors/aimasteracc)** to help us continue building excellent tools for the developer community!

---

## 10. 🤝 Contributing & License

### 🤝 Contributing Guide

We welcome all kinds of contributions! Please check our [Contributing Guide](CONTRIBUTING.md) for details.

### ⭐ Give us a star!

If this project has been helpful to you, please give us a ⭐ on GitHub - that's the biggest support for us!

### 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

---

**🎯 Built for developers working with large codebases and AI assistants**

*Making every line of code understandable to AI, enabling every project to break through token limitations*