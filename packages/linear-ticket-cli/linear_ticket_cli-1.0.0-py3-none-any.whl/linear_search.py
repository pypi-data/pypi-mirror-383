#!/usr/bin/env python3
"""
Linear Ticket Management CLI
A command-line tool for searching, creating, and managing Linear tickets.

Usage:
    python linear_search.py "project: Issues, Epic 1 Ticket 1.5"  # Search
    python linear_search.py add --title "Fix bug"                   # Create ticket
    python linear_search.py --refresh                               # Refresh cache
    python linear_search.py --projects                              # List projects
"""
import argparse
import sys
import os
from typing import List, Optional, Dict, Any
from linear_client import LinearClient
from ticket_search import TicketSearchEngine


def setup_argparser() -> argparse.ArgumentParser:
    """Set up command line argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="""Linear Ticket Management CLI - Search, create, and manage Linear tickets from command line.
        
This tool allows you to interact with Linear's API to:
        - Search for existing tickets using natural language queries
        - Create new tickets with full metadata (team, project, assignee, labels, etc.)
        - Update existing ticket properties (status, title, description, priority, assignee)
        - List available resources (teams, projects, users, labels, workflow states)
        
IMPORTANT: You must set LINEAR_API_TOKEN environment variable before using this tool.
        Get your token from Linear → Settings → API → Personal API tokens.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
DETAILED USAGE EXAMPLES:

=== SEARCHING TICKETS ===
# Direct ticket lookup by identifier (fastest method)
%(prog)s "ZIF-19"                              
# Result: Shows full details of ticket ZIF-19

# Complex search with project filter and epic/ticket numbers
%(prog)s "project: Issues, Epic 1 Ticket 1.5" 
# Result: Searches within "Issues" project for tickets related to Epic 1, Ticket 1.5

# Keyword search across all tickets
%(prog)s "bug fix authentication"              
# Result: Finds tickets containing words "bug", "fix", "authentication" in title/description

# Search within specific project
%(prog)s "project: Frontend database optimization"
# Result: Searches for "database optimization" within "Frontend" project

=== CREATING TICKETS ===
# Minimal ticket creation (only title required)
%(prog)s add --title "Fix authentication bug"  
# Result: Creates ticket with default settings, displays full ticket info including ZIF-XX ID

# Complete ticket creation with all metadata
%(prog)s add --title "New user dashboard" --description "Create comprehensive user management interface" --team "Frontend" --project "Q4 Features" --assignee "john@company.com" --priority high --labels "feature,frontend" --parent "ZIF-19"
# Result: Creates fully configured ticket and displays ZIF-XX identifier

# Script-friendly creation (returns only ticket ID)
%(prog)s add --title "Automated ticket" --team "Backend" --id-only
# Result: Outputs only "ZIF-XX" (perfect for shell scripts and automation)

=== UPDATING TICKETS ===
# Change ticket status (must use existing workflow state name)
%(prog)s "ZIF-19" --status "In Progress"       
# Result: Updates ticket ZIF-19 status, displays updated ticket

# Update ticket title
%(prog)s "ZIF-19" --title "New ticket title"   
# Result: Changes ticket title, shows updated ticket details

# Set ticket priority (accepts: urgent, high, normal, low OR 1, 2, 3, 4)
%(prog)s "ZIF-19" --priority urgent            
# Result: Sets priority to urgent (1), displays updated ticket

# Assign ticket to user (use email or display name)
%(prog)s "ZIF-19" --assignee "user@company.com"
# Result: Assigns ticket to user, shows updated assignment

# Unassign ticket
%(prog)s "ZIF-19" --assignee none
# Result: Removes assignee from ticket

=== UTILITY COMMANDS (List Available Resources) ===
# List all teams (needed for --team parameter)
%(prog)s --teams                              
# Result: Shows numbered list of all teams in your Linear workspace

# List all projects (needed for --project parameter)  
%(prog)s --projects                            
# Result: Shows all available projects you can assign tickets to

# List all users (needed for --assignee parameter)
%(prog)s --assignees                          
# Result: Shows all users with names and email addresses for assignment

# List all labels (needed for --labels parameter)
%(prog)s --labels                             
# Result: Shows all available labels grouped by team

# List workflow states (needed for --status parameter)
%(prog)s --states                              
# Result: Shows all available status names you can use with --status

# Refresh local ticket cache (improves search speed)
%(prog)s --refresh                             
# Result: Downloads latest tickets from Linear API, updates local cache

=== AUTOMATION EXAMPLES ===
# Create ticket and capture ID for further processing
TICKET_ID=$(%(prog)s add --title "Deploy v2.1.0" --team "DevOps" --id-only)
echo "Deployment tracked in ticket: $TICKET_ID"

# Batch update multiple aspects of a ticket
%(prog)s "ZIF-19" --status "In Review" --priority high --assignee "reviewer@company.com"
# Result: Updates status, priority, and assignee in one command

