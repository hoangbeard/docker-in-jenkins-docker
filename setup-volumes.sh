#!/bin/bash
set -e

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

# Set permissions - use a common group ID that all containers can access
# 1000:1000 is typically the first non-root user on Linux systems
# This assumes your containers use UIDs like 1000, 999, etc.

# Jenkins - Jenkins typically runs as uid 1000
chown -R 1000:1000 persistent-data/jenkins

# Prometheus - Prometheus typically runs as nobody (65534)
chown -R 65534:65534 persistent-data/prometheus

# Grafana - Grafana typically runs as uid 472
chown -R 472:472 persistent-data/grafana

# SonarQube - SonarQube runs as sonarqube user (uid 1000 in the container)
chown -R 1000:1000 persistent-data/sonarqube

# Set directory permissions to be group writable
find persistent-data -type d -exec chmod 775 {} \;

# Set file permissions to be group writable
find persistent-data -type f -exec chmod 664 {} \; 2>/dev/null || true

echo "Volume permissions set successfully"
