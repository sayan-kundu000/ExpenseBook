# 💰 ExpenseBook — Personal Expense Tracker with AI Financial Advisor & Transformers

An advanced, full-stack personal finance web application featuring an **offline AI Financial Advisor powered by PyTorch Multi-Head Self-Attention Transformers**. 

Built strictly adhering to the requirements of **"Python - Personal Expense Tracker Web App.pdf"** with **zero external cloud API dependencies** (no OpenAI, no Anthropic, no paid external endpoints). Everything runs 100% locally on your machine with total privacy, sub-millisecond inference, and offline capability.

---

## 🌟 Key Features

### 1. 🤖 AI Financial Advisor (100% Local Transformers, No APIs)
- **Zero API Keys Required**: Runs entirely via local PyTorch neural networks on your CPU.
- **Interactive Conversational AI**:
  - Ask free-form financial questions:
    - *"How is my overall financial health?"*
    - *"Analyze my 50/30/20 budget breakdown"*
    - *"How can I save $300 next month?"*
    - *"Forecast my spending for next month"*
    - *"Detect any spending leaks or anomalies"*
  - The AI parses your intent using Transformer Self-Attention, extracts your actual financial metrics, and generates tailored, mathematically sound advice with actionable checklists.
- **Explainable AI Attention Visualizer**:
  - Live interactive token attention inspector: type any expense note (e.g. *"Whole Foods organic market groceries"*) and watch the Transformer's self-attention weights highlight across every word!
- **Real-Time Auto-Categorization**:
  - As you type an expense description, the Transformer classifies it into the right category in real time with confidence percentages.
- **50/30/20 Financial Health Engine**:
  - Live breakdown of **Needs (50%)**, **Wants (30%)**, and **Savings (20%)** with color-coded warning indicators.
- **Financial Health Scorecard (0–100 & Letter Grade A+ to D)**:
  - Multi-attribute neural attention model evaluating 8 key financial vitals:
    1. Savings Rate %
    2. Needs vs 50% Target Proximity
    3. Wants Discretionary Discipline
    4. Budget Utilization Compliance
    5. Emergency Buffer Runway
    6. Spending Volatility Stability
    7. Income Stability
    8. Debt & Goal Progress

### 2. 🧠 Transformer Model Architectures (`ai/`)
1. **`TransformerTextClassifier` (`ai/transformer_models.py`)**:
   - Multi-layer Transformer Encoder (`nn.Embedding` &rarr; Sinusoidal Positional Encoding &rarr; Multi-Head Self-Attention with custom explainable weight extraction &rarr; LayerNorm & FeedForward &rarr; Classification Heads).
   - Maps transaction text to financial categories and classifies conversational questions into financial advisory intents.
2. **`TemporalExpenseTransformer` (`ai/transformer_models.py`)**:
   - Multi-Head Temporal Self-Attention Transformer for time-series forecasting.
   - Takes 30-day sequential feature vectors `[amount, sin(day_of_week), cos(day_of_week), day_of_month, category_index]`.
   - Generates a **14-day future daily spending trajectory** and computes anomaly risk scores based on sequence reconstruction variance.
3. **`FinAdvisorAttentionModel` (`ai/transformer_models.py`)**:
   - Attends across 8 financial health vitals to synthesize an accurate, weighted Financial Health Score (0–100).

### 3. 💸 Core Expense Management (Full CRUD)
- **CRUD Operations**: Add, view, edit, and delete expenses with confirmation dialogs.
- **Categorization**: Pre-configured categories (Food & Dining, Transportation, Housing & Rent, Utilities, Entertainment, Shopping, Healthcare, Education, Investments, Miscellaneous) with icons and color tokens.
- **Filtering & Search**:
  - Real-time search across descriptions and notes.
  - Category dropdown filter.
  - Date range filters (Start Date &rarr; End Date).
  - Sorting by Date (Newest/Oldest) and Amount (Highest/Lowest).
- **CSV Export**: One-click download of all transactions formatted as CSV (`/expenses/export`).
- **Recurring Transactions**: Tag recurring monthly expenses (Rent, Netflix, Gym, Subscriptions).

### 4. 🎯 Category Budget Planner
- Set custom monthly spending ceilings per category.
- Visual progress bars with color-coded threshold warnings:
  - 🟢 Green: Under 80%
  - 🟡 Amber: 80% – 100% (Warning)
  - 🔴 Red: Over 100% (Exceeded)
- Real-time calculation of remaining allowance and total allocated funds.

### 5. 📊 Interactive Analytics & Charts
- Powered by modern **Chart.js 4**:
  - **Monthly Spending Trend**: 6-month historical curve with smooth gradient fill.
  - **Category Share Doughnut**: Interactive breakdown of spending by category.
  - **14-Day Temporal Forecast**: AI projected spending trajectory.
  - **Anomaly & Leak Detection**: Identifies transactions exceeding 2.5 standard deviations from baseline averages.

