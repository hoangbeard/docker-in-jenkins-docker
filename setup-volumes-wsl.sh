#!/bin/bash
set -e

# This script is specifically for Windows WSL environments
# It handles the special permission requirements for Docker volumes in WSL

echo "Setting up volume permissions for WSL environment..."

# Create directories if they don't exist
mkdir -p persistent-data/jenkins/home
mkdir -p persistent-data/jenkins/backup
mkdir -p persistent-data/prometheus
mkdir -p persistent-data/grafana
mkdir -p persistent-data/sonarqube/data
mkdir -p persistent-data/sonarqube/extensions
mkdir -p persistent-data/sonarqube/logs
mkdir -p persistent-data/sonarqube/postgresql
mkdir -p persistent-data/sonarqube/postgresql/data

# In WSL, we need to ensure directories are fully accessible
# This is more permissive than ideal but solves WSL-specific issues
chmod -R 777 persistent-data/

echo "WSL volume permissions set successfully"
echo "NOTE: This script uses very permissive permissions (777) which is"
echo "      only recommended for development environments in WSL."
echo "      For production, consider a more restrictive permission model."
