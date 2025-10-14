#!/bin/bash
#
# OGC SensorThings API Schema Validator - Demo Script
#
# This script sets up and runs a complete demo environment with:
# - FROST-Server (SensorThings API implementation)
# - PostgreSQL database
# - Sample data provisioning
# - Automated validation with intentional errors
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Check for required commands
check_requirements() {
    print_header "Checking Requirements"

    local missing_requirements=0

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        missing_requirements=1
    else
        print_success "Docker is installed"
    fi

    if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        missing_requirements=1
    else
        print_success "Docker Compose is installed"
    fi

    if [ $missing_requirements -eq 1 ]; then
        exit 1
    fi
}

# Clean up old demo environment
cleanup() {
    print_header "Cleaning Up Previous Demo"

    print_info "Stopping and removing containers..."
    docker compose down -v 2>/dev/null || true

    print_success "Cleanup complete"
}

# Start the demo
start_demo() {
    print_header "Starting Demo Environment"

    print_info "This demo will:"
    echo "  1. Start FROST-Server and PostgreSQL"
    echo "  2. Provision sample entities (some valid, some invalid)"
    echo "  3. Run validation and show results"
    echo ""
    print_info "Building and starting containers..."
    echo ""

    docker compose up --build
}

# Show demo info
show_info() {
    print_header "Demo Information"

    echo "The demo environment includes:"
    echo ""
    echo -e "  ${BLUE}FROST-Server:${NC}"
    echo "    - URL: http://localhost:8080/FROST-Server/v1.1"
    echo "    - Web UI: http://localhost:8080/FROST-Server/"
    echo ""
    echo -e "  ${BLUE}Sample Data:${NC}"
    echo "    - Things: 2 entities (1 valid, 1 invalid)"
    echo "    - Sensors: 2 entities (1 valid, 1 invalid)"
    echo "    - Observations: 2 entities (1 valid, 1 invalid)"
    echo "    - Datastreams: 2 entities (1 valid, 1 invalid)"
    echo ""
    echo -e "  ${BLUE}Validation Errors to Expect:${NC}"
    echo "    - Missing required fields (name, description)"
    echo "    - Invalid data types (string vs number)"
    echo "    - Invalid enum values (status, qualityFlag)"
    echo "    - Invalid date formats"
    echo "    - Out of range values"
    echo ""
    print_info "After the demo completes, you can:"
    echo "  - Browse the FROST-Server web UI"
    echo "  - Re-run validation: docker compose run validator --config config/config.demo.yaml validate-all --include-valid"
    echo "  - Stop the demo: docker compose down"
    echo "  - Clean up volumes: docker compose down -v"
    echo ""
}

# Main script
main() {
    print_header "OGC SensorThings API Schema Validator Demo"

    # Check requirements
    check_requirements

    # Show demo information
    show_info

    # Ask for confirmation
    read -p "$(echo -e ${YELLOW}Press Enter to start the demo, or Ctrl+C to cancel...${NC})"

    # Clean up previous runs
    cleanup

    # Start the demo
    start_demo

    # Show final message
    echo ""
    print_header "Demo Complete"
    print_success "The validation has finished!"
    echo ""
    print_info "To clean up the demo environment:"
    echo "  docker compose down -v"
    echo ""
}

# Run main function
main
