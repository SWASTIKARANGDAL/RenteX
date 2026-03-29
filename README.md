<<<<<<< HEAD
<<<<<<< HEAD
# RenteX
=======
# RenteX — Electronics Rental Platform

A **production-ready, full-featured Django startup platform** for renting electronics. Renters can find and book laptops, cameras, phones, gaming consoles, drones, and more from verified owners near them.

---

## ✨ Features

| Category | Details |
|---|---|
| **Authentication** | Signup/login, email verification, password reset, Google OAuth (allauth), role-based (Renter / Owner) |
| **Product Management** | List electronics with images, pricing (daily/weekly/monthly), condition, location, specs |
| **Booking System** | Real-time availability, date picker, accept/reject, order history, printable invoices |
| **Payments** | Razorpay + Stripe integration, demo payment mode for testing |
| **Search & Filter** | By category, city, price range, condition, rating; sort options |
| **Reviews & Ratings** | Post-rental reviews, star ratings, owner/product profiles |
| **Notifications** | In-app + email notifications for all booking events |
| **Dashboards** | Separate owner/renter dashboards with analytics |
| **Admin Panel** | Full Django admin with custom views for users, products, bookings, payments |
| **REST API** | DRF-powered API for availability checks, price calculation, wishlist |
| **Wishlist** | Save favourite products |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- pip

### Option A — Automated Setup (Recommended)

```bash
# 1. Clone / unzip the project
cd rentex

# 2. Run the setup script
chmod +x setup.sh
./setup.sh

# 3. Start the server
source venv/bin/activate
python manage.py runserver
```

Open **http://localhost:8000** 🎉

### Option B — Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your values (email, payment keys, etc.)

# 4. Run migrations
python manage.py makemigrations accounts products bookings payments reviews notifications core
python manage.py makemigrations
python manage.py migrate

# 5. Configure Sites framework
python manage.py shell -c "
from django.contrib.sites.models import Site
s, _ = Site.objects.get_or_create(id=1)
s.domain = 'localhost:8000'; s.name = 'RenteX'; s.save()
"

# 6. Seed sample data
python manage.py seed_data

# 7. Collect static files
python manage.py collectstatic --no-input

# 8. Start the server
python manage.py runserver
```

---

## 🔑 Demo Credentials

| Role    | Email                  | Password   |
|---------|------------------------|------------|
| Admin   | admin@rentex.com       | admin123   |
| Owner   | owner@rentex.com       | owner123   |
| Owner 2 | owner2@rentex.com      | owner123   |
| Renter  | renter@rentex.com      | renter123  |
| Renter 2| renter2@rentex.com     | renter123  |

**Admin Panel:** http://localhost:8000/admin/

---

## 🗂 Project Structure

```
rentex/
├── apps/
│   ├── accounts/        # User model, auth, profiles, dashboards
│   ├── products/        # Product listing, categories, images, wishlist
│   ├── bookings/        # Booking flow, status management, invoices
│   ├── payments/        # Razorpay/Stripe integration
│   ├── reviews/         # Product & owner reviews
│   ├── notifications/   # In-app + email notifications
│   └── core/            # Home, about, API URLs, context processors, seed command
├── templates/
│   ├── base.html        # Master layout (navbar, footer, toasts)
│   ├── account/         # allauth overrides (login, signup)
│   ├── core/            # Home, about, how-it-works, contact
│   ├── dashboard/       # Owner & renter dashboards
│   ├── products/        # List, detail, form, my-products, wishlist
│   ├── bookings/        # Create, detail, list, invoice
│   ├── payments/        # Checkout, history
│   ├── reviews/         # Create review
│   ├── notifications/   # Notification list
│   ├── emails/          # Email templates
│   └── partials/        # Reusable components (product card)
├── static/
│   ├── css/main.css     # Custom styles
│   └── js/main.js       # Custom JavaScript
├── rentex/
│   ├── settings.py      # Full configuration
│   ├── urls.py          # Root URL config
│   ├── wsgi.py
│   └── celery.py        # Async task config
├── manage.py
├── requirements.txt
├── .env.example
├── setup.sh             # One-click setup
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```

---

## ⚙️ Configuration (.env)

Edit `.env` to configure:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (console for dev, SMTP for prod)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Payment Gateway
PAYMENT_GATEWAY=razorpay
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
```

