#!/bin/bash
# Checkpoint - push both repos to GitHub

MAIN_BRANCH="main"
AGENT_BRANCH="master"

echo "=== Checkpoint: Pushing both repos ==="

# insilver-v2
echo ""
echo "📦 Pushing insilver-v2..."
cd ~/.openclaw/workspace/insilver-v2
git add -A
git commit -m "chkp $(date +%Y-%m-%d)" 2>/dev/null || echo "No changes in insilver-v2"
git push origin $MAIN_BRANCH
if [ $? -eq 0 ]; then
  echo "✓ insilver-v2 pushed"
else
  echo "✗ insilver-v2 push failed"
fi

# insilver-agent
echo ""
echo "🤖 Pushing insilver-agent..."
cd ~/.openclaw/workspace/insilver-agent
git add -A
git commit -m "chkp $(date +%Y-%m-%d)" 2>/dev/null || echo "No changes in insilver-agent"
git push origin $AGENT_BRANCH
if [ $? -eq 0 ]; then
  echo "✓ insilver-agent pushed"
else
  echo "✗ insilver-agent push failed"
fi

echo ""
echo "=== Checkpoint complete ==="
