# AI-Powered Digital Twin for MALE UAV Piston Engines
### Prototype Implementation for DRDO Problem Statement 26054
**Focus**: Predictive Powertrain Health Monitoring & Prognostics vs. Reactive Threshold Alarms

---

> [!IMPORTANT]
> **SIMULATION MODE NOTICE**: This application operates in **SIMULATION MODE** using a high-fidelity synthetic physics simulator modeled on a 4-cylinder turbocharged aircraft piston engine (Rotax 914 / 915 iS class). It is designed strictly for research, engineering demonstration, and evaluation of DRDO Problem Statement 26054, and is not interfaced with operational military hardware.

---

## 1. Executive Summary & Problem Context

Traditional Unmanned Aerial Vehicle (UAV) powertrain health management relies heavily on static redline threshold alarms (e.g., alert triggers only after Cylinder Head Temperature exceeds 135?C or Oil Pressure drops below 1.8 bar). In high-altitude or hot-weather missions, such reactive alerting leaves zero margin for preventative pilot intervention, leading to in-flight engine seizures, loss of propulsion, or airframe loss.

This Digital Twin platform demonstrates **predictive, physics-infused prognostics**:
1. It simulates continuous physical telemetry coupled across RPM, manifold pressure, thermal inertia, fuel flow, air density, and mechanical vibration.
2. It runs a **first-principles thermodynamic Digital Twin** alongside incoming data, computing theoretical expected states and residuals ($R = \text{Observed} - \text{Expected}$).
3. It deploys an **AI/ML Prognostic Engine**:
   - **Unsupervised Anomaly Detection**: `IsolationForest` detecting multivariate deviations long before hard thresholds trip.
   - **Multi-Class Fault Classifier**: `RandomForestClassifier` identifying 8 specific failure modes with high confidence.
   - **Prognostic Remaining Useful Life (RUL)**: Physics-guided wear degradation estimating remaining flight hours.
   - **Explainable AI (XAI)**: Feature attribution ranking and plain-English engineering root-cause diagnoses.
4. It features a defense-grade **Aerospace Operator Dashboard** with live telemetry matrix, multi-signal charting, chronological mission replay, and one-click PDF debrief generation.

---

## 2. End-to-End System Architecture

```
ENGINE SENSORS (Simulated Rotax 915 iS)
       ? (RPM, CHT, EGT, Oil P/T, MAP, Fuel, Vib)
CAN / SOCKETCAN LAYER (Virtual vcan0, 10-20 Hz, 1.9 ms latency)
       ?
EDGE PREPROCESSING (Spike rejection, rolling stats, derived features)
       ?
DIGITAL TWIN CORE
 ?                  ?
PHYSICS MODEL            AI/ML ENGINE
(Expected states)       (Isolation Forest + Multi-Class RF)
 ?                  ?
HEALTH FUSION ENGINE (0-100 Health Score, Early Warnings)
       ?
BACKEND & PERSISTENCE (FastAPI, SQLite, SQLAlchemy)
       ? (WebSocket @ 10 Hz)
AEROSPACE OPERATOR DASHBOARD (React, Vite, Tailwind CSS, Recharts)
```

---

## 3. Technology Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Recharts, Lucide React icons
- **Backend API**: Python 3.10+, FastAPI, Uvicorn, WebSockets
- **AI/ML Engine**: Scikit-learn (`IsolationForest`, `RandomForestClassifier`), NumPy, Pandas, Joblib
- **Physics Model**: Thermodynamic equations, barometric lapse, dynamic residual calculator
- **Persistence**: SQLite with SQLAlchemy ORM
- **Reporting**: ReportLab automated PDF mission debrief generator

---

## 4. Modeled Engine & Physical Relationships

The simulator models a 4-cylinder turbocharged aircraft piston engine (Rotax 914 / 915 iS class):

