# FuelWise LEO — Orbital Sustainability & CDM Triage System

*FuelWise LEO* is a cross-platform decision-support dashboard built to help Low Earth Orbit (LEO) satellite operators triage Conjunction Data Messages (CDMs), prioritize high-risk debris encounters, and optimize station-keeping fuel expenditure across web, desktop, and mobile environments.


## Live Access & Installable Builds

* *Live Web Dashboard:* [Launch on Streamlit Cloud](https://fuelwise-leo-gnxqqsyugr3c769nfycdkt.streamlit.app/)
* *Android App (.apk):* [Download FuelWiseLEO.apk from Releases](https://github.com/paarth25bas10023/FuelWise-LEO/releases/latest)
* *Windows Desktop App (.exe):* Available in the [Latest Release Assets](https://github.com/paarth25bas10023/FuelWise-LEO/releases/latest) 
* *Demonstration Video :* (https://drive.google.com/file/d/1ZoZ_dzO7jW09MsOww_bV2xXoHKGvEbJf/view?usp=drive_link)

## Key Features

* *Automated CDM Triage & Risk Scoring:* Filters active satellite and space debris conjunction datasets (active_sats.csv, debris_sats.csv) to surface critical collision threats requiring immediate operator attention.
* *Fuel-Aware Maneuver Decision Support:* Balances collision avoidance urgency against onboard propellant budgets to prevent unnecessary fuel depletion and extend mission lifetimes.
* *Interactive Orbital Telemetry Views:* Real-time filtering, threshold inspection, and tabular analytics powered by Python, Pandas, NumPy, and Streamlit.
* *Cross-Platform Native Wrappers:* Packaged as both a standalone Windows desktop executable (via pywebview + PyInstaller) and a native Android application (via Capacitor + Android Studio).

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| *Core Analytics & Data* | Python 3, Pandas, NumPy |
| *Frontend Dashboard* | Streamlit (Custom Dark Orbital Theme) |
| *Cloud Hosting* | GitHub + Streamlit Community Cloud |
| *Android Mobile App* | Capacitor (@capacitor/android), Android Studio / Gradle |
| *Windows Desktop App* | pywebview, PyInstaller |

---

## Repository Structure

```text
FuelWise-LEO/
├── .streamlit/
│   └── config.toml          # Custom dark-mode UI theme configuration
├── app.py                   # Main Streamlit dashboard & CDM triage logic
├── debris_sats.csv          # Tracked orbital debris conjunction dataset
├── requirements.txt         # Python runtime dependencies
└── README.md                # Project documentation & release links
└── Demo Video               # Demonstration of the app
