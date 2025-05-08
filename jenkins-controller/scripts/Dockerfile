FROM jenkins/jenkins:lts-jdk11

USER root
# Install necessary tools
RUN apt-get update && apt-get install -y curl python3 python3-pip

# Install Python dependencies
RUN pip3 install requests

# Copy compatibility checker script
COPY compatibility_checker.py /usr/local/bin/
RUN chmod +x /usr/local/bin/compatibility_checker.py

# Run compatibility check during build
RUN python3 /usr/local/bin/compatibility_checker.py

# Switch back to Jenkins user
USER jenkins

# Install plugins from the generated plugins.txt
COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Copy the healthcheck script
COPY --chown=jenkins:jenkins scripts/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Health check using exec form with the script
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD ["bash", "/usr/local/bin/healthcheck.sh"]
