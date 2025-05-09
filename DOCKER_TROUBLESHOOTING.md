# Docker Troubleshooting Guide

This guide addresses common issues with Docker in WSL environments, specifically:

1. Port binding permission issues
2. Volume mount permission problems

## Quick Start

For the fastest solution, run the master setup script:

```bash
./docker-setup.sh
```

This script will:
1. Detect if you're running in WSL
2. Check for port conflicts
3. Update configuration files if needed
4. Set up proper volume permissions
5. Guide you through next steps

## Port Binding Issues

### The Problem

You encountered this error:
```
Error response from daemon: Ports are not available: exposing port TCP 0.0.0.0:55679 -> 127.0.0.1:0: listen tcp 0.0.0.0:55679: bind: An attempt was made to access a socket in a way forbidden by its access permissions.
```

This is a common issue in Windows/WSL environments where certain ports have permission restrictions.

### The Solution

We've modified two files to use port 55680 instead of 55679:

1. `docker-compose.yaml`: Changed the port mapping from 55679:55679 to 55680:55680
2. `config/otel/otel-collector-config.yaml`: Updated the zpages extension endpoint from :55679 to :55680

## Volume Permission Issues

### The Problem

Different containers run as different users:
- Some run as root (UID 0) and create files owned by root
- Others run as non-root users and can't access those root-owned files

### The Solution

We've implemented a comprehensive approach:

1. **User Mapping**: Each service in docker-compose.yaml now has the correct user ID
2. **Setup Scripts**:
   - `setup-volumes.sh`: For standard Linux environments
   - `setup-volumes-wsl.sh`: For WSL environments (uses more permissive permissions)
3. **Diagnostic Tool**: `check-container-users.sh` helps identify user ID mismatches

## Documentation

For more detailed information, see:

- `VOLUME_PERMISSIONS.md`: Comprehensive guide to Docker volume permissions
- `docker-compose.yaml`: Updated configuration with proper user mappings
- `setup-volumes.sh` and `setup-volumes-wsl.sh`: Scripts to set up volume permissions
- `check-container-users.sh`: Tool to diagnose user ID issues

## Usage Instructions

1. Run the setup script:
   ```bash
   ./docker-setup.sh
   ```

2. Start your containers:
   ```bash
   docker compose up -d
   ```

3. If you encounter issues, check container users:
   ```bash
   ./check-container-users.sh
   ```

4. For persistent issues in WSL, consider using Docker Desktop for Windows instead