NOTE: All commands require LINEAR_API_TOKEN environment variable to be set.
        """
    )
    
    # Global arguments with detailed descriptions for AI agents
    parser.add_argument(
        "--token",
        help="""OPTIONAL: Linear API token for authentication. Overrides LINEAR_API_TOKEN environment variable.
        Example: --token "lin_api_abcd1234..."
        Note: Generally better to set LINEAR_API_TOKEN env var instead.
        Get token from Linear → Settings → API → Personal API tokens."""
    )
    
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="""UTILITY: Downloads latest tickets from Linear API and updates local cache.
        Usage: Run this periodically to ensure searches include recent tickets.
        Effect: Improves search speed by caching tickets locally.
        Example: linear --refresh (shows progress and count of cached tickets)"""
    )
    
    parser.add_argument(
        "--projects",
        action="store_true",
        help="""UTILITY: Display numbered list of all available projects in your Linear workspace.
        Usage: Use this before creating tickets to see valid --project values.
        Output: Shows project names that can be used with 'linear add --project "Name"'.
        Example: linear --projects (lists: 1. Q4 Features, 2. Bug Fixes, etc.)"""
    )
    
    parser.add_argument(
        "--teams",
        action="store_true",
        help="""UTILITY: Display numbered list of all available teams in your Linear workspace.
        Usage: Use this before creating tickets to see valid --team values.
        Output: Shows team names and descriptions that can be used with 'linear add --team "Name"'.
        Example: linear --teams (lists: 1. Backend, 2. Frontend Engineering, etc.)"""
    )
    
    parser.add_argument(
        "--states",
        action="store_true",
        help="""UTILITY: Display all available workflow states/statuses grouped by team.
        Usage: Use this before updating tickets to see valid --status values.
        Output: Shows status names like "Todo", "In Progress", "Done" by team.
        Example: linear --states (shows all status options for 'linear "ZIF-19" --status "Name"')"""
    )
    
    parser.add_argument(
        "--assignees",
        action="store_true",
        help="""UTILITY: Display numbered list of all users available for ticket assignment.
        Usage: Use this before creating/updating tickets to see valid --assignee values.
        Output: Shows display names and email addresses for assignment.
        Example: linear --assignees (lists: 1. John Smith (john@company.com), etc.)"""
    )
    
    parser.add_argument(
        "--labels",
        action="store_true",
        help="""UTILITY: Display all available labels grouped by team with descriptions and colors.
        Usage: Use this before creating tickets to see valid --labels values.
        Output: Shows label names, colors, and descriptions by team.
        Example: linear --labels (shows labels like "bug", "feature", "critical" for --labels parameter)"""
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add ticket creation subcommand
    add_parser = subparsers.add_parser(
        "add", 
        help="Create a new Linear ticket with specified title, team, project, assignee, labels, and other metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Create a new ticket in Linear with comprehensive metadata support.
        
This subcommand creates tickets with full Linear integration including:
- Team assignment (use --teams to see available teams)
- Project assignment (use --projects to see available projects)  
- User assignment (use --assignees to see available users)
- Priority levels (urgent/high/normal/low or 1/2/3/4)
- Label tagging (use --labels to see available labels)
- Parent-child relationships (reference existing ticket IDs)
- Rich descriptions with markdown support
        
OUTPUT MODES:
- Default: Shows full ticket creation details with prominent ticket ID
- --id-only: Returns only the ticket identifier (e.g., "ZIF-123") for scripting""",
        epilog="""
STEP-BY-STEP TICKET CREATION EXAMPLES:

=== MINIMAL CREATION (AI Agent Recommended Steps) ===
1. First, list available teams to choose from:
   linear --teams
   
2. Create basic ticket with chosen team:
   %(prog)s --title "Fix authentication bug" --team "Backend"
   
3. Result: Creates ticket and displays format like:
   ✅ Successfully created ticket: ZIF-XX
   📋 Title: Fix authentication bug
   🎫 Ticket ID: ZIF-XX

=== COMPLETE TICKET CREATION (Full Workflow) ===
1. Check available resources:
   linear --teams          # Choose team name
   linear --projects       # Choose project name  
   linear --assignees      # Choose user email
   linear --labels         # Choose label names
   
2. Create comprehensive ticket:
   %(prog)s --title "Add user dashboard" --description "Create comprehensive user management interface with role-based access control" --team "Frontend" --project "Q4 Features" --assignee "john@company.com" --priority high --labels "feature,frontend,ui" --parent "ZIF-19"
   
3. Result: Creates ticket with all metadata and displays:
   ✅ Successfully created ticket: ZIF-XX
   📋 Title: Add user dashboard  
   Team: Frontend | Project: Q4 Features | Assignee: John Doe | Parent: ZIF-19 | Priority: High | Labels: feature, frontend, ui
   🔗 Direct link: https://linear.app/...
   🎫 Ticket ID: ZIF-XX

=== AUTOMATION/SCRIPTING MODE ===
1. Create ticket and capture only the ID for further processing:
   TICKET_ID=$(%(prog)s --title "Automated deployment" --team "DevOps" --id-only)
   
2. Result: Outputs only ticket identifier (e.g., "ZIF-123") with no extra formatting
   
3. Use the captured ID in subsequent operations:
   echo "Created ticket: $TICKET_ID"
   linear "$TICKET_ID" --status "In Progress"

=== PARAMETER VALIDATION NOTES ===
- --team: Must match exact team name from 'linear --teams'
- --project: Must match exact project name from 'linear --projects'  
- --assignee: Use email address or exact display name from 'linear --assignees'
- --priority: Use 'urgent', 'high', 'normal', 'low' OR numeric 1, 2, 3, 4
- --labels: Comma-separated list, no spaces after commas (e.g., "bug,frontend,critical")
- --parent: Must be existing ticket identifier (e.g., "ZIF-19")
- --description: Supports markdown formatting

=== ERROR HANDLING ===
If any parameter is invalid, the command will:
1. Display specific error message
2. Show available valid options when possible
3. Exit with error code 1 (for script detection)
4. Not create a partial ticket (atomic operation)
        """
    )
    
    # Ticket creation arguments with detailed descriptions for AI agents
    add_parser.add_argument(
        "--title",
        required=True,
        help="""REQUIRED: Ticket title as a string. This will be the main heading visible in Linear.
        Example: --title "Fix authentication login bug" 
        Note: Wrap in quotes if title contains spaces or special characters."""
    )
    
    add_parser.add_argument(
        "--description",
        help="""OPTIONAL: Detailed ticket description. Supports markdown formatting.
        Example: --description "Users cannot log in when using OAuth. Error occurs on callback URL."
        Note: Wrap in quotes. Can include markdown like **bold** or `code` blocks."""
    )
    
    add_parser.add_argument(
        "--team",
        help="""OPTIONAL: Exact team name to assign ticket to. Must match team name from 'linear --teams' output.
        Example: --team "Backend" or --team "Frontend Engineering"
        Note: Case-sensitive. Use quotes if team name contains spaces.
        Validation: Run 'linear --teams' first to see available team names."""
    )
    
    add_parser.add_argument(
        "--project",
        help="""OPTIONAL: Exact project name to assign ticket to. Must match project name from 'linear --projects' output.
        Example: --project "Q4 Features" or --project "Bug Fixes"
        Note: Case-sensitive. Use quotes if project name contains spaces.
        Validation: Run 'linear --projects' first to see available project names."""
    )
    
    add_parser.add_argument(
        "--parent",
        help="""OPTIONAL: Parent ticket identifier for creating sub-tickets. Must be existing ticket ID.
        Example: --parent "ZIF-19" or --parent "ABC-123"
        Note: Use exact ticket identifier format. Creates parent-child relationship.
        Validation: Parent ticket must exist and be accessible to your account."""
    )
    
    add_parser.add_argument(
        "--assignee",
        help="""OPTIONAL: User to assign ticket to. Use email address or exact display name from 'linear --assignees'.
        Example: --assignee "john@company.com" or --assignee "John Smith"
        Note: Must exactly match email or display name from assignees list.
        Validation: Run 'linear --assignees' first to see available users."""
    )
    
    add_parser.add_argument(
        "--priority",
        choices=["urgent", "high", "normal", "low", "1", "2", "3", "4"],
        default="normal",
        help="""OPTIONAL: Ticket priority level. Accepts text or numeric values.
        Text options: 'urgent' (highest), 'high', 'normal' (default), 'low' (lowest)
        Numeric options: '1' (urgent), '2' (high), '3' (normal), '4' (low)
        Example: --priority urgent or --priority 1
        Default: 'normal' if not specified."""
    )
    
    add_parser.add_argument(
        "--labels",
        help="""OPTIONAL: Comma-separated list of label names. NO spaces after commas.
        Example: --labels "bug,frontend,critical" or --labels "feature,backend"
        Note: Labels must exist in Linear. Use quotes around entire list.
        Format: "label1,label2,label3" (no spaces after commas)
        Validation: Run 'linear --labels' first to see available labels."""
    )
    
    add_parser.add_argument(
        "--interactive",
        action="store_true",
        help="""OPTIONAL: Enable interactive mode for missing fields (not commonly used).
        When specified: Tool will prompt for missing information interactively.
        Default: Non-interactive mode - uses provided parameters only."""
    )
    
    add_parser.add_argument(
        "--id-only",
        action="store_true",
        help="""OPTIONAL: Return only the ticket identifier for scripting/automation.
        When specified: Outputs only ticket ID (e.g., "ZIF-123") with no formatting.
        Default: Shows full ticket creation details with metadata.
        Usage: Perfect for shell scripts - TICKET_ID=$(linear add --title "test" --id-only)"""
    )
    
    # Add project creation subcommand

    # Add team creation subcommand
    create_team_parser = subparsers.add_parser(
        "create-team",
        help="Create a new Linear team with specified name, description, and customization options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Create a new team in Linear with comprehensive customization support.
        
This subcommand creates teams with full Linear integration including:
- Custom team key/identifier (auto-generated if not provided)
- Team icon and color customization
- Rich descriptions with markdown support
- Full team configuration options
        
OUTPUT MODES:
- Default: Shows full team creation details with prominent team information
- --id-only: Returns only the team identifier for scripting""",
        epilog="""
STEP-BY-STEP TEAM CREATION EXAMPLES:

=== MINIMAL CREATION (AI Agent Recommended Steps) ===
1. Create basic team with just a name:
   %(prog)s --name "Backend Engineering"
   
2. Result: Creates team and displays:
   ✅ Successfully created team: Backend Engineering
   🔑 Team Key: BACKEND
   🆔 Team ID: [team-id]

=== COMPLETE TEAM CREATION (Full Workflow) ===
1. Create comprehensive team with all customization:
   %(prog)s --name "Frontend Development" --description "Responsible for all user-facing features and interfaces" --key "FE" --icon "palette" --color "3b82f6"
   
2. Result: Creates team with all metadata and displays:
   ✅ Successfully created team: Frontend Development
   🔑 Team Key: FE | 📍 Icon: palette | 🎨 Color: #3b82f6
   📋 Description: Responsible for all user-facing features and interfaces
   🆔 Team ID: [team-id]

=== AUTOMATION/SCRIPTING MODE ===
1. Create team and capture only the ID:
   TEAM_ID=$(%(prog)s --name "DevOps" --key "DEVOPS" --id-only)
   
2. Result: Outputs only team identifier with no formatting
   
3. Use the captured ID for further operations

=== PARAMETER VALIDATION NOTES ===
- --name: Required, will be the team name visible in Linear
- --key: Optional, team identifier/prefix for issues (auto-generated if not provided)
- --description: Supports markdown formatting
- --icon: Single emoji or icon name (e.g., "🚀", "rocket")
- --color: Hex color code without # (e.g., "3b82f6", "ff6b6b")

=== COMMON TEAM ICONS ===
- Development: rocket, desktop, database, settings
- Design: palette, lightbulb, chart, desktop
- Product: chart, lightbulb, shield, rocket
- Marketing: chart, lightbulb, desktop, shield
- Support: shield, lightbulb, desktop, settings

=== POPULAR TEAM COLORS ===
- Blue: 3b82f6, 1e40af, 2563eb
- Green: 10b981, 059669, 16a34a
- Purple: 8b5cf6, 7c3aed, 9333ea
- Red: ef4444, dc2626, f87171
- Orange: f97316, ea580c, fb923c

=== ERROR HANDLING ===
If any parameter is invalid, the command will:
1. Display specific error message
2. Show suggestions for valid values
3. Exit with error code 1 (for script detection)
4. Not create a partial team (atomic operation)
        """
    )
    
    # Team creation arguments with detailed descriptions for AI agents
    create_team_parser.add_argument(
        "--name",
        required=True,
        help="""REQUIRED: Team name as a string. This will be the main team name visible in Linear.
        Example: --name "Backend Engineering" or --name "Product Design Team"
        Note: Wrap in quotes if name contains spaces or special characters."""
    )
    
    create_team_parser.add_argument(
        "--description",
        help="""OPTIONAL: Detailed team description. Supports markdown formatting.
        Example: --description "Responsible for all backend services and API development."
        Note: Wrap in quotes. Can include markdown like **bold** or `code` blocks."""
    )
    
    create_team_parser.add_argument(
        "--key",
        help="""OPTIONAL: Team key/identifier used as prefix for issues (e.g., "BACKEND" creates issues like BACKEND-123).
        Example: --key "BE" or --key "FRONTEND" or --key "DESIGN"
        Note: Should be short (2-10 characters), uppercase recommended. Auto-generated if not provided.
        Validation: Must be unique across your Linear workspace."""
    )
    
    create_team_parser.add_argument(
        "--icon",
        help="""OPTIONAL: Team icon name (not emoji). Must be a valid Linear icon identifier.
        Example: --icon "database" or --icon "desktop" or --icon "rocket"
        Note: Linear uses predefined icon names, not custom emojis. Will be displayed next to team name.
        Common icons: database, desktop, rocket, lightbulb, palette, chart, shield, settings"""
    )
    
    create_team_parser.add_argument(
        "--color",
        help="""OPTIONAL: Team color as hex code without the # symbol.
        Example: --color "3b82f6" (blue) or --color "ef4444" (red) or --color "10b981" (green)
        Note: Use 6-character hex codes. Will be used for team theming in Linear interface.
        Popular choices: 3b82f6 (blue), 10b981 (green), 8b5cf6 (purple), ef4444 (red), f97316 (orange)"""
    )
    
    create_team_parser.add_argument(
        "--id-only",
        action="store_true",
        help="""OPTIONAL: Return only the team identifier for scripting/automation.
        When specified: Outputs only team ID with no formatting.
        Default: Shows full team creation details with metadata.
        Usage: Perfect for shell scripts - TEAM_ID=$(linear create-team --name "test" --id-only)"""
    )
    
    # Search/update behavior - positional argument with detailed AI guidance
    create_project_parser = subparsers.add_parser(
        "create-project",
        help="Create a new Linear project with specified name, description, teams, and metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Create a new project in Linear with comprehensive metadata support.
        
This subcommand creates projects with full Linear integration including:
- Team assignment (use --teams to see available teams)
- Project lead assignment (use --assignees to see available users)
- Target date setting for project completion
- Project state management (planned, started, completed, canceled)
- Rich descriptions with markdown support
        
OUTPUT MODES:
- Default: Shows full project creation details with prominent project ID
- --id-only: Returns only the project identifier for scripting""",
        epilog="""
STEP-BY-STEP PROJECT CREATION EXAMPLES:

=== MINIMAL CREATION (AI Agent Recommended Steps) ===
1. Create basic project with just a name:
   %(prog)s --name "Q1 2024 Features"
   
2. Result: Creates project and displays:
   ✅ Successfully created project: Q1 2024 Features
   🆔 Project ID: [project-id]

=== COMPLETE PROJECT CREATION (Full Workflow) ===
1. Check available resources:
   linear --teams          # Choose team names
   linear --assignees      # Choose project lead email
   
2. Create comprehensive project:
   %(prog)s --name "Mobile App Redesign" --description "Complete redesign of mobile application with new UX patterns" --teams "Frontend,Backend,Design" --lead "john@company.com" --target-date "2024-06-30" --state "planned"
   
3. Result: Creates project with all metadata and displays:
   ✅ Successfully created project: Mobile App Redesign
   Teams: Frontend, Backend, Design | Lead: John Doe | Target: 2024-06-30 | State: Planned
   🔗 Direct link: https://linear.app/...
   🆔 Project ID: [project-id]

=== AUTOMATION/SCRIPTING MODE ===
1. Create project and capture only the ID:
   PROJECT_ID=$(%(prog)s --name "Automated Project" --teams "DevOps" --id-only)
   
2. Result: Outputs only project identifier with no formatting
   
3. Use the captured ID for further operations

=== PARAMETER VALIDATION NOTES ===
- --name: Required, will be the project name visible in Linear
- --teams: Comma-separated team names from 'linear --teams' (e.g., "Backend,Frontend")
- --lead: Email address or exact display name from 'linear --assignees'
- --target-date: ISO date format YYYY-MM-DD (e.g., "2024-12-31")
- --state: Must be one of: "planned", "started", "completed", "canceled"
- --description: Supports markdown formatting

=== ERROR HANDLING ===
If any parameter is invalid, the command will:
1. Display specific error message
2. Show available valid options when possible
3. Exit with error code 1 (for script detection)
4. Not create a partial project (atomic operation)
        """
    )
    
    # Project creation arguments with detailed descriptions for AI agents
    create_project_parser.add_argument(
        "--name",
        required=True,
        help="""REQUIRED: Project name as a string. This will be the main heading visible in Linear.
        Example: --name "Q4 2024 Features" 
        Note: Wrap in quotes if name contains spaces or special characters."""
    )
    
    create_project_parser.add_argument(
        "--description",
        help="""OPTIONAL: Detailed project description. Supports markdown formatting.
        Example: --description "Complete mobile app redesign with new user experience patterns."
        Note: Wrap in quotes. Can include markdown like **bold** or `code` blocks."""
    )
    
    create_project_parser.add_argument(
        "--teams",
        required=True,
        help="""REQUIRED: Comma-separated list of team names to associate with project. Must match team names from 'linear --teams' output.
        Example: --teams "Backend,Frontend" or --teams "Frontend Engineering,Design"
        Note: Case-sensitive. Use quotes around entire list, no spaces after commas.
        Validation: Run 'linear --teams' first to see available team names."""
    )
    
    create_project_parser.add_argument(
        "--lead",
        help="""OPTIONAL: Project lead to assign. Use email address or exact display name from 'linear --assignees'.
        Example: --lead "john@company.com" or --lead "John Smith"
        Note: Must exactly match email or display name from assignees list.
        Validation: Run 'linear --assignees' first to see available users."""
    )
    
    create_project_parser.add_argument(
        "--target-date",
        help="""OPTIONAL: Target completion date in ISO format (YYYY-MM-DD).
        Example: --target-date "2024-12-31" or --target-date "2024-06-15"
        Note: Must be valid date in the future. Will be used for project planning and tracking."""
    )
    
    create_project_parser.add_argument(
        "--state",
        choices=["planned", "started", "completed", "canceled"],
        default="planned",
        help="""OPTIONAL: Project state/status.
        Options: 'planned' (default), 'started', 'completed', 'canceled'
        Example: --state started
        Default: 'planned' if not specified."""
    )
    
    create_project_parser.add_argument(
        "--id-only",
        action="store_true",
        help="""OPTIONAL: Return only the project identifier for scripting/automation.
        When specified: Outputs only project ID with no formatting.
        Default: Shows full project creation details with metadata.
        Usage: Perfect for shell scripts - PROJECT_ID=$(linear create-project --name "test" --id-only)"""
    )
    
    # Search/update behavior - positional argument with detailed AI guidance
    parser.add_argument(
        "query",
        nargs="?",
        help="""SEARCH/UPDATE: Search query string or ticket identifier for operations.
        
        FOR SEARCHING:
        - Direct ticket lookup: "ZIF-19" (fastest, shows full ticket details)
        - Project filter: "project: Issues, Epic 1 Ticket 1.5" (searches within Issues project)
        - Keyword search: "bug fix authentication" (searches titles and descriptions)
        - Complex search: "project: Frontend database optimization" (project + keywords)
        
        FOR UPDATING:
        - Must be exact ticket identifier: "ZIF-19" (combined with --status, --title, etc.)
        - Example: linear "ZIF-19" --status "Done" (updates ticket ZIF-19 status)
        
        Note: Wrap in quotes if query contains spaces or special characters."""
    )
    
    # Update arguments with detailed descriptions for AI agents
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="""SEARCH OPTION: Maximum number of search results to display.
        Range: 1-100, Default: 10
        Example: --limit 5 (shows only top 5 matches)
        Usage: Only applies to search operations, ignored for updates."""
    )
    
    parser.add_argument(
        "--status",
        help="""UPDATE: Change ticket status/workflow state. Must use exact status name from 'linear --states'.
        Example: --status "In Progress" or --status "Done"
        Usage: Combine with ticket ID - linear "ZIF-19" --status "Done"
        Validation: Status must exist in the ticket's team workflow.
        Note: Status names are case-sensitive, wrap in quotes if contains spaces."""
    )
    
    parser.add_argument(
        "--title",
        help="""UPDATE: Change ticket title. New title will replace the existing one completely.
        Example: --title "Fixed authentication bug"
        Usage: Combine with ticket ID - linear "ZIF-19" --title "New Title"
        Note: Wrap in quotes, supports Unicode and special characters."""
    )
    
    parser.add_argument(
        "--description",
        help="""UPDATE: Change ticket description. New description replaces existing one completely.
        Example: --description "Updated implementation using OAuth 2.0 flow"
        Usage: Combine with ticket ID - linear "ZIF-19" --description "New description"
        Note: Supports markdown formatting, wrap in quotes."""
    )
    
    parser.add_argument(
        "--priority",
        help="""UPDATE: Change ticket priority level.
        Text options: 'urgent' (1), 'high' (2), 'normal' (3), 'low' (4)
        Numeric options: '1' (urgent), '2' (high), '3' (normal), '4' (low)
        Example: --priority urgent or --priority 1
        Usage: Combine with ticket ID - linear "ZIF-19" --priority high"""
    )
    
    parser.add_argument(
        "--assignee",
        help="""UPDATE: Change ticket assignee. Use email or exact display name from 'linear --assignees'.
        Assign: --assignee "john@company.com" or --assignee "John Smith"
        Unassign: --assignee none (removes current assignee)
        Usage: Combine with ticket ID - linear "ZIF-19" --assignee "user@company.com"
        Validation: User must exist and be accessible in your Linear workspace."""
    )
    
    return parser


