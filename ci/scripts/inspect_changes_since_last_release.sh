latest_tag=$(gh release list --limit 1 | awk '{print $1}')

echo Inspecting changes since: $latest_tag
echo ""

echo "Change files:"
echo "==================="
git --no-pager diff --name-only "$latest_tag"..origin/main

echo ""
echo "Commits:"
echo "==================="
git --no-pager log --oneline "$latest_tag"..origin/main


# echo ""
# echo "All Changes:"
# echo "==================="
# git --no-pager diff "$latest_tag"..origin/main

# echo ""
# echo "All Changes in docs:"
# echo "==================="
# git diff "$latest_tag"..origin/main -- docs/

# echo ""
# echo "All Changes in simpleval:"
# echo "==================="
# git diff "$latest_tag"..origin/main -- simpleval/

# echo ""
# echo "All Changes in reports-frontend:"
# echo "==================="
# git diff "$latest_tag"..origin/main -- reports-frontend/
