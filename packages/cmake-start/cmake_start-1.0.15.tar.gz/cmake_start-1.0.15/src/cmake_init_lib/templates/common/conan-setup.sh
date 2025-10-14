#!/bin/bash
# Automated Conan profile detection and setup script
# This script helps manage multiple Conan profiles for different environments

set -e

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BUILD_TYPE="${1:-Debug}"
CONAN_PROFILE=""

echo -e "${BLUE}==> Detecting build environment...${NC}"

# Detect environment and select appropriate profile
if [ -n "${IN_NIX_SHELL}" ] || [ -n "${NIX_BUILD_TOP}" ]; then
  echo -e "${GREEN}✓ Nix environment detected${NC}"
  CONAN_PROFILE="nix"
else
  echo -e "${GREEN}✓ Native environment detected${NC}"
  CONAN_PROFILE="default"
fi

# Check if the profile exists
if ! conan profile show "$CONAN_PROFILE" >/dev/null 2>&1; then
  echo -e "${YELLOW}! Profile '$CONAN_PROFILE' not found${NC}"

  if [ "$CONAN_PROFILE" = "default" ]; then
    echo -e "${BLUE}==> Creating default profile...${NC}"
    conan profile detect --force
  else
    echo -e "${YELLOW}! Please create a '$CONAN_PROFILE' profile first${NC}"
    echo -e "${YELLOW}! Run: conan profile detect --name $CONAN_PROFILE${NC}"
    echo -e "${YELLOW}! Then edit ~/.conan2/profiles/$CONAN_PROFILE to match your environment${NC}"
    exit 1
  fi
fi

echo -e "${BLUE}==> Using Conan profile: ${GREEN}$CONAN_PROFILE${NC}"
echo -e "${BLUE}==> Build type: ${GREEN}$BUILD_TYPE${NC}"

# Run conan install with the selected profile
echo -e "${BLUE}==> Installing dependencies...${NC}"
conan install . \
  --profile="$CONAN_PROFILE" \
  --settings=build_type="$BUILD_TYPE" \
  --output-folder=. \
  --build=missing

echo -e "${GREEN}✓ Conan setup complete!${NC}"
echo -e "${BLUE}==> You can now run: cmake --preset=dev${NC}"