def print_banner():
    """Print the application banner."""
    print("🎫 Linear Ticket Manager")
    print("=" * 50)


def print_projects(search_engine: TicketSearchEngine):
    """Print all available projects."""
    print("\n📁 Available Projects:")
    print("-" * 30)
    
    projects = search_engine.get_projects()
    if not projects:
        print("No projects found.")
        return
    
    for i, project in enumerate(sorted(projects), 1):
        print(f"{i:2d}. {project}")


def print_states(search_engine: TicketSearchEngine):
    """Print all available workflow states."""
    print("\n🔄 Available Workflow States:")
    print("-" * 40)
    
    states = search_engine.get_available_states()
    if not states:
        print("No workflow states found.")
        return
    
    # Group by team
    teams = {}
    for state in states:
        team_name = state.get('team', {}).get('name', 'Global') if state.get('team') else 'Global'
        if team_name not in teams:
            teams[team_name] = []
        teams[team_name].append(state)
    
    for team_name, team_states in sorted(teams.items()):
        print(f"\n{team_name}:")
        for state in sorted(team_states, key=lambda x: x['name']):
            state_type = state.get('type', 'unknown')
            print(f"  • {state['name']} ({state_type})")


def print_assignees(search_engine: TicketSearchEngine):
    """Print all available users for assignment."""
    print("\n👤 Available Users for Assignment:")
    print("-" * 45)
    
    assignees = search_engine.get_available_assignees()
    if not assignees:
        print("No users found.")
        return
    
    for i, user in enumerate(sorted(assignees, key=lambda x: x.get('name', '')), 1):
        name = user.get('displayName') or user.get('name') or 'Unknown'
        email = user.get('email', '')
        if email:
            print(f"{i:2d}. {name} ({email})")
        else:
            print(f"{i:2d}. {name}")


