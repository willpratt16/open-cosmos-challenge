# Spacecraft Solar Power Simulation

A simulation tool for modelling the energy output of a satellite's solar panels over time. Given an orbital scenario configuration, the simulation computes solar panel illumination fractions and battery energy levels across the orbit, accounting for eclipse intervals.  

---

## Features


- Propagate spacecraft orbit with **Keplerian elements**.
- Compute **solar panel illumination fraction** over time.
- Detect **solar eclipses**.
- Compute **battery energy storage** considering constant power consumption.
- Generate **output reports** and **plots**.
- Supports **multiple spacecraft** scenarios.
- Accepts **custom scenario configurations** in JSON format.


---


## Project Structure

```
open-cosmos-challenge/
│
├── .vscode/
│   └── settings.json             # VSCode settings to suppress Pylance
│
├── src/
│   ├── main.py                   # Entry point
│   ├── scenario.py               # Scenario loading and orchestration
│   ├── spacecraft.py             # Spacecraft and solar panel modelling
│   └── propagation.py            # Orbital propagation logic 
│
├── config/                       # Create and store scenario config files here
│   │ 
│   ├── example_scenario1.json
│   └── example_scenario2.json
│
├── results/                      # Simulation outputs appear here
│
├── Dockerfile
├── entrypoint.sh
├── environment.yml
└── .gitignore
```

---

## Requirements

- [Docker](https://www.docker.com/get-started) (no other dependencies needed)

---

## Installation & Setup

**1. Clone the repository:**
```bash
git clone 
cd coding_challenge
```

**2. Build the Docker image:**
```bash
docker build -t solar-panel-sim .
```

This installs all dependencies inside the container via the `environment.yml` file - nothing needs to be installed on your machine beyond Docker.

---

## Usage

Run the simulation by passing a scenario config filename from the `config/` directory. Select the command for your operating system:

**macOS / Linux (Terminal):**
```bash
docker run -v "$(pwd)/results:/results" -v "$(pwd)/config:/app/config" solar-panel-sim example_scenario1.json
```

**Windows (PowerShell):**
```powershell
docker run -v "${PWD}/results:/results" -v "${PWD}/config:/app/config" solar-panel-sim example_scenario1.json
```

After the run completes, results will appear in your local `results/` folder.

---

## Outputs

Results are written to `results/<scenario_name>/` and organised by spacecraft ID:

```
results/
└── example_scenario1/
    ├── Simulation_Plots.png        # Solar panel illumination & battery energy charts
    └── spacecraft_1/
        ├── Output_Report.txt       # Time-series: elapsed time, illumination fraction, battery energy
        └── Eclipse_Report.txt      # Eclipse intervals: start and stop times
```

### Output_Report.txt
| Column | Description |
|---|---|
| `time_s` | Elapsed simulation time (seconds) |
| `illumination_fraction` | Fraction of solar panel area illuminated (0–1) |
| `battery_energy_J` | Battery energy level (Joules) |

### Eclipse_Report.txt
| Column | Description |
|---|---|
| `eclipse_number` | Sequential eclipse index |
| `start_time_s` | Eclipse start time (seconds) |
| `stop_time_s` | Eclipse end time (seconds) |

### Simulation_Plots.png
A two-panel chart showing:
- **Top:** Solar panel illuminated fraction over time, with eclipse periods shaded
- **Bottom:** Battery energy over time

---

## Configuration

Scenarios are defined as JSON files in the `config/` directory. To create a new scenario, add a new `.json` file and pass its filename as the argument to `docker run`.


### Top-level fields

| Field | Type | Description |
|---|---|---|
| `ScenarioName` | string | Human-readable name for the scenario, used to label the output folder |
| `Spacecrafts` | array | List of one or more spacecraft definitions (see below) |
| `StartEpoch` | object | UTC date and time at which the simulation begins |
| `DurationSeconds` | float | How long to run the simulation, in seconds |

### StartEpoch

| Field | Type | Description |
|---|---|---|
| `Year` | int | Full year (e.g. `2030`) |
| `Month` | int | Month of year (1–12) |
| `Day` | int | Day of month (1–31) |
| `Hour` | int | Hour of day (0–23) |
| `Minute` | int | Minute (0–59) |
| `Second` | float | Second (0.0–59.9) |

### Spacecraft fields

| Field | Type | Description |
|---|---|---|
| `Id` | string | Unique identifier for this spacecraft (e.g. `"SC1"`), used to label output subfolders |
| `Name` | string | Human-readable name |
| `Hardware` | object | Solar panel and battery configuration (see below) |
| `Orbit` | object | Keplerian orbital elements (see below) |

### Hardware

| Field | Type | Description |
|---|---|---|
| `Type` | string | Hardware type — currently `"SolarPanel"` |
| `PanelArea` | float | Total solar panel area in m² (e.g. `1.5`) |
| `PanelEfficiency` | float | Panel efficiency as a fraction from 0 to 1 (e.g. `0.3` = 30%) |
| `BatteryCapacity` | float | Maximum battery energy storage in Joules |
| `InitialBatteryEnergy` | float | Battery charge at the start of the simulation, in Joules |
| `PowerConsumption` | float | Constant power draw of the spacecraft in Watts |

### Orbit (Keplerian Elements)

| Field | Type | Description |
|---|---|---|
| `sma` | float | Semi-major axis in metres (e.g. `7191938.8` ≈ 820 km altitude) |
| `ecc` | float | Eccentricity — 0 is circular, values approaching 1 are highly elliptical |
| `inc` | float | Inclination in degrees (e.g. `23.44` for a low-inclination orbit) |
| `raan` | float | Right Ascension of the Ascending Node in degrees (0–360) |
| `aop` | float | Argument of Perigee in degrees (0–360) |
| `true_anomaly` | float | True anomaly at epoch in degrees |

### Example config

```json
{
    "ScenarioName": "My Scenario",
    "Spacecrafts": [
        {
            "Id": "SC1",
            "Name": "Spacecraft 1",
            "Hardware": {
                "Type": "SolarPanel",
                "PanelArea": 1.5,
                "PanelEfficiency": 0.3,
                "BatteryCapacity": 1000000.0,
                "InitialBatteryEnergy": 500000.0,
                "PowerConsumption": 100.0
            },
            "Orbit": {
                "sma": 7191938.817629013,
                "ecc": 0.05,
                "inc": 23.44,
                "raan": 0.0,
                "aop": 0.0,
                "true_anomaly": 0.0
            }
        }
    ],
    "StartEpoch": {
        "Year": 2030,
        "Month": 6,
        "Day": 1,
        "Hour": 0,
        "Minute": 0,
        "Second": 0.0
    },
    "DurationSeconds": 43200.0
}
```