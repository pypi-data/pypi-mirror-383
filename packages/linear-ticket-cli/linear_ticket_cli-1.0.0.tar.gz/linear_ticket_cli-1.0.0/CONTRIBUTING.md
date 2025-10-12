# Contributing to Linear Ticket Manager CLI

🎉 Thank you for your interest in contributing to the Linear Ticket Manager CLI! This project is designed to be AI-agent friendly while providing powerful command-line functionality for human users.

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Linear workspace access
- Linear API token with appropriate permissions

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/vittoridavide/linear-cli.git
   cd linear-cli
   ```

2. **Set Up Development Environment**
   ```bash
   # Quick setup using the provided script (recommended)
   ./dev-setup.sh
   
   # Or manual setup:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Linear API token
   export LINEAR_API_TOKEN="your_linear_api_token"
   ```

4. **Test Installation**
   ```bash
   python linear_search.py --teams
   # Should display your Linear teams without errors
   ```

## 🎯 Development Principles

This tool follows specific design principles to ensure consistency and usability:

### AI-Agent Friendly Design
- **Detailed help text**: Every command includes comprehensive examples and validation notes
- **Consistent output formats**: Maintain predictable JSON-friendly responses
- **Clear error messages**: Provide actionable error messages with suggestions
- **Exit code standards**: Use standard exit codes (0=success, 1=error, 2=invalid args)

### Human-Friendly Interface
- **Intuitive commands**: Natural language-style commands where possible
- **Comprehensive documentation**: Rich help text and examples
- **Progress feedback**: Show progress for long-running operations
- **Graceful error handling**: User-friendly error messages

## 📋 Types of Contributions

### 🐛 Bug Reports
When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS)
- Linear workspace configuration (team/project structure)

### 🌟 Feature Requests
For new features, please provide:
- Use case description
- Proposed implementation approach
- AI-agent integration considerations
- Impact on existing functionality

### 💻 Code Contributions
We welcome code contributions! Please follow these guidelines:

#### Code Standards
- **Python Style**: Follow PEP 8 conventions
- **Type Hints**: Use type hints for function parameters and return values
- **Docstrings**: Document all functions with comprehensive docstrings
- **Error Handling**: Implement robust error handling with informative messages

#### AI-Agent Considerations
When adding new functionality:
- Include detailed `--help` text with examples
- Ensure consistent output formatting
- Add appropriate error messages and exit codes
- Update documentation with AI-agent examples

## 🔧 Development Workflow

### 1. Branch Creation
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Development Guidelines

#### Testing Your Changes
```bash
# Test basic functionality
python linear_search.py --teams
python linear_search.py add --title "Test ticket" --team "YourTeam"

# Test error handling
python linear_search.py add --title "Test" --team "NonexistentTeam"

# Test AI-agent workflows
python linear_search.py --help
```

#### Code Structure
- **`linear_search.py`**: Main CLI application and argument parsing
- **`linear_client.py`**: Linear API client and data models
- **`ticket_search.py`**: Search engine and ticket operations
- **`examples/`**: AI-agent workflow documentation

### 3. Documentation Updates
When adding features:
- Update `README.md` with new command examples
- Add AI-agent workflow examples to `examples/ai_agent_workflows.md`
- Update `examples/quick_reference.md` for new commands
- Include help text examples in code

### 4. Pull Request Process

#### Before Submitting
- [ ] Test all functionality manually
- [ ] Verify AI-agent friendly features work correctly
- [ ] Update documentation
- [ ] Check that examples in README work
- [ ] Ensure error messages are helpful

#### PR Description Should Include
- Clear description of changes
- Screenshots/examples of new functionality
- AI-agent usage examples
- Breaking changes (if any)
- Testing performed

## 🧪 Testing Guidelines

### Manual Testing Checklist
- [ ] All existing commands still work
- [ ] New commands work as expected
- [ ] Error conditions handled gracefully
- [ ] Help text is comprehensive and accurate
- [ ] AI-agent workflows function correctly
- [ ] Exit codes are appropriate

### Test Scenarios
1. **Resource Discovery**: Test `--teams`, `--projects`, `--assignees` commands
2. **Ticket Creation**: Test various ticket creation scenarios
3. **Ticket Updates**: Test status, priority, assignee updates
4. **Search Functionality**: Test different search query types
5. **Error Handling**: Test invalid inputs, API errors, network issues

## 📚 Architecture Overview

### Key Components
```
linear-cli/
├── linear_search.py       # Main CLI application
├── linear_client.py       # Linear API client
├── ticket_search.py       # Search and ticket operations
├── requirements.txt       # Python dependencies
├── setup_alias.sh         # Installation helper
└── examples/             # AI-agent documentation
```

### Data Flow
1. **CLI Parser** (`linear_search.py`): Parses arguments and validates input
2. **API Client** (`linear_client.py`): Handles Linear GraphQL API communication
3. **Search Engine** (`ticket_search.py`): Processes queries and manages ticket operations
4. **Output Formatter**: Formats results for human and AI consumption

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Provide constructive feedback
- Help newcomers get started
- Focus on technical merit of contributions

### Communication
- Use clear, descriptive commit messages
- Respond to feedback constructively
- Ask questions if requirements are unclear
- Share knowledge and help others

## 🎯 Specific Contribution Areas

### High-Priority Improvements
- Performance optimizations for large workspaces
- Enhanced search capabilities
- Additional Linear API feature coverage
- Improved error handling and user feedback

### AI-Agent Enhancements
- More comprehensive help text
- Additional output format options
- Enhanced validation and error messages
- Workflow documentation improvements

### Documentation Needs
- Video tutorials for setup
- More AI-agent integration examples
- Advanced usage patterns
- Troubleshooting guides

## 📞 Getting Help

If you need help with development:
- Check existing issues for similar questions
- Create a new issue with the "question" label
- Review the extensive help text in the CLI
- Study the AI-agent workflow examples

## 🏆 Recognition

Contributors will be recognized in:
- Project README
- Release notes for significant contributions
- Special thanks for first-time contributors

---

Thank you for contributing to Linear Ticket Manager CLI! Your contributions help make this tool better for both AI agents and human users. 🚀