| Parameter | Nominal Range | Unit | Physical Coupling |
|---|---|---|---|
| **RPM** | 1800 - 5800 | RPM | Driven by throttle setpoint & governor |
| **Cylinder Head Temp (CHT)** | 85 - 110 | ?C | Thermal balance between heat flux & dynamic ram air |
| **Oil Temperature** | 78 - 98 | ?C | Heat transfer from cylinder heads with thermal lag |
| **Oil Pressure** | 3.5 - 5.0 | bar | Driven by engine oil pump; decays with oil temperature rise |
| **Fuel Flow** | 12 - 38 | L/h | Proportional to RPM, MAP, and air-fuel equivalence ratio |
| **Manifold Pressure (MAP)** | 22 - 38 | inHg | Turbocharger boost adjusted by wastegate and altitude |
| **Exhaust Gas Temp (EGT)** | 700 - 820 | ?C | Combustion chamber temperature, highly sensitive to fuel mixture |
| **RMS Vibration** | 0.8 - 2.5 | mm/s | Mechanical harmonic baseline linked to RPM & piston firing |
| **Flight Altitude** | 0 - 25,000 | ft | Barometric pressure lapse modulates cooling density & turbo boost |

---

## 5. Fault Simulation Matrix (Continuous Progression)

The platform supports 7 aerospace failure modes with gradual progression (`LOW`, `MEDIUM`, `HIGH` severity):

1. **Overheating**: Coolant pump cavitation or airflow duct restriction. CHT climbs (+1.5?C/s), secondary oil temperature rises, oil viscosity drops.
2. **Cylinder Misfire**: Intermittent ignition/spark loss. Causes cyclic RPM ripple, severe vibration spikes (+4-8 mm/s), and unburnt fuel passage in EGT.
3. **Oil Pressure Failure**: Oil pump wear or seal leakage. Hydraulic pressure drops progressively below 2.0 bar, compounding friction heating.
4. **Excessive Vibration**: Propeller blade pitch tracking error or dynamic imbalance. RMS vibration climbs above 6.0 mm/s without thermal coupling.
5. **Fuel System Abnormality**: Fuel injector clogging or fuel filter restriction. Lean mixture condition causes rapid EGT spike while fuel flow drops.
6. **Sensor Calibration Drift**: Electronic ADC transducer drift. CHT reads +25?C artificially without corresponding thermal rise in oil or EGT.
7. **Bearing Degradation**: Crankshaft or turbocharger journal bearing spalling. Generates high-frequency vibration harmonics and localized friction heating.

---

## 6. Digital Twin & Explainable AI (XAI)

### A. Physics Residual Computation
$$\text{Residual} = X_{\text{observed}} - X_{\text{expected}}$$
$$Z\text{-score} = \frac{\text{Residual}}{\sigma_{\text{baseline}}}$$
$$\text{Composite Residual Norm} = \sqrt{\frac{1}{N} \sum_{i=1}^N Z_i^2}$$

### B. Health Fusion Algorithm (0-100 Score)
$$\text{Health Score} = 100 - (\text{Physics Penalty} + \text{ML Penalty} + \text{Fault Penalty} + \text{Rate Penalty})$$
- **HEALTHY** (80 - 100%): Emerald green
- **DEGRADING** (50 - 79%): Amber warning
- **CRITICAL** (0 - 49%): Rose critical alarm

### C. Prognostic RUL Estimation
Calibrated against a nominal 500-hour Time-Between-Overhaul (TBO) design limit, factoring cumulative thermal fatigue, vibration stress, and anomaly intensity into an acceleration multiplier:
- **Healthy Engine**: RUL ~ 450 - 480 hours
- **Early Degradation**: RUL ~ 260 - 310 hours
- **Active Warning**: RUL ~ 130 - 150 hours
- **Critical Excursion**: RUL ~ 25 - 40 hours

### D. Explainable AI Feature Attribution
Ranked horizontal bars quantify each feature's contribution percentage (e.g. Temperature Trend 38%, Physics Residual 27%, Vibration Rate 19%, Oil Pressure Delta 11%, Load 5%), coupled with natural-language engineering diagnoses.

---

## 7. How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js v18+ and npm

### Installation
1. Install Python backend requirements:
```bash
pip install -r requirements.txt
```

2. Install Frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

3. Train ML Models (Automatically generated if not present):
```bash
python ml/train_models.py
```

### Launching the Application
You can launch both services using the provided batch scripts on Windows:
- Double click `start_all.bat` (launches Backend on port 8000 and Frontend on port 5173).

Or launch individually from terminal:
```bash
# Terminal 1: Backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open your browser at:
- **Operator Dashboard**: `http://localhost:5173`
- **FastAPI Interactive Docs**: `http://localhost:8000/docs`

