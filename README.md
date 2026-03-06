# ✦ StyleSense — Generative AI-Powered Fashion Recommendation System

A sophisticated, hackathon-ready fashion intelligence platform powered by Google Gemini AI with a Liquid Glass / Glassmorphism UI theme.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Step 1: Clone / Extract the Project
```bash
cd stylesense
```

### Step 2: Create a Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys
```bash
cp .env.example .env
```
Edit `.env` and add your **Gemini API Key**:
```
GEMINI_API_KEY=your_key_here
```
> Get a free key at: https://aistudio.google.com/app/apikey

### Step 5: Run the App
```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **AI Style Me** | Personalized outfit recommendations based on body type, occasion, budget |
| **Outfit Analyzer** | Upload any outfit photo for instant AI visual feedback |
| **Trend Intelligence** | 2024-2025 fashion trend reports personalized to your aesthetic |
| **Style DNA Quiz** | 5-question quiz to discover your unique fashion persona |
| **Dashboard** | Analytics, capsule wardrobe builder, color pairing tool |

---

## 🏗️ Project Structure

```
stylesense/
├── app.py                 # Flask backend + all API routes
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── templates/
│   └── index.html         # Main SPA template
└── static/
    ├── css/
    │   └── style.css      # Glassmorphism theme + all styles
    └── js/
        └── app.js         # Frontend logic + API calls
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/recommend` | POST | Get personalized outfit recommendation |
| `/api/analyze-outfit` | POST | Analyze uploaded outfit image |
| `/api/trends` | POST | Get fashion trend report |
| `/api/style-quiz` | POST | Calculate style persona from quiz answers |
| `/api/wardrobe-essentials` | POST | Get capsule wardrobe items |
| `/api/color-match` | POST | Get color pairing suggestions |
| `/api/stats` | GET | Get platform statistics |

---

## 🎨 Without API Key

The app works **fully without an API key** using smart fallback recommendations based on a curated fashion knowledge base. Adding the Gemini key unlocks:
- AI-generated, hyper-personalized recommendations
- Real image vision analysis
- Personalized trend reports
- AI capsule wardrobe guides

---

## 🏆 Hackathon Highlights

- **Liquid Glass UI** — Multi-layered glassmorphism with animated orbs
- **Zero dependencies on external CSS frameworks** — Pure custom CSS
- **AI-powered + offline fallback** — Always functional
- **Responsive** — Desktop & mobile optimized
- **Drag & Drop** image upload
- **Live stat animations** on dashboard
- **Real-time toast notifications**
- **Canvas donut chart** — No chart library needed
- **Style DNA Quiz** — Interactive multi-step personality quiz
- **Color pairing engine** — Fashion color theory built-in

---

## 📱 Responsive Design

Tested on: Desktop (1440px), Laptop (1024px), Tablet (768px), Mobile (375px)

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Flask-CORS
- **AI**: Google Gemini 1.5 Flash (Vision + Text)
- **Frontend**: Vanilla HTML, CSS, JavaScript
- **UI Theme**: Custom Liquid Glass / Glassmorphism
- **Fonts**: Cormorant Garamond + DM Sans (Google Fonts)
