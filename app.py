import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.request

# --- PAGE SETUP ---
st.set_page_config(page_title="FuelWise LEO", page_icon="🛰️", layout="wide")
st.title("🛰️ FuelWise LEO: End-to-End Orbital Sustainability & Propellant Co-Pilot")
st.caption("Pre-Launch Rideshare Slot Advisor • Ballistic Decay & Space Weather Engine • Smart Collision Triage")

# --- ORBITAL PHYSICS & DATA LOADING ---
def compute_orbital_elements(df):
    mu = 398600.4418  # Earth's gravitational parameter (km^3/s^2)
    earth_radius = 6371.0
    n_rad_s = df["MEAN_MOTION"] * (2 * np.pi) / 86400.0
    semi_major_axis = (mu / (n_rad_s ** 2)) ** (1 / 3)
    df["ALTITUDE_KM"] = semi_major_axis - earth_radius
    if "INCLINATION" not in df.columns:
        np.random.seed(42)
        df["INCLINATION"] = np.random.choice([53.0, 70.0, 86.4, 97.6], size=len(df))
    return df[(df["ALTITUDE_KM"] >= 250) & (df["ALTITUDE_KM"] <= 1500)]

def fetch_celestrak_csv(url, local_filename, fallback_alts, fallback_incs):
    if os.path.exists(local_filename):
        df = pd.read_csv(local_filename)
        if "INCLINATION" in df.columns:
            return df
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            df = pd.read_csv(resp)
        df.to_csv(local_filename, index=False)
        return df
    except Exception:
        n_rad_day = 86400.0 / (2 * np.pi * np.sqrt(((6371.0 + fallback_alts) ** 3) / 398600.4418))
        return pd.DataFrame({"MEAN_MOTION": n_rad_day, "INCLINATION": fallback_incs})

@st.cache_data
def load_catalogs():
    np.random.seed(42)
    active_alts = np.concatenate([
        np.random.normal(550, 18, 7500),
        np.random.normal(530, 15, 3500),
        np.random.normal(1200, 25, 1200),
        np.random.uniform(380, 900, 4500),
    ])
    active_incs = np.concatenate([
        np.random.normal(53.0, 1.5, 7500),
        np.random.normal(70.0, 2.0, 3500),
        np.random.normal(87.9, 1.0, 1200),
        np.random.normal(97.6, 1.2, 4500),
    ])
    active_df = fetch_celestrak_csv(
        "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv",
        "active_sats.csv",
        active_alts,
        active_incs
    )
    active_df = compute_orbital_elements(active_df)
    active_df["TYPE"] = "Active Satellite"

    debris_alts = np.concatenate([
        np.random.normal(790, 65, 1400),
        np.random.normal(850, 80, 2200),
        np.random.uniform(450, 1100, 1500),
    ])
    debris_incs = np.concatenate([
        np.random.normal(74.0, 2.5, 1400),
        np.random.normal(98.8, 2.0, 2200),
        np.random.uniform(50.0, 99.0, 1500),
    ])
    debris_df = fetch_celestrak_csv(
        "https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-2251-debris&FORMAT=csv",
        "debris_sats.csv",
        debris_alts,
        debris_incs
    )
    debris_df = compute_orbital_elements(debris_df)
    debris_df["TYPE"] = "Tracked Debris"

    return active_df, debris_df

@st.cache_data
def load_cdm_alerts():
    data = [
        {"Alert_ID": "CDM-8841", "Chaser_Object": "COSMOS 2251 DEB", "Time_to_TCA_Days": 1.2, "Miss_Distance_m": 68,   "Relative_Speed_ms": 14210, "Log10_Risk": -2.85},
        {"Alert_ID": "CDM-8842", "Chaser_Object": "FENGYUN 1C DEB",  "Time_to_TCA_Days": 3.8, "Miss_Distance_m": 1450, "Relative_Speed_ms": 11850, "Log10_Risk": -5.60},
        {"Alert_ID": "CDM-8843", "Chaser_Object": "SL-16 R/B",       "Time_to_TCA_Days": 2.1, "Miss_Distance_m": 115,  "Relative_Speed_ms": 13400, "Log10_Risk": -3.45},
        {"Alert_ID": "CDM-8844", "Chaser_Object": "STARLINK-4102",   "Time_to_TCA_Days": 0.9, "Miss_Distance_m": 920,  "Relative_Speed_ms": 9800,  "Log10_Risk": -4.95},
        {"Alert_ID": "CDM-8845", "Chaser_Object": "IRIDIUM 33 DEB",  "Time_to_TCA_Days": 4.2, "Miss_Distance_m": 190,  "Relative_Speed_ms": 14650, "Log10_Risk": -3.70},
        {"Alert_ID": "CDM-8846", "Chaser_Object": "COSMOS 1408 DEB", "Time_to_TCA_Days": 1.6, "Miss_Distance_m": 82,   "Relative_Speed_ms": 13920, "Log10_Risk": -3.10},
        {"Alert_ID": "CDM-8847", "Chaser_Object": "CZ-2C DEB",       "Time_to_TCA_Days": 2.9, "Miss_Distance_m": 2100, "Relative_Speed_ms": 10500, "Log10_Risk": -6.15},
        {"Alert_ID": "CDM-8848", "Chaser_Object": "ONEWEB-0318",     "Time_to_TCA_Days": 1.8, "Miss_Distance_m": 140,  "Relative_Speed_ms": 12100, "Log10_Risk": -3.88},
        {"Alert_ID": "CDM-8849", "Chaser_Object": "FENGYUN 1C DEB",  "Time_to_TCA_Days": 3.4, "Miss_Distance_m": 780,  "Relative_Speed_ms": 13100, "Log10_Risk": -4.72},
        {"Alert_ID": "CDM-8850", "Chaser_Object": "COSMOS 2251 DEB", "Time_to_TCA_Days": 1.1, "Miss_Distance_m": 54,   "Relative_Speed_ms": 14480, "Log10_Risk": -2.62},
    ]
    return pd.DataFrame(data)

