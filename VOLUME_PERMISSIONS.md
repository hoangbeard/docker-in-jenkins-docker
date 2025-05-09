# Docker Volume Permissions Guide

This guide explains how to handle volume permission issues in your Docker Compose setup.

## The Problem

When using bind mounts in Docker, you may encounter permission issues because:

1. Different containers run as different users (UIDs)
2. Files created by one container may not be accessible to another
3. Root-owned files on the host can't be modified by non-root users in containers

## The Solution

We've implemented a two-part solution:

### 1. Setup Script

The `setup-volumes.sh` script:
- Creates all necessary directories for persistent data
- Sets appropriate ownership for each service's data directories
- Sets permissions to allow group access

### 2. User Mapping in docker-compose.yaml

Each service is configured with the appropriate user ID:

- Jenkins: `user: "1000:1000"` (typical Jenkins user)
- Prometheus: `user: "65534:65534"` (nobody:nogroup)
- Grafana: `user: "472:472"` (grafana user)
- SonarQube: `user: "1000:1000"` (sonarqube user)
- PostgreSQL: `user: "999:999"` (postgres user)

## How to Use

Before starting your containers for the first time:

1. Run the setup script to prepare your volume directories:

```bash
sudo ./setup-volumes.sh
```

2. Start your containers:

```bash
docker compose up -d
```

## Troubleshooting

If you still encounter permission issues:

1. Run the container user check script to get detailed information:
```bash
./check-container-users.sh
```

This script will:
- Show the actual user IDs inside each running container
- Display process information for the main process in each container
- Show the current permissions of your volume directories

2. If needed, adjust the user IDs in docker-compose.yaml to match the actual users in your containers

3. Re-run the appropriate setup script:
```bash
# For Linux:
sudo ./setup-volumes.sh

# For WSL:
sudo ./setup-volumes-wsl.sh
```

## Additional Notes

- Some containers may require root access for certain operations
- Consider using named volumes instead of bind mounts for better permission handling

## Windows/WSL Specific Instructions

If you're running in a Windows Subsystem for Linux (WSL) environment, use the WSL-specific script instead:

```bash
sudo ./setup-volumes-wsl.sh
```

This script sets more permissive permissions (777) which solves most WSL-specific issues. Note that this approach is only recommended for development environments, not production.

### Common WSL Permission Issues

1. **Access Denied Errors**: In WSL, file permissions can behave differently than in native Linux
2. **Port Binding Issues**: As you experienced with port 55679, some ports may have permission restrictions
3. **Docker Socket Access**: The `/var/run/docker.sock` binding may require special handling in WSL

### WSL Best Practices

1. Use the WSL-specific script for permissions
2. Consider running Docker Desktop for Windows instead of Docker in WSL
3. For persistent issues, try using named volumes instead of bind mounts
4. If a specific port has issues (like 55679), try an alternative port
