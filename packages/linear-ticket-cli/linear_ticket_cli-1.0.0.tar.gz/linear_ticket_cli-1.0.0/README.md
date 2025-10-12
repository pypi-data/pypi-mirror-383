# Linear Ticket Manager CLI

🎫 **A comprehensive command-line tool for managing Linear tickets with AI-agent friendly interfaces**

This tool provides complete Linear ticket management capabilities through an intuitive CLI, designed to work seamlessly with AI agents, automation scripts, and human users.

## 🚀 Quick Start for AI Agents

```bash
# 1. Set your Linear API token (REQUIRED)
export LINEAR_API_TOKEN="your_token_here"

# 2. Basic usage - create a ticket
linear add --title "Fix authentication bug" --team "Backend"
# Output: ✅ Successfully created ticket: ZIF-123

# 3. Search for tickets  
linear "ZIF-123"
# Output: Full ticket details

# 4. List available resources
linear --teams      # See all teams
linear --projects   # See all projects
linear --assignees  # See all users
```

## 📋 Table of Contents

- [Installation](#installation)
- [Authentication](#authentication)
- [Core Features](#core-features)
- [AI Agent Usage Guide](#ai-agent-usage-guide)
- [Command Reference](#command-reference)
- [Examples](#examples)
- [Automation & Scripting](#automation--scripting)
- [Troubleshooting](#troubleshooting)

## 🛠 Installation

### Prerequisites
- Python 3.7 or higher
- Linear workspace access
- Linear API token

### 🚀 Quick Installation (Recommended)

**Install via pip (coming soon to PyPI):**
```bash
pip install linear-cli
```

**Install directly from GitHub:**
```bash
pip install git+https://github.com/vittoridavide/linear-cli.git
```

After installation, you can use the `linear` command directly:
```bash
linear --help
```

### 🔧 Development Installation

**Option 1: Quick Setup (Recommended)**
```bash
git clone https://github.com/vittoridavide/linear-cli.git
cd linear-cli
./dev-setup.sh
```

**Option 2: Manual Setup**
```bash
git clone https://github.com/vittoridavide/linear-cli.git
cd linear-cli
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

**Option 3: Legacy Method (Clone and Run)**
```bash
git clone https://github.com/vittoridavide/linear-cli.git
cd linear-cli
pip install -r requirements.txt
# Use: python linear_search.py instead of linear
```

### 🔑 Authentication Setup

1. **Get Linear API Token**
   - Go to Linear → Settings → API → Personal API tokens
   - Create new token with read/write permissions
   - Copy the token

2. **Configure Authentication**
   ```bash
   export LINEAR_API_TOKEN="your_linear_api_token_here"
   # Add to ~/.zshrc or ~/.bashrc for persistence
   ```

## 🔐 Authentication

**Environment Variable (Recommended):**
```bash
export LINEAR_API_TOKEN="lin_api_..."
```

**Command Line Override:**
```bash
linear --token "lin_api_..." add --title "Test ticket"
```

## ✨ Core Features

- 🔍 **Smart Ticket Search** - Natural language queries, direct ID lookup
- 🎯 **Ticket Creation** - Full metadata support (teams, projects, assignees, labels)
- ✏️ **Ticket Updates** - Status, title, description, priority, assignee changes
- 📊 **Resource Discovery** - List teams, projects, users, labels, workflow states
- 🤖 **AI-Agent Friendly** - Detailed help text, consistent output formats
- 📝 **Script Integration** - JSON output modes, exit codes, ID-only responses
- ⚡ **Performance** - Local caching for fast searches
- 🔄 **Real-time Sync** - Automatic cache refresh after modifications

## 🤖 AI Agent Usage Guide

### Step-by-Step Workflow for AI Agents

#### 1. Resource Discovery (ALWAYS DO THIS FIRST)
```bash
# Get available teams (required for ticket creation)
linear --teams
# Output: 1. Backend, 2. Frontend Engineering, 3. DevOps

# Get available projects  
linear --projects
# Output: 1. Q4 Features, 2. Bug Fixes, 3. Technical Debt

# Get available users for assignment
linear --assignees  
# Output: 1. John Smith (john@company.com), 2. Jane Doe (jane@company.com)

# Get workflow states for status updates
linear --states
# Output: Backend: Todo, In Progress, In Review, Done
```

#### 2. Create Tickets with Validation
```bash
# Basic creation (minimal required info)
linear add --title "Fix login issue" --team "Backend"
# Output: ✅ Successfully created ticket: ZIF-124

# Full creation with all metadata
linear add \
  --title "Add user dashboard" \
  --description "Create comprehensive user management interface" \
  --team "Frontend Engineering" \
  --project "Q4 Features" \
  --assignee "john@company.com" \
  --priority high \
  --labels "feature,frontend,ui"
# Output: ✅ Successfully created ticket: ZIF-125
```

#### 3. Script-Friendly Operations
```bash
# Get only ticket ID for automation
TICKET_ID=$(linear add --title "Automated task" --team "Backend" --id-only)
echo "Created: $TICKET_ID"
# Output: Created: ZIF-126

# Search and update
linear "$TICKET_ID" --status "In Progress" --assignee "jane@company.com"
# Output: ✅ Updated ticket: ZIF-126
```

### AI Agent Best Practices

1. **Always validate resources first** - Run `--teams`, `--projects`, `--assignees` before creating tickets
2. **Use exact names** - Team and project names are case-sensitive
3. **Wrap parameters in quotes** - Especially for titles, descriptions, and names with spaces
4. **Check exit codes** - Non-zero exit codes indicate errors
5. **Use `--id-only` for scripting** - Clean output perfect for variable capture
6. **Handle errors gracefully** - Commands show specific error messages with suggestions

## 📖 Command Reference

### Ticket Creation
```bash
linear add [OPTIONS]

Required:
  --title "Ticket Title"              # Main ticket heading

Optional:
  --description "Detailed description" # Supports markdown
  --team "Team Name"                   # From --teams output
  --project "Project Name"             # From --projects output  
  --assignee "user@email.com"          # From --assignees output
  --priority urgent|high|normal|low    # Or numeric 1|2|3|4
  --labels "bug,frontend,critical"     # Comma-separated, no spaces
  --parent "ZIF-19"                    # Parent ticket ID
  --id-only                            # Return only ticket ID

Examples:
  linear add --title "Fix bug" --team "Backend"
  linear add --title "New feature" --team "Frontend" --project "Q4" --id-only
```

### Ticket Search
```bash
linear "QUERY" [OPTIONS]

Query Types:
  "ZIF-19"                            # Direct ticket lookup
  "project: Issues, Epic 1"           # Project + epic search
  "bug authentication"                # Keyword search
  
Options:
  --limit 5                           # Max results (default: 10)

Examples:
  linear "ZIF-123"
  linear "project: Backend database" --limit 5
  linear "critical bug" --limit 3
```

### Ticket Updates
```bash
linear "TICKET-ID" [UPDATE_OPTIONS]

Update Options:
  --status "Status Name"              # From --states output
  --title "New Title"                 # Replace existing title
  --description "New description"     # Replace existing description
  --priority urgent|high|normal|low   # Or numeric 1|2|3|4
  --assignee "user@email.com"         # From --assignees, or "none" to unassign

Examples:
  linear "ZIF-19" --status "Done"
  linear "ZIF-19" --assignee "user@company.com" --priority high
  linear "ZIF-19" --title "Updated title" --status "In Review"
```

### Utility Commands
```bash
linear --teams                        # List all teams
linear --projects                     # List all projects  
linear --assignees                    # List all users
linear --labels                       # List all labels
linear --states                       # List workflow states
linear --refresh                      # Update local cache
```

## 💡 Examples

### For AI Agents - Complete Workflows

#### Create and Track a Bug Report
```bash
# 1. Discover resources
TEAMS=$(linear --teams)
USERS=$(linear --assignees) 

# 2. Create bug ticket
BUG_ID=$(linear add \
  --title "Login fails with OAuth" \
  --description "Users cannot authenticate via OAuth provider" \
  --team "Backend" \
  --assignee "backend-lead@company.com" \
  --priority urgent \
  --labels "bug,authentication,critical" \
  --id-only)

echo "Created bug report: $BUG_ID"

# 3. Update as work progresses
linear "$BUG_ID" --status "In Progress"
linear "$BUG_ID" --description "Root cause identified: OAuth callback URL misconfigured"
linear "$BUG_ID" --status "In Review"
linear "$BUG_ID" --status "Done"
```

#### Create Feature with Sub-tasks
```bash
# 1. Create parent feature
FEATURE_ID=$(linear add \
  --title "User Dashboard v2" \
  --description "Redesigned user dashboard with analytics" \
  --team "Frontend" \
  --project "Q4 Features" \
  --priority high \
  --id-only)

# 2. Create sub-tasks
SUBTASK1=$(linear add \
  --title "Dashboard layout component" \
  --parent "$FEATURE_ID" \
  --team "Frontend" \
  --assignee "ui-dev@company.com" \
  --id-only)

SUBTASK2=$(linear add \
  --title "Analytics integration" \
  --parent "$FEATURE_ID" \
  --team "Frontend" \
  --assignee "data-dev@company.com" \
  --id-only)

echo "Feature: $FEATURE_ID, Subtasks: $SUBTASK1, $SUBTASK2"
```

### For Humans - Interactive Usage

#### Daily Ticket Management
```bash
# Check my assigned tickets
linear "assignee: john@company.com"

# Create quick ticket
linear add --title "Fix header alignment" --team "Frontend"

# Update ticket status
linear "ZIF-45" --status "Done"

# Search for recent bugs
linear "bug" --limit 5
```

## 🔧 Automation & Scripting

### Exit Codes
- `0` - Success
- `1` - Error (validation failed, API error, ticket not found)
- `2` - Invalid arguments

### Scripting Examples

#### CI/CD Integration
```bash
#!/bin/bash

# Create deployment ticket
DEPLOY_ID=$(linear add \
  --title "Deploy v${VERSION} to production" \
  --description "Automated deployment of version ${VERSION}" \
  --team "DevOps" \
  --assignee "$DEPLOY_ENGINEER" \
  --labels "deployment,production" \
  --id-only)

if [ $? -eq 0 ]; then
  echo "Deployment tracked in ticket: $DEPLOY_ID"
  
  # Update ticket during deployment
  linear "$DEPLOY_ID" --status "In Progress"
  
  # Deploy application...
  if deploy_application; then
    linear "$DEPLOY_ID" --status "Done" --description "Successfully deployed v${VERSION}"
  else
    linear "$DEPLOY_ID" --status "Failed" --description "Deployment failed: check logs"
    exit 1
  fi
else
  echo "Failed to create deployment ticket"
  exit 1
fi
```

#### Batch Operations
```bash
#!/bin/bash

# Process multiple tickets
TICKETS=("ZIF-10" "ZIF-11" "ZIF-12")

for ticket in "${TICKETS[@]}"; do
  echo "Processing $ticket..."
  linear "$ticket" --status "Done" --assignee "none"
  if [ $? -eq 0 ]; then
    echo "✅ Updated $ticket"
  else
    echo "❌ Failed to update $ticket"
  fi
done
```

## 🐛 Troubleshooting

### Common Issues

#### Authentication Errors
```bash
# Problem: "LINEAR_API_TOKEN environment variable not set"
# Solution:
export LINEAR_API_TOKEN="your_token_here"

# Problem: "400 Client Error: Bad Request"  
# Solution: Check token permissions in Linear settings
```

#### Validation Errors
```bash
# Problem: "Team 'backend' not found"
# Solution: Check exact team name
linear --teams  # See available teams

# Problem: "User 'john' not found"
# Solution: Use email or exact display name
linear --assignees  # See available users
```

#### Search Issues
```bash
# Problem: "No tickets found"
# Solution: Refresh cache and check query
linear --refresh
linear --projects  # Verify project names
```

### Debug Mode
```bash
# Add --token flag to see API requests
linear --token "$LINEAR_API_TOKEN" add --title "Debug test"
```

### Getting Help
```bash
linear --help              # Main help
linear add --help          # Ticket creation help
```

## 📂 Project Structure

```
linear-cli/
├── linear_search.py       # Main CLI application
├── linear_client.py       # Linear API client
├── ticket_search.py       # Search engine and ticket operations  
├── requirements.txt       # Python dependencies
├── setup_alias.sh         # Installation helper
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🤝 Contributing

We welcome contributions! This tool is designed to be AI-agent friendly while maintaining excellent usability for humans.

### Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up development environment** (see Installation section)
4. **Make your changes** following our development principles
5. **Test thoroughly** with real Linear workspaces
6. **Submit a pull request** with detailed description

### Development Principles

When extending functionality:

1. **Add detailed help text** - Include examples and validation notes
2. **Use consistent output formats** - Maintain JSON-friendly responses
3. **Handle errors gracefully** - Provide actionable error messages
4. **Document new features** - Update README with AI-agent examples
5. **Test with real scenarios** - Validate against actual Linear workspaces

For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the Linear community
- Designed with AI agents in mind
- Inspired by the need for powerful CLI tools in modern development workflows

## 📞 Support

If you encounter issues or have questions:
1. Check the [troubleshooting section](#-troubleshooting) in this README
2. Review existing [issues](https://github.com/vittoridavide/linear-cli/issues)
3. Create a new issue with detailed information
4. Consider contributing a fix!

## 🔗 Related Projects

- [Linear](https://linear.app) - The excellent project management tool this CLI interacts with
- [Linear API](https://developers.linear.app) - Official Linear API documentation

---

**Built for AI agents, humans, and automation. Happy ticket managing! 🎫**