import sys
from scenario import Scenario

def main():

    if len(sys.argv) < 2:
        print("Usage: python main.py <config_file>")
        sys.exit(1)

    config_path = sys.argv[1]

    scenario = Scenario(config_path=config_path)
    scenario.propagate_scenario()
    scenario.create_output_reports()
    scenario.plot_results()


if __name__ == "__main__":
    main()