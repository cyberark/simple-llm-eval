# Exit immediately if a command exits with a non-zero status
set -e

cd reports-frontend

# Building react reports
echo "Installing react reports dependencies..."
npm install 

echo "Building react reports..."
npm run build

echo "Running npm audit..."
npm audit --audit-level=low

echo "Running npm test (once, no watch)..."
npm run test-no-watch
