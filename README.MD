# WEC Telemetry Strategy Dashboard

**Built for:** WEC LMP/Hypercar endurance racing data analysis  
**Purpose:** Demonstrate data-driven race strategy optimization for 24-hour racing  
**Status:** v1.0 - Initial build based on engineering principles, iterating with technical references

## Overview

This project simulates the core data analysis tasks a WEC Data Engineer performs during a 24-hour race:
- Hybrid energy deployment optimization
- Tire degradation prediction and stint planning
- Fuel strategy and pit window calculation

Built to demonstrate understanding of endurance racing telemetry for MTS Data Acquisition Technician Course application.

## Components

### 1. Hybrid Deployment Analyzer (`hybrid_optimizer.py`)
Simulates MGU-K energy recovery and deployment strategy for LMP Hypercars.

**Current features:**
- Energy recovery zones (braking phases)
- Deployment zones (corner exit, straights)
- Battery state-of-charge tracking
- Lap time impact estimation

**Planned improvements** (after reading *Le Mans Prototype Engineering*):
- Regulatory deployment limits per lap
- Temperature-based degradation
- Traffic impact on deployment efficiency

### 2. Tire Degradation Predictor (`tire_strategy.py`)
Predicts tire wear and optimal stint length based on compound, track temp, and fuel load.

**Current features:**
- Degradation model based on previous MacGyver toolkit
- Compound comparison (soft/medium/hard)
- Track temperature impact
- Stint length optimization

**Planned improvements:**
- Contact patch temperature distribution modeling
- Camber/pressure sensitivity
- 24-hour consistency vs. peak performance tradeoffs

### 3. Fuel Strategy Calculator (`fuel_optimizer.py`)
Calculates optimal pit windows and stint lengths for fuel efficiency.

**Current features:**
- Fuel consumption modeling
- Pit stop time loss calculation
- Stint length vs. fuel load tradeoff
- Safety margin for FCY/code 60

**Planned improvements:**
- Driver consistency modeling
- Traffic impact on consumption
- Multi-car strategy coordination

## Tech Stack

- **Python 3.10+**
- **pandas** - Data manipulation
- **numpy** - Numerical computation
- **matplotlib** - Visualization
- **streamlit** - Dashboard UI (optional)

## Installation

```bash
git clone https://github.com/yourusername/wec-telemetry-dashboard.git
cd wec-telemetry-dashboard
pip install -r requirements.txt
```

## Usage

```bash
# Run individual modules
python hybrid_optimizer.py
python tire_strategy.py
python fuel_optimizer.py

# Run full dashboard (if Streamlit implemented)
streamlit run dashboard.py
```

## Data Sources

Currently using simulated data based on:
- Public WEC lap time data
- Known LMP2/Hypercar performance parameters
- Engineering estimates from race broadcasts

**Future:** Integrate actual telemetry data when available.

## Development Roadmap

**Phase 1 (Current):** Core algorithms with simulated data  
**Phase 2 (After reading):** Refinement based on *Le Mans Prototype Engineering* chapters  
**Phase 3:** Integration with real WEC timing data  
**Phase 4:** Interactive Streamlit dashboard  

## Technical References

- *Le Mans Prototype Engineering* - Aerodynamics, Hybrid Systems, Data Analysis (Chapters 5, 9, 10)
- *GT3 Race Car Engineering* - Tire management, setup optimization
- WEC Technical Regulations 2024-2026
- Public WEC timing data (FIA WEC Live Timing)

## Why This Project

This demonstrates the intersection of:
- **Data engineering** (my CS background)
- **Domain expertise** (WEC endurance racing systems)
- **Strategic thinking** (optimization under constraints)

As a prospective WEC Data Engineer, I need to understand:
1. What the telemetry data represents (hybrid SOC, tire temps, fuel flow)
2. How to analyze it (degradation patterns, efficiency metrics)
3. Why it matters (race strategy decisions that win Le Mans)

This project is my attempt to connect those dots before formal training.

## License

MIT

## Contact

[Your Name] - Aspiring WEC Data Engineer  
Applying to: MTS Data Acquisition Technician Course (November 2026)