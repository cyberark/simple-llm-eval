
echo "Usage: ./inspect_changes_since_last_release.sh [section1,section2,...]"
echo "Sections: all, docs, simpleval, frontend"
echo "Example: ./inspect_changes_since_last_release.sh all,python"
echo ""

sections_arg="$1"
IFS=',' read -r -a sections <<< "$sections_arg"

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



# Optionally run extra diff sections if argument(s) provided
if [ -n "$sections_arg" ]; then
  for section in "${sections[@]}"; do
    case "$section" in
      all)
        echo ""
        echo "All Changes:"
        echo "==================="
        git --no-pager diff "$latest_tag"..origin/main
        ;;
      docs)
        echo ""
        echo "All Changes in docs:"
        echo "==================="
        git --no-pager diff "$latest_tag"..origin/main -- docs/
        ;;
      simpleval)
        echo ""
        echo "All Changes in simpleval:"
        echo "==================="
        git --no-pager diff "$latest_tag"..origin/main -- simpleval/
        ;;
      frontend)
        echo ""
        echo "All Changes in reports-frontend:"
        echo "==================="
        git --no-pager diff "$latest_tag"..origin/main -- reports-frontend/
        ;;
      *)
        echo ""
        echo "Unknown section: $section"
        ;;
    esac
  done
fi

echo ""
echo "To show detailed changes, run: ./inspect_changes_since_last_release.sh [section1,section2,...]"
echo "Sections: all, docs, simpleval, frontend"
