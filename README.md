# 🏠 LuxeEstate AI – Real Estate Chatbot

A production-ready AI chatbot for real estate agencies built with **Streamlit**, **LangChain**, and **Groq**.

---

## ✨ Features

| Feature | Description |
|---------|------------|
| 🤖 AI Chat | LLM-powered assistant using Groq (ultra-fast inference) |
| 🏘️ Property Search | Search by city, type, price, bedrooms, and location |
| 📅 Site Visit Booking | Collect user info and schedule visits → saved to CSV |
| 📞 Consultation Booking | Book expert call slots → saved to CSV |
| 💰 EMI Calculator | Instant home loan EMI calculations |
| 📋 Leads CRM | View, filter, export all leads from a dashboard |
| 🏘️ Property Manager | Add/edit/delete properties via UI or CSV upload |
| 🌐 Embeddable | Embed on any website via iframe |

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/yourusername/real-estate-chatbot
cd real-estate-chatbot
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get a free Groq API key at: https://console.groq.com

### 3. Run
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
real_estate_chatbot/
├── app.py               # Main Streamlit UI (Chat + CRM + Settings)
├── chatbot.py           # LangChain + Groq agent engine
├── config.py            # All configuration (reads from .env)
├── utils/
│   ├── data_manager.py  # CSV read/write operations
│   └── tools.py         # LangChain tools (search, book, EMI, etc.)
├── data/
│   ├── properties.csv   # Your property listings (EDITABLE)
│   └── leads.csv        # Auto-generated leads storage
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🏘️ Managing Properties

Edit `data/properties.csv` directly, or use the **Properties** page in the app:
- Add/edit/delete via table editor
- Import a CSV file
- Download the CSV template

### CSV Columns
| Column | Description |
|--------|-------------|
| id | Unique ID (P001, P002…) |
| name | Property name |
| type | Apartment / Villa / Plot / Commercial / Studio |
| location | Locality/Area |
| city | City |
| price | Price in ₹ |
| bedrooms | Number of bedrooms |
| bathrooms | Number of bathrooms |
| area_sqft | Area in sq.ft |
| amenities | Comma-separated list |
| status | Available / Sold / Pending |
| description | Short description |

---

## 📊 Leads Data

All chatbot bookings are auto-saved to `data/leads.csv`. You can:
- View in the **Leads** dashboard
- Filter by type / status
- Export as CSV
- Update lead status (New → Contacted → Completed)

---

## 🌐 Deploy & Embed

### Deploy to Streamlit Cloud (Free)
1. Push to GitHub
2. Visit https://share.streamlit.io
3. Connect repo → Add `GROQ_API_KEY` in Secrets
4. Deploy!

### Embed on Any Website
```html
<iframe src="https://your-app.streamlit.app?embedded=true"
  width="400" height="600"
  style="border:none; border-radius:16px;">
</iframe>
```

---

## 🎨 Customization (For Freelancing)

To customize for a client, just update `.env`:
```bash
COMPANY_NAME=ABC Realtors
APP_TITLE=ABC Realtors AI
AGENT_NAME=Nova
COMPANY_PHONE=+91-9999999999
COMPANY_EMAIL=hello@abcrealtors.com
```

Replace `data/properties.csv` with the client's property data.

---

## 🔑 Groq Models

| Model | Best For |
|-------|----------|
| `llama-3.3-70b-versatile` | Best quality (default) |
| `mixtral-8x7b-32768` | Long conversations |
| `gemma2-9b-it` | Fastest, lightweight |

---

## 📜 License
MIT License – free to use for client projects.
