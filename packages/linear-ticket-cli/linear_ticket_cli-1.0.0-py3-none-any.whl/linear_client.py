"""
Linear API client for fetching tickets and projects.
"""
import os
import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LinearTicket:
    """Represents a Linear ticket/issue."""
    id: str
    identifier: str
    title: str
    description: str
    state: str
    priority: int
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    team_name: Optional[str] = None
    assignee: Optional[str] = None
    parent_id: Optional[str] = None
    parent_title: Optional[str] = None
    parent_description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    url: Optional[str] = None


class LinearClient:
    """Client for interacting with Linear's GraphQL API."""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize the Linear client."""
        self.api_token = api_token or os.getenv('LINEAR_API_TOKEN')
        if not self.api_token:
            raise ValueError("LINEAR_API_TOKEN environment variable must be set or passed as parameter")
        
        self.api_url = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
        }
    
    def _make_request(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GraphQL request to Linear API."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(self.api_url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        
        return data["data"]
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Fetch all projects from Linear."""
        query = """
        query {
            projects {
                nodes {
                    id
                    name
                    description
                    state
                    teams {
                        nodes {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        
        result = self._make_request(query)
        return result["projects"]["nodes"]
    
    def get_issues_by_project(self, project_name: str, limit: int = 100) -> List[LinearTicket]:
        """Fetch all issues from a specific project."""
        query = """
        query($projectName: String!, $first: Int!) {
            issues(
                filter: { project: { name: { eq: $projectName } } }
                first: $first
            ) {
                nodes {
                    id
                    identifier
                    title
                    description
                    state {
                        name
                    }
                    priority
                    project {
                        name
                        description
                    }
                    team {
                        name
                    }
                    assignee {
                        name
                        email
                    }
                    parent {
                        id
                        title
                        description
                    }
                    createdAt
                    updatedAt
                    url
                }
            }
        }
        """
        
        variables = {"projectName": project_name, "first": limit}
        result = self._make_request(query, variables)
        
        tickets = []
        for issue in result["issues"]["nodes"]:
            ticket = LinearTicket(
                id=issue["id"],
                identifier=issue["identifier"],
                title=issue["title"],
                description=issue.get("description", ""),
                state=issue["state"]["name"],
                priority=issue.get("priority", 0),
                project_name=issue["project"]["name"] if issue.get("project") else None,
                project_description=issue["project"]["description"] if issue.get("project") else None,
                team_name=issue["team"]["name"] if issue.get("team") else None,
                assignee=issue["assignee"]["name"] if issue.get("assignee") else None,
                parent_id=issue["parent"]["id"] if issue.get("parent") else None,
                parent_title=issue["parent"]["title"] if issue.get("parent") else None,
                parent_description=issue["parent"]["description"] if issue.get("parent") else None,
                created_at=issue.get("createdAt"),
                updated_at=issue.get("updatedAt"),
                url=issue.get("url")
            )
            tickets.append(ticket)
        
        return tickets
    
    def get_all_issues(self, limit: int = 250) -> List[LinearTicket]:
        """Fetch all issues from all projects."""
        query = """
        query($first: Int!) {
            issues(first: $first) {
                nodes {
                    id
                    identifier
                    title
                    description
                    state {
                        name
                    }
                    priority
                    project {
                        name
                        description
                    }
                    team {
                        name
                    }
                    assignee {
                        name
                        email
                    }
                    parent {
                        id
                        title
                        description
                    }
                    createdAt
                    updatedAt
                    url
                }
            }
        }
        """
        
        variables = {"first": limit}
        result = self._make_request(query, variables)
        
        tickets = []
        for issue in result["issues"]["nodes"]:
            ticket = LinearTicket(
                id=issue["id"],
                identifier=issue["identifier"],
                title=issue["title"],
                description=issue.get("description", ""),
                state=issue["state"]["name"],
                priority=issue.get("priority", 0),
                project_name=issue["project"]["name"] if issue.get("project") else None,
                project_description=issue["project"]["description"] if issue.get("project") else None,
                team_name=issue["team"]["name"] if issue.get("team") else None,
                assignee=issue["assignee"]["name"] if issue.get("assignee") else None,
                parent_id=issue["parent"]["id"] if issue.get("parent") else None,
                parent_title=issue["parent"]["title"] if issue.get("parent") else None,
                parent_description=issue["parent"]["description"] if issue.get("parent") else None,
                created_at=issue.get("createdAt"),
                updated_at=issue.get("updatedAt"),
                url=issue.get("url")
            )
            tickets.append(ticket)
        
        return tickets
    
    def search_issues(self, query: str, limit: int = 50) -> List[LinearTicket]:
        """Search issues by title, description, or identifier."""
        graphql_query = """
        query($query: String!, $first: Int!) {
            issueSearch(query: $query, first: $first) {
                nodes {
                    id
                    identifier
                    title
                    description
                    state {
                        name
                    }
                    priority
                    project {
                        name
                        description
                    }
                    team {
                        name
                    }
                    assignee {
                        name
                        email
                    }
                    parent {
                        id
                        title
                        description
                    }
                    createdAt
                    updatedAt
                    url
                }
            }
        }
        """
        
        variables = {"query": query, "first": limit}
        result = self._make_request(graphql_query, variables)
        
        tickets = []
        for issue in result["issueSearch"]["nodes"]:
            ticket = LinearTicket(
                id=issue["id"],
                identifier=issue["identifier"],
                title=issue["title"],
                description=issue.get("description", ""),
                state=issue["state"]["name"],
                priority=issue.get("priority", 0),
                project_name=issue["project"]["name"] if issue.get("project") else None,
                project_description=issue["project"]["description"] if issue.get("project") else None,
                team_name=issue["team"]["name"] if issue.get("team") else None,
                assignee=issue["assignee"]["name"] if issue.get("assignee") else None,
                parent_id=issue["parent"]["id"] if issue.get("parent") else None,
                parent_title=issue["parent"]["title"] if issue.get("parent") else None,
                parent_description=issue["parent"]["description"] if issue.get("parent") else None,
                created_at=issue.get("createdAt"),
                updated_at=issue.get("updatedAt"),
                url=issue.get("url")
            )
            tickets.append(ticket)
        
        return tickets
    
    def get_workflow_states(self, team_id: str = None) -> List[Dict[str, Any]]:
        """Get all workflow states (statuses) available."""
        query = """
        query {
            workflowStates {
                nodes {
                    id
                    name
                    type
                    team {
                        id
                        name
                    }
                }
            }
        }
        """
        
        result = self._make_request(query)
        return result["workflowStates"]["nodes"]
    
    def get_child_issues(self, parent_issue_id: str, limit: int = 50) -> List[LinearTicket]:
        """Get all child issues for a given parent issue."""
        query = """
        query($parentId: String!, $first: Int!) {
            issues(
                filter: { parent: { id: { eq: $parentId } } }
                first: $first
            ) {
                nodes {
                    id
                    identifier
                    title
                    description
                    state {
                        name
                    }
                    priority
                    project {
                        name
                        description
                    }
                    team {
                        name
                    }
                    assignee {
                        name
                        email
                    }
                    parent {
                        id
                        title
                        description
                    }
                    createdAt
                    updatedAt
                    url
                }
            }
        }
        """
        
        variables = {"parentId": parent_issue_id, "first": limit}
        result = self._make_request(query, variables)
        
        tickets = []
        for issue in result["issues"]["nodes"]:
            ticket = LinearTicket(
                id=issue["id"],
                identifier=issue["identifier"],
                title=issue["title"],
                description=issue.get("description", ""),
                state=issue["state"]["name"],
                priority=issue.get("priority", 0),
                project_name=issue["project"]["name"] if issue.get("project") else None,
                project_description=issue["project"]["description"] if issue.get("project") else None,
                team_name=issue["team"]["name"] if issue.get("team") else None,
                assignee=issue["assignee"]["name"] if issue.get("assignee") else None,
                parent_id=issue["parent"]["id"] if issue.get("parent") else None,
                parent_title=issue["parent"]["title"] if issue.get("parent") else None,
                parent_description=issue["parent"]["description"] if issue.get("parent") else None,
                created_at=issue.get("createdAt"),
                updated_at=issue.get("updatedAt"),
                url=issue.get("url")
            )
            tickets.append(ticket)
        
        return tickets
    
    def update_issue_state(self, issue_id: str, state_id: str) -> bool:
        """Update an issue's state/status."""
        mutation = """
        mutation($issueId: String!, $stateId: String!) {
            issueUpdate(id: $issueId, input: { stateId: $stateId }) {
                success
                issue {
                    id
                    identifier
                    state {
                        name
                    }
                }
            }
        }
        """
        
        variables = {"issueId": issue_id, "stateId": state_id}
        result = self._make_request(mutation, variables)
        
        return result["issueUpdate"]["success"]
    
    def update_issue_title(self, issue_id: str, title: str) -> bool:
        """Update an issue's title."""
        mutation = """
        mutation($issueId: String!, $title: String!) {
            issueUpdate(id: $issueId, input: { title: $title }) {
                success
                issue {
                    id
                    identifier
                    title
                }
            }
        }
        """
        
        variables = {"issueId": issue_id, "title": title}
        result = self._make_request(mutation, variables)
        
        return result["issueUpdate"]["success"]
    
    def update_issue_description(self, issue_id: str, description: str) -> bool:
        """Update an issue's description."""
        mutation = """
        mutation($issueId: String!, $description: String!) {
            issueUpdate(id: $issueId, input: { description: $description }) {
                success
                issue {
                    id
                    identifier
                    description
                }
            }
        }
        """
        
        variables = {"issueId": issue_id, "description": description}
        result = self._make_request(mutation, variables)
        
        return result["issueUpdate"]["success"]
    
    def update_issue_priority(self, issue_id: str, priority: int) -> bool:
        """Update an issue's priority (1=Urgent, 2=High, 3=Normal, 4=Low)."""
        mutation = """
        mutation($issueId: String!, $priority: Int!) {
            issueUpdate(id: $issueId, input: { priority: $priority }) {
                success
                issue {
                    id
                    identifier
                    priority
                }
            }
        }
        """
        
        variables = {"issueId": issue_id, "priority": priority}
        result = self._make_request(mutation, variables)
        
        return result["issueUpdate"]["success"]
    
    def update_issue_assignee(self, issue_id: str, assignee_id: Optional[str]) -> bool:
        """Update an issue's assignee. Use None to unassign."""
        mutation = """
        mutation($issueId: String!, $assigneeId: String) {
            issueUpdate(id: $issueId, input: { assigneeId: $assigneeId }) {
                success
                issue {
                    id
                    identifier
                    assignee {
                        name
                        email
                    }
                }
            }
        }
        """
        
        variables = {"issueId": issue_id, "assigneeId": assignee_id}
        result = self._make_request(mutation, variables)
        
        return result["issueUpdate"]["success"]
    
    def get_team_members(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all team members or members of a specific team."""
        if team_id:
            query = """
            query($teamId: String!) {
                team(id: $teamId) {
                    members {
                        nodes {
                            id
                            name
                            email
                            displayName
                        }
                    }
                }
            }
            """
            variables = {"teamId": team_id}
            result = self._make_request(query, variables)
            return result["team"]["members"]["nodes"]
        else:
            query = """
            query {
                users {
                    nodes {
                        id
                        name
                        email
                        displayName
                        active
                    }
                }
            }
            """
            result = self._make_request(query)
            # Filter to active users only
            return [user for user in result["users"]["nodes"] if user.get("active", True)]
    
    def find_user_by_email_or_name(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Find a user by email or name."""
        users = self.get_team_members()
        identifier_lower = identifier.lower()
        
        # Try exact email match first
        for user in users:
            if user.get("email", "").lower() == identifier_lower:
                return user
        
        # Try exact name match
        for user in users:
            if user.get("name", "").lower() == identifier_lower:
                return user
            if user.get("displayName", "").lower() == identifier_lower:
                return user
        
        # Try partial name match
        for user in users:
            if identifier_lower in user.get("name", "").lower():
                return user
            if identifier_lower in user.get("displayName", "").lower():
                return user
        
        return None
    
    def update_multiple_fields(self, issue_id: str, updates: Dict[str, Any]) -> bool:
        """Update multiple fields of an issue in a single mutation."""
        # Build the input object dynamically
        input_fields = []
        variables = {"issueId": issue_id}
        
        if "title" in updates:
            input_fields.append("title: $title")
            variables["title"] = updates["title"]
        
        if "description" in updates:
            input_fields.append("description: $description")
            variables["description"] = updates["description"]
        
        if "priority" in updates:
            input_fields.append("priority: $priority")
            variables["priority"] = updates["priority"]
        
        if "stateId" in updates:
            input_fields.append("stateId: $stateId")
            variables["stateId"] = updates["stateId"]
        
        if "assigneeId" in updates:
            input_fields.append("assigneeId: $assigneeId")
            variables["assigneeId"] = updates["assigneeId"]
        
        if not input_fields:
            return False  # No updates to perform
        
        # Build variable declarations for the mutation
        var_declarations = ["$issueId: String!"]
        if "title" in updates:
            var_declarations.append("$title: String!")
        if "description" in updates:
            var_declarations.append("$description: String!")
        if "priority" in updates:
            var_declarations.append("$priority: Int!")
        if "stateId" in updates:
            var_declarations.append("$stateId: String!")
        if "assigneeId" in updates:
            var_declarations.append("$assigneeId: String")
        
        mutation = f"""
        mutation({', '.join(var_declarations)}) {{
            issueUpdate(id: $issueId, input: {{ {', '.join(input_fields)} }}) {{
                success
                issue {{
                    id
                    identifier
                    title
                    description
                    priority
                    state {{
                        name
                    }}
                    assignee {{
                        name
                        email
                    }}
                }}
            }}
        }}
        """
        
        result = self._make_request(mutation, variables)
        return result["issueUpdate"]["success"]
    
    def create_issue(self, title: str, description: str = "", team_id: Optional[str] = None, 
                    project_id: Optional[str] = None, parent_id: Optional[str] = None,
                    assignee_id: Optional[str] = None, priority: int = 3, 
                    label_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Create a new issue.
        
        Args:
            title: Issue title (required)
            description: Issue description
            team_id: Team ID to create the issue in
            project_id: Project ID to assign the issue to
            parent_id: Parent issue ID for sub-issues
            assignee_id: User ID to assign the issue to
            priority: Priority level (1=Urgent, 2=High, 3=Normal, 4=Low)
            label_ids: List of label IDs to apply
            
        Returns:
            Dict containing the created issue data or None if failed
        """
        # Build the input object dynamically
        input_fields = []
        variables = {"title": title}
        
        input_fields.append("title: $title")
        
        if description:
            input_fields.append("description: $description")
            variables["description"] = description
        
        if team_id:
            input_fields.append("teamId: $teamId")
            variables["teamId"] = team_id
        
        if project_id:
            input_fields.append("projectId: $projectId")
            variables["projectId"] = project_id
        
        if parent_id:
            input_fields.append("parentId: $parentId")
            variables["parentId"] = parent_id
        
        if assignee_id:
            input_fields.append("assigneeId: $assigneeId")
            variables["assigneeId"] = assignee_id
        
        if priority != 3:  # Only set if not default
            input_fields.append("priority: $priority")
            variables["priority"] = priority
        
        if label_ids:
            input_fields.append("labelIds: $labelIds")
            variables["labelIds"] = label_ids
        
        # Build variable declarations for the mutation
        var_declarations = ["$title: String!"]
        if description:
            var_declarations.append("$description: String")
        if team_id:
            var_declarations.append("$teamId: String!")
        if project_id:
            var_declarations.append("$projectId: String")
        if parent_id:
            var_declarations.append("$parentId: String")
        if assignee_id:
            var_declarations.append("$assigneeId: String")
        if priority != 3:
            var_declarations.append("$priority: Int")
        if label_ids:
            var_declarations.append("$labelIds: [String!]")
        
        mutation = f"""
        mutation({', '.join(var_declarations)}) {{
            issueCreate(input: {{ {', '.join(input_fields)} }}) {{
                success
                issue {{
                    id
                    identifier
                    title
                    description
                    state {{
                        name
                    }}
                    priority
                    project {{
                        name
                    }}
                    team {{
                        name
                    }}
                    assignee {{
                        name
                        email
                    }}
                    parent {{
                        id
                        identifier
                        title
                    }}
                    labels {{
                        nodes {{
                            id
                            name
                            color
                        }}
                    }}
                    url
                }}
            }}
        }}
        """
        
        try:
            result = self._make_request(mutation, variables)
            if result["issueCreate"]["success"]:
                return result["issueCreate"]["issue"]
            else:
                return None
        except Exception as e:
            print(f"Error creating issue: {str(e)}")
            return None
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Fetch all teams."""
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                    description
                    states {
                        nodes {
                            id
                            name
                            type
                        }
                    }
                }
            }
        }
        """
        
        result = self._make_request(query)
        return result["teams"]["nodes"]
    
    def get_labels(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch all labels, optionally filtered by team."""
        if team_id:
            query = """
            query($teamId: String!) {
                team(id: $teamId) {
                    labels {
                        nodes {
                            id
                            name
                            color
                            description
                        }
                    }
                }
            }
            """
            variables = {"teamId": team_id}
            result = self._make_request(query, variables)
            return result["team"]["labels"]["nodes"]
        else:
            query = """
            query {
                issueLabels {
                    nodes {
                        id
                        name
                        color
                        description
                        team {
                            id
                            name
                        }
                    }
                }
            }
            """
            result = self._make_request(query)
            return result["issueLabels"]["nodes"]
    
    def create_project(self, name: str, description: str = "", 
                      team_ids: Optional[List[str]] = None, 
                      lead_id: Optional[str] = None,
                      target_date: Optional[str] = None,
                      state: str = "planned") -> Optional[Dict[str, Any]]:
        """Create a new project.
        
        Args:
            name: Project name (required)
            description: Project description
            team_ids: List of team IDs to associate with the project
            lead_id: User ID for the project lead
            target_date: Target completion date in ISO format (YYYY-MM-DD)
            state: Project state ("planned", "started", "completed", "canceled")
            
        Returns:
            Dict containing the created project data or None if failed
        """
        # Build the input object dynamically
        input_fields = []
        variables = {"name": name}
        
        input_fields.append("name: $name")
        
        if description:
            input_fields.append("description: $description")
            variables["description"] = description
        
        if team_ids:
            input_fields.append("teamIds: $teamIds")
            variables["teamIds"] = team_ids
        
        if lead_id:
            input_fields.append("leadId: $leadId")
            variables["leadId"] = lead_id
        
        if target_date:
            input_fields.append("targetDate: $targetDate")
            variables["targetDate"] = target_date
        
        # Note: Linear doesn't support setting state during project creation
        # Projects are created in 'planned' state by default
        
        # Build variable declarations for the mutation
        var_declarations = ["$name: String!"]
        if description:
            var_declarations.append("$description: String")
        if team_ids:
            var_declarations.append("$teamIds: [String!]!")
        if lead_id:
            var_declarations.append("$leadId: String")
        if target_date:
            var_declarations.append("$targetDate: DateTime")
        
        mutation = f"""
        mutation({', '.join(var_declarations)}) {{
            projectCreate(input: {{ {', '.join(input_fields)} }}) {{
                success
                project {{
                    id
                    name
                    description
                    state
                    url
                    teams {{
                        nodes {{
                            id
                            name
                        }}
                    }}
                    lead {{
                        id
                        name
                        email
                    }}
                    targetDate
                    createdAt
                }}
            }}
        }}
        """
        
        try:
            result = self._make_request(mutation, variables)
            if result["projectCreate"]["success"]:
                return result["projectCreate"]["project"]
            else:
                return None
        except Exception as e:
            print(f"Error creating project: {str(e)}")
            return None
    
    def create_team(self, name: str, description: str = "", 
                   key: Optional[str] = None, 
                   icon: Optional[str] = None,
                   color: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new team.
        
        Args:
            name: Team name (required)
            description: Team description
            key: Team key/identifier (auto-generated if not provided)
            icon: Team icon (emoji or icon name)
            color: Team color (hex color code without #)
            
        Returns:
            Dict containing the created team data or None if failed
        """
        # Build the input object dynamically
        input_fields = []
        variables = {"name": name}
        
        input_fields.append("name: $name")
        
        if description:
            input_fields.append("description: $description")
            variables["description"] = description
        
        if key:
            input_fields.append("key: $key")
            variables["key"] = key
        
        if icon:
            input_fields.append("icon: $icon")
            variables["icon"] = icon
        
        if color:
            input_fields.append("color: $color")
            variables["color"] = color
        
        # Build variable declarations for the mutation
        var_declarations = ["$name: String!"]
        if description:
            var_declarations.append("$description: String")
        if key:
            var_declarations.append("$key: String")
        if icon:
            var_declarations.append("$icon: String")
        if color:
            var_declarations.append("$color: String")
        
        mutation = f"""
        mutation({', '.join(var_declarations)}) {{
            teamCreate(input: {{ {', '.join(input_fields)} }}) {{
                success
                team {{
                    id
                    name
                    key
                    description
                    icon
                    color
                    private
                    autoArchivePeriod
                    autoCloseStateId
                    defaultIssueEstimate
                    defaultTemplateForMembersId
                    defaultTemplateForNonMembersId
                    draftWorkflowState {{
                        id
                        name
                    }}
                    issueEstimationAllowZero
                    issueEstimationExtended
                    issueEstimationType
                    issueOrderingNoPriorityFirst
                    issueSortOrderDefaultToBottom
                    markedAsDuplicateWorkflowState {{
                        id
                        name
                    }}
                    requirePriorityToLeaveTriage
                    triageEnabled
                    upcomingCycleCount
                    createdAt
                }}
            }}
        }}
        """
        
        try:
            result = self._make_request(mutation, variables)
            if result["teamCreate"]["success"]:
                return result["teamCreate"]["team"]
            else:
                return None
        except Exception as e:
            print(f"Error creating team: {str(e)}")
            return None
    
