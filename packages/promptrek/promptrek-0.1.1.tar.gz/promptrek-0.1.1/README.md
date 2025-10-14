# PrompTrek

[![CI](https://github.com/flamingquaks/promptrek/actions/workflows/ci.yml/badge.svg)](https://github.com/flamingquaks/promptrek/actions/workflows/ci.yml)
[![PR Validation](https://github.com/flamingquaks/promptrek/actions/workflows/pr.yml/badge.svg)](https://github.com/flamingquaks/promptrek/actions/workflows/pr.yml)
[![Python Versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://github.com/flamingquaks/promptrek)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Taking your coding prompts on a journey to every AI editor!*

A universal AI Editor prompt storage solution that dynamically maps prompt data to a wide-range of agentic/AI editors and tools. This tool allows you to create generic prompts and workflows in a standardized format, then generate editor-specific prompts for your preferred AI coding assistant.

## 🎯 Problem It Solves

AI coding assistants like GitHub Copilot, Cursor, Continue, and others all use different prompt formats and configuration methods. When working across teams or switching between editors, you have to maintain separate prompt configurations for each tool. PrompTrek solves this by:

- **Universal Format**: Create prompts once in a standardized format (now with **v2.0.0 schema** - simpler and more aligned with how editors work!)
- **Multi-Editor Support**: Generate prompts for any supported AI editor automatically (no `targets` field needed in v2!)
- **Bidirectional Sync**: Parse editor files back to `.promptrek.yaml` without data loss (v2 lossless sync)
- **Team Consistency**: Share prompt configurations across team members regardless of their editor choice
- **Easy Migration**: Switch between AI editors without losing your prompt configurations

## 🚀 Quick Example

1. Create a universal prompt file (`.promptrek.yaml`) using the **new v2 format** (recommended):
```yaml
schema_version: "2.0.0"
metadata:
  title: "My Project Assistant"
  description: "AI assistant for React TypeScript project"
  tags: [react, typescript, web]
content: |
  # My Project Assistant

  ## Project Details
  **Technologies:** React, TypeScript, Node.js

  ## Development Guidelines

  ### General Principles
  - Use TypeScript for all new files
  - Follow React functional component patterns
  - Write comprehensive tests

  ### Code Style
  - Use functional components with hooks
  - Prefer const over let
  - Use meaningful variable names
variables:
  PROJECT_NAME: "my-react-app"
```

<details>
<summary>📚 Click to see v1 format (legacy)</summary>

```yaml
schema_version: "1.0.0"
metadata:
  title: "My Project Assistant"
  description: "AI assistant for React TypeScript project"
targets: [copilot, cursor, continue]
instructions:
  general:
    - "Use TypeScript for all new files"
    - "Follow React functional component patterns"
    - "Write comprehensive tests"
```

</details>

2. Generate editor-specific prompts:
```bash
# Generate for GitHub Copilot
promptrek generate --editor copilot

# Generate for Cursor
promptrek generate --editor cursor

# Generate for all configured editors
promptrek generate --all
```

3. Use the generated prompts in your preferred editor!

## 📖 Documentation

**📚 Complete documentation is available on our [GitHub Pages site](https://flamingquaks.github.io/promptrek):**

- **[Quick Start Guide](https://flamingquaks.github.io/promptrek/quick-start.html)** - Get up and running in minutes
- **[User Guide](https://flamingquaks.github.io/promptrek/user-guide.html)** - Comprehensive documentation covering:
  - UPF Specification - Universal Prompt Format details
  - Advanced Features - Variables, conditionals, and imports
  - Editor Adapters - All supported AI editors
  - Adapter Capabilities - Feature comparison matrix
  - Sync Feature - Bidirectional synchronization
  - Pre-commit Integration - Automated workflows
- **[Contributing Guide](https://flamingquaks.github.io/promptrek/contributing.html)** - How to contribute to the project

### Developer Resources
For technical architecture and development planning, see the developer documentation on our website:
- [System Architecture](https://flamingquaks.github.io/promptrek/developer/architecture.html) - Technical design and structure
- [Implementation Roadmap](https://flamingquaks.github.io/promptrek/developer/roadmap.html) - Development status and future plans
- [Project Structure](https://flamingquaks.github.io/promptrek/developer/project-structure.html) - Repository organization
- [Changelog Process](https://flamingquaks.github.io/promptrek/developer/changelog-process.html) - Contribution guidelines
- [Pre-commit Implementation](https://flamingquaks.github.io/promptrek/developer/pre-commit-implementation.html) - Technical implementation details
- [UV Workflows](https://flamingquaks.github.io/promptrek/developer/uv-workflows.html) - Developer workflows

## 🎨 Supported Editors

### ✅ All Implemented
- **GitHub Copilot** - `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/prompts/*.prompt.md` - Repository-wide and path-specific instructions with bidirectional sync
- **Cursor** - `.cursor/rules/index.mdc`, `.cursor/rules/*.mdc`, `AGENTS.md`, `.cursorignore`, `.cursorindexingignore` - Modern 2025 rules system with Always/Auto Attached rule types and project overview
- **Continue** - `.continue/rules/*.md` - Organized markdown rules directory with bidirectional sync support
- **Kiro** - `.kiro/steering/*.md` - Comprehensive steering system with YAML frontmatter
- **Cline** - `.clinerules/*.md` - Markdown-based rules configuration
- **Claude Code** - `.claude/context.md` - Rich context format with detailed project information
- **Windsurf** - `.windsurf/rules/*.md` - Organized markdown rule files for AI-powered coding assistance
- **Tabnine** - `.tabnine_commands` - Basic context guidance (limited support - full config via IDE)
- **Amazon Q** - `.amazonq/rules/*.md`, `.amazonq/cli-agents/*.json` - Rules directory and CLI agents with sync support
- **JetBrains AI** - `.assistant/rules/*.md` - Markdown rules for IDE-integrated AI assistance

## 🗂️ Example Configurations

See the [`examples/`](https://github.com/flamingquaks/promptrek/tree/main/examples/) directory for sample configurations:

### Basic Examples
- [React TypeScript Project](https://github.com/flamingquaks/promptrek/tree/main/examples/basic/react-typescript.promptrek.yaml)
- [Node.js API Service](https://github.com/flamingquaks/promptrek/tree/main/examples/basic/node-api.promptrek.yaml)

### Advanced Examples
- [NX Monorepo](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/monorepo-nx.promptrek.yaml) - Multi-package workspace with NX
- [Microservices + Kubernetes](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/microservices-k8s.promptrek.yaml) - Cloud-native architecture
- [React Native Mobile](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/mobile-react-native.promptrek.yaml) - Cross-platform mobile apps
- [FastAPI Backend](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/python-fastapi.promptrek.yaml) - Modern Python async API
- [Next.js Full-Stack](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/fullstack-nextjs.promptrek.yaml) - App Router with SSR
- [Rust CLI Tool](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/rust-cli.promptrek.yaml) - Systems programming
- [Go Backend Service](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/golang-backend.promptrek.yaml) - High-performance APIs
- [Data Science ML](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/data-science-python.promptrek.yaml) - MLOps and experiments

## 🚀 Installation & Quick Start

### Installation

#### Option 1: Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install from source
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
uv sync
```

#### Option 2: Traditional pip

```bash
# Clone and install from source
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
pip install -e .
```

**Note:** PrompTrek is not yet available on PyPI. Install from source using the methods above.

### Quick Start

```bash
# 1. Initialize a new project with pre-commit hooks (v2 format by default)
uv run promptrek init --template react --output my-project.promptrek.yaml --setup-hooks
# or with traditional pip: promptrek init --template react --output my-project.promptrek.yaml --setup-hooks

# 2. Validate your configuration
uv run promptrek validate my-project.promptrek.yaml

# 3. Generate editor-specific prompts
uv run promptrek generate my-project.promptrek.yaml --all

# 4. Your AI editor prompts are ready!
ls .github/copilot-instructions.md
ls .cursor/rules/index.mdc
ls .continue/rules/
```

**Note:** The `--setup-hooks` flag automatically configures pre-commit hooks to validate your `.promptrek.yaml` files and prevent accidental commits of generated files.

### 🆕 Schema v2.0.0 (Recommended)

PrompTrek now supports **v2.0.0 schema** which is simpler and more aligned with how AI editors actually work:

**Key Benefits:**
- ✅ **No `targets` field** - Works with ALL editors automatically
- ✅ **Lossless bidirectional sync** - Parse editor files back without data loss
- ✅ **Simpler format** - Just markdown content, no complex nested structures
- ✅ **Editor-friendly** - Matches how Claude Code, Copilot, and others use markdown
- ✅ **Multi-file support** - Use `documents` field for multi-file editors (Continue, Windsurf, Kiro)

**Quick Migration:**
```bash
# Migrate existing v1 file to v2
uv run promptrek migrate old.promptrek.yaml -o new.promptrek.yaml

# Or create a new v2 file from scratch
uv run promptrek init  # v2 is now the default!

# Create a v1 file (legacy)
uv run promptrek init --v1
```

**V2 Format Example:**
```yaml
schema_version: "2.0.0"
metadata:
  title: "My Project"
  description: "AI assistant"
  version: "1.0.0"
  author: "Your Name"
  tags: [ai, project]

content: |
  # My Project

  ## Guidelines
  - Write clean code
  - Follow best practices

variables:
  PROJECT_NAME: "my-project"

# Optional: For multi-file editors
documents:
  - name: "general-rules"
    content: |
      # General Rules
      - Rule 1
      - Rule 2
```

### Available Commands

- `promptrek init` - Create a new universal prompt file with templates (use `--setup-hooks` to automatically configure pre-commit)
- `promptrek validate` - Check your configuration for errors
- `promptrek generate` - Create editor-specific prompts
- `promptrek preview` - Preview generated output without creating files
- `promptrek sync` - Sync editor files back to PrompTrek format
- `promptrek agents` - Generate agent-specific instructions
- `promptrek install-hooks` - Set up pre-commit hooks (use `--activate` to activate automatically)
- `promptrek list-editors` - Show supported editors and their status

For detailed usage instructions, see [`GETTING_STARTED.md`](./GETTING_STARTED.md).

## 🔧 Development Setup

### Pre-commit Hooks

PrompTrek includes pre-commit hooks to ensure code quality and prevent accidental commits of generated files:

```bash
# Install development dependencies
uv sync --group dev
# or with pip: pip install -e .[dev]

# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually (optional)
uv run pre-commit run --all-files
```

The pre-commit hooks will:
- Validate `.promptrek.yaml` files using `promptrek validate`
- Prevent committing generated prompt files (they should be generated locally)
- Run code formatting (black, isort) and linting (flake8, yamllint)
- Check for common issues (trailing whitespace, merge conflicts, etc.)

### Generated Files

PrompTrek generates editor-specific files that should **not** be committed to version control:

- `.github/copilot-instructions.md`, `.github/instructions/`, `.github/prompts/` - GitHub Copilot
- `.cursor/`, `AGENTS.md`, `.cursorignore`, `.cursorindexingignore` - Cursor
- `.continue/` - Continue
- `.claude/` - Claude Code
- `.windsurf/` - Windsurf
- `.clinerules/` - Cline
- `.kiro/` - Kiro
- `.amazonq/` - Amazon Q
- `.assistant/` - JetBrains AI
- `.tabnine_commands` - Tabnine

These files are automatically ignored via `.gitignore` and the pre-commit hooks will prevent accidental commits.

## 🤝 Contributing

This project is actively developing! We welcome:
- Bug reports and feature requests
- Pull requests for additional editor support
- Documentation improvements
- Testing and feedback on the UPF format
- Ideas for advanced features

### Conventional Commits & Changelog

PrompTrek uses [Conventional Commits](https://www.conventionalcommits.org/) for automated changelog generation:

```bash
# Commit format
type(scope): description

# Examples
feat(adapters): add support for new editor
fix(parser): handle edge case in YAML parsing
docs(readme): update installation instructions
```

All commit messages are validated in CI. See [Changelog Process](https://flamingquaks.github.io/promptrek/developer/changelog-process.html) for detailed guidelines.

See the [Implementation Roadmap](https://flamingquaks.github.io/promptrek/developer/roadmap.html) for planned features and current progress.

## 🧪 Testing and Quality Assurance

PrompTrek maintains high quality standards with comprehensive testing:

### Automated Testing
- **Continuous Integration**: Tests run on every push and PR across multiple Python versions (3.9-3.12)
- **Cross-Platform Testing**: Validates functionality on Linux, macOS, and Windows
- **Security Scanning**: Automated security vulnerability detection
- **Code Quality**: Enforced formatting (black), import sorting (isort), and linting (flake8)
- **Coverage**: Maintains >80% test coverage with detailed reporting

### Test Categories
- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test complete workflows and CLI functionality
- **Performance Tests**: Monitor memory usage and execution speed
- **Compatibility Tests**: Ensure compatibility across Python versions and platforms

### Running Tests Locally

#### Using uv (Recommended)

```bash
# Install development dependencies
uv sync --group dev

# Run all tests
make test-fast  # Fast tests without coverage
make test       # All tests with coverage

# Run specific test categories
uv run python -m pytest tests/unit/        # Unit tests only
uv run python -m pytest tests/integration/ # Integration tests only

# Code quality checks
make format     # Format code
make lint       # Run linters
make typecheck  # Type checking
```

#### Using pip (Traditional)

```bash
# Install development dependencies
uv sync --group dev
# or with pip: pip install -e ".[dev]"

# Run all tests
uv run pytest

# Run with coverage
pytest --cov=src/promptrek --cov-report=html

# Run specific test categories
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests only

# Code quality checks
black src/ tests/         # Format code
isort src/ tests/         # Sort imports
flake8 src/ tests/        # Lint code
mypy src/                # Type checking
```

For detailed uv workflows, see [UV Workflows Guide](https://flamingquaks.github.io/promptrek/developer/uv-workflows.html).

For contribution guidelines, see [CONTRIBUTING.md](./.github/CONTRIBUTING.md).

## 📚 Documentation

### Core Documentation
- **[Getting Started Guide](./GETTING_STARTED.md)** - Comprehensive setup and usage guide
- **[Advanced Template Features](https://flamingquaks.github.io/promptrek/user-guide/advanced-features.html)** - Variables, conditionals, and imports
- **[Editor Adapters](https://flamingquaks.github.io/promptrek/user-guide/adapters.html)** - Detailed guide to all supported AI editors
- **[Implementation Roadmap](https://flamingquaks.github.io/promptrek/developer/roadmap.html)** - Development progress and plans

### Key Features

#### 🔄 Variable Substitution
Use template variables to create reusable, customizable prompts:

```yaml
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  author: "{{{ AUTHOR_EMAIL }}}"

variables:
  PROJECT_NAME: "MyProject"
  AUTHOR_EMAIL: "team@example.com"
```

Override variables from CLI:
```bash
promptrek generate --editor claude project.promptrek.yaml \
  -V PROJECT_NAME="CustomProject" \
  -V AUTHOR_EMAIL="custom@example.com"
```

#### 🎯 Conditional Instructions
Provide editor-specific instructions:

```yaml
conditions:
  - if: "EDITOR == \"claude\""
    then:
      instructions:
        general:
          - "Claude: Provide detailed explanations"
  - if: "EDITOR == \"continue\""
    then:
      instructions:
        general:
          - "Continue: Generate comprehensive completions"
```

#### 📦 Import System
Share common configurations across projects:

```yaml
imports:
  - path: "shared/base-config.promptrek.yaml"
    prefix: "shared"

# Imported instructions get prefixed: [shared] Follow coding standards
# Imported examples get prefixed: shared_example_name
# Imported variables get prefixed: shared_VARIABLE_NAME
```

#### 🎨 Multiple Editor Support
Generate optimized configurations for all major AI coding assistants:

- **GitHub Copilot** → `.github/copilot-instructions.md` + path-specific instructions + bidirectional sync
- **Cursor** → `.cursor/rules/index.mdc` + `.cursor/rules/*.mdc` + `AGENTS.md` with modern rule types
- **Continue** → `.continue/rules/*.md` with organized rules + bidirectional sync
- **Kiro** → `.kiro/steering/*.md` with YAML frontmatter
- **Cline** → `.clinerules/*.md` with project-specific rules
- **Claude Code** → `.claude/context.md` with rich context
- **Windsurf** → `.windsurf/rules/*.md` with organized guidelines
- **Amazon Q** → `.amazonq/rules/*.md` + CLI agents + sync support
- **JetBrains AI** → `.assistant/rules/*.md` for IDE integration
- **Tabnine** → `.tabnine_commands` (limited support)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🌐 Website

Visit our comprehensive [GitHub Pages site](https://flamingquaks.github.io/promptrek) for:
- Detailed documentation and user guides
- Quick start tutorials
- Contributing guidelines
- Community feedback and support
