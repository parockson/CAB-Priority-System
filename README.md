# CAB Priority System

The **CAB Priority System** is a professional governance framework and digital dashboard designed specifically for Fintech operations. It brings mathematical objectivity to the Change Advisory Board's (CAB) decision-making process by replacing subjective assessments with a rigid, weighted scoring model. 

This system ensures that every change request is evaluated against its true impact on financial integrity, regulatory compliance, technical stability, and pressing deadlines.

## ✨ Key Features

- **Mathematical Prioritization Engine**: Scores requests dynamically based on complex combinations of 9 distinct metrics (from Financial Integrity to Security Pressure).
- **Dynamic Priority Matrix**: Visualizes all active requests in real-time across four critical quadrants (P1: DO, P2: SCHEDULE, P3: DELEGATE, P4: ELIMINATE). As deadlines approach, items organically transition across quadrants.
- **Role-Based Access Control (RBAC)**: Secure authentication system distinguishing between `admin` (CRUD operations) and `user` (read-only view) roles.
- **Complete Lifecycle Management**: Tracks requests from initial submission ("CR-raised") through "In dev", "UAT", into a "Live Archive" or "Suspended Archive".
- **Real-Time Cloud Synchronization**: Powered by Supabase for instantaneous data storage and retrieval.
- **Modern UI**: Sleek, premium aesthetic utilizing inter typography, refined spacing, and Plotly interactive data visualizations.

---

## 🛠 Tech Stack

- **Frontend & Routing**: [Dash (Plotly)](https://dash.plotly.com/) & [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)
- **Data Visualization**: Plotly Express & Graph Objects
- **Backend & Database**: Python 3.x & [Supabase](https://supabase.com/) (PostgreSQL)
- **Deployment**: Gunicorn (Optimized for PaaS like Render or Heroku)

---

## 🚀 Installation & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/fintech-cab-dashboard.git
cd fintech-cab-dashboard
```

### 2. Set up a virtual environment (Recommended)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Supabase Database Configuration
You must create two tables in your Supabase project. Open the **SQL Editor** in Supabase and run the following queries:

**Table 1: CAB Prioritization Data**
```sql
CREATE TABLE cab_prioritization (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'CR-raised',
    target_date DATE NOT NULL,
    days_to_deadline INTEGER,
    x_coord FLOAT,
    y_coord FLOAT,
    quadrant TEXT,
    financial_integrity INTEGER,
    service_criticality INTEGER,
    blast_radius INTEGER,
    regulatory_weight INTEGER,
    strategic_priority INTEGER,
    security_pressure INTEGER,
    contractual_clock INTEGER,
    system_health INTEGER,
    implementation_risk INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Table 2: User Roles & Authentication**
```sql
CREATE TABLE cab_roles (
    email TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    password TEXT NOT NULL
);

-- Insert your initial admin user
INSERT INTO cab_roles (email, name, role, password) 
VALUES ('admin@yourdomain.com', 'Admin User', 'admin', 'secure_password');
```

### 5. Environment Variables
Create a `.env` file in the root directory of your project and add your Supabase credentials:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
```

### 6. Run the Application locally
```bash
python app.py
```
Visit `http://127.0.0.1:8050/` in your browser and log in with the admin credentials you created.

---

## 🌐 Deployment (Render / Heroku)

This application is deployment-ready and includes a `Procfile` configured for Gunicorn.

1. Create a new Web Service on your hosting provider (e.g., Render).
2. Connect your GitHub repository.
3. Set the build command to `pip install -r requirements.txt`.
4. Set the start command to `gunicorn app:server`.
5. **Crucial**: Ensure you add your `SUPABASE_URL` and `SUPABASE_KEY` as Environment Variables in your hosting dashboard so the cloud server can connect to your database.

---

## 📊 The Scoring Methodology

The Priority Matrix places requests using two coordinates (ranging 0-100):

### Importance Score (Y-Axis)
Reflects business value and risk profile.
* Financial Integrity (35%)
* Service Criticality (25%)
* Blast Radius (15%)
* Regulatory Weight (15%)
* Strategic Priority (10%)

### Technical Urgency Score (X-Axis)
Measures the pressure to deploy immediately.
* Deadline Proximity (40%) *Dynamically calculated based on current date vs target date*
* Contractual Clock / SLAs (30%)
* Security Pressure (30%)

*(Note: Implementation Risk & System Health are tracked as metadata for developers but can be integrated into the main axes depending on your organization's specific SLA definitions).*

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome. Feel free to check the issues page if you want to contribute.

## 📝 License
This project is proprietary software designed for internal organizational governance.
