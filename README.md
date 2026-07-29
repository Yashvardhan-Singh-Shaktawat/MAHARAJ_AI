# 🥗 MAHARAJ AI | Wellness Architect & AI Chef

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Scikit-Learn](https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Vercel](https://img.shields.io/badge/Vercel-Deployment_Ready-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)
[![License](https://img.shields.io/badge/License-MIT-blue.style=for-the-badge)](#license)

> **MAHARAJ AI** is an intelligent, machine learning-driven personalized nutrition advisor and AI Chef. It leverages TF-IDF natural language vectorization, cosine similarity, multi-variable nutritional constraints, and multi-lingual translation to generate tailored diet plans, suggest optimal recipes based on ingredients, and accommodate strict user health conditions and allergies.

---

## 🌟 Key Features

### 🍲 1. AI Recipe & Food Recommender
- **Natural Language Query Matching**: Utilizes `TfidfVectorizer` and Cosine Similarity across a dataset of over **7,400+ Indian & Global recipes**.
- **Allergen & Preference Exclusion**: Automatically filters out specified allergens (e.g., nuts, dairy, gluten, mushrooms) in real-time.
- **Detailed Culinary Instructions**: Provides recipe names, cuisine origin, full ingredient lists, calorie count, and step-by-step cooking instructions.

### 📊 2. Smart Diet & Meal Planner
- **Goal-Oriented Recommendations**: Tailored plans for weight loss (low-calorie, high-protein) and weight gain (high-calorie, high-protein).
- **Health-Aware Filters**: Integrated logic for sugar issues and diabetic safety (filters sugar < 5g, carbs < 40g).
- **Nutritional Insights**: Returns precise macro breakdowns (calories, protein, carbs).

### 🌐 3. Multi-Lingual Support
- Dynamic translation engine powered by `deep-translator` allowing users to query and receive meal plans in multiple languages.

### 👤 4. User Profiles & Analytics Dashboard
- User authentication (Sign Up / Login / Logout).
- Track liked/disliked ingredients and personal health preferences.
- Visual dashboard for recipe history and macro progress.

### ⚡ 5. Serverless & Vercel Ready
- Configured with `vercel.json` and WSGI serverless entry points for one-click deployment.

---

## 🏗️ Architecture & ML Engine Overview

```
                      +-----------------------------+
                      |       User Interface        |
                      |  (HTML5/CSS3/JS Web App)    |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |       Django Gateway        |
                      |    (urls.py / views.py)     |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |         ML Engine           |
                      |  (TF-IDF + Cosine Similarity|
                      |   + Macro Nutri-Filtering)  |
                      +--------------+--------------+
                                     |
           +-------------------------+-------------------------+
           |                         |                         |
           v                         v                         v
+--------------------+    +--------------------+    +--------------------+
| 7,400+ Recipe CSVs |    | Steps JSON Data    |    |  Deep Translator   |
| (Indian + World)   |    | (Cooking Guides)   |    |    Translation     |
+--------------------+    +--------------------+    +--------------------+
```

---

## 🛠️ Tech Stack

- **Backend Framework**: [Django 5.x / 6.0](https://www.djangoproject.com/)
- **Machine Learning**: `scikit-learn`, `pandas`, `numpy`, `joblib`, `nltk`
- **Translation API**: `deep-translator`
- **Frontend**: HTML5, Vanilla CSS3, JavaScript, Django Templates
- **Database**: SQLite3 (Local / Dev)
- **Deployment**: Vercel (`@vercel/python` serverless)

---

## ⚡ Quick Start & Local Setup

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Yashvardhan-Singh-Shaktawat/MAHARAJ_AI.git
   cd MAHARAJ_AI
   ```

2. **Create & Activate Virtual Environment**
   - **Windows**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

6. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000/
   ```

---

## 🌐 Application Routes & API Endpoints

| Route | Method | Description |
|---|---|---|
| `/` | `GET` | Main Landing & Home Page |
| `/dashboard/` | `GET` | User Analytics & Preferences Dashboard |
| `/diet/` | `GET` | AI Diet Planner Chat Interface |
| `/food/` | `GET` | AI Recipe Recommendation Chat Interface |
| `/login/` & `/signup/` | `GET / POST` | User Authentication |
| `/api/diet/` | `POST` | JSON API endpoint for diet recommendations |
| `/api/food/` | `POST` | JSON API endpoint for recipe search |
| `/api/feedback/` | `POST` | Recipe feedback (Like / Dislike) |

---

## ☁️ Vercel Deployment

This repository includes a pre-configured `vercel.json` file for effortless serverless deployment on Vercel.

### Deploying via Vercel Dashboard
1. Push your changes to GitHub.
2. Go to [Vercel New Project](https://vercel.com/new).
3. Import the repository **`Yashvardhan-Singh-Shaktawat/MAHARAJ_AI`**.
4. Leave Framework Preset as **Other**.
5. Click **Deploy**.

---

## 📁 Repository Structure

```
MAHARAJ_AI/
├── MAHARAJ_AI/
│   ├── settings.py         # Django Settings & Static Root
│   ├── urls.py             # Root Routing
│   └── wsgi.py             # Serverless WSGI Entrypoint
├── recommendations/
│   ├── data/               # Recipe CSVs & JSON Datasets (7,400+ entries)
│   ├── templates/          # HTML UI Templates
│   ├── ml_engine.py        # Core Machine Learning & TF-IDF Logic
│   ├── models.py           # User Preferences & Feedback Models
│   ├── urls.py             # Application URLs
│   └── views.py            # Route Controllers & API Endpoints
├── manage.py               # Django Management Script
├── requirements.txt        # Dependencies
├── vercel.json             # Vercel Deployment Configuration
├── .gitignore              # Git Ignore Directives
└── README.md               # Project Documentation
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more details.

---

<p center>Crafted with ❤️ by <b>Yashvardhan Singh Shaktawat</b></p>