def print_teams(search_engine: TicketSearchEngine):
    """Print all available teams."""
    print("\n👥 Available Teams:")
    print("-" * 30)
    
    teams = search_engine.get_teams()
    if not teams:
        print("No teams found.")
        return
    
    for i, team in enumerate(sorted(teams, key=lambda x: x['name']), 1):
        name = team['name']
        description = team.get('description', '')
        if description:
            print(f"{i:2d}. {name} - {description}")
        else:
            print(f"{i:2d}. {name}")


def print_labels(search_engine: TicketSearchEngine, team_name: Optional[str] = None):
    """Print all available labels."""
    if team_name:
        print(f"\n🏷️  Available Labels for Team '{team_name}':")
    else:
        print("\n🏷️  Available Labels:")
    print("-" * 45)
    
    # Get team ID if team name provided
    team_id = None
    if team_name:
        teams = search_engine.get_teams()
        for team in teams:
            if team['name'].lower() == team_name.lower():
                team_id = team['id']
                break
        if not team_id:
            print(f"❌ Team '{team_name}' not found")
            return
    
    labels = search_engine.get_labels(team_id)
    if not labels:
        print("No labels found.")
        return
    
    # Group labels by team if showing all labels
    if not team_name:
        teams_labels = {}
        for label in labels:
            team_info = label.get('team')
            team_key = team_info['name'] if team_info else 'Global'
            if team_key not in teams_labels:
                teams_labels[team_key] = []
            teams_labels[team_key].append(label)
        
        for team_key, team_labels in sorted(teams_labels.items()):
            print(f"\n{team_key}:")
            for label in sorted(team_labels, key=lambda x: x['name']):
                color = label.get('color', '#000000')
                desc = label.get('description', '')
                if desc:
                    print(f"  • {label['name']} ({color}) - {desc}")
                else:
                    print(f"  • {label['name']} ({color})")
    else:
        for i, label in enumerate(sorted(labels, key=lambda x: x['name']), 1):
            color = label.get('color', '#000000')
            desc = label.get('description', '')
            if desc:
                print(f"{i:2d}. {label['name']} ({color}) - {desc}")
            else:
                print(f"{i:2d}. {label['name']} ({color})")


