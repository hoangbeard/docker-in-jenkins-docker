#!/bin/bash
set -e

# Wait for Jenkins to start up
curl -s http://localhost:8080/jenkins/pluginManager/ | grep -q "Plugin Manager"