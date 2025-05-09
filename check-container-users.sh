#!/bin/bash
set -e

# This script checks the actual user IDs inside each container
# Useful for troubleshooting permission issues

echo "Checking user IDs in running containers..."
echo "----------------------------------------"

# Check if containers are running
containers=("jenkins" "prometheus" "grafana" "jaeger" "zipkin" "otel-collector" "sonarqube" "sonarqube-db")

for container in "${containers[@]}"; do
  echo "Container: $container"
  if docker ps -q --filter "name=$container" | grep -q .; then
    echo "  Status: Running"
    echo "  User info:"
    docker exec -it $container id 2>/dev/null || echo "  Could not execute 'id' command in container"
    echo "  Process info:"
    docker exec -it $container ps aux | grep -v "ps aux" | head -n 1 2>/dev/null || echo "  Could not execute 'ps' command in container"
  else
    echo "  Status: Not running"
  fi
  echo "----------------------------------------"
done

echo "Volume directory permissions:"
echo "----------------------------------------"
ls -la persistent-data/
echo "----------------------------------------"

echo "Check complete. Use this information to adjust user IDs in docker-compose.yaml if needed."
