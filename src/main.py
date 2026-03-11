import sys
from pathlib import Path
from scenario import Scenario

def main():

    if len(sys.argv) < 2:
        print("Usage: python main.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    config_path = Path("/app/config") / config_file

    scenario = Scenario(config_path=str(config_path))
    scenario.propagate_scenario()
    scenario.create_output_reports()
    scenario.plot_results()

if __name__ == "__main__":
    main()