---

## 8. Step-by-Step 16-Step DRDO Demo Flow

The system supports an automated one-click demonstration or manual execution of the exact required flow:

1. **Step 1**: Open `http://localhost:5173`. Notice baseline healthy engine (Health 96%, Status HEALTHY, RUL ~480h).
2. **Step 2**: Click **1-CLICK DEMO MODE** on the top header bar (or manually go to **Mission Control** and select **High Altitude Climax**).
3. **Step 3**: Observe altitude climbing to 18,000 ft. MAP and cooling air density adjust realistically via thermodynamic equations.
4. **Step 4**: Navigate to **Digital Twin View**; verify physical observed vs expected virtual states are aligned ($Z < 1.0\sigma$).
5. **Step 5**: Fault injection triggers gradual **Overheating** (Medium/High severity).
6. **Step 6**: Observe continuous sensor trends: CHT climbs +15?C, secondary oil pressure decays, physics residual reaches +14?C.
7. **Step 7**: Early warning alert triggers: Health score degrades **96% ? 78% ? 54%**.
8. **Step 8**: Navigate to **AI Diagnostics (XAI)**; model classifies fault as **OVERHEATING** with ~90% confidence.
9. **Step 9**: Prognostic RUL contracts dynamically from **420 hours ? 260 hours ? 140 hours**.
10. **Step 10**: Check **"Why this prediction?"** panel: feature attribution bars highlight Temperature Trend (38%) and Physics Residual (28%).
11. **Step 11**: Review defense maintenance directive: *"Immediately reduce engine load by 20-30%. Enrich fuel mixture and pitch down to restore cooling airflow."*
12. **Step 12**: In **Mission Control**, click **STOP** to complete the flight sortie.
13. **Step 13**: Navigate to **History & Replay**; select the completed mission and use the timeline scrubber to replay the exact chronological telemetry stream.
14. **Step 14**: Navigate to **Mission Report**; view the technical debrief report and click **"EXPORT PDF REPORT"** to download the official PDF document.

---

## 9. API & WebSocket Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Overall system and engine health status |
| `GET` | `/api/sensors/latest` | Latest cleaned sensor telemetry and derived rates |
| `GET` | `/api/sensors/history` | Historical sliding buffer for sparklines |
| `GET` | `/api/quality` | Per-sensor streaming quality metrics |
| `GET` | `/api/twin/state` | Observed vs expected physics values & residuals |
| `GET` | `/api/prediction` | ML fault class, confidence, XAI, and RUL |
| `GET` | `/api/alerts` | Active warnings and maintenance alarms |
| `POST` | `/api/alerts/acknowledge` | Acknowledge specific alert |
| `GET` | `/api/missions` | Active mission state and completed sortie history |
| `POST` | `/api/missions/start` | Launch predefined mission flight profile |
| `POST` | `/api/missions/pause` | Pause active simulation |
| `POST` | `/api/missions/resume` | Resume paused simulation |
| `POST` | `/api/missions/stop` | Conclude and save mission to database |
| `POST` | `/api/missions/reset` | Reset engine to baseline idle |
| `POST` | `/api/fault/inject` | Inject 1 of 7 gradual aerospace fault models |
| `POST` | `/api/fault/clear` | Clear active injected faults |
| `GET` | `/api/missions/{id}/replay` | Chronological replay telemetry points |
| `GET` | `/api/report/{id}` | Post-flight debrief JSON summary |
| `GET` | `/api/report/{id}/pdf` | ReportLab downloadable debrief PDF document |
| `POST` | `/api/demo/start` | Launch automated 16-step demonstration sequence |
| `WS` | `/ws/engine` | Live 10 Hz telemetry, twin state, AI, and alert broadcast |

---

## 10. DRDO Engineering Standards & Limitations

- **Synthetic Modeling**: Operating parameters are calibrated from public Rotax 914 / 915 iS engine manuals and standard atmosphere tables (ICAO Doc 7488).
- **Communication Simulation**: SocketCAN vcan0 is modeled in software (packets/sec, jitter, latency, drop rate) without physical CAN transceiver hardware.
- **Maintenance Recommendations**: Guidance represents simulated engineering protocols for demonstration purposes.
