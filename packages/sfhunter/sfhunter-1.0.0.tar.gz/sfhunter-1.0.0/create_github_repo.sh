#!/bin/bash

# SFHunter GitHub Repository Creation Script
# This script helps create a private GitHub repository for SFHunter

echo "SFHunter GitHub Repository Setup"
echo "================================"
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    echo "Or create the repository manually on GitHub.com"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "Please authenticate with GitHub CLI first:"
    echo "gh auth login"
    exit 1
fi

echo "Creating private GitHub repository for SFHunter..."
echo ""

# Create the repository
gh repo create sfhunter \
    --private \
    --description "High-performance Salesforce URL scanner with Discord/Telegram integration" \
    --homepage "https://github.com/$(gh api user --jq .login)/sfhunter" \
    --source=. \
    --remote=origin \
    --push

if [ $? -eq 0 ]; then
    echo ""
    echo "Repository created successfully!"
    echo "Repository URL: https://github.com/$(gh api user --jq .login)/sfhunter"
    echo ""
    echo "Next steps:"
    echo "1. Update the repository URL in README.md"
    echo "2. Add any additional documentation"
    echo "3. Create issues and milestones as needed"
else
    echo "Failed to create repository. Please check your GitHub CLI setup."
fi
