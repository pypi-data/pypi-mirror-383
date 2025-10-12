# AI Agent Workflows for Linear CLI

This document provides step-by-step workflows that AI agents can follow to effectively use the Linear Ticket Manager CLI.

## 🤖 Prerequisites for AI Agents

Before executing any Linear commands, ensure:

1. **Environment Setup**
   ```bash
   export LINEAR_API_TOKEN="your_linear_api_token"
   ```

2. **Test Connection**
   ```bash
   linear --teams
   # Should return list of teams without errors
   ```

## 📋 Workflow 1: Basic Ticket Creation

**Use Case:** Create a simple ticket with minimal information

### Step 1: Discover Available Teams
```bash
linear --teams
```
**Expected Output:**
```
🎫 Linear Ticket Manager
==================================================

👥 Available Teams:
------------------------------
 1. Backend
 2. Frontend Engineering  
 3. DevOps
```

### Step 2: Create Basic Ticket
```bash
linear add --title "Fix authentication bug" --team "Backend"
```
**Expected Output:**
```
✅ Successfully created ticket: ZIF-123
📋 Title: Fix authentication bug
   Team: Backend | Priority: Normal
🔗 Direct link: https://linear.app/...
🎫 Ticket ID: ZIF-123
```

### Step 3: Verify Ticket Creation
```bash
linear "ZIF-123"
```
**Expected Output:** Full ticket details display

---

## 📋 Workflow 2: Complete Ticket Creation with All Metadata

**Use Case:** Create a fully specified ticket with team, project, assignee, labels, and priority

### Step 1: Gather All Required Information
```bash
# Get teams
linear --teams

# Get projects  
linear --projects

# Get available users
linear --assignees

# Get available labels
linear --labels
```

### Step 2: Create Comprehensive Ticket
```bash
linear add \
  --title "Implement user dashboard analytics" \
  --description "Create analytics dashboard showing user engagement metrics with real-time data visualization" \
  --team "Frontend Engineering" \
  --project "Q4 Features" \
  --assignee "john@company.com" \
  --priority high \
  --labels "feature,frontend,analytics"
```

**Expected Output:**
```
✅ Successfully created ticket: ZIF-124
📋 Title: Implement user dashboard analytics
   Team: Frontend Engineering | Project: Q4 Features | Assignee: John Doe | Priority: High | Labels: feature, frontend, analytics
🔗 Direct link: https://linear.app/...
🎫 Ticket ID: ZIF-124
```

---

## 📋 Workflow 3: Script-Friendly Ticket Creation

**Use Case:** Create tickets for automation/scripting with clean output

### Step 1: Create Ticket with ID-Only Output
```bash
TICKET_ID=$(linear add --title "Automated deployment ticket" --team "DevOps" --id-only)
```
**Expected Output:** `ZIF-125` (clean ticket ID only)

### Step 2: Use Ticket ID in Further Operations
```bash
echo "Created deployment ticket: $TICKET_ID"
linear "$TICKET_ID" --status "In Progress" --assignee "devops@company.com"
```

### Step 3: Complete the Workflow
```bash
# Update ticket as work progresses
linear "$TICKET_ID" --status "Done" --description "Deployment completed successfully"
```

---

## 📋 Workflow 4: Parent-Child Ticket Relationship

**Use Case:** Create a feature with multiple sub-tasks

### Step 1: Create Parent Feature Ticket
```bash
PARENT_ID=$(linear add \
  --title "User Authentication System v2" \
  --description "Complete overhaul of authentication system with OAuth integration" \
  --team "Backend" \
  --project "Q4 Features" \
  --priority high \
  --id-only)

echo "Parent feature ticket: $PARENT_ID"
```

### Step 2: Create Child Tickets
```bash
# Sub-task 1
SUBTASK1=$(linear add \
  --title "OAuth provider integration" \
  --parent "$PARENT_ID" \
  --team "Backend" \
  --assignee "backend-dev@company.com" \
  --labels "oauth,integration" \
  --id-only)

# Sub-task 2  
SUBTASK2=$(linear add \
  --title "User session management" \
  --parent "$PARENT_ID" \
  --team "Backend" \
  --assignee "security-dev@company.com" \
  --labels "security,sessions" \
  --id-only)

# Sub-task 3
SUBTASK3=$(linear add \
  --title "Frontend login component" \
  --parent "$PARENT_ID" \
  --team "Frontend Engineering" \
  --assignee "ui-dev@company.com" \
  --labels "frontend,ui" \
  --id-only)

echo "Created feature with sub-tasks:"
echo "Parent: $PARENT_ID"
echo "Sub-tasks: $SUBTASK1, $SUBTASK2, $SUBTASK3"
```

### Step 3: Track Progress
```bash
# Update sub-tasks as they progress
linear "$SUBTASK1" --status "In Progress"
linear "$SUBTASK2" --status "In Progress"  
linear "$SUBTASK3" --status "Todo"

# When sub-tasks complete
linear "$SUBTASK1" --status "Done"
linear "$SUBTASK2" --status "In Review"
```

---

## 📋 Workflow 5: Ticket Search and Update

**Use Case:** Find and update existing tickets

### Step 1: Search for Tickets
```bash
# Direct ticket lookup
linear "ZIF-123"

# Search by keywords
linear "authentication bug" --limit 5

# Search within project
linear "project: Backend database optimization" --limit 3
```

### Step 2: Update Found Tickets
```bash
# Update status
linear "ZIF-123" --status "In Review"

# Update multiple properties
linear "ZIF-123" --status "Done" --assignee "reviewer@company.com" --priority normal

# Update description
linear "ZIF-123" --description "Bug fixed: Updated OAuth callback handling to properly validate state parameter"
```

