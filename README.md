# 💳 Paystack SaaS API

> A white-label payment API that lets your clients accept payments through Paystack without managing API keys directly.

Your clients get API keys from you. They make payment requests to your API. You handle all Paystack integration behind the scenes.

---

## 🏗️ Architecture

```
Client's App → Your API (with your API key) → Paystack → Webhooks back to your API
```

**Example Flow:**
1. Your client "S" gets API key `pk_abc123...` from your admin panel
2. S's website calls your API: `POST /api/payments/initialize/` with her API key
3. Your API talks to Paystack using YOUR Paystack credentials
4. Customer completes payment on Paystack
5. Paystack sends webhook to your API
6. Your API stores transaction and notifies S

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Mortoti/paystack-saas.git
cd paystack-saas
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file:

```env
SECRET_KEY=your-django-secret-key
PAYSTACK_SECRET_KEY=your-paystack-secret-key
DEBUG=True
```

Get Paystack key: [Dashboard](https://dashboard.paystack.com/) → Settings → API Keys

### 4. Set Up Database

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API running at `http://127.0.0.1:8000/` 🚀

---

## 🔑 Generate API Keys

Go to `http://127.0.0.1:8000/admin/` → **API Keys** → **Add API Key**

The key auto-generates (starts with `pk_`). Give this to your clients.

---

## 📡 API Endpoints

All requests require: `X-API-Key: pk_your_key` header

### Initialize Payment
```http
POST /api/payments/initialize/
Content-Type: application/json
X-API-Key: pk_your_key

{
  "email": "customer@example.com",
  "amount": 5000
}
```

### Verify Payment
```http
GET /api/payments/verify/{reference}/
X-API-Key: pk_your_key
```

### List Transactions
```http
GET /api/payments/transactions/
X-API-Key: pk_your_key
```



---

## 🚀 Deployment

### Heroku
```bash
heroku create your-app-name
heroku config:set PAYSTACK_SECRET_KEY=your_key
heroku config:set SECRET_KEY=your_secret
heroku config:set DEBUG=False
git push heroku main
heroku run python manage.py migrate
```

### Railway
1. Push to GitHub
2. Connect repo on [Railway.app](https://railway.app)
3. Add environment variables
4. Deploy automatically

### Configure Webhook
After deployment, add webhook URL in Paystack dashboard:
`https://your-domain.com/api/payments/webhook/`

---

## 📧 Support

- **Email:** mortoti.dev@gmail.com


---

<div align="center">

**Built by [Mortoti Jephthah](https://github.com/Mortoti)**

</div>
