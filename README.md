# AI-Powered FSSAI Compliance Checker

An intelligent food label analysis tool that uses **Claude Vision AI** to extract data from food product labels and automatically checks compliance against **FSSAI (Food Safety and Standards Authority of India)** regulations.

Built as part of the Biosafety & Food Safety Experiential Learning project at RVCE, 2025-26.

---

## Features

### AI-Powered Label Extraction
- Upload a photo of any food label (JPG, PNG, WebP)
- Claude Vision reads the label and extracts structured data: ingredients, additives, allergens, nutritional info, claims, FSSAI license, dates, and more
- No OCR pipeline needed — single-shot multimodal extraction

### 5-Module Compliance Engine
| Module | What It Checks |
|--------|---------------|
| **Additives** | Cross-references extracted additives against FSSAI's permitted additives database (75 entries). Flags banned, restricted, or unrecognized additives. |
| **Allergens** | Detects allergen-triggering ingredients using 90+ keywords across 8 categories (Milk, Eggs, Peanuts, Tree Nuts, Soy, Wheat, Fish, Crustaceans). Flags undeclared allergens. |
| **Claims** | Validates nutritional claims ("Sugar Free", "High Protein", "Low Fat", etc.) against FSSAI threshold rules. Catches misleading claims. |
| **License** | Validates FSSAI license number format (14-digit check). |
| **Labelling** | Checks for mandatory label fields: product name, ingredients, net weight, dates, vegetarian mark, nutritional info, manufacturer details. |

### Risk Scoring
- Weighted scoring across all 5 modules (Allergens: 30%, Additives: 25%, Claims: 20%, Labelling: 15%, License: 10%)
- Overall score 0-100 with grade (A/B/C/F)
- Per-module scores with critical/warning counts

### Rich Dashboard
- **Circular Score Gauge** — animated SVG gauge with color-coded arc
- **Module Score Cards** — 5 cards with mini progress bars
- **Compliance Tabs** — browse findings by module with issue count badges
- **Ingredient Panel** — color-coded risk dots (green/yellow/red) for each ingredient
- **Allergen Cross-Reference Table** — detected vs. declared allergens with compliance status
- **Severity-Sorted Findings** — CRITICAL > WARNING > INFO with filter pills
- **What-If Simulator** — toggle ingredients/additives/allergens/claims, re-run compliance, see score change
- **PDF Report Download** — generates a professional multi-page compliance audit report

### Other
- Animated loading pipeline showing analysis steps
- 10MB file size limit with clear error messages
- Responsive design (mobile, tablet, desktop)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI** | Claude Sonnet (Anthropic) — multimodal vision for label extraction |
| **Backend** | Python, FastAPI, Pydantic, SQLite |
| **Frontend** | React 19, Vite, Tailwind CSS 4 |
| **PDF Generation** | jsPDF |
| **HTTP Client** | Axios |

---

## Project Structure

