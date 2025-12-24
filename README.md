# Chance Store — Admin Panel & API (Overview)

This repository contains the Django-based admin panel and API for Chance Store. The project provides a backend for managing products, inventory, orders, offline sales, suppliers, invoices, and services (service bookings). This repository does NOT include a customer-facing storefront — interactions are via the admin UI and API.

## Quick summary
- Purpose: Admin dashboard + API for managing store operations.
- Scope: Admin users (staff/superuser) manage data; customers can be created/selected from admin or use API endpoints.

## Key Features / Flows
- Users & Roles: Django users with `UserRole` and `UserProfile` for admin/customer differentiation.
- Products & Inventory: Categories, products, variants, stock, cost/price and per-product shipping.
- Orders & Payments: Checkout, order snapshots (price, shipping, tax), invoice generation, payment status handling.
- Offline Sales: Manual/physical sales entry with payments and outstanding balance tracking.
- Suppliers & Purchases: Supplier records, purchases and purchase invoices.
- Services & Bookings: Service types (e.g. Electrician, Plumber) and customer bookings with dates and status.
- Notifications: Simple notification records for important events.

## Project layout (important folders)
- `ecommerce/` — Django project settings and root.
- `dashboard/` — core app that implements admin views, models, templates and urls.
- `templates/dashboard/` — admin UI templates (pages, components, sidebar, sales pages, services pages).
- `api/` — API routes and views (exposed under `/api/`).
- `media/` and `static/` — uploaded files and static assets.

## Setup (local development)
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Run migrations and create a superuser:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

4. Run the development server:

```bash
python manage.py runserver
```

## Where to access the admin UI
- Django admin: `/admin/` (default Django admin)
- Custom admin dashboard pages: `/admin-dashboard/` (main entry for the project admin UI)

Example admin pages added in this project (URLs under the dashboard app):
- Services: `/admin-dashboard/services/`
- Service Bookings: `/admin-dashboard/service-bookings/`
- Sales (offline): `/admin-dashboard/sales/`

## API
- The project exposes API endpoints under `/api/`. Inspect the `api/` app to see available routes and representations.
- The API is intended for integrations and mobile/admin clients; authentication is configured in the project settings (check `ecommerce/settings.py`).

## Templates & UI
- Admin UI follows a consistent layout under `templates/dashboard/components/` (sidebar, base layout). Sales and Services pages share table and form styles.

---

