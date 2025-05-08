#!/usr/bin/env python3
# Enhanced compatibility_checker.py
#
# This script checks the compatibility of Jenkins plugins with a specific Jenkins version
# and Java version. Instead of using the rarely populated 'minimumJavaVersion' field,
# it determines Java compatibility based on the Jenkins version requirements as per
# https://www.jenkins.io/doc/book/platform-information/support-policy-java/
#
# Usage:
#   1. Place a plugins.txt file in the same directory as this script with plugin names
#      (one per line, with or without version specifiers like 'git:4.11.5')
#   2. Run this script: python compatibility_checker.py
#   3. The script will generate compatible-plugins.txt with compatible plugin versions
#
# If no plugins.txt file is found, the script will use a default list of common plugins.

import requests
import json
import sys

# Try to import packaging, provide guidance if not available
try:
    from packaging import version
except ImportError:
    print("Error: The 'packaging' module is not installed.")
    print("Please install it using: pip install packaging")
    sys.exit(1)

# Java version to check compatibility against
JENKINS_VERSION_FALLBACK = "2.479.1"  # Replace with your Jenkins version, e.g., 2.479.1 for LTS with Java 21
JAVA_VERSION = "21"  # Replace with your Java version

# Load plugins from plugins.txt file or use default list
try:
    with open("plugins.txt", "r") as f:
        # Read lines, strip whitespace, and filter out empty lines and comments
        plugins = []
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            # If the line contains a version specifier (plugin:version), extract just the plugin name
            if ':' in line:
                plugin_name = line.split(':', 1)[0].strip()
            else:
                plugin_name = line
            plugins.append(plugin_name)
except FileNotFoundError:
    # Fallback to default plugin list if file not found
    print("⚠️ plugins.txt file not found. Using default plugin list.")
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

def get_required_java_version(jenkins_version):
    """Determine required Java version based on Jenkins version

    This function uses the Jenkins version to determine the compatible Java versions
    based on the Jenkins support policy documented at:
    https://www.jenkins.io/doc/book/platform-information/support-policy-java/

    Args:
        jenkins_version: String containing Jenkins version (e.g., "2.426.1")

    Returns:
        List of strings representing compatible Java versions (e.g., ["11", "17", "21"])
    """
    # Convert string versions to comparable objects
    try:
        v = version.parse(jenkins_version)

        # Based on https://www.jenkins.io/doc/book/platform-information/support-policy-java/
        if v >= version.parse("2.479.1"):
            return ["17", "21"]  # Java 17 or Java 21
        elif v >= version.parse("2.426.1"):
            return ["11", "17", "21"]  # Java 11, Java 17, or Java 21
        elif v >= version.parse("2.361.1"):
            return ["11", "17"]  # Java 11 or Java 17
        elif v >= version.parse("2.346.1"):
            return ["8", "11", "17"]  # Java 8, Java 11, or Java 17
        elif v >= version.parse("2.164.1"):
            return ["8", "11"]  # Java 8 or Java 11
        elif v >= version.parse("2.60.1"):
            return ["8"]  # Java 8
        else:
            return ["7"]  # Java 7 for very old versions
    except Exception as e:
        print(f"Error parsing Jenkins version: {e}")
        return ["8", "11", "17", "21"]  # Return all supported versions as fallback

def check_java_compatibility(plugin_info, plugin_name, latest_version, java_version, jenkins_version=None):
    """Check if plugin is compatible with Java version based on Jenkins version requirements

    This function:
    1. Gets the plugin's 'requiredCore' (minimum Jenkins version)
    2. Determines which Java versions are compatible with that Jenkins version
    3. Checks if the current Java version is in that list of compatible versions

    Since plugins rarely specify 'minimumJavaVersion' directly, we infer Java
    compatibility through Jenkins version requirements.

    Args:
        plugin_info: Dictionary containing plugin metadata
        plugin_name: String with the plugin name
        latest_version: String with the plugin version
        java_version: String with the current Java version
        jenkins_version: String with the current Jenkins version

    Returns:
        None if compatible, or a string explaining the incompatibility
    """
    required_jenkins = plugin_info.get("requiredCore", "1.0")

    # Get the required Java versions for the plugin's minimum Jenkins version
    required_java_versions = get_required_java_version(required_jenkins)

    # Check if current Java version is compatible with plugin's required Jenkins version
    if java_version not in required_java_versions:
        min_java = required_java_versions[0]  # First version is the minimum required
        return f"Plugin {plugin_name}:{latest_version} requires Jenkins {required_jenkins}, which needs Java {min_java}+ but you have Java {java_version}"

    return None

def generate_plugins_file(plugins, plugin_versions, file_path="compatible-plugins.txt"):
    """Generate plugins.txt file with compatible versions"""
    try:
        with open(file_path, "w") as f:
            for plugin_name in plugins:
                plugin_name = plugin_name.strip()
                if not plugin_name:  # Skip empty plugin names
                    continue

                if plugin_name in plugin_versions:
                    f.write(f"{plugin_name}:{plugin_versions[plugin_name]}\n")
                else:
                    f.write(f"# {plugin_name} - NOT FOUND OR INCOMPATIBLE\n")

        print(f"\n📄 Generated {file_path} with compatible plugin versions")
    except Exception as e:
        print(f"\n⚠️ Error writing {file_path}: {e}")

def main():
    # Display startup banner and help
    print("\n" + "=" * 80)
    print("Jenkins Plugin Compatibility Checker".center(80))
    print("=" * 80)
    print("This script checks Jenkins plugins for compatibility with a specific Jenkins and Java version.")
    print("It reads plugin names from plugins.txt (if present) or uses a default plugin list.")
    print("The output will be saved to compatible-plugins.txt with compatible version numbers.")
    print("=" * 80 + "\n")

    # Get latest Jenkins LTS version
    jenkins_version = get_latest_jenkins_lts()
    java_version = JAVA_VERSION
    print(f"🔍 Checking plugin compatibility with Jenkins LTS {jenkins_version} and Java {java_version}")

    # Check if current Java version is compatible with the Jenkins version
    required_java_versions = get_required_java_version(jenkins_version)
    if java_version not in required_java_versions:
        print(f"⚠️ Warning: Jenkins {jenkins_version} requires Java version(s): {', '.join(required_java_versions)}, but you have Java {java_version}")
        print("    This may cause compatibility issues. See: https://www.jenkins.io/doc/book/platform-information/support-policy-java/")

    print("\nℹ️ Java compatibility is determined by checking each plugin's required Jenkins version")
    print("   and then mapping that to Java requirements based on the Jenkins support policy.")

    # Get Jenkins update center data
    data = fetch_update_center()

    compatibility_issues = []
    compatible_plugins = []
    plugin_versions = {}

    # Check each plugin
    for plugin_name in plugins:
        # Remove any trailing whitespace or newlines
        plugin_name = plugin_name.strip()
        if not plugin_name:  # Skip empty plugin names
            continue

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

        java_issue = check_java_compatibility(plugin_info, plugin_name, latest_version, java_version, jenkins_version)
        if java_issue:
            compatibility_issues.append(java_issue)
            continue

        # If we got here, the plugin is compatible
        compatible_plugins.append(f"{plugin_name}:{latest_version}")

    # Report results
    print_results(compatible_plugins, compatibility_issues)

    # Generate plugins.txt
    file_path = "../config/compatible-plugins.txt"
    generate_plugins_file(plugins, plugin_versions, file_path)

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
