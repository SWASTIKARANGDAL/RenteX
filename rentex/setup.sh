#!/bin/bash
# ════════════════════════════════════════════════════════════════
#  RenteX Setup Script — Run this once to bootstrap the project
# ════════════════════════════════════════════════════════════════
set -e

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║           RenteX — Electronics Rental Platform       ║"
echo "║                  Setup Script v1.0                   ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# 1. Python version check
echo "▶ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python $python_version found ✓"

# 2. Create and activate virtual environment
echo ""
echo "▶ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Created venv/ ✓"
else
    echo "  venv/ already exists, skipping"
fi

echo "▶ Activating virtual environment..."
source venv/bin/activate

# 3. Upgrade pip
echo ""
echo "▶ Upgrading pip..."
pip install --upgrade pip -q

# 4. Install requirements
echo ""
echo "▶ Installing Python dependencies..."
pip install -r requirements.txt -q
echo "  All dependencies installed ✓"

# 5. Environment file
echo ""
echo "▶ Setting up environment file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  Created .env from template ✓"
    echo "  ⚠️  Edit .env with your actual credentials before production use"
else
    echo "  .env already exists, skipping"
fi

# 6. Run migrations
echo ""
echo "▶ Running database migrations..."
python manage.py makemigrations accounts products bookings payments reviews notifications core --no-input 2>/dev/null || true
python manage.py makemigrations --no-input
python manage.py migrate --no-input
echo "  Migrations complete ✓"

# 7. Create django sites entry
echo ""
echo "▶ Setting up Django Sites framework..."
python manage.py shell -c "
from django.contrib.sites.models import Site
site, created = Site.objects.get_or_create(id=1)
site.domain = 'localhost:8000'
site.name = 'RenteX'
site.save()
print('  Sites framework configured ✓')
" 2>/dev/null || echo "  Sites already configured"

# 8. Seed data
echo ""
echo "▶ Seeding sample data..."
python manage.py seed_data
echo "  Sample data seeded ✓"

# 9. Collect static files
echo ""
echo "▶ Collecting static files..."
python manage.py collectstatic --no-input -v 0
echo "  Static files collected ✓"

# 10. Done!
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║                  ✅ Setup Complete!                  ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║                                                      ║"
echo "║  Start server:  python manage.py runserver           ║"
echo "║  Open browser:  http://localhost:8000                ║"
echo "║                                                      ║"
echo "║  Demo Logins:                                        ║"
echo "║    Admin  → admin@rentex.com  / admin123             ║"
echo "║    Owner  → owner@rentex.com  / owner123             ║"
echo "║    Renter → renter@rentex.com / renter123            ║"
echo "║                                                      ║"
echo "║  Admin panel: http://localhost:8000/admin/           ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