---

## 📋 Workflow 6: Batch Operations

**Use Case:** Process multiple tickets in automation

### Step 1: Define Ticket List
```bash
#!/bin/bash

TICKETS=("ZIF-120" "ZIF-121" "ZIF-122" "ZIF-123")
NEW_STATUS="Done"
REVIEWER="qa@company.com"
```

### Step 2: Process Each Ticket
```bash
for ticket in "${TICKETS[@]}"; do
    echo "Processing ticket: $ticket"
    
    # Update ticket
    if linear "$ticket" --status "$NEW_STATUS" --assignee "$REVIEWER"; then
        echo "✅ Successfully updated $ticket"
    else
        echo "❌ Failed to update $ticket"
        # Log error or continue based on requirements
    fi
done
```

### Step 3: Verify Updates
```bash
# Check each updated ticket
for ticket in "${TICKETS[@]}"; do
    echo "Verifying $ticket:"
    linear "$ticket" | grep -E "(Status|Assignee)"
done
```

---

## 📋 Workflow 7: Error Handling for AI Agents

**Use Case:** Robust error handling in automated workflows

### Step 1: Validate Resources Before Creating Tickets
```bash
#!/bin/bash

validate_resources() {
    local team_name="$1"
    local project_name="$2"
    local assignee="$3"
    
    # Check team exists
    if ! linear --teams | grep -q "$team_name"; then
        echo "❌ Team '$team_name' not found"
        linear --teams  # Show available teams
        return 1
    fi
    
    # Check project exists (if specified)
    if [[ -n "$project_name" ]] && ! linear --projects | grep -q "$project_name"; then
        echo "❌ Project '$project_name' not found"
        linear --projects  # Show available projects
        return 1
    fi
    
    # Check assignee exists (if specified)
    if [[ -n "$assignee" ]] && ! linear --assignees | grep -q "$assignee"; then
        echo "❌ Assignee '$assignee' not found"
        linear --assignees  # Show available users
        return 1
    fi
    
    return 0
}
```

### Step 2: Create Ticket with Validation
```bash
create_validated_ticket() {
    local title="$1"
    local team="$2"
    local project="$3"
    local assignee="$4"
    
    # Validate first
    if validate_resources "$team" "$project" "$assignee"; then
        echo "✅ Resources validated, creating ticket..."
        
        # Create ticket
        TICKET_ID=$(linear add \
            --title "$title" \
            --team "$team" \
            --project "$project" \
            --assignee "$assignee" \
            --id-only)
        
        if [[ $? -eq 0 && -n "$TICKET_ID" ]]; then
            echo "✅ Created ticket: $TICKET_ID"
            return 0
        else
            echo "❌ Failed to create ticket"
            return 1
        fi
    else
        echo "❌ Resource validation failed"
        return 1
    fi
}
```

### Step 3: Usage with Error Handling
```bash
# Example usage
if create_validated_ticket "Fix login issue" "Backend" "Bug Fixes" "dev@company.com"; then
    echo "Ticket creation successful"
    # Continue with next steps
else
    echo "Ticket creation failed, aborting workflow"
    exit 1
fi
```

---

## 🔧 Common AI Agent Patterns

### Pattern 1: Resource Discovery Cache
```bash
# Cache resources at start of workflow
TEAMS=$(linear --teams)
PROJECTS=$(linear --projects) 
USERS=$(linear --assignees)
LABELS=$(linear --labels)

# Use cached data for validation without repeated API calls
```

### Pattern 2: Exit Code Checking
```bash
# Always check exit codes for error handling
if linear add --title "Test" --team "Backend" --id-only; then
    echo "Success"
else
    echo "Failed with exit code: $?"
    # Handle error appropriately
fi
```

### Pattern 3: Output Parsing
```bash
# Parse ticket details from search results
TICKET_INFO=$(linear "ZIF-123")
STATUS=$(echo "$TICKET_INFO" | grep "State:" | cut -d: -f2 | xargs)
ASSIGNEE=$(echo "$TICKET_INFO" | grep "Assignee:" | cut -d: -f2 | xargs)
```

### Pattern 4: Conditional Operations
```bash
# Only update if ticket is in specific state
CURRENT_STATUS=$(linear "ZIF-123" | grep "State:" | cut -d: -f2 | xargs)

if [[ "$CURRENT_STATUS" == "In Progress" ]]; then
    linear "ZIF-123" --status "Done"
    echo "✅ Moved ticket to Done"
else
    echo "⚠️ Ticket not in Progress, current status: $CURRENT_STATUS"
fi
```

---

## 📊 Expected Output Examples

### Successful Ticket Creation
```
🎫 Linear Ticket Manager
==================================================

🎆 Creating Ticket
==================================================
✅ Successfully created ticket: ZIF-126
📋 Title: Example ticket title
   Team: Backend | Project: Q4 Features | Assignee: John Doe | Priority: High
🔗 Direct link: https://linear.app/company/issue/ZIF-126
🎫 Ticket ID: ZIF-126
```

### Error: Team Not Found
```
❌ Team 'NonExistentTeam' not found
Available teams: Backend, Frontend Engineering, DevOps
```

### Error: Authentication Failed
```
❌ Error: LINEAR_API_TOKEN environment variable not set.

To get your Linear API token:
1. Go to Linear Settings → API → Personal API tokens
2. Create a new token with appropriate permissions
3. Export it: export LINEAR_API_TOKEN='your_token_here'
```

---

**These workflows provide comprehensive examples for AI agents to effectively use the Linear CLI tool. Each workflow includes validation, error handling, and expected outputs for reliable automation.**