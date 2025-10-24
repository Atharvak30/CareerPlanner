#!/bin/bash

# LinkedIn Job Scraper - Airflow Setup Script
# This script helps you quickly set up Apache Airflow for automating job scraping

set -e  # Exit on error

echo "=================================="
echo "LinkedIn Job Scraper - Airflow Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running from project directory
if [ ! -d "scrapers" ] || [ ! -d "airflow" ]; then
    print_error "Please run this script from the CareerPlanner project directory"
    exit 1
fi

print_success "Running from project directory"

# Step 1: Check prerequisites
echo ""
echo "Step 1: Checking prerequisites..."

# Check Docker
if command -v docker &> /dev/null; then
    print_success "Docker installed: $(docker --version)"
else
    print_error "Docker not found. Please install Docker first:"
    echo "  https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose installed: $(docker-compose --version)"
else
    print_error "Docker Compose not found. Please install Docker Compose:"
    echo "  https://docs.docker.com/compose/install/"
    exit 1
fi

# Step 2: Create directories
echo ""
echo "Step 2: Creating required directories..."

mkdir -p airflow/dags airflow/logs airflow/plugins airflow/config data

# Copy DAG file if not exists
if [ ! -f "airflow/dags/linkedin_job_scraper_dag.py" ]; then
    print_warning "DAG file not found in airflow/dags/"
    echo "  Please ensure linkedin_job_scraper_dag.py is in airflow/dags/"
fi

print_success "Directories created"

# Step 3: Setup environment variables
echo ""
echo "Step 3: Setting up environment variables..."

if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."

    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Created .env from .env.example"
        echo "  Please edit .env and add your LinkedIn credentials!"
    else
        # Create basic .env file
        cat > .env << EOL
# LinkedIn Credentials
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password_here

# Airflow Web UI Credentials
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin123

# Airflow UID
AIRFLOW_UID=$(id -u)
EOL
        print_success "Created .env file"
        print_warning "Please edit .env and add your LinkedIn credentials!"
    fi

    # Check if credentials are set
    if grep -q "your_email@example.com" .env; then
        print_error "LinkedIn credentials not set in .env file!"
        echo "  Edit .env and replace:"
        echo "    - LINKEDIN_EMAIL with your LinkedIn email"
        echo "    - LINKEDIN_PASSWORD with your LinkedIn password"
        echo ""
        read -p "Press Enter after updating .env file..."
    fi
else
    print_success ".env file exists"
fi

# Set AIRFLOW_UID for Linux/Mac
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    if ! grep -q "AIRFLOW_UID" .env; then
        echo "AIRFLOW_UID=$(id -u)" >> .env
        print_success "Added AIRFLOW_UID to .env"
    fi
fi

# Step 4: Initialize Airflow
echo ""
echo "Step 4: Initializing Airflow database..."

print_warning "This may take a few minutes..."

if docker-compose up airflow-init; then
    print_success "Airflow initialized"
else
    print_error "Airflow initialization failed"
    echo "  Check the error messages above"
    exit 1
fi

# Step 5: Start services
echo ""
echo "Step 5: Starting Airflow services..."

print_warning "Starting containers in background..."

if docker-compose up -d; then
    print_success "Airflow services started"
else
    print_error "Failed to start Airflow services"
    exit 1
fi

# Wait for services to be healthy
echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check service status
echo ""
echo "Service Status:"
docker-compose ps

# Step 6: Configuration guide
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
print_success "Airflow is now running!"
echo ""
echo "📊 Access Airflow Web UI:"
echo "   http://localhost:8080"
echo ""
echo "🔐 Login Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   (or check your .env file for custom credentials)"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure Airflow Variables (in Web UI):"
echo "   - Go to Admin → Variables"
echo "   - Add these variables:"
echo ""
echo "   Variable Name                    | Value Example"
echo "   -------------------------------- | -------------"
echo "   linkedin_job_queries             | Software Engineer,Data Scientist"
echo "   linkedin_locations               | San Francisco,New York"
echo "   linkedin_time_filter             | 24hrs (options: 24hrs, 1week, 1month, any)"
echo "   linkedin_max_jobs_per_search     | 20"
echo "   linkedin_output_dir              | /opt/airflow/data"
echo "   linkedin_archive_days            | 7"
echo ""
echo "2. Enable the DAG:"
echo "   - Find 'linkedin_job_scraper' DAG in the UI"
echo "   - Toggle it to 'On' (unpause)"
echo ""
echo "3. Trigger a test run:"
echo "   - Click the 'Play' button → 'Trigger DAG'"
echo ""
echo "4. Monitor progress:"
echo "   - Click on the DAG to see task status"
echo "   - View logs by clicking on individual tasks"
echo ""
echo "📂 Data Output:"
echo "   Scraped jobs will be saved to: ./data/"
echo ""
echo "🛠 Useful Commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo "   Restart:          docker-compose restart"
echo ""
echo "📚 Full Documentation:"
echo "   See AIRFLOW_SETUP.md for detailed instructions"
echo ""
echo "=================================="

# Open browser (optional)
read -p "Open Airflow UI in browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v open &> /dev/null; then
        open http://localhost:8080
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8080
    else
        echo "Please open http://localhost:8080 in your browser"
    fi
fi

echo ""
print_success "Setup complete! Happy scraping! 🚀"