def print_search_results(results: List, search_engine: TicketSearchEngine):
    """Print search results."""
    if not results:
        print("\n❌ No tickets found matching your query.")
        print("\nTip: Try broader keywords or check project names with --projects")
        return
    
    print(f"\n🎯 Found {len(results)} matching ticket(s):")
    print("=" * 80)
    
    for i, (ticket, score) in enumerate(results, 1):
        print(f"\n{i}.")
        print(search_engine.format_ticket_result(ticket, score, True))
        
        if i < len(results):
            print("-" * 80)


def handle_ticket_creation(args, search_engine: TicketSearchEngine):
    """Handle ticket creation command."""
    if not args.id_only:
        print("\n🎆 Creating Ticket")
        print("=" * 50)
    
    # Parse labels
    label_names = None
    if args.labels:
        label_names = [label.strip() for label in args.labels.split(",")]
    
    # Create ticket with provided arguments
    result = search_engine.create_ticket(
        title=args.title,
        description=args.description or "",
        team_name=args.team,
        project_name=args.project,
        parent_identifier=args.parent,
        assignee_identifier=args.assignee,
        priority=args.priority,
        label_names=label_names,
        quiet_mode=args.id_only
    )
    
    if not result:
        sys.exit(1)
    
    # If --id-only flag is set, just print the ticket ID
    if args.id_only:
        print(result['identifier'])
    
    return result