### 6. 🎨 Premium Obsidian Fintech Design System
- Modern dark obsidian theme with crisp glassmorphic cards and micro-animations.
- Built-in **Theme Toggle** (Obsidian Dark / Crisp Light) with local storage persistence.
- Fully responsive layout for desktop, tablet, and mobile.

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/sayan-kundu000/ExpenseBook.git
cd ExpenseBook
```

### 2. Requirements & Virtual Environment
- Python 3.10+ (Tested with Python 3.12)
- Set up a virtual environment and install dependencies:
  ```bash
  python -m venv .venv
  # On Windows:
  .\.venv\Scripts\activate
  # On macOS/Linux:
  source .venv/bin/activate

  pip install -r requirements.txt
  ```

### 3. Run the Web Application
Simply launch `app.py`:
```bash
python app.py
```
Open your browser and navigate to:
```
http://localhost:3000
```

### 4. 👥 3-Role Login System (PDF Page 4 Requirements)
The app implements a **3-Login System** tailored for the 3 distinct practical use cases from **Page 4 of the PDF**:

| Role / Persona | Pre-seeded Account | Password | Key Tailored Features |
| :--- | :--- | :--- | :--- |
| 👤 **Individual User** | `individual@expensebook.com` *(or `demo@expensebook.com`)* | `password123` | • Daily personal spending & cashflow tracking<br>• 50/30/20 Budget rule compliance<br>• Emergency buffer & wealth growth goals |
| 🎓 **Student** | `student@expensebook.com` | `password123` | • Monthly pocket money & allowance tracker<br>• Safe daily burn-rate limit (`₹X.XX/day`)<br>• Campus dining, textbook & transit categories<br>• Student savings goals (Laptop, textbooks) |
| 💼 **Freelancer / Business** | `freelancer@expensebook.com` | `password123` | • Business expense & receipt bookkeeping<br>• Tax-deductible write-off calculator (@ 25%)<br>• Client/Project billing allocation (Acme Corp, Nova)<br>• IRS Schedule C / ITR tax ledger export (CSV) |
| 👑 **Monarch (Easter Egg)** | `doom@latveria.gov` | `password123` | • Imperial Latverian Treasury, Doombot fleet & War Vault |

- **1-Click Instant Login**: The `/login` page provides one-click login cards to instantly access any role without typing passwords.
- **Topbar Role Switcher**: Switch between any of the roles on the fly directly from the top navigation bar with 1 click.
- **Custom Role Registration**: During sign-up (`/register`), users can select their role persona to receive customized starter budgets and tailored features.

---

## 🧪 Running Automated Unit Tests

A comprehensive unit test suite is included in `tests/test_app.py` verifying:
- 3-Role instant logins (`/role-login/individual`, `/role-login/student`, `/role-login/freelancer`, `/role-login/doom`)
- Active session role switching (`/switch-role/<role>`)
- User registration with role selection (Student, Freelancer, Individual)
- Dedicated Student Hub (`/student-hub`) & pocket money goal contributions
- Dedicated Freelancer Bookkeeping (`/bookkeeping`) & Tax Schedule CSV export
- Tax-deductible flags & client/project tagging on expenses (create & edit)
- PyTorch `TransformerTextClassifier` forward pass & attention map extraction
- PyTorch `TemporalExpenseTransformer` forward pass & forecast shape
- PyTorch `FinAdvisorAttentionModel` 8-vitals scoring
- AI Category Prediction API & AI Chatbot Response Engine
- Standard and Tax-specific CSV Data Exports

To run the test suite:
```bash
python -m unittest discover tests -v
```
All 15 tests execute and pass with zero errors.

---

## 📂 Project Architecture

```
ExpenseBook/
├── app.py                      # Main Flask application & routes (Auth, Expenses, Budgets, Analytics, AI Advisor API)
├── config.py                   # Application settings & database URI (SQLite / PostgreSQL)
├── models.py                   # SQLAlchemy models (User, Expense, Income, Budget, FinancialGoal, Category)
├── seed_data.py                # Database seeder with realistic sample financial data & demo users
├── ai/                         # Local PyTorch Transformer AI Package (Zero APIs)
│   ├── __init__.py             # AI package entrypoint
│   ├── tokenizer.py            # Local subword financial tokenizer
│   ├── transformer_models.py   # Text Classifier, Temporal Transformer, Attention Models
│   └── advisor.py              # Financial Health Scoring, 50/30/20 Engine, Chatbot, Anomaly Detection
├── templates/                  # Modern Jinja2 templates
│   ├── base.html               # Master layout with sidebar, topbar, theme switch, modals
│   ├── dashboard.html          # Main financial command center with KPIs and Chart.js graphs
│   ├── expenses.html           # Full CRUD expense manager with filters & CSV export
│   ├── student_hub.html        # Dedicated Student pocket money & allowance management
│   ├── bookkeeping.html        # Dedicated Freelancer / Business tax deductions & client ledger
│   ├── budgets.html            # Category budget limits with progress bars
│   ├── analytics.html          # Deep-dive analytics, 14-day transformer forecast & anomalies
│   ├── advisor.html            # Dedicated AI Financial Advisor Hub & Attention visualizer
│   ├── login.html              # Sleek auth login with 1-click demo button
│   └── register.html           # User registration page
├── static/
│   ├── css/
│   │   └── style.css           # Custom Fintech Obsidian Design System (Glassmorphic, Responsive)
│   └── js/
│       ├── main.js             # General UI interactivity, modals, real-time AI auto-categorization
│       ├── dashboard.js        # Chart.js 4 initialization for trends and doughnut charts
│       └── advisor.js          # Interactive AI chat, prompt chips, attention token visualizer
├── tests/
│   └── test_app.py             # Automated unit tests for models, transformers, and endpoints
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules for Python, venv, and SQLite
└── README.md                   # Complete documentation
```

---

## 🔒 Privacy & Compliance
- **No Cloud Calls**: Your personal financial transactions are never sent to external servers or third-party LLMs.
- **Local Inference**: All calculations, predictions, and chat advisories run on your machine's CPU using local PyTorch weights.
