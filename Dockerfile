# Use Cypress included image with Node.js and all required dependencies
FROM cypress/included:13.16.0

WORKDIR /app

# Copy app files
COPY . .

# Run the environment setup script.
RUN /bin/bash setup.sh

# Use the script to start the app and run Cypress tests
ENTRYPOINT ["/bin/bash", "run.sh"]
