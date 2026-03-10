
import orekit
orekit.initVM()

from orekit.pyhelpers import setup_orekit_curdir
setup_orekit_curdir("src/utils/orekit-data")

from org.orekit.frames import FramesFactory
from org.orekit.bodies import OneAxisEllipsoid, CelestialBodyFactory
from org.orekit.orbits import KeplerianOrbit, PositionAngleType
from org.orekit.time import AbsoluteDate
from org.orekit.utils import Constants
from org.orekit.propagation.analytical import KeplerianPropagator
from org.orekit.propagation.events import EclipseDetector, EventsLogger
from org.orekit.propagation.events.handlers import ContinueOnEvent

import numpy as np
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from spacecraft import Spacecraft

class Propagation:
    def __init__(self, spacecraft: Spacecraft, starting_epoch: AbsoluteDate, scenario_duration: float):
        self.starting_orbit = KeplerianOrbit(
            spacecraft.sma,
            spacecraft.ecc,
            spacecraft.inc,
            spacecraft.aop,
            spacecraft.raan,
            spacecraft.true_anomaly,
            PositionAngleType.TRUE,
            FramesFactory.getEME2000(),
            starting_epoch,
            Constants.WGS84_EARTH_MU
        )
        
        self.starting_epoch = starting_epoch
        self.propagation_duration = scenario_duration
        self.solar_panel_illuminated_fraction = []
        self.vector_timestamps = []
        self.eclipse_events = []
        self.spacecraft = spacecraft

    def getStateVectorsAtTimestep(self, state): 
        date = state.getDate()
        r_sc = state.getPVCoordinates(FramesFactory.getEME2000()).getPosition()
        r_sun = CelestialBodyFactory.getSun().getPVCoordinates(date, FramesFactory.getEME2000()).getPosition()

        self.solar_panel_illuminated_fraction.append(self.get_spacecraft_illuminated_area_as_fraction(r_sc, r_sun))
        self.solar_irradiance = self.get_solar_irradiance(r_sc, r_sun)
        self.vector_timestamps.append(date)

    def propagate(self):

        propagator = KeplerianPropagator(self.starting_orbit)

        current_date = self.starting_epoch
        end_date = self.starting_epoch.shiftedBy(self.propagation_duration)

        while current_date.compareTo(end_date) <= 0:
            state = propagator.propagate(current_date)
            self.getStateVectorsAtTimestep(state)
            current_date = current_date.shiftedBy(60.0)
   
        moon = CelestialBodyFactory.getMoon()
        moon_model = OneAxisEllipsoid(
            Constants.MOON_EQUATORIAL_RADIUS,
            0.0,
            moon.getBodyOrientedFrame()
        )
        sun = CelestialBodyFactory.getSun()

        moon_eclipse_detector = EclipseDetector(sun, Constants.SUN_RADIUS, moon_model).withUmbra().withPenumbra().withHandler(ContinueOnEvent()) 
        logger = EventsLogger()
        moon_logged_detector = logger.monitorDetector(moon_eclipse_detector)
        propagator.addEventDetector(moon_logged_detector) 
        

        final_date = self.starting_epoch.shiftedBy(self.propagation_duration)

        propagator.propagate(self.starting_epoch, final_date)

        start_time = None

        for event in logger.getLoggedEvents():
        
            if not event.isIncreasing():
                start_time = event.getState().getDate()
            elif start_time:
                stop_time = event.getState().getDate()
                self.eclipse_events.append({    "Start":start_time, 
                            "Stop":stop_time})
                start_time = None
            
        elapsed_timestamps = []
        for time in self.vector_timestamps:
            elapsed_timestamps.append(time.durationFrom(self.starting_epoch))

        eclipse_intervals = []
        for eclipse in self.eclipse_events:
            start = eclipse["Start"].durationFrom(self.starting_epoch)
            stop = eclipse["Stop"].durationFrom(self.starting_epoch)
            eclipse_intervals.append((start, stop))

        for i in range(len(eclipse_intervals)):
            for j in range(len(elapsed_timestamps)):
                if elapsed_timestamps[j] >= eclipse_intervals[i][0] and elapsed_timestamps[j] <= eclipse_intervals[i][1]:
                    self.solar_panel_illuminated_fraction[j] = 0.0

        
        battery_energy = self.spacecraft.hardware.get_solar_panel_energy_output(self.solar_irradiance, self.solar_panel_illuminated_fraction, dt=60.0)

        results_dict = {
            "elapsed_timestamps": elapsed_timestamps,
            "solar_panel_illuminated_fraction": self.solar_panel_illuminated_fraction,
            "eclipse_intervals": eclipse_intervals,
            "battery_energy": battery_energy
        }

        return results_dict

    def get_spacecraft_illuminated_area_as_fraction(self, r_sc, r_sun):

        r_sc0 = np.array([r_sc.getX(), r_sc.getY(), r_sc.getZ()])
        r_sun0 = np.array([r_sun.getX(), r_sun.getY(), r_sun.getZ()])

        r_sc_normalised = r_sc0 / np.linalg.norm(r_sc0)

        sc_sun_vector = r_sun0 - r_sc0
        sc_sun_vector_normalised = sc_sun_vector / np.linalg.norm(sc_sun_vector)

        illuminated_fraction = max(0.0, np.dot(r_sc_normalised,sc_sun_vector_normalised))

        return illuminated_fraction
    
    def get_solar_irradiance(self, r_sc, r_sun):

        r_sc0 = np.array([r_sc.getX(), r_sc.getY(), r_sc.getZ()])
        r_sun0 = np.array([r_sun.getX(), r_sun.getY(), r_sun.getZ()])
        
        distance = np.linalg.norm(r_sun0 - r_sc0)
        solar_irradiance = 1361.0 * (Constants.JPL_SSD_ASTRONOMICAL_UNIT / distance)**2
        
        return solar_irradiance
        