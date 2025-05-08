#!/usr/bin/env python3
# Enhanced compatibility_checker.py

import requests
import json
import sys
import re

# Java version to check compatibility against
JENKINS_VERSION_FALLBACK = "2.479.1"  # Replace with your Jenkins version, e.g., 2.479.1 for LTS with Java 21
JAVA_VERSION = "21"  # Replace with your Java version

# List of plugins to check
plugins = [
    "ansicolor",
    "aws-credentials",
    "blueocean",
    "build-timeout",
    "cloudbees-disk-usage-simple",
    "cloudbees-folder",
    "configuration-as-code",
    "credentials-binding",
    "dark-theme",
    "dashboard-view",
    "dependency-check-jenkins-plugin",
    "dependency-track",
    "docker-plugin",
    "ec2",
    "email-ext",
    "extended-read-permission",
    "git",
    "javax-mail-api",
    "opentelemetry",
    "pipeline-build-step",
    "pipeline-graph-view",
    "pipeline-stage-view",
    "pipeline-utility-steps",
    "prometheus",
    "role-strategy",
    "saferestart",
    "saml",
    "schedule-build",
    "sonar",
    "ssh-slaves",
    "sshd",
    "theme-manager",
    "thinBackup",
    "timestamper",
    "workflow-aggregator",
    "ws-cleanup",
]

def get_latest_jenkins_lts():
    """Fetch the latest stable LTS version of Jenkins"""
    try:
        response = requests.get("https://updates.jenkins.io/stable/latestCore.txt")
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"Error fetching latest Jenkins LTS: {e}")
        print("Falling back to update center for version info")
        try:
            update_center = requests.get("https://updates.jenkins.io/stable/update-center.json")
            update_center.raise_for_status()
            data = update_center.json()
            return data.get("core", {}).get("version", JENKINS_VERSION_FALLBACK)  # Fallback to a default if all else fails
        except Exception as e2:
            print(f"Error with fallback method: {e2}")
            return JENKINS_VERSION_FALLBACK  # Default fallback version
        
def fetch_update_center():
    """Fetch and parse the Jenkins update center data"""
    # Try the correct URL for the update center JSON
    urls_to_try = [
        "https://updates.jenkins.io/stable/update-center.json",
        "https://updates.jenkins.io/stable/update-center.actual.json",
        # "https://updates.jenkins.io/update-center.actual.json",
        # "https://updates.jenkins.io/current/update-center.actual.json"
    ]
    
    for url in urls_to_try:
        try:
            print(f"Trying to fetch update center data from: {url}")
            response = requests.get(url)
            response.raise_for_status()
            
            # Check if the response starts with "updateCenter.post("
            content = response.text
            if content.startswith("updateCenter.post("):
                # Extract the JSON part
                json_str = content.replace("updateCenter.post(", "").strip()
                # Remove the trailing ");", if present
                if json_str.endswith(");"):
                    json_str = json_str[:-2]
                data = json.loads(json_str)
            else:
                # Regular JSON
                data = response.json()
                
            print(f"Successfully fetched update center data from {url}")
            return data
        except requests.RequestException as e:
            print(f"Request error with {url}: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON parsing error with {url}: {e}")
        except Exception as e:
            print(f"Unexpected error with {url}: {e}")
    
    # If we've tried all URLs and none worked
    print("Failed to fetch update center data from all sources")
    sys.exit(1)

def check_jenkins_compatibility(plugin_info, plugin_name, latest_version, jenkins_version):
    """Check if plugin is compatible with Jenkins version"""
    requires_jenkins = plugin_info.get("requiredCore", "1.0")
    if requires_jenkins > jenkins_version:
        return f"Plugin {plugin_name}:{latest_version} requires Jenkins {requires_jenkins} but you have {jenkins_version}"
    return None

def check_java_compatibility(plugin_info, plugin_name, latest_version, java_version):
    """Check if plugin is compatible with Java version"""
    java_req = plugin_info.get("minimumJavaVersion", "")
    if java_req:
        # Extract Java version number
        match = re.search(r'Java\s+(\d+)', java_req)
        if match and int(match.group(1)) > int(java_version):
            return f"Plugin {plugin_name}:{latest_version} requires {java_req} but you have Java {java_version}"
    return None

def generate_plugins_file(plugins, plugin_versions):
    """Generate plugins.txt file with compatible versions"""
    with open("plugins.txt", "w") as f:
        for plugin_name in plugins:
            if plugin_name in plugin_versions:
                f.write(f"{plugin_name}:{plugin_versions[plugin_name]}\n")
            else:
                f.write(f"# {plugin_name} - NOT FOUND OR INCOMPATIBLE\n")
    
    print("\n📄 Generated plugins.txt with compatible plugin versions")

def main():
    # Get latest Jenkins LTS version
    jenkins_version = get_latest_jenkins_lts()
    java_version = JAVA_VERSION
    print(f"🔍 Checking plugin compatibility with Jenkins LTS {jenkins_version} and Java {java_version}")
    
    # Get Jenkins update center data
    data = fetch_update_center()
    
    compatibility_issues = []
    compatible_plugins = []
    plugin_versions = {}
    
    # Check each plugin
    for plugin_name in plugins:
        if plugin_name not in data["plugins"]:
            compatibility_issues.append(f"Plugin {plugin_name} not found in update center")
            continue
            
        plugin_info = data["plugins"][plugin_name]
        latest_version = plugin_info["version"]
        plugin_versions[plugin_name] = latest_version
        
        # Check compatibility
        jenkins_issue = check_jenkins_compatibility(plugin_info, plugin_name, latest_version, jenkins_version)
        if jenkins_issue:
            compatibility_issues.append(jenkins_issue)
            continue
        
        java_issue = check_java_compatibility(plugin_info, plugin_name, latest_version, java_version)
        if java_issue:
            compatibility_issues.append(java_issue)
            continue
        
        # If we got here, the plugin is compatible
        compatible_plugins.append(f"{plugin_name}:{latest_version}")
    
    # Report results
    print_results(compatible_plugins, compatibility_issues)
    
    # Generate plugins.txt
    generate_plugins_file(plugins, plugin_versions)
    
    if compatibility_issues:
        sys.exit(1)
    else:
        print(f"\n✅ All plugins are compatible with Jenkins {jenkins_version} and Java {java_version}")

def print_results(compatible_plugins, compatibility_issues):
    """Print the compatibility results"""
    if compatible_plugins:
        print("\n✅ COMPATIBLE PLUGINS:")
        for plugin in compatible_plugins:
            print(f"  - {plugin}")
    
    if compatibility_issues:
        print("\n🚨 COMPATIBILITY ISSUES FOUND:")
        for issue in compatibility_issues:
            print(f"  - {issue}")

if __name__ == "__main__":
    main()