import sys
import os
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class OrbitalElements:
    def __init__(self, sma, ecc, inc, raan, aop, true_anomaly):
        self.sma = sma
        self.ecc = ecc
        self.inc = inc
        self.raan = raan
        self.aop = aop
        self.true_anomaly = true_anomaly


class Hardware:
    class SolarPanel:
        def __init__(self, panel_area, panel_efficiency, battery_capacity, initial_battery_energy, power_consumption):
            self.panel_area = panel_area
            self.panel_efficiency = panel_efficiency
            self.battery_capacity = battery_capacity
            self.initial_battery_energy = initial_battery_energy
            self.power_consumption = power_consumption

        def get_solar_panel_energy_output(self, solar_irradiance, illuminated_fraction, dt=60.0):

            power = self.panel_area * self.panel_efficiency * solar_irradiance * np.array(illuminated_fraction)
            delta_energy = (power - self.power_consumption) * dt

            battery_energy = np.zeros(len(delta_energy))
            battery_energy[0] = self.initial_battery_energy

            for i in range(1, len(delta_energy)):

                new_energy = battery_energy[i-1] + delta_energy[i]

                new_energy = max(0.0, min(self.battery_capacity, new_energy))

                battery_energy[i] = new_energy

            return power, battery_energy
        

class Spacecraft:
    def __init__(self, id, name, orbital_elements: OrbitalElements, hardware: Hardware):
        self.id = id
        self.name = name
        self.sma = orbital_elements.sma
        self.ecc = orbital_elements.ecc
        self.inc = orbital_elements.inc
        self.raan = orbital_elements.raan
        self.aop = orbital_elements.aop
        self.true_anomaly = orbital_elements.true_anomaly
        self.hardware = hardware