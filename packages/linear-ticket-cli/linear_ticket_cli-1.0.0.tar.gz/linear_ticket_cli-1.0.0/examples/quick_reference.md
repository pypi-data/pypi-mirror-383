# Quick Reference for AI Agents

## 🚀 Essential Commands

### Authentication Setup
```bash
export LINEAR_API_TOKEN="lin_api_your_token_here"
```

### Resource Discovery (Always Do First)
```bash
linear --teams      # Get team names for --team parameter
linear --projects   # Get project names for --project parameter  
linear --assignees  # Get user emails for --assignee parameter
linear --labels     # Get label names for --labels parameter
linear --states     # Get status names for --status parameter
```

### Create Tickets
```bash
# Minimal creation
linear add --title "Ticket title" --team "Team Name"

# Full creation
linear add --title "Title" --description "Description" --team "Team" --project "Project" --assignee "user@email.com" --priority high --labels "label1,label2"

# Script-friendly (returns only ticket ID)
linear add --title "Title" --team "Team" --id-only
```

### Search Tickets
```bash
linear "ZIF-123"                    # Direct lookup
linear "keyword search"             # Keyword search
linear "project: Project Name"      # Project search
```

### Update Tickets
```bash
linear "ZIF-123" --status "Done"
linear "ZIF-123" --assignee "user@email.com"
linear "ZIF-123" --priority urgent
linear "ZIF-123" --title "New title"
linear "ZIF-123" --description "New description"
```

## ⚠️ Validation Rules

- **Team names**: Case-sensitive, must exist in `linear --teams`
- **Project names**: Case-sensitive, must exist in `linear --projects`
- **User assignments**: Use email or exact display name from `linear --assignees`
- **Priority levels**: `urgent`, `high`, `normal`, `low` OR `1`, `2`, `3`, `4`
- **Status names**: Must exist in `linear --states` for ticket's team
- **Labels**: Comma-separated, NO spaces: `"label1,label2,label3"`
- **Ticket IDs**: Format like `ZIF-123`, case-insensitive

## 🔧 AI Agent Best Practices

1. **Always validate resources first**: `linear --teams`, `--projects`, `--assignees`
2. **Use exact names**: Resources are case-sensitive
3. **Wrap parameters in quotes**: Especially titles and descriptions with spaces
4. **Check exit codes**: `0` = success, `1` = error, `2` = invalid arguments
5. **Use `--id-only` for automation**: Returns clean ticket ID for scripts
6. **Handle errors gracefully**: Commands show specific error messages

## 📊 Exit Codes
- `0`: Success
- `1`: Error (validation failed, API error, ticket not found)
- `2`: Invalid command arguments

## 🎯 Common Patterns

### Script-friendly ticket creation:
```bash
TICKET_ID=$(linear add --title "Task" --team "Backend" --id-only)
if [ $? -eq 0 ]; then
    echo "Created: $TICKET_ID"
else
    echo "Failed to create ticket"
    exit 1
fi
```

### Resource validation:
```bash
if ! linear --teams | grep -q "Backend"; then
    echo "Team 'Backend' not found"
    exit 1
fi
```

### Batch operations:
```bash
for ticket in "ZIF-10" "ZIF-11" "ZIF-12"; do
    linear "$ticket" --status "Done"
done
```