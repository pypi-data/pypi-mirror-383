#!/bin/bash

# Linear Ticket Manager CLI - Setup Script
# Installs dependencies and sets up the 'linear' command alias

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHELL_PROFILE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🎫 Linear Ticket Manager CLI - Setup${NC}"
    echo -e "${BLUE}=====================================
${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Detect shell and profile file
detect_shell() {
    if [[ $SHELL == *"zsh"* ]]; then
        SHELL_PROFILE="$HOME/.zshrc"
    elif [[ $SHELL == *"bash"* ]]; then
        SHELL_PROFILE="$HOME/.bashrc"
    elif [[ -f "$HOME/.bash_profile" ]]; then
        SHELL_PROFILE="$HOME/.bash_profile"
    else
        SHELL_PROFILE="$HOME/.profile"
        print_warning "Using fallback profile: ~/.profile"
    fi
    echo "Shell profile: $SHELL_PROFILE"
}

# Check Python version
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Found Python $PYTHON_VERSION"
}

# Install Python dependencies
install_dependencies() {
    echo "Installing Python dependencies..."
    
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$SCRIPT_DIR/venv"
    fi
    
    source "$SCRIPT_DIR/venv/bin/activate"
    pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
    
    print_success "Dependencies installed"
}

# Set up shell alias
setup_alias() {
    local alias_cmd="alias linear='cd $SCRIPT_DIR && source venv/bin/activate && python linear_search.py'"
    
    # Check if alias already exists
    if grep -q "alias linear=" "$SHELL_PROFILE" 2>/dev/null; then
        print_warning "Alias 'linear' already exists in $SHELL_PROFILE"
        echo "Please check and update manually if needed."
        return
    fi
    
    # Add alias to shell profile
    {
        echo ""
        echo "# Linear Ticket Manager CLI"
        echo "$alias_cmd"
        echo ""
    } >> "$SHELL_PROFILE"
    
    print_success "Added 'linear' alias to $SHELL_PROFILE"
}

# Display usage instructions
show_usage() {
    echo ""
    echo -e "${BLUE}🚀 Setup Complete! Usage Examples:${NC}"
    echo ""
    echo "First, restart your terminal or run: source $SHELL_PROFILE"
    echo ""
    echo -e "${YELLOW}# 1. Set your Linear API token (REQUIRED)${NC}"
    echo "export LINEAR_API_TOKEN='your_token_here'"
    echo ""
    echo -e "${YELLOW}# 2. List available resources${NC}"
    echo "linear --teams      # See all teams"
    echo "linear --projects   # See all projects"
    echo "linear --assignees  # See all users"
    echo ""
    echo -e "${YELLOW}# 3. Create tickets${NC}"
    echo "linear add --title 'Fix authentication bug' --team 'Backend'"
    echo "linear add --title 'New feature' --team 'Frontend' --id-only"
    echo ""
    echo -e "${YELLOW}# 4. Search tickets${NC}"
    echo "linear 'ZIF-19'"
    echo "linear 'project: Issues, Epic 1'"
    echo ""
    echo -e "${YELLOW}# 5. Update tickets${NC}"
    echo "linear 'ZIF-19' --status 'Done'"
    echo "linear 'ZIF-19' --assignee 'user@company.com'"
    echo ""
    echo -e "${GREEN}For detailed help: linear --help${NC}"
    echo -e "${GREEN}For ticket creation help: linear add --help${NC}"
}

# Main setup process
main() {
    print_header
    
    echo "Setting up Linear Ticket Manager CLI..."
    echo "Installation directory: $SCRIPT_DIR"
    echo ""
    
    detect_shell
    check_python
    install_dependencies
    setup_alias
    show_usage
    
    echo ""
    print_success "Setup completed successfully!"
    echo -e "${BLUE}Don't forget to set your LINEAR_API_TOKEN environment variable!${NC}"
}

# Run main function
main
