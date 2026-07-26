# Luma - AI-Powered Mental Wellness Web Application

Luma is a professional mental wellness companion platform designed to help users reflect, understand emotions, log moods, and interact with an empathetic AI assistant.

This repository contains the **Initial Foundation Skeleton & UI Prototype**.

## Architecture & Tech Stack

- **Frontend**: HTML5, Tailwind CSS v3 (via CDN), Vanilla JavaScript, Lucide Icons, Chart.js
- **Backend**: Python, Flask Blueprints (Modular routing)
- **Database**: MongoDB/PyMongo structure prepared (Unconnected)
- **AI Integration**: Groq API service stubs prepared (Unconnected)

## Folder Structure

```
luma/
├── app.py                # Flask application entrypoint & factory
├── config.py             # App configurations & settings
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── README.md
│
├── static/               # Client-side static assets
│   ├── css/              # Custom stylesheets (style.css)
│   ├── js/               # Global scripts (main.js)
│   ├── images/           # Images folder
│   ├── icons/            # Icons folder
│   └── audio/            # Wellness audio assets
│
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Main shared layout wrapper
│   ├── landing.html      # Product landing page
│   ├── auth/             # Authentication pages (login/signup)
│   ├── dashboard/        # User dashboard
│   ├── chat/             # AI companion interface
│   ├── journal/          # Reflection journal
│   ├── analytics/        # Chart.js visualization panels
│   ├── wellness/         # Meditation & breathing hub
│   ├── profile/          # Profile view
│   ├── settings/         # Settings panel
│   └── components/       # Sub-components & widgets
│
├── routes/               # Flask routing blueprints
│   ├── auth.py
│   ├── dashboard.py
│   └── [modules].py
│
├── services/             # Core service logic stubs
│   ├── mongo_service.py
│   ├── ai_service.py
│   └── [helpers].py
│
├── models/               # MongoDB models & doc structures
│   ├── user_model.py
│   └── [models].py
│
└── utils/                # Helper utilities
    ├── helpers.py
    ├── validators.py
    └── security.py
```

## Getting Started

### Prerequisites

- Python 3.8+ installed on your system.

### Installation

1. Clone or copy the project files to your environment.
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template:
   ```bash
   copy .env.example .env
   ```

### Running the Application

Launch the Flask development server:
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000) in your web browser.
- Navigate to the **Login** and **Sign Up** pages using the buttons in the navigation bar.
- To access the interactive dashboards/modules (Dashboard, AI Companion, Journal, Analytics, Wellness), log in with any username and password (which currently acts as a mockup session trigger).