```
BiosafetyEL/
├── backend/
│   ├── main.py                          # FastAPI app with CORS
│   ├── requirements.txt
│   ├── .env                             # ANTHROPIC_API_KEY (not in repo)
│   ├── models/
│   │   └── schemas.py                   # Pydantic models (LabelData, ComplianceFinding, RiskScore, etc.)
│   ├── routers/
│   │   ├── analyze.py                   # POST /api/analyze — upload & full analysis
│   │   └── simulate.py                  # POST /api/simulate — what-if scenario testing
│   ├── services/
│   │   ├── nlp_parser.py                # Claude Vision integration
│   │   ├── compliance_checker.py        # 5-module compliance engine
│   │   └── risk_scorer.py               # Weighted risk scoring
│   └── database/
│       ├── init_db.py                   # SQLite schema creation
│       ├── seed_data.py                 # FSSAI additive/allergen/claims data
│       └── fssai_compliance.db          # Pre-seeded SQLite database
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js                   # Dev proxy: /api → localhost:8000
│   ├── index.html
│   └── src/
│       ├── App.jsx                      # Root component (upload/dashboard toggle)
│       ├── main.jsx                     # Entry point
│       ├── index.css                    # Tailwind imports
│       ├── services/
│       │   └── api.js                   # Axios client (analyzeLabel, runSimulation)
│       └── components/
│           ├── UploadPage.jsx           # Drag-drop upload with animated loader
│           ├── Dashboard.jsx            # Orchestrator — composes all dashboard components
│           ├── ScoreGauge.jsx           # Circular SVG score gauge
│           ├── ComplianceTabs.jsx       # 5-tab module findings browser
│           ├── IngredientPanel.jsx      # Color-coded ingredient risk indicators
│           ├── FlaggedIssues.jsx        # Severity-sorted filterable findings
│           ├── AllergenTable.jsx        # Allergen detection vs. declaration table
│           ├── ScenarioSimulator.jsx    # What-if modification UI
│           ├── ReportDownload.jsx       # PDF report generation (jsPDF)
│           └── AnimatedLoader.jsx       # Pipeline step loading animation
│
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Clone the repository

```bash
git clone https://github.com/Arun-Sanjay/AI-Powered-FSSAI-Compliance-Checker.git
cd AI-Powered-FSSAI-Compliance-Checker
```

### 2. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Initialize and seed the database (skip if `fssai_compliance.db` already exists):

```bash
python database/init_db.py
python database/seed_data.py
```

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

### 3. Set up the frontend

```bash
cd ../frontend
npm install
npm run dev
```

### 4. Open the app

Navigate to **http://localhost:5173** in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze` | Upload a food label image. Returns full analysis (extracted data + compliance findings + risk score). |
| `POST` | `/api/simulate` | Send label data with modifications (remove ingredients, add allergens, etc.) and get re-calculated compliance results. |
| `GET` | `/api/additives` | Browse the full FSSAI permitted additives database. |
| `GET` | `/api/allergens` | Browse allergen keyword mappings. |

### Example: Analyze a label

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@label.jpg"
```

### Example: Run a simulation

```bash
curl -X POST http://localhost:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "label_data": { ... },
    "modifications": {
      "remove_ingredients": ["Sodium Benzoate"],
      "add_allergen_declaration": ["Milk"]
    }
  }'
```

---

## How It Works

```
┌──────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  Upload Image │────>│  Claude Vision    │────>│  Structured JSON   │
│  (Frontend)   │     │  (nlp_parser.py)  │     │  (LabelData)       │
└──────────────┘     └──────────────────┘     └────────┬───────────┘
                                                        │
                                                        v
                                              ┌────────────────────┐
                                              │  Compliance Engine │
                                              │  5 modules check   │
                                              │  against FSSAI DB  │
                                              └────────┬───────────┘
                                                        │
                                                        v
                                              ┌────────────────────┐
                                              │  Risk Scorer       │
                                              │  Weighted score +  │
                                              │  grade + summary   │
                                              └────────┬───────────┘
                                                        │
                                                        v
                                              ┌────────────────────┐
                                              │  Dashboard UI      │
                                              │  Gauge, tabs,      │
                                              │  simulator, PDF    │
                                              └────────────────────┘
```

1. **Upload** — User uploads a food label photo
2. **Extract** — Claude Vision analyzes the image and returns structured JSON (product name, ingredients, additives, allergens, nutritional info, claims, license, dates)
3. **Check** — Five compliance modules cross-reference the extracted data against FSSAI regulations stored in SQLite
4. **Score** — A weighted risk score (0-100) is calculated with per-module breakdowns
5. **Display** — The rich dashboard shows the score gauge, findings by module, ingredient risk levels, allergen table, and all findings sorted by severity
6. **Simulate** — Users can toggle ingredients/allergens/claims and re-run compliance to see how changes affect the score
7. **Export** — A PDF compliance audit report can be downloaded

---

## FSSAI Regulations Referenced

- **FSS (Packaging and Labelling) Regulations, 2011** — Mandatory label fields, allergen declaration requirements
- **FSS (Food Products Standards and Food Additives) Regulations, 2011** — Permitted additives list, E-codes, maximum limits
- **FSS (Advertising and Claims) Regulations, 2018** — Nutritional claim thresholds (Sugar Free, Low Fat, High Protein, etc.)
- **FSSAI Licensing and Registration** — 14-digit license number format validation

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
