#!/bin/bash
# Checkpoint - push all repos to GitHub
echo "=== Checkpoint: Pushing all repos ==="

# insilver-v2
echo ""
echo "📦 Pushing insilver-v2..."
cd ~/.openclaw/workspace/insilver-v2
git add -A
git commit -m "chkp $(date +%Y-%m-%d)" 2>/dev/null || echo "No changes in insilver-v2"
git push origin main
if [ $? -eq 0 ]; then echo "✓ insilver-v2 pushed"
else echo "✗ insilver-v2 push failed"; fi

# openclaw-kit (Кіт)
echo ""
echo "🐱 Pushing openclaw-kit..."
cd ~/.openclaw/workspace
git add -A
git commit -m "chkp $(date +%Y-%m-%d)" 2>/dev/null || echo "No changes in openclaw-kit"
git push origin main
if [ $? -eq 0 ]; then echo "✓ openclaw-kit pushed"
else echo "✗ openclaw-kit push failed"; fi

echo ""
echo "=== Checkpoint complete ==="