active_df, debris_df = load_catalogs()
all_objects_df = pd.concat([active_df, debris_df], ignore_index=True)
base_cdm_df = load_cdm_alerts()

# --- SIDEBAR: EXPANDED AEROSPACE PARAMETERS ---
st.sidebar.header("🚀 1. Orbit & Space Weather")
mission_name = st.sidebar.text_input("Satellite / Mission Name", "VIT-CubeSat-1")
target_alt = st.sidebar.slider("Target Altitude (km)", 350, 1000, 550, step=10)
target_inc = st.sidebar.slider("Orbital Inclination (deg)", 0.0, 98.0, 53.0, step=0.5, help="51.6° = ISS | 53° = Starlink Shell | 97.6° = Sun-Synchronous (SSO)")
solar_cycle = st.sidebar.selectbox(
    "Solar Activity (F10.7 Flux)",
    ["Solar Maximum (Dense Atmosphere — Faster Decay)", "Moderate Solar Activity", "Solar Minimum (Thin Atmosphere — Slower Decay)"],
    index=1
)

st.sidebar.header("🛰️ 2. Spacecraft Geometry & Mass")
sc_mass = st.sidebar.slider("Spacecraft Wet Mass (kg)", 1.0, 200.0, 6.0, step=1.0, help="3U CubeSat ≈ 4 kg | 6U ≈ 12 kg | MicroSat ≈ 100 kg")
drag_area = st.sidebar.slider("Max Solar Panel / Drag Area (m²)", 0.01, 2.00, 0.06, step=0.01)
cd = 2.2  # Standard aerodynamic drag coefficient in LEO
ballistic_coeff = round(sc_mass / (cd * drag_area), 1)
area_to_mass = round(drag_area / sc_mass, 4)
st.sidebar.caption(f"Ballistic Coeff: **{ballistic_coeff} kg/m²** | Area/Mass: **{area_to_mass} m²/kg**")

st.sidebar.header("⛽ 3. Propulsion & Safety Rules")
propulsion = st.sidebar.selectbox(
    "Propulsion System",
    [
        "Chemical Thrusters (High Thrust)",
        "Electric / Ion (Low Thrust — Early Burn)",
        "No Thrusters (Passive CubeSat — Differential Drag)"
    ]
)

if "No Thrusters" in propulsion:
    total_fuel = 0.0
    eol_reserve = 0.0
    st.sidebar.info("Passive mode: Relies on solar-panel Differential Drag.")
else:
    total_fuel = st.sidebar.slider("Total Onboard Fuel Budget (m/s Δv)", 1.0, 15.0, 4.5, step=0.5)
    eol_reserve = st.sidebar.slider("Locked EOL Deorbit Reserve (m/s Δv)", 0.5, 5.0, 2.5, step=0.5)
    st.sidebar.caption(f"Usable Collision Dodge Budget: **{max(0.0, round(total_fuel - eol_reserve, 2))} m/s Δv**")

risk_threshold = st.sidebar.select_slider(
    "Collision Action Red-Line (Log10 Pc)",
    options=[-5.0, -4.5, -4.0, -3.5, -3.0],
    value=-4.0,
    help="-4.0 = 1 in 10,000 (NASA/ESA Standard) | -5.0 = 1 in 100,000 (Strict)"
)

# --- MAIN TABS ---
tab1, tab2, tab3 = st.tabs([
    "1️⃣ Pre-Launch Slot & 5-Yr Compliance",
    "2️⃣ Collision Triage & Threat Simulator",
    "3️⃣ Regulatory Compliance Export"
])

