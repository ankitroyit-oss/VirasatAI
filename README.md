# VirasatAI — AI-Powered Indian Heritage Discovery 🇮🇳

> **"Point. Discover. Experience India."**

A comprehensive cultural heritage innovation platform combining **Google Gemini Vision AI**, **Augmented Reality Camera HUD with real-time GPS & bearing calculations**, and a **rich cultural knowledge base** to create an immersive digital experience celebrating India's 5,000-year legacy.

---

## 🎯 Key Features

- 🤖 **Google Gemini Vision AI Scanner** — Point your camera at or upload an image of an Indian monument; Google Gemini Vision API identifies the site in real time, providing architectural details, historical timelines, and cultural significance.
- 🧭 **AR Viewfinder HUD (Live Geolocation & Bearing)** — Full-screen camera viewfinder overlay with live GPS coordinates (Latitude & Longitude), compass orientation heading, and mathematical relative bearing and distance calculations (via Haversine formula) to known landmarks.
- 🛍️ **Authentic GI Products Showcase** — Catalog of India's Geographical Indication (GI) tagged crafts, textiles, and artifacts (Pashmina, Banarasi Silk, Channapatna Toys, etc.) with exact verified prices (all strictly under ₹10,000) and artisan provenance.
- 🗺️ **Interactive India Map** — Click any state to explore its folk dances, classical music, culinary traditions, festivals, and indigenous arts.
- ⏳ **Cultural Timeline** — Interactive historical voyage across 9 eras, from the Indus Valley Civilization to Modern India.
- 🎨 **Heritage Gallery** — Curated showcase of iconic UNESCO World Heritage sites and monuments with high-resolution imagery and architectural breakdowns.
- 🧩 **Heritage Quiz** — 52 questions across 5 categories with real-time scoring, cultural mastery badges, and celebratory animations.
- 📸 **Dataset Collector (`image-collector.html`)** — Dedicated utility for collecting, curating, and exporting image datasets for machine learning training.
- 📊 **Architecture & Flow Visualizer (`diagrams.html`)** — Interactive visual documentation of system workflows, data pipelines, and component architecture.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Vision Engine** | Google Gemini Vision API (`gemini-2.5-flash` / Google AI Studio) |
| **Spatial / AR** | HTML5 Geolocation API, DeviceOrientation API, Haversine & Azimuth Algorithms |
| **Frontend Core** | Vanilla HTML5, Modern JavaScript (ES6+ Modules) |
| **Styling** | Vanilla CSS3 (Custom Properties, Glassmorphism, Responsive Grid/Flexbox) |
| **Mapping** | Custom Interactive SVG-based India Vector Map |
| **Typography** | Google Fonts (*Outfit* & *Noto Serif Devanagari*) |
| **Data Layer** | Client-side Modular JavaScript Knowledge Base |

---

## 📁 Project Structure

```text
VirasatAI/
├── index.html                  # Main application UI (Scanner, HUD, Map, Gallery, Quiz, GI)
├── image-collector.html        # Cultural heritage dataset collection & training utility
├── diagrams.html               # Visual system architecture & pipeline diagrams
├── README.md                   # Project documentation & structure
├── images/                     # Curated high-resolution image assets
│   ├── taj-mahal.jpg
│   ├── hampi.jpg
│   ├── qutb-minar.jpg
│   ├── meenakshi-temple.jpg
│   ├── kashmir-pashmina.jpg
│   ├── varanasi-banarasi-silk.jpg
│   ├── channapatna-toys.jpg
│   └── ... (40+ heritage site & GI product assets)
└── src/
    ├── app.js                  # Core controller: Gemini Vision, AR HUD, GPS, UI logic
    ├── styles/
    │   ├── variables.css       # Design tokens, color palette, glassmorphism vars
    │   └── index.css           # Complete responsive stylesheet & AR HUD styles
    └── data/
        ├── heritageSites.js    # 20 heritage sites with GPS coordinates, history & stories
        ├── giProducts.js       # Authentic GI products with verified pricing (< ₹10,000)
        ├── indianStates.js     # Cultural database across 29 Indian states & UTs
        ├── quizQuestions.js    # 52 heritage trivia quiz questions across 5 categories
        └── timeline.js         # 9 historical eras from Indus Valley to Modern India
```

---

## 🚀 Getting Started

No heavy build steps or bundlers required. Run with any local static HTTP server:

```bash
# Using Python 3
python3 -m http.server 3000

# Or using Node.js / npx
npx serve .
```

Then open **http://localhost:3000** in your browser.

### 🔑 Configuring Google Gemini Vision API

1. Obtain a free API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Launch VirasatAI and navigate to the **AI Scanner** section.
3. Click the **⚙️ API Key** button to enter your key and click **Test & Save**.
4. The key is saved securely in your browser's `localStorage` and the setup button auto-hides once configured.

---

## 🎨 Design System

- **Color Palette**: Saffron (`#FF9933`), Deep Indigo (`#0B1021`), Royal Gold (`#FFD700`), Temple Red (`#8B0000`), Peacock Teal (`#005F73`)
- **Aesthetic**: Premium dark mode with frosted glassmorphism overlays (`backdrop-filter`)
- **Typography**: Google Fonts *Outfit* (Modern UI) + *Noto Serif Devanagari* (Cultural accents)
- **Micro-Interactions**: Rotating mandalas, HUD target locks, particle confetti, and smooth state transitions

---

## 📜 License

Student Innovation Project — 2026

---

*विरासत बचाओ, संस्कृति अपनाओ — Save the Heritage, Embrace the Culture*
