#!/bin/bash
# Enhanced script to check plugin compatibility at build time

# Java version to check against
JAVA_VERSION="21"  # Replace with your Java version

# Fetch the latest Jenkins LTS version
echo "Fetching latest Jenkins LTS version..."
JENKINS_VERSION=$(curl -s https://updates.jenkins.io/stable/latestCore.txt)
if [ -z "$JENKINS_VERSION" ]; then
  echo "Failed to fetch Jenkins version, falling back to default"
  JENKINS_VERSION="2.479.1"
fi

echo "Using Jenkins version: $JENKINS_VERSION and Java $JAVA_VERSION"

# Create a list of plugins to check - you can modify this list
cat > plugins.txt << EOF
credentials:latest
git:latest
workflow-aggregator:latest
blueocean:latest
EOF

# Download the plugin manager CLI
PLUGIN_MANAGER_VERSION="2.12.11"
PLUGIN_MANAGER_URL="https://github.com/jenkinsci/plugin-installation-manager-tool/releases/download/${PLUGIN_MANAGER_VERSION}/jenkins-plugin-manager-${PLUGIN_MANAGER_VERSION}.jar"

echo "Downloading Jenkins Plugin Manager..."
curl -L "$PLUGIN_MANAGER_URL" -o jenkins-plugin-manager.jar

# Download Jenkins WAR file to check against
JENKINS_WAR_URL="https://get.jenkins.io/war-stable/${JENKINS_VERSION}/jenkins.war"
echo "Downloading Jenkins WAR file for version ${JENKINS_VERSION}..."
curl -L "$JENKINS_WAR_URL" -o jenkins.war

echo "Checking plugin compatibility..."
# Check compatibility and download compatible versions
java -jar jenkins-plugin-manager.jar \
  --war jenkins.war \
  --plugin-file plugins.txt \
  --verbose \
  --view-security-warnings \
  --available-updates \
  --list > compatibility_report.txt

# Check if there are any warnings or errors in the report
if grep -E "WARNING:|ERROR:" compatibility_report.txt; then
  echo "⚠️ Compatibility issues detected, see report in compatibility_report.txt"
  exit 1
else
  echo "✅ All plugins are compatible with Jenkins ${JENKINS_VERSION} and Java ${JAVA_VERSION}"
  # Generate the final plugin file with specific versions
  java -jar jenkins-plugin-manager.jar \
    --war jenkins.war \
    --plugin-file plugins.txt \
    --verbose \
    --output plugins-with-versions.txt

  echo "📄 Generated plugins-with-versions.txt with compatible plugin versions"
fi

# Cleanup
#rm jenkins.war
