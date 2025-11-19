#!/bin/bash
# Launch Chrome with a specific cyclebot profile for manual login

PROFILE_NAME="${1:-tradingview}"
PROFILE_DIR="$HOME/.config/cyclebot/chrome-profile-$PROFILE_NAME"

# Create profile directory if it doesn't exist
mkdir -p "$PROFILE_DIR"

echo "Launching Chrome with profile: $PROFILE_NAME"
echo "Profile directory: $PROFILE_DIR"
echo ""
echo "Use this to manually log in to websites."
echo "The script will reuse this profile and stay logged in."
echo ""

# Launch Chrome with the profile
# Use basic password store to avoid keyring encryption issues with Playwright
google-chrome --user-data-dir="$PROFILE_DIR" --password-store=basic "$@"
