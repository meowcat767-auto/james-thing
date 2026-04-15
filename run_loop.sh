#!/bin/bash

# Configuration
AGENT_VENV="./venv/bin/python"
AGENT_SCRIPT="agent.py"

echo "--- Bash Loop for Groq Code Agent ---"
echo "Enter your prompts below. Type 'exit' to quit."

while true; do
    read -p "Bash Loop Prompt: " prompt
    
    if [[ "$prompt" == "exit" ]]; then
        break
    fi
    
    if [[ -z "$prompt" ]]; then
        continue
    fi
    
    echo "Processing..."
    # Call the python agent with the prompt as an argument
    $AGENT_VENV $AGENT_SCRIPT "$prompt"
    echo "------------------------------------"
done

echo "Loop exited."