def handle_project_creation(args, client: LinearClient):
    """Handle project creation command."""
    if not args.id_only:
        print("\n🏗️ Creating Project")
        print("=" * 50)
    
    # Parse team names and get team IDs (teams are required)
    team_names = [name.strip() for name in args.teams.split(",")]
    teams = client.get_teams()
    team_ids = []
    
    for team_name in team_names:
        team = next((t for t in teams if t["name"] == team_name), None)
        if not team:
            print(f"❌ Error: Team '{team_name}' not found.")
            print("\nAvailable teams:")
            for i, t in enumerate(teams, 1):
                print(f"  {i}. {t['name']}")
            sys.exit(1)
        team_ids.append(team["id"])
    
    # Get lead user ID if specified
    lead_id = None
    if args.lead:
        user = client.find_user_by_email_or_name(args.lead)
        if not user:
            print(f"❌ Error: User '{args.lead}' not found.")
            print("\nAvailable users:")
            users = client.get_team_members()
            for i, u in enumerate(users[:10], 1):  # Show first 10
                print(f"  {i}. {u.get('displayName', u.get('name', ''))} ({u.get('email', '')})")
            sys.exit(1)
        lead_id = user["id"]
    
    # Create project with provided arguments
    result = client.create_project(
        name=args.name,
        description=args.description or "",
        team_ids=team_ids,
        lead_id=lead_id,
        target_date=args.target_date,
        state=args.state
    )
    
    if not result:
        print("❌ Error: Failed to create project. Please check your parameters and try again.")
        sys.exit(1)
    
    # If --id-only flag is set, just print the project ID
    if args.id_only:
        print(result['id'])
        return result
    
    # Display success message and project details
    print(f"✅ Successfully created project: {result['name']}")
    print(f"🆔 Project ID: {result['id']}")
    
    # Show additional details
    details = []
    if result.get('teams', {}).get('nodes'):
        team_names = [team['name'] for team in result['teams']['nodes']]
        details.append(f"Teams: {', '.join(team_names)}")
    
    if result.get('lead'):
        lead_name = result['lead'].get('name', result['lead'].get('email', 'Unknown'))
        details.append(f"Lead: {lead_name}")
    
    if result.get('targetDate'):
        details.append(f"Target: {result['targetDate'][:10]}")
    
    if result.get('state'):
        details.append(f"State: {result['state'].title()}")
    
    if details:
        print(" | ".join(details))
    
    if result.get('description'):
        print(f"\n📝 Description: {result['description']}")
    
    if result.get('url'):
        print(f"🔗 Direct link: {result['url']}")
    
    print(f"\n🆔 Project ID: {result['id']}")
    
    return result

def handle_team_creation(args, client: LinearClient):
    """Handle team creation command."""
    if not args.id_only:
        print("\n👥 Creating Team")
        print("=" * 50)
    
    # Validate color format if provided
    if args.color:
        # Remove # if user included it
        color = args.color.lstrip('#')
        if len(color) != 6 or not all(c in '0123456789abcdefABCDEF' for c in color):
            print(f"❌ Error: Invalid color format '{args.color}'. Use 6-character hex code without #.")
            print("Examples: 3b82f6, ef4444, 10b981")
            sys.exit(1)
        args.color = color
    
    # Create team with provided arguments
    result = client.create_team(
        name=args.name,
        description=args.description or "",
        key=args.key,
        icon=args.icon,
        color=args.color
    )
    
    if not result:
        print("❌ Error: Failed to create team. Please check your parameters and try again.")
        sys.exit(1)
    
    # If --id-only flag is set, just print the team ID
    if args.id_only:
        print(result['id'])
        return result
    
    # Display success message and team details
    print(f"✅ Successfully created team: {result['name']}")
    print(f"🆔 Team ID: {result['id']}")
    
    # Show additional details
    details = []
    if result.get('key'):
        details.append(f"🔑 Key: {result['key']}")
    
    if result.get('icon'):
        details.append(f"📍 Icon: {result['icon']}")
    
    if result.get('color'):
        color = result['color'].lstrip('#')  # Remove # if already present
        details.append(f"🎨 Color: #{color}")
    
    if details:
        print(" | ".join(details))
    
    if result.get('description'):
        print(f"\n📝 Description: {result['description']}")
    
    # Show some team configuration info
    config_info = []
    if result.get('private') is not None:
        visibility = "Private" if result['private'] else "Public"
        config_info.append(f"👁️ Visibility: {visibility}")
    
    if result.get('triageEnabled') is not None:
        triage = "Enabled" if result['triageEnabled'] else "Disabled"
        config_info.append(f"📥 Triage: {triage}")
    
    if result.get('issueEstimationType'):
        config_info.append(f"📊 Estimation: {result['issueEstimationType'].title()}")
    
    if config_info:
        print(" | ".join(config_info))
    
    print(f"\n✨ Team '{result['name']}' is ready for use!")
    print(f"🆔 Team ID: {result['id']}")
    
    return result
    """Handle project creation command."""
    if not args.id_only:
        print("\n🏗️ Creating Project")
        print("=" * 50)
    
    # Parse team names and get team IDs (teams are required)
    team_names = [name.strip() for name in args.teams.split(",")]
    teams = client.get_teams()
    team_ids = []
    
    for team_name in team_names:
        team = next((t for t in teams if t["name"] == team_name), None)
        if not team:
            print(f"❌ Error: Team '{team_name}' not found.")
            print("\nAvailable teams:")
            for i, t in enumerate(teams, 1):
                print(f"  {i}. {t['name']}")
            sys.exit(1)
        team_ids.append(team["id"])
    
    # Get lead user ID if specified
    lead_id = None
    if args.lead:
        user = client.find_user_by_email_or_name(args.lead)
        if not user:
            print(f"❌ Error: User '{args.lead}' not found.")
            print("\nAvailable users:")
            users = client.get_team_members()
            for i, u in enumerate(users[:10], 1):  # Show first 10
                print(f"  {i}. {u.get('displayName', u.get('name', ''))} ({u.get('email', '')})")
            sys.exit(1)
        lead_id = user["id"]
    
    # Create project with provided arguments
    result = client.create_project(
        name=args.name,
        description=args.description or "",
        team_ids=team_ids,
        lead_id=lead_id,
        target_date=args.target_date,
        state=args.state
    )
    
    if not result:
        print("❌ Error: Failed to create project. Please check your parameters and try again.")
        sys.exit(1)
    
    # If --id-only flag is set, just print the project ID
    if args.id_only:
        print(result['id'])
        return result
    
    # Display success message and project details
    print(f"✅ Successfully created project: {result['name']}")
    print(f"🆔 Project ID: {result['id']}")
    
    # Show additional details
    details = []
    if result.get('teams', {}).get('nodes'):
        team_names = [team['name'] for team in result['teams']['nodes']]
        details.append(f"Teams: {', '.join(team_names)}")
    
    if result.get('lead'):
        lead_name = result['lead'].get('name', result['lead'].get('email', 'Unknown'))
        details.append(f"Lead: {lead_name}")
    
    if result.get('targetDate'):
        details.append(f"Target: {result['targetDate'][:10]}")
    
    if result.get('state'):
        details.append(f"State: {result['state'].title()}")
    
    if details:
        print(" | ".join(details))
    
    if result.get('description'):
        print(f"\n📝 Description: {result['description']}")
    
    if result.get('url'):
        print(f"🔗 Direct link: {result['url']}")
    
    print(f"\n🆔 Project ID: {result['id']}")
    
    return result


def main():
    """Main CLI function."""
    parser = setup_argparser()
    args = parser.parse_args()
    
    # Check for required API token
    api_token = args.token or os.getenv('LINEAR_API_TOKEN')
    if not api_token:
        print("❌ Error: LINEAR_API_TOKEN environment variable not set.")
        print("\nTo get your Linear API token:")
        print("1. Go to Linear Settings → API → Personal API tokens")
        print("2. Create a new token with appropriate permissions")
        print("3. Export it: export LINEAR_API_TOKEN='your_token_here'")
        sys.exit(1)
    
    try:
        # Initialize client and search engine
        client = LinearClient(api_token)
        search_engine = TicketSearchEngine(client)
        
        # Only print banner if not in quiet mode for commands with --id-only
        show_banner = True
        if hasattr(args, 'command') and args.command in ['add', 'create-project', 'create-team'] and hasattr(args, 'id_only') and args.id_only:
            show_banner = False
        
        if show_banner:
            print_banner()
        
        # Handle subcommands first
        if args.command == "add":
            handle_ticket_creation(args, search_engine)
            return
        
        if args.command == "create-project":
            handle_project_creation(args, client)
            return
        
        if args.command == "create-team":
            handle_team_creation(args, client)
            return
        
        # Handle global utility commands only if no subcommand is specified
        if args.refresh:
            print("\n🔄 Refreshing ticket cache...")
            search_engine.refresh_cache()
            print("✅ Cache refreshed successfully!")
            return
        
        if args.projects:
            print_projects(search_engine)
            return
        
        if args.teams:
            print_teams(search_engine)
            return
        
        if args.states:
            print_states(search_engine)
            return
        
        if args.assignees:
            print_assignees(search_engine)
            return
        
        if args.labels:
            print_labels(search_engine)
            return
        
        # Handle search and update (backward compatibility)
        if not args.query:
            print("\n❌ Error: No query provided.")
            print("Use --help for usage examples, or try 'add --title \"Your Title\"' to create a ticket.")
            sys.exit(1)
        
        # Check if any update arguments are provided (but not if we're in add subcommand)
        update_args = []
        if hasattr(args, 'status') and args.status:
            update_args.append('status')
        if hasattr(args, 'title') and args.title and args.command != 'add':
            update_args.append('title')
        if hasattr(args, 'description') and args.description and args.command != 'add':
            update_args.append('description')
        if hasattr(args, 'priority') and args.priority and args.command != 'add':
            update_args.append('priority')
        if hasattr(args, 'assignee') and args.assignee and args.command != 'add':
            update_args.append('assignee')
        
        is_update = bool(update_args)
        
        if is_update:
            # Handle updates (status, title, description, priority, assignee)
            update_made = False
            
            if 'status' in update_args:
                success = search_engine.change_ticket_status(args.query, args.status)
                update_made = True
                if not success:
                    return
            
            if 'title' in update_args:
                success = search_engine.update_ticket_title(args.query, args.title)
                update_made = True
                if not success:
                    return
            
            if 'description' in update_args:
                success = search_engine.update_ticket_description(args.query, args.description)
                update_made = True
                if not success:
                    return
            
            if 'priority' in update_args:
                success = search_engine.update_ticket_priority(args.query, args.priority)
                update_made = True
                if not success:
                    return
            
            if 'assignee' in update_args:
                success = search_engine.update_ticket_assignee(args.query, args.assignee)
                update_made = True
                if not success:
                    return
            
            if update_made:
                # Show the updated ticket
                print(f"\n🔍 Updated ticket: {args.query}")
                results = search_engine.search_tickets(args.query, limit=1)
                print_search_results(results, search_engine)
                return
        
        # Perform search
        print(f"\n🔍 Searching for: '{args.query}'")
        results = search_engine.search_tickets(args.query, limit=args.limit)
        print_search_results(results, search_engine)
        
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if "LINEAR_API_TOKEN" in str(e):
            print("\nPlease check your Linear API token and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()