# ==================== TAB 1: PRE-LAUNCH ====================
with tab1:
    st.subheader("Pre-Launch Rideshare Congestion & Ballistic 5-Year Deorbit Check")

    # 1. Total shell congestion (+/- 25 km) vs Co-Planar congestion (+/- 25 km AND +/- 5 deg inclination)
    shell_active = len(active_df[(active_df["ALTITUDE_KM"].between(target_alt - 25, target_alt + 25))])
    shell_debris = len(debris_df[(debris_df["ALTITUDE_KM"].between(target_alt - 25, target_alt + 25))])
    shell_total = shell_active + shell_debris

    coplanar_objs = len(all_objects_df[
        (all_objects_df["ALTITUDE_KM"].between(target_alt - 25, target_alt + 25)) &
        (all_objects_df["INCLINATION"].between(target_inc - 5.0, target_inc + 5.0))
    ])

    # 2. Physics-scaled atmospheric decay time using Ballistic Coefficient & Solar Flux
    solar_mult = 0.65 if "Maximum" in solar_cycle else (1.55 if "Minimum" in solar_cycle else 1.0)
    bc_ref = 45.5  # Reference 6 kg / (2.2 * 0.06 m^2)
    decay_years = round(0.12 * np.exp(0.0085 * target_alt) * (ballistic_coeff / bc_ref) * solar_mult, 1)

    # Required deorbit delta-v scales with altitude above 400 km
    req_deorbit_dv = round(max(0.0, (target_alt - 420) * 0.015), 2)
    compliant_5yr = decay_years <= 5.0 or (eol_reserve >= req_deorbit_dv and "No Thrusters" not in propulsion)

    # 3. Recommend cleanest altitude within +/- 100 km matching inclination
    candidates = range(max(350, target_alt - 100), min(1000, target_alt + 100), 15)
    best_alt = min(
        candidates,
        key=lambda a: len(all_objects_df[
            (all_objects_df["ALTITUDE_KM"].between(a - 25, a + 25)) &
            (all_objects_df["INCLINATION"].between(target_inc - 5.0, target_inc + 5.0))
        ])
    )
    best_coplanar = len(all_objects_df[
        (all_objects_df["ALTITUDE_KM"].between(best_alt - 25, best_alt + 25)) &
        (all_objects_df["INCLINATION"].between(target_inc - 5.0, target_inc + 5.0))
    ])
    reduction_pct = round((1 - best_coplanar / max(coplanar_objs, 1)) * 100) if coplanar_objs > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Co-Planar Traffic (±25 km, ±5°)", f"{coplanar_objs:,}", f"{shell_total:,} total in altitude band", delta_color="off")
    c2.metric("Ballistic Natural Decay", f"{decay_years} yrs", f"Needs {req_deorbit_dv} m/s EOL Δv" if decay_years > 5 else "Natural Decay ≤ 5 Yrs", delta_color="normal" if decay_years <= 5 else "inverse")
    c3.metric("Recommended Cleaner Slot", f"{best_alt} km", f"-{reduction_pct}% Co-Planar Traffic" if best_alt != target_alt and reduction_pct > 0 else "Optimal Plane")
    c4.metric("5-Year Rule Status", "PASS ✅" if compliant_5yr else "FAIL ❌")

    if not compliant_5yr:
        st.error(f"⚠️ **Regulatory Warning:** At **{target_alt} km** (BC = {ballistic_coeff} kg/m²), natural decay takes **~{decay_years} years**. You need at least **{req_deorbit_dv} m/s Δv** locked in your EOL Deorbit Reserve—or a lower deployment altitude / larger drag sail.")
    elif best_alt != target_alt and reduction_pct > 15:
        st.info(f"💡 **Rideshare Optimization:** Shifting deployment from **{target_alt} km** to **{best_alt} km** (at {target_inc}° inclination) cuts co-planar collision exposure by **{reduction_pct}%**.")
    else:
        st.success(f"✅ **{target_alt} km @ {target_inc}°** is a low-congestion, 5-year compliant orbital slot.")

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.write("### LEO Altitude Distribution")
        bins = range(250, 1250, 50)
        labels = [f"{b}-{b+50}" for b in bins[:-1]]
        active_hist = pd.cut(active_df["ALTITUDE_KM"], bins=bins, labels=labels).value_counts().sort_index()
        debris_hist = pd.cut(debris_df["ALTITUDE_KM"], bins=bins, labels=labels).value_counts().sort_index()
        st.bar_chart(pd.DataFrame({"Active Satellites": active_hist, "Tracked Debris": debris_hist}))
with col_chart2:
        st.write("### 2D Orbital Plane Map (Altitude vs. Inclination)")
        cols = ["ALTITUDE_KM", "INCLINATION", "TYPE"]
        sample_df = all_objects_df[cols].sample(min(1200, len(all_objects_df)), random_state=42)
        user_point = pd.DataFrame([{"ALTITUDE_KM": target_alt, "INCLINATION": target_inc, "TYPE": f"🎯 {mission_name}"}])
        map_df = pd.concat([sample_df, user_point], ignore_index=True)
        st.scatter_chart(map_df, x="ALTITUDE_KM", y="INCLINATION", color="TYPE")