"""
Ticket search functionality with query parsing and fuzzy matching.
"""
import re
from typing import List, Dict, Optional, Tuple, Any
from fuzzywuzzy import fuzz
from linear_client import LinearClient, LinearTicket


class TicketQuery:
    """Represents a parsed ticket search query."""
    
    def __init__(self, raw_query: str):
        self.raw_query = raw_query
        self.project: Optional[str] = None
        self.epic: Optional[str] = None
        self.ticket: Optional[str] = None
        self.ticket_id: Optional[str] = None
        self.keywords: List[str] = []
        self._parse_query()
    
    def _parse_query(self):
        """Parse the query string to extract components."""
        # Remove extra whitespace and normalize
        query = re.sub(r'\s+', ' ', self.raw_query.strip())
        
        # Check if the entire query looks like a ticket ID (e.g., ZIF-19, ABC-123)
        ticket_id_pattern = r'^[A-Z]{2,}-\d+$'
        if re.match(ticket_id_pattern, query.strip()):
            self.ticket_id = query.strip()
            return
        
        # Extract project
        project_match = re.search(r'project:\s*([^,]+)', query, re.IGNORECASE)
        if project_match:
            self.project = project_match.group(1).strip()
            query = query.replace(project_match.group(0), '').strip()
        
        # Extract epic
        epic_match = re.search(r'epic\s+(\d+(?:\.\d+)?)', query, re.IGNORECASE)
        if epic_match:
            self.epic = epic_match.group(1)
            query = query.replace(epic_match.group(0), '').strip()
        
        # Extract ticket
        ticket_match = re.search(r'ticket\s+(\d+(?:\.\d+)?)', query, re.IGNORECASE)
        if ticket_match:
            self.ticket = ticket_match.group(1)
            query = query.replace(ticket_match.group(0), '').strip()
        
        # Clean up remaining commas and whitespace
        query = re.sub(r'[,\s]+', ' ', query).strip()
        
        # Remaining words are keywords
        if query:
            self.keywords = [word for word in query.split() if word]
    
    def __str__(self):
        parts = []
        if self.ticket_id:
            parts.append(f"Ticket ID: {self.ticket_id}")
        if self.project:
            parts.append(f"Project: {self.project}")
        if self.epic:
            parts.append(f"Epic: {self.epic}")
        if self.ticket:
            parts.append(f"Ticket: {self.ticket}")
        if self.keywords:
            parts.append(f"Keywords: {', '.join(self.keywords)}")
        return " | ".join(parts) if parts else "Empty query"


