#!/bin/bash

set -e

# Healthcheck function.
wait_for_frontend() {
	echo "Waiting for Frontend on http://localhost:5173 to be ready..."

	for i in $(seq 1 5); do
		# Check if port 5173 is open using a simple socket connection
		if timeout 2 bash -c "</dev/tcp/localhost/5173" >/dev/null 2>&1; then
			echo "Frontend is ready on http://localhost:5173."
			return 0
		fi

		echo "Retrying Frontend readiness check ($i/5)..."
		sleep 3
	done

	echo "Frontend failed to start after 5 retries."
	return 1
}

# Start the frontend server
echo "Starting the frontend server..."
cd /app
npm run dev &
FRONTEND_PID=$!

# Wait for the frontend server to be ready
wait_for_frontend || exit 1

# Run Cypress tests
echo "Running Cypress tests..."
cd /app/eval
npx cypress run --headless --browser chrome
EVAL_EXIT_CODE=$?

# Stop frontend server
echo "Stopping the frontend server..."
kill $FRONTEND_PID

# Exit with the Selenium test exit code
exit $EVAL_EXIT_CODE
