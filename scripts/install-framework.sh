#!/bin/bash
set -e

# System Governance Framework - Installation Script
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/4-b100m/system-governance-framework/main/scripts/install-framework.sh)

VERSION="${1:-v3.0.0}"
PRESET="${2:-standard}"
REPO_URL="https://raw.githubusercontent.com/4-b100m/system-governance-framework"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  System Governance Framework - Installer                  ║"
echo "║  Framework-as-Code for Modern Development                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Check if in git repository
if [ ! -d ".git" ]; then
  echo -e "${RED}❌ Error: Not in a git repository${NC}"
  echo "Please run this script from the root of your git repository."
  exit 1
fi

# Check for required tools
echo "🔍 Checking prerequisites..."
if ! command -v curl &> /dev/null; then
    echo -e "${RED}❌ curl is required but not installed${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ git is required but not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites met${NC}"
echo ""

# Display configuration
echo "📋 Installation Configuration:"
echo -e "  ${BLUE}Version:${NC} $VERSION"
echo -e "  ${BLUE}Preset:${NC} $PRESET"
echo ""

# Confirm installation
read -p "Proceed with installation? [Y/n] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Create .github directory if it doesn't exist
echo "📁 Creating directory structure..."
mkdir -p .github/workflows
mkdir -p .github/configs
echo -e "${GREEN}✅ Directories created${NC}"

# Download governance configuration
echo ""
echo "📥 Downloading governance configuration..."
CONFIG_URL="$REPO_URL/$VERSION/config/presets/$PRESET.yml"

if curl -fsSL "$CONFIG_URL" -o .github/governance.yml 2>/dev/null; then
    echo -e "${GREEN}✅ Configuration downloaded${NC}"
else
    echo -e "${YELLOW}⚠️  Could not download preset, using embedded default${NC}"

    # Create default standard configuration
    cat > .github/governance.yml <<'EOF'
# System Governance Framework Configuration
# For full schema: https://github.com/4-b100m/system-governance-framework/blob/main/config/schema.json

framework:
  version: "3.0.0"
  preset: "standard"

project:
  # Automatically detected if not specified
  languages: []

features:
  ci:
    enabled: true
    test-coverage: true
    parallel-jobs: 3

  security:
    enabled: true
    codeql: true
    dependency-scan: true

  quality:
    enabled: true
    linting: true
    pre-commit: true

  dependabot:
    enabled: true
    schedule: "weekly"
EOF

    echo -e "${GREEN}✅ Default configuration created${NC}"
fi

# Create wrapper workflows
echo ""
echo "⚙️  Creating wrapper workflows..."

# CI Workflow
cat > .github/workflows/governance-ci.yml <<EOF
name: 'Governance: CI'

on:
  push:
    branches: [main, master, develop]
  pull_request:
    branches: [main, master, develop]

jobs:
  ci:
    name: Continuous Integration
    uses: 4-b100m/system-governance-framework/.github/workflows/reusable-ci.yml@$VERSION
    with:
      config-path: '.github/governance.yml'
    secrets: inherit
EOF

echo -e "${GREEN}  ✅ governance-ci.yml created${NC}"

# Security Workflow
cat > .github/workflows/governance-security.yml <<EOF
name: 'Governance: Security'

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  security:
    name: Security Scanning
    uses: 4-b100m/system-governance-framework/.github/workflows/reusable-security.yml@$VERSION
    with:
      config-path: '.github/governance.yml'
    secrets: inherit
EOF

echo -e "${GREEN}  ✅ governance-security.yml created${NC}"

# Detect project languages
echo ""
echo "🔍 Detecting project languages..."
LANGUAGES=()

if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    LANGUAGES+=("python")
    echo "  ${GREEN}✓${NC} Python"
fi

if [ -f "package.json" ]; then
    if grep -q "typescript" package.json 2>/dev/null; then
        LANGUAGES+=("typescript")
        echo "  ${GREEN}✓${NC} TypeScript"
    else
        LANGUAGES+=("javascript")
        echo "  ${GREEN}✓${NC} JavaScript"
    fi
fi

if [ -f "go.mod" ]; then
    LANGUAGES+=("go")
    echo "  ${GREEN}✓${NC} Go"
fi

if [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
    LANGUAGES+=("java")
    echo "  ${GREEN}✓${NC} Java"
fi

if [ -f "Cargo.toml" ]; then
    LANGUAGES+=("rust")
    echo "  ${GREEN}✓${NC} Rust"
fi

if [ -f "Gemfile" ]; then
    LANGUAGES+=("ruby")
    echo "  ${GREEN}✓${NC} Ruby"
fi

if [ -f "composer.json" ]; then
    LANGUAGES+=("php")
    echo "  ${GREEN}✓${NC} PHP"
fi

if [ ${#LANGUAGES[@]} -eq 0 ]; then
    echo -e "  ${YELLOW}⚠️  No languages detected${NC}"
else
    echo -e "${GREEN}✅ Detected ${#LANGUAGES[@]} language(s)${NC}"

    # Update configuration with detected languages
    if command -v yq &> /dev/null; then
        for lang in "${LANGUAGES[@]}"; do
            yq eval ".project.languages += [\"$lang\"]" -i .github/governance.yml 2>/dev/null || true
        done
    fi
fi

# Create markdown link check config if not exists
if [ ! -f ".github/configs/markdown-link-check.json" ]; then
    mkdir -p .github/configs
    cat > .github/configs/markdown-link-check.json <<'EOF'
{
  "ignorePatterns": [
    {
      "pattern": "^http://localhost"
    },
    {
      "pattern": "^https://localhost"
    }
  ],
  "retryOn429": true,
  "retryCount": 3,
  "fallbackRetryDelay": "30s",
  "aliveStatusCodes": [200, 206]
}
EOF
    echo -e "${GREEN}✅ Markdown link check config created${NC}"
fi

# Display next steps
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Installation Complete!                                ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1. Review and customize your configuration:"
echo -e "   ${YELLOW}   .github/governance.yml${NC}"
echo ""
echo "2. (Optional) Configure required secrets in GitHub:"
echo "   • CODECOV_TOKEN - For coverage reporting"
echo "   • SEMGREP_APP_TOKEN - For enhanced security scanning (Pro)"
echo ""
echo "3. Commit the framework setup:"
echo -e "   ${YELLOW}git add .github/${NC}"
echo -e "   ${YELLOW}git commit -m \"chore: Add governance framework v$VERSION\"${NC}"
echo ""
echo "4. Push to GitHub and watch workflows run:"
echo -e "   ${YELLOW}git push${NC}"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "   https://github.com/4-b100m/system-governance-framework#readme"
echo ""
echo -e "${BLUE}🆘 Support:${NC}"
echo "   https://github.com/4-b100m/system-governance-framework/discussions"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
