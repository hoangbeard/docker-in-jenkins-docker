#!/bin/bash
set -e

# Master script for Docker setup and troubleshooting
# This script handles both the port binding issue and volume permissions

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Docker Setup and Troubleshooting Script${NC}"
echo "================================================"

# Detect if running in WSL
if grep -q -i WSL /proc/version; then
  echo -e "${YELLOW}WSL environment detected${NC}"
  IS_WSL=true
else
  echo -e "${GREEN}Linux environment detected${NC}"
  IS_WSL=false
fi

# Function to setup volume permissions
setup_volumes() {
  echo -e "\n${GREEN}Setting up volume permissions...${NC}"
  
  if [ "$IS_WSL" = true ]; then
    echo "Using WSL-specific permissions"
    sudo ./setup-volumes-wsl.sh
  else
    echo "Using standard Linux permissions"
    sudo ./setup-volumes.sh
  fi
}

# Function to check for port conflicts
check_ports() {
  echo -e "\n${GREEN}Checking for port conflicts...${NC}"
  
  PORTS=("8080" "50000" "9090" "3000" "16686" "9411" "1888" "8888" "8889" "13133" "4317" "9000")
  
  for PORT in "${PORTS[@]}"; do
    if netstat -tuln | grep -q ":$PORT "; then
      echo -e "${RED}Port $PORT is already in use!${NC}"
      echo "This may cause conflicts with your Docker services."
    fi
  done
  
  echo -e "${GREEN}Port check complete.${NC}"
}

# Main execution
echo -e "\n${GREEN}Step 1: Checking for port conflicts${NC}"
check_ports

echo -e "\n${GREEN}Step 2: Setting up volume permissions${NC}"
setup_volumes

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "You can now run: ${YELLOW}docker compose up -d${NC}"
echo -e "If you encounter any issues, run: ${YELLOW}./check-container-users.sh${NC}"
echo -e "For more information, see: ${YELLOW}VOLUME_PERMISSIONS.md${NC}"
