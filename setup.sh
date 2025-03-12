#!/bin/bash

# Directory containing this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Environment name and path
ENV_NAME="pdf-env"
ENV_PATH="$SCRIPT_DIR/$ENV_NAME"

# Function to setup/update the environment
setup_env() {
    echo "Setting up Python virtual environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$ENV_PATH" ]; then
        echo "Creating new virtual environment: $ENV_NAME"
        python3 -m venv "$ENV_PATH"
    fi
    
    # Activate virtual environment
    source "$ENV_PATH/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install/upgrade requirements
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        echo "Installing/updating requirements..."
        pip install -r "$SCRIPT_DIR/requirements.txt"
    else
        echo "Warning: requirements.txt not found!"
    fi
    
    echo "Environment setup complete!"
}

# Function to activate the environment
activate_env() {
    if [ -d "$ENV_PATH" ]; then
        source "$ENV_PATH/bin/activate"
        echo "Virtual environment '$ENV_NAME' activated."
        echo "Use 'deactivate' to exit the virtual environment."
    else
        echo "Virtual environment not found. Run setup_env first."
        return 1
    fi
}

# Function to run a command in the virtual environment
run_in_env() {
    if [ -z "$1" ]; then
        echo "Usage: run_in_env <command>"
        return 1
    fi
    
    if [ ! -d "$ENV_PATH" ]; then
        echo "Virtual environment not found. Running setup_env first..."
        setup_env
    fi
    
    source "$ENV_PATH/bin/activate"
    "$@"
    deactivate
}

# If script is sourced, make functions available
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    export -f setup_env
    export -f activate_env
    export -f run_in_env
else
    # If script is run directly, show usage
    echo "This script provides the following functions:"
    echo "  setup_env      - Create/update the virtual environment"
    echo "  activate_env   - Activate the virtual environment"
    echo "  run_in_env     - Run a command within the virtual environment"
    echo ""
    echo "To use these functions, source this script:"
    echo "  source setup.sh"
fi 