---

## 💳 Payment Integration

### Razorpay (Recommended for India)
1. Create an account at [dashboard.razorpay.com](https://dashboard.razorpay.com)
2. Get test API keys from Settings → API Keys
3. Set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in `.env`
4. Set `PAYMENT_GATEWAY=razorpay`

### Stripe
1. Create an account at [dashboard.stripe.com](https://dashboard.stripe.com)
2. Get test keys from Developers → API Keys
3. Set `STRIPE_PUBLISHABLE_KEY` and `STRIPE_SECRET_KEY`
4. Set `PAYMENT_GATEWAY=stripe`

### Demo Mode
For testing without real payment keys, use the **"[DEMO] Simulate Successful Payment"** button on the checkout page. No real money is charged.

---

## 📧 Email Setup

### Development (console output)
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production (Gmail SMTP)
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```
> Generate an App Password from your Google Account → Security → App Passwords

---

## 🐳 Docker Deployment

```bash
# 1. Build and start all services
docker-compose up --build

# 2. Run migrations inside container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_data

# 3. Access at http://localhost:80
```

---

## 🌐 Production Deployment

### On Ubuntu / Debian server

```bash
# Install system dependencies
sudo apt update && sudo apt install python3-pip python3-venv nginx

# Clone & setup
git clone <your-repo> /var/www/rentex
cd /var/www/rentex
./setup.sh

# Update .env for production
nano .env
# Set: DEBUG=False, ALLOWED_HOSTS=yourdomain.com, strong SECRET_KEY

# Configure Gunicorn as a systemd service
sudo nano /etc/systemd/system/rentex.service
```

**Gunicorn systemd service:**
```ini
[Unit]
Description=RenteX Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/rentex
ExecStart=/var/www/rentex/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/run/rentex.sock \
          rentex.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable rentex && sudo systemctl start rentex
```

### Nginx configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ { alias /var/www/rentex/staticfiles/; }
    location /media/  { alias /var/www/rentex/media/; }

    location / {
        proxy_pass http://unix:/run/rentex.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Add HTTPS with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🔌 REST API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/check-availability/<slug>/` | GET | Check product availability for dates |
| `/api/calculate-price/` | GET | Calculate rental price for date range |
| `/api/wishlist/<slug>/` | POST | Toggle wishlist for a product |
| `/api/notifications/unread/` | GET | Get unread notification count |
| `/api/notifications/mark-all-read/` | POST | Mark all notifications as read |
| `/payments/webhook/razorpay/` | POST | Razorpay webhook handler |

---

## 🔧 Key Django Admin Features

- **Users** → Manage all users, verify accounts, change roles
- **Products** → Full CRUD, feature/unfeature, bulk availability toggle
- **Bookings** → Confirm/complete bookings in bulk, view all transactions
- **Payments** → View payment history, gateway details
- **Reviews** → Approve/reject reviews, manage moderation
- **Notifications** → View and manage all system notifications
- **Categories** → Add/edit product categories with icons

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Django 4.2 |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Auth** | django-allauth (email + Google OAuth) |
| **Payments** | Razorpay + Stripe |
| **Frontend** | Bootstrap 5.3 + Bootstrap Icons |
| **Fonts** | Syne (display) + DM Sans (body) |
| **Async Tasks** | Celery + Redis |
| **File Storage** | Local / Django Storages (S3-compatible) |
| **API** | Django REST Framework |
| **Web Server** | Gunicorn + Nginx |
| **Container** | Docker + Docker Compose |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License. See `LICENSE` for details.

---

**Built with ❤️ for the electronics sharing economy. RenteX — Rent Smarter.**
>>>>>>> f1e5053 (Initial commit - RenteX project)
=======
# RenteX
>>>>>>> 468c5ea43f10278ff8a8bb633de0b82c9ce9a33f
