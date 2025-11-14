# 💳 Paystack SaaS API

White-label payment API for Paystack. Generate API keys for your clients, they process payments through your API, you handle everything with Paystack.

**Live:** [paystack-saas.onrender.com](https://paystack-saas.onrender.com/)

---

## Features

- 🔐 API key authentication for clients
- 💰 Multi-currency payments (default: GHS)
- 📊 Transaction tracking dashboard
- 🔔 Paystack webhook integration
- 📚 Interactive API documentation

---

## Quick Start

**1. Install**
```bash
git clone https://github.com/Mortoti/paystack-saas.git
cd paystack-saas
pip install -r requirements.txt
```

**2. Configure `.env`**
```env
SECRET_KEY=your-django-secret-key
PAYSTACK_SECRET_KEY=sk_test_xxxxx
DEBUG=True
```

**3. Run**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for docs

---

## Usage

**Generate client API keys:** Admin Panel → API Keys → Add

**Initialize payment:**
```bash
curl -X POST https://paystack-saas.onrender.com/api/payments/initialize/ \
  -H "X-API-Key: pk_xxxxx" \
  -H "Content-Type: application/json" \
  -d '{"email": "customer@example.com", "amount": 50000}'
```

**Verify payment:**
```bash
curl https://paystack-saas.onrender.com/api/payments/verify/{reference}/ \
  -H "X-API-Key: pk_xxxxx"
```

Full API docs: [paystack-saas.onrender.com](https://paystack-saas.onrender.com/)

---

## Tech Stack

Django • Django REST Framework • PostgreSQL • Paystack • Render

---

**Built by [Mortoti Jephthah](https://github.com/Mortoti)** • mortoti.dev@gmail.com
