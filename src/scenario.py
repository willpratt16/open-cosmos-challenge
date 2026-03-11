import orekit
orekit.initVM()

from orekit.pyhelpers import setup_orekit_curdir
setup_orekit_curdir("src/utils/orekit-data")

from spacecraft import Spacecraft, OrbitalElements, Hardware
from propagation import Propagation

from pathlib import Path
from math import radians
import matplotlib.pyplot as plt
import json
import os
import logging

from org.orekit.time import AbsoluteDate, TimeScalesFactory

utc = TimeScalesFactory.getUTC() # Get the UTC time scale
BASE_RESULTS_DIR = Path(os.environ.get("OUTPUT_DIR", "/results"))
logger = logging.getLogger(__name__)

class Scenario:
    def __init__(self, config_path: str):  

        try:
            with open(config_path, "r") as f:
                config = json.load(f)

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON format in config file")
            raise ValueError("Config file is not valid JSON") from e

        self.validate_config(config)
        self.initialise_scenario(config)

    def validate_config(self, config):

        required_fields = [
            "ScenarioName",
            "Spacecrafts",
            "StartEpoch",
            "DurationSeconds"
        ]

        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required config field: {field}")

        if config["DurationSeconds"] <= 0:
            raise ValueError("DurationSeconds must be positive")

        logger.info(f"Config validated.")

        

    def initialise_scenario(self, config):

        self.scenario_name = config["ScenarioName"]

        self.spacecrafts = []

        try: 
            for spacecraft in config["Spacecrafts"]:

                sc_hardware = Hardware.SolarPanel(
                    panel_area=spacecraft["Hardware"]["PanelArea"],
                    panel_efficiency=spacecraft["Hardware"]["PanelEfficiency"],
                    battery_capacity=spacecraft["Hardware"]["BatteryCapacity"],
                    initial_battery_energy=spacecraft["Hardware"]["InitialBatteryEnergy"],
                    power_consumption=spacecraft["Hardware"]["PowerConsumption"]
                )
                orbital_elements = OrbitalElements(
                    sma=spacecraft["Orbit"]["sma"],
                    ecc=spacecraft["Orbit"]["ecc"],
                    inc=radians(spacecraft["Orbit"]["inc"]),
                    raan=radians(spacecraft["Orbit"]["raan"]),
                    aop=radians(spacecraft["Orbit"]["aop"]),
                    true_anomaly=radians(spacecraft["Orbit"]["true_anomaly"])
                )
                self.spacecrafts.append(
                    Spacecraft(
                        id=spacecraft["Id"],
                        name=spacecraft["Name"],
                        orbital_elements=orbital_elements,
                        hardware=sc_hardware
                    )
                )
        except Exception as e:
            raise ValueError(f"Spacecraft config is missing required field: {e}") from e

        try:
            self.starting_epoch = AbsoluteDate(
                config["StartEpoch"]["Year"],
                config["StartEpoch"]["Month"],
                config["StartEpoch"]["Day"],
                config["StartEpoch"]["Hour"],
                config["StartEpoch"]["Minute"],
                config["StartEpoch"]["Second"],
                utc
            )
        except Exception as e:
            raise ValueError(f"StartEpoch config is missing required field: {e}") from e
        
        try:
            self.scenario_duration = config["DurationSeconds"]
        except Exception as e:
            raise ValueError(f"DurationSeconds config is missing required field: {e}") from e

        logger.info(f"Scenario '{self.scenario_name}' initialised with {len(self.spacecrafts)} spacecraft(s).")


    def propagate_scenario(self):

        logger.info("Starting scenario propagation")

        self.results = {}

        try:
            for spacecraft in self.spacecrafts:
                logger.info(f"Propagating {spacecraft.id}...")
                propagation = Propagation(spacecraft, self.starting_epoch, self.scenario_duration)
                self.results[spacecraft.id] = propagation.propagate()
        except Exception:
            logger.exception(f"Error during scenario propagation.")
            raise
        
        logger.info("Scenario propagation complete.")

    def create_output_reports(self):

        logger.info("Creating output reports.")

        for sc_id in self.results.keys():

            output_dir = BASE_RESULTS_DIR / self.scenario_name.replace(' ', '_') / sc_id
            output_dir.mkdir(parents=True, exist_ok=True)

            with open(output_dir / "Output_Report.txt", "w") as f:
                f.write(f"{'time_s':<15}{'illumination_fraction':<25}{'battery_energy_J':<20}\n")
                for t, illum, energy in zip(self.results[sc_id]['elapsed_timestamps'], self.results[sc_id]['solar_panel_illuminated_fraction'], self.results[sc_id]['battery_energy']):
                    f.write(f"{t:<15.2f}{illum:<25.4f}{energy:<20.2f}\n")
                
            if self.results[sc_id]['eclipse_intervals']:
                with open(output_dir / "Eclipse_Report.txt", "w") as f:
                    f.write(f"{'eclipse_number':<15}{'start_time_s':<15}{'stop_time_s':<15}\n")
                    for i, (start, stop) in enumerate(self.results[sc_id]['eclipse_intervals']):
                        f.write(f"{i:<15}{start:<15.2f}{stop:<15.2f}\n")


    def plot_results(self):

        print("Plotting results...")

        output_dir = BASE_RESULTS_DIR / self.scenario_name.replace(' ', '_')
        output_dir.mkdir(parents=True, exist_ok=True)

        fig, axes = plt.subplots(2, 1, figsize=(10, 8))

        ax1 = axes[0]
        ax2 = axes[1]

        plot_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        for idx, sc_id in enumerate(self.results.keys()):
            color = plot_colors[idx % len(plot_colors)]
            for i, (start, stop) in enumerate(self.results[sc_id]['eclipse_intervals']):
                ax1.axvspan(
                    start,
                    stop,
                    facecolor=color,
                    hatch="//",
                    edgecolor=color,
                    alpha=0.3,
                )
            ax1.plot(
                self.results[sc_id]['elapsed_timestamps'],
                self.results[sc_id]['solar_panel_illuminated_fraction'],
                color=color,
                label=sc_id
            )

        ax1.set_xlabel('Elapsed Time (s)')
        ax1.set_ylabel('Solar Panel Illuminated Fraction')
        ax1.set_title('Solar Panel Illuminated Fraction Over Time')

        for sc_id in self.results.keys():
            ax2.plot(
                self.results[sc_id]['elapsed_timestamps'],
                self.results[sc_id]['battery_energy'],
                label=sc_id
            )

        ax2.legend(title="Spacecraft ID")
        ax2.set_xlabel('Elapsed Time (s)')
        ax2.set_ylabel('Battery Energy (J)')
        ax2.set_title('Battery Energy Over Time')

        plt.tight_layout()

        fig.savefig(output_dir / "Simulation_Plots.png", dpi=300)
