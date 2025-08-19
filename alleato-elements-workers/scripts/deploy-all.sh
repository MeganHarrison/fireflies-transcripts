#!/bin/bash

# Deploy all Alleato Elements Workers
# Usage: ./scripts/deploy-all.sh [environment]

ENVIRONMENT=${1:-dev}

echo "🚀 Deploying Alleato Elements Workers to $ENVIRONMENT environment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to deploy a worker
deploy_worker() {
    local worker_name=$1
    local worker_dir=$2
    
    echo -e "${YELLOW}📦 Deploying $worker_name...${NC}"
    
    if [ ! -d "$worker_dir" ]; then
        echo -e "${RED}❌ Directory $worker_dir not found${NC}"
        return 1
    fi
    
    cd "$worker_dir" || return 1
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo -e "${RED}❌ No package.json found in $worker_dir${NC}"
        cd ..
        return 1
    fi
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing dependencies for $worker_name..."
        npm install
    fi
    
    # Deploy with wrangler
    if wrangler deploy; then
        echo -e "${GREEN}✅ $worker_name deployed successfully${NC}"
        cd ..
        return 0
    else
        echo -e "${RED}❌ Failed to deploy $worker_name${NC}"
        cd ..
        return 1
    fi
}

# Store the original directory
ORIGINAL_DIR=$(pwd)

# Deploy each worker
FAILED_DEPLOYMENTS=()

deploy_worker "AI Agent Worker" "ai-agent-worker" || FAILED_DEPLOYMENTS+=("ai-agent-worker")
deploy_worker "Fireflies Ingest Worker" "fireflies-ingest-worker" || FAILED_DEPLOYMENTS+=("fireflies-ingest-worker") 
deploy_worker "Vectorize Worker" "vectorize-worker" || FAILED_DEPLOYMENTS+=("vectorize-worker")

# Only deploy insights worker if it has implementation
if [ -f "insights-worker/package.json" ]; then
    deploy_worker "Insights Worker" "insights-worker" || FAILED_DEPLOYMENTS+=("insights-worker")
else
    echo -e "${YELLOW}⚠️ Skipping Insights Worker (not implemented yet)${NC}"
fi

# Return to original directory
cd "$ORIGINAL_DIR"

# Summary
echo ""
echo "🏁 Deployment Summary:"

if [ ${#FAILED_DEPLOYMENTS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All workers deployed successfully!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some deployments failed:${NC}"
    for failed in "${FAILED_DEPLOYMENTS[@]}"; do
        echo -e "${RED}  - $failed${NC}"
    done
    exit 1
fi