class TicketSearchEngine:
    """Search engine for Linear tickets with fuzzy matching capabilities."""
    
    def __init__(self, client: LinearClient):
        self.client = client
        self._tickets_cache: List[LinearTicket] = []
        self._projects_cache: List[Dict[str, Any]] = []
    
    def refresh_cache(self):
        """Refresh the local cache of tickets and projects."""
        print("Refreshing ticket cache...")
        self._tickets_cache = self.client.get_all_issues()
        self._projects_cache = self.client.get_projects()
        print(f"Cached {len(self._tickets_cache)} tickets from {len(self._projects_cache)} projects")
    
    def get_projects(self) -> List[str]:
        """Get list of all project names."""
        if not self._projects_cache:
            self._projects_cache = self.client.get_projects()
        return [project['name'] for project in self._projects_cache]
    
    def search_tickets(self, query: str, limit: int = 10) -> List[Tuple[LinearTicket, float]]:
        """
        Search for tickets based on a query string.
        Returns a list of tuples (ticket, relevance_score).
        """
        if not self._tickets_cache:
            self.refresh_cache()
        
        parsed_query = TicketQuery(query)
        print(f"Parsed query: {parsed_query}")
        
        # Fast path for direct ticket ID lookup
        if parsed_query.ticket_id:
            exact_ticket = self.find_exact_ticket(parsed_query.ticket_id)
            if exact_ticket:
                return [(exact_ticket, 10.0)]  # Perfect score for exact match
            else:
                print(f"No ticket found with ID: {parsed_query.ticket_id}")
                return []
        
        # Filter and score tickets
        scored_tickets = []
        
        for ticket in self._tickets_cache:
            score = self._calculate_relevance_score(ticket, parsed_query)
            if score > 0:
                scored_tickets.append((ticket, score))
        
        # Sort by relevance score (descending)
        scored_tickets.sort(key=lambda x: x[1], reverse=True)
        
        return scored_tickets[:limit]
    
    def _calculate_relevance_score(self, ticket: LinearTicket, query: TicketQuery) -> float:
        """Calculate the relevance score of a ticket for the given query."""
        total_score = 0.0
        
        # Project matching (high weight)
        if query.project:
            if ticket.project_name:
                project_score = fuzz.partial_ratio(
                    query.project.lower(), 
                    ticket.project_name.lower()
                ) / 100.0
                total_score += project_score * 3.0
            else:
                # If no project match and project was specified, heavily penalize
                total_score -= 2.0
        
        # Direct ticket ID matching (highest priority)
        if query.ticket_id:
            if ticket.identifier.upper() == query.ticket_id.upper():
                total_score += 10.0  # Perfect match
            elif query.ticket_id.upper() in ticket.identifier.upper():
                total_score += 5.0   # Partial match
        
        # Exact identifier matching (highest weight)
        if query.epic or query.ticket:
            identifier_parts = ticket.identifier.split('-')
            if len(identifier_parts) >= 2:
                try:
                    ticket_number = float(identifier_parts[1])
                    
                    if query.epic:
                        epic_number = float(query.epic)
                        if abs(ticket_number - epic_number) < 0.1:  # Exact epic match
                            total_score += 5.0
                        elif str(int(ticket_number)) == str(int(epic_number)):  # Same integer part
                            total_score += 3.0
                    
                    if query.ticket:
                        ticket_query_number = float(query.ticket)
                        if abs(ticket_number - ticket_query_number) < 0.01:  # Exact ticket match
                            total_score += 5.0
                        elif abs(ticket_number - ticket_query_number) < 1.0:  # Close match
                            total_score += 2.0
                            
                except (ValueError, IndexError):
                    pass
        
        # Keyword matching in title and description
        if query.keywords:
            title_text = ticket.title.lower()
            desc_text = ticket.description.lower() if ticket.description else ""
            
            for keyword in query.keywords:
                keyword_lower = keyword.lower()
                
                # Exact word match in title (high weight)
                if keyword_lower in title_text:
                    total_score += 2.0
                
                # Fuzzy match in title
                title_fuzzy_score = fuzz.partial_ratio(keyword_lower, title_text) / 100.0
                if title_fuzzy_score > 0.6:
                    total_score += title_fuzzy_score * 1.5
                
                # Exact word match in description (medium weight)
                if keyword_lower in desc_text:
                    total_score += 1.0
                
                # Fuzzy match in description
                if desc_text:
                    desc_fuzzy_score = fuzz.partial_ratio(keyword_lower, desc_text) / 100.0
                    if desc_fuzzy_score > 0.6:
                        total_score += desc_fuzzy_score * 0.5
        
        # Boost for active tickets
        if ticket.state.lower() not in ['done', 'canceled', 'closed']:
            total_score += 0.5
        
        return max(0.0, total_score)
    
    def find_exact_ticket(self, identifier: str) -> Optional[LinearTicket]:
        """Find a ticket by exact identifier match."""
        if not self._tickets_cache:
            self.refresh_cache()
        
        for ticket in self._tickets_cache:
            if ticket.identifier.lower() == identifier.lower():
                return ticket
        return None
    
    def get_tickets_by_project(self, project_name: str) -> List[LinearTicket]:
        """Get all tickets from a specific project."""
        if not self._tickets_cache:
            self.refresh_cache()
        
        matching_tickets = []
        for ticket in self._tickets_cache:
            if ticket.project_name and fuzz.partial_ratio(
                project_name.lower(), 
                ticket.project_name.lower()
            ) > 80:
                matching_tickets.append(ticket)
        
        return matching_tickets
    
    def format_ticket_result(self, ticket: LinearTicket, score: float = None, full_description: bool = False) -> str:
        """Format a ticket for display."""
        lines = []
        
        # Header with identifier and title
        header = f"🎫 {ticket.identifier}: {ticket.title}"
        if score is not None:
            header += f" (Score: {score:.2f})"
        lines.append(header)
        
        # Project and team info
        info_parts = []
        if ticket.project_name:
            info_parts.append(f"Project: {ticket.project_name}")
        if ticket.team_name:
            info_parts.append(f"Team: {ticket.team_name}")
        if info_parts:
            lines.append("   " + " | ".join(info_parts))
        
        # State and assignee
        status_parts = []
        status_parts.append(f"State: {ticket.state}")
        if ticket.assignee:
            status_parts.append(f"Assignee: {ticket.assignee}")
        lines.append("   " + " | ".join(status_parts))
        
        # Parent ticket context
        if ticket.parent_title:
            lines.append(f"   🔺 Parent: {ticket.parent_title}")
            if ticket.parent_description:
                parent_desc_lines = ticket.parent_description.split('\n')
                for desc_line in parent_desc_lines:
                    if desc_line.strip():
                        lines.append(f"      {desc_line.strip()}")
        
        # Project context
        if ticket.project_description:
            lines.append(f"   📋 Project Context:")
            project_desc_lines = ticket.project_description.split('\n')
            for desc_line in project_desc_lines:
                if desc_line.strip():
                    lines.append(f"      {desc_line.strip()}")
        
        # Ticket description (always full)
        if ticket.description:
            desc_lines = ticket.description.split('\n')
            lines.append("   📝 Description:")
            for desc_line in desc_lines:
                if desc_line.strip():
                    lines.append(f"      {desc_line.strip()}")
        
        # URL
        if ticket.url:
            lines.append(f"   🔗 {ticket.url}")
        
        return "\n".join(lines)
    
    def get_available_states(self) -> List[Dict[str, Any]]:
        """Get all available workflow states."""
        return self.client.get_workflow_states()
    
    def get_child_tickets(self, parent_ticket_id: str) -> List[LinearTicket]:
        """Get all child tickets for a given parent ticket."""
        # First find the parent ticket to get its internal ID
        parent_ticket = self.find_exact_ticket(parent_ticket_id)
        if not parent_ticket:
            print(f"❌ Parent ticket {parent_ticket_id} not found")
            return []
        
        try:
            child_tickets = self.client.get_child_issues(parent_ticket.id)
            return child_tickets
        except Exception as e:
            print(f"❌ Error fetching child tickets for {parent_ticket_id}: {str(e)}")
            return []
    
    def change_ticket_status(self, ticket_id: str, new_status: str) -> bool:
        """Change a ticket's status by name."""
        # Find the ticket first
        ticket = self.find_exact_ticket(ticket_id)
        if not ticket:
            print(f"❌ Ticket {ticket_id} not found")
            return False
        
        # Get available states
        states = self.get_available_states()
        
        # Find the state ID by name (case insensitive)
        target_state_id = None
        available_states = []
        
        for state in states:
            available_states.append(state['name'])
            if state['name'].lower() == new_status.lower():
                target_state_id = state['id']
                break
        
        if not target_state_id:
            print(f"❌ Status '{new_status}' not found")
            print(f"Available statuses: {', '.join(available_states)}")
            return False
        
        # Update the ticket
        try:
            success = self.client.update_issue_state(ticket.id, target_state_id)
            if success:
                print(f"✅ Updated {ticket_id} status to '{new_status}'")
                # Refresh cache to show updated status
                self.refresh_cache()
                return True
            else:
                print(f"❌ Failed to update {ticket_id} status")
                return False
        except Exception as e:
            print(f"❌ Error updating {ticket_id}: {str(e)}")
            return False
    
    def update_ticket_title(self, ticket_id: str, new_title: str) -> bool:
        """Update a ticket's title."""
        ticket = self.find_exact_ticket(ticket_id)
        if not ticket:
            print(f"❌ Ticket {ticket_id} not found")
            return False
        
        try:
            success = self.client.update_issue_title(ticket.id, new_title)
            if success:
                print(f"✅ Updated {ticket_id} title to: '{new_title}'")
                self.refresh_cache()
                return True
            else:
                print(f"❌ Failed to update {ticket_id} title")
                return False
        except Exception as e:
            print(f"❌ Error updating {ticket_id}: {str(e)}")
            return False
    
    def update_ticket_description(self, ticket_id: str, new_description: str) -> bool:
        """Update a ticket's description."""
        ticket = self.find_exact_ticket(ticket_id)
        if not ticket:
            print(f"❌ Ticket {ticket_id} not found")
            return False
        
        try:
            success = self.client.update_issue_description(ticket.id, new_description)
            if success:
                print(f"✅ Updated {ticket_id} description")
                self.refresh_cache()
                return True
            else:
                print(f"❌ Failed to update {ticket_id} description")
                return False
        except Exception as e:
            print(f"❌ Error updating {ticket_id}: {str(e)}")
            return False
    
    def update_ticket_priority(self, ticket_id: str, priority: str) -> bool:
        """Update a ticket's priority. Accepts: urgent, high, normal, low or 1, 2, 3, 4."""
        ticket = self.find_exact_ticket(ticket_id)
        if not ticket:
            print(f"❌ Ticket {ticket_id} not found")
            return False
        
        # Convert priority string to number
        priority_map = {
            'urgent': 1, '1': 1,
            'high': 2, '2': 2,
            'normal': 3, '3': 3, 'medium': 3,
            'low': 4, '4': 4
        }
        
        priority_lower = priority.lower()
        if priority_lower not in priority_map:
            print(f"❌ Invalid priority '{priority}'")
            print("Valid priorities: urgent (1), high (2), normal/medium (3), low (4)")
            return False
        
        priority_num = priority_map[priority_lower]
        priority_names = {1: 'Urgent', 2: 'High', 3: 'Normal', 4: 'Low'}
        
        try:
            success = self.client.update_issue_priority(ticket.id, priority_num)
            if success:
                print(f"✅ Updated {ticket_id} priority to {priority_names[priority_num]}")
                self.refresh_cache()
                return True
            else:
                print(f"❌ Failed to update {ticket_id} priority")
                return False
        except Exception as e:
            print(f"❌ Error updating {ticket_id}: {str(e)}")
            return False
    
    def update_ticket_assignee(self, ticket_id: str, assignee: str) -> bool:
        """Update a ticket's assignee. Use 'none' or 'unassign' to remove assignee."""
        ticket = self.find_exact_ticket(ticket_id)
        if not ticket:
            print(f"❌ Ticket {ticket_id} not found")
            return False
        
        # Handle unassignment
        if assignee.lower() in ['none', 'unassign', 'null', '']:
            try:
                success = self.client.update_issue_assignee(ticket.id, None)
                if success:
                    print(f"✅ Unassigned {ticket_id}")
                    self.refresh_cache()
                    return True
                else:
                    print(f"❌ Failed to unassign {ticket_id}")
                    return False
            except Exception as e:
                print(f"❌ Error updating {ticket_id}: {str(e)}")
                return False
        
        # Find user by email or name
        user = self.client.find_user_by_email_or_name(assignee)
        if not user:
            print(f"❌ User '{assignee}' not found")
            print("Try using their email address or exact display name")
            return False
        
        try:
            success = self.client.update_issue_assignee(ticket.id, user['id'])
            if success:
                user_name = user.get('displayName') or user.get('name') or user.get('email')
                print(f"✅ Assigned {ticket_id} to {user_name}")
                self.refresh_cache()
                return True
            else:
                print(f"❌ Failed to assign {ticket_id}")
                return False
        except Exception as e:
            print(f"❌ Error updating {ticket_id}: {str(e)}")
            return False
    
    def update_ticket_multiple(self, ticket_id: str, updates: dict) -> bool:
        """Update multiple fields of a ticket at once."""
        ticket = self.find_exact_ticket(ticket_id)
        if not ticket:
            print(f"❌ Ticket {ticket_id} not found")
            return False
        
        # Process updates to convert to Linear API format
        api_updates = {}
        update_descriptions = []
        
        if 'title' in updates:
            api_updates['title'] = updates['title']
            update_descriptions.append(f"title to '{updates['title']}'")
        
        if 'description' in updates:
            api_updates['description'] = updates['description']
            update_descriptions.append("description")
        
        if 'priority' in updates:
            priority_map = {
                'urgent': 1, '1': 1,
                'high': 2, '2': 2,
                'normal': 3, '3': 3, 'medium': 3,
                'low': 4, '4': 4
            }
            priority_lower = str(updates['priority']).lower()
            if priority_lower in priority_map:
                api_updates['priority'] = priority_map[priority_lower]
                priority_names = {1: 'Urgent', 2: 'High', 3: 'Normal', 4: 'Low'}
                update_descriptions.append(f"priority to {priority_names[priority_map[priority_lower]]}")
            else:
                print(f"❌ Invalid priority '{updates['priority']}'")
                return False
        
        if 'status' in updates:
            states = self.get_available_states()
            target_state_id = None
            for state in states:
                if state['name'].lower() == updates['status'].lower():
                    target_state_id = state['id']
                    break
            if target_state_id:
                api_updates['stateId'] = target_state_id
                update_descriptions.append(f"status to '{updates['status']}'")
            else:
                print(f"❌ Invalid status '{updates['status']}'")
                return False
        
        if 'assignee' in updates:
            assignee = updates['assignee']
            if assignee.lower() in ['none', 'unassign', 'null', '']:
                api_updates['assigneeId'] = None
                update_descriptions.append("assignee (unassigned)")
            else:
                user = self.client.find_user_by_email_or_name(assignee)
                if user:
                    api_updates['assigneeId'] = user['id']
                    user_name = user.get('displayName') or user.get('name') or user.get('email')
                    update_descriptions.append(f"assignee to {user_name}")
                else:
                    print(f"❌ User '{assignee}' not found")
                    return False
        
        if not api_updates:
            print("❌ No valid updates provided")
            return False
        
        try:
            success = self.client.update_multiple_fields(ticket.id, api_updates)
            if success:
                print(f"✅ Updated {ticket_id}: {', '.join(update_descriptions)}")
                self.refresh_cache()
                return True
            else:
                print(f"❌ Failed to update {ticket_id}")
                return False
        except Exception as e:
            print(f"❌ Error updating {ticket_id}: {str(e)}")
            return False
    
    def get_available_assignees(self) -> List[Dict[str, Any]]:
        """Get list of available users for assignment."""
        try:
            return self.client.get_team_members()
        except Exception as e:
            print(f"❌ Error fetching team members: {str(e)}")
            return []
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get list of all teams."""
        try:
            return self.client.get_teams()
        except Exception as e:
            print(f"❌ Error fetching teams: {str(e)}")
            return []
    
    def get_labels(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of labels, optionally filtered by team."""
        try:
            return self.client.get_labels(team_id)
        except Exception as e:
            print(f"❌ Error fetching labels: {str(e)}")
            return []
    
    def create_ticket(self, title: str, description: str = "", team_name: Optional[str] = None, 
                     project_name: Optional[str] = None, parent_identifier: Optional[str] = None,
                     assignee_identifier: Optional[str] = None, priority: str = "normal", 
                     label_names: Optional[List[str]] = None, quiet_mode: bool = False) -> Optional[Dict[str, Any]]:
        """Create a new ticket with user-friendly parameters.
        
        Args:
            title: Ticket title (required)
            description: Ticket description
            team_name: Team name to create the ticket in
            project_name: Project name to assign the ticket to
            parent_identifier: Parent ticket identifier (e.g., 'ZIF-19')
            assignee_identifier: User email or name to assign the ticket to
            priority: Priority level (urgent, high, normal, low)
            label_names: List of label names to apply
            quiet_mode: If True, suppress all output except errors
            
        Returns:
            Dict containing the created ticket data or None if failed
        """
        # Convert priority string to number
        priority_map = {
            'urgent': 1, '1': 1,
            'high': 2, '2': 2,
            'normal': 3, '3': 3, 'medium': 3,
            'low': 4, '4': 4
        }
        
        priority_lower = priority.lower()
        if priority_lower not in priority_map:
            if not quiet_mode:
                print(f"❌ Invalid priority '{priority}'")
                print("Valid priorities: urgent (1), high (2), normal/medium (3), low (4)")
            return None
        
        priority_num = priority_map[priority_lower]
        
        # Resolve team ID
        team_id = None
        if team_name:
            teams = self.get_teams()
            for team in teams:
                if team['name'].lower() == team_name.lower():
                    team_id = team['id']
                    break
            if not team_id:
                if not quiet_mode:
                    print(f"❌ Team '{team_name}' not found")
                    available_teams = [team['name'] for team in teams]
                    print(f"Available teams: {', '.join(available_teams)}")
                return None
        
        # Resolve project ID
        project_id = None
        if project_name:
            projects = self.client.get_projects()
            for project in projects:
                if project['name'].lower() == project_name.lower():
                    project_id = project['id']
                    break
            if not project_id:
                if not quiet_mode:
                    print(f"❌ Project '{project_name}' not found")
                    available_projects = [project['name'] for project in projects]
                    print(f"Available projects: {', '.join(available_projects)}")
                return None
        
        # Resolve parent ID
        parent_id = None
        if parent_identifier:
            parent_ticket = self.find_exact_ticket(parent_identifier)
            if parent_ticket:
                parent_id = parent_ticket.id
            else:
                if not quiet_mode:
                    print(f"❌ Parent ticket '{parent_identifier}' not found")
                return None
        
        # Resolve assignee ID
        assignee_id = None
        if assignee_identifier and assignee_identifier.lower() not in ['none', 'unassign', 'null', '']:
            user = self.client.find_user_by_email_or_name(assignee_identifier)
            if user:
                assignee_id = user['id']
            else:
                if not quiet_mode:
                    print(f"❌ User '{assignee_identifier}' not found")
                    print("Try using their email address or exact display name")
                return None
        
        # Resolve label IDs
        label_ids = None
        if label_names:
            labels = self.get_labels(team_id)
            resolved_labels = []
            
            for label_name in label_names:
                label_found = False
                for label in labels:
                    if label['name'].lower() == label_name.lower():
                        resolved_labels.append(label['id'])
                        label_found = True
                        break
                
                if not label_found:
                    if not quiet_mode:
                        print(f"❌ Label '{label_name}' not found")
                        if team_id:
                            available_labels = [label['name'] for label in labels]
                            print(f"Available labels for team: {', '.join(available_labels)}")
                    return None
            
            label_ids = resolved_labels if resolved_labels else None
        
        try:
            created_issue = self.client.create_issue(
                title=title,
                description=description,
                team_id=team_id,
                project_id=project_id,
                parent_id=parent_id,
                assignee_id=assignee_id,
                priority=priority_num,
                label_ids=label_ids
            )
            
            if created_issue:
                if not quiet_mode:
                    # Display ticket ID prominently
                    ticket_id = created_issue['identifier']
                    print(f"✅ Successfully created ticket: {ticket_id}")
                    print(f"📋 Title: {created_issue['title']}")
                    
                    # Print ticket details
                    details = []
                    team_info = created_issue.get('team')
                    if team_info and team_info.get('name'):
                        details.append(f"Team: {team_info['name']}")
                    
                    project_info = created_issue.get('project')
                    if project_info and project_info.get('name'):
                        details.append(f"Project: {project_info['name']}")
                    
                    assignee_info = created_issue.get('assignee')
                    if assignee_info and assignee_info.get('name'):
                        details.append(f"Assignee: {assignee_info['name']}")
                    
                    parent_info = created_issue.get('parent')
                    if parent_info and parent_info.get('identifier'):
                        details.append(f"Parent: {parent_info['identifier']}")
                    
                    priority_names = {1: 'Urgent', 2: 'High', 3: 'Normal', 4: 'Low'}
                    details.append(f"Priority: {priority_names.get(created_issue.get('priority', 3), 'Normal')}")
                    
                    labels_info = created_issue.get('labels')
                    if labels_info and labels_info.get('nodes'):
                        label_names = [label['name'] for label in labels_info['nodes'] if label and label.get('name')]
                        if label_names:
                            details.append(f"Labels: {', '.join(label_names)}")
                    
                    if details:
                        print(f"   {' | '.join(details)}")
                    
                    if created_issue.get('url'):
                        print(f"🔗 Direct link: {created_issue['url']}")
                    
                    # Print ticket ID again for easy copying
                    print(f"\n🎫 Ticket ID: {ticket_id}")
                
                # Refresh cache to include the new ticket
                self.refresh_cache()
                
                return created_issue
            else:
                if not quiet_mode:
                    print("❌ Failed to create ticket")
                return None
                
        except Exception as e:
            if not quiet_mode:
                print(f"❌ Error creating ticket: {str(e)}")
            return None
