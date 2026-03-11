from pathlib import Path
from scenario import Scenario
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("/results/simulation.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():

    try:
        config_file = sys.argv[1]

    except IndexError:
        logger.error("No config file provided")
        print("Usage: python main.py <config_file>")
        sys.exit(1)

    config_path = Path("/app/config") / config_file

    try:
        scenario = Scenario(config_path=str(config_path))
        scenario.propagate_scenario()
        scenario.create_output_reports()
        scenario.plot_results()

        logger.info("Simulation completed successfully")

    except Exception:
        logger.exception("Simulation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()