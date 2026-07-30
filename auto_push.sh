#!/bin/bash
# BLACK VEIL Auto-Push Script
# Monitors changes and auto-pushes to GitHub

echo "🔁 BLACK VEIL Auto-Push Started"
echo "==============================="

cd /home/eroz/Documents/black_veil

while true; do
    # Check for changes
    if [[ -n $(git status -s) ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Changes detected!"
        
        # Add all changes
        git add .
        
        # Commit with timestamp
        git commit -m "Auto-update: $(date '+%Y-%m-%d %H:%M:%S')"
        
        # Push to GitHub
        git push origin main
        
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Changes pushed to GitHub!"
    fi
    
    # Wait 60 seconds before next check
    sleep 60
done
