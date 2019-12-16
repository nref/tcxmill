import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
from io import BytesIO

tcx_time_format = '%Y-%m-%dT%H:%M:%S.%fZ'

def get_elems_of_name(tree, name):
    '''
        Recursively find Elements of the given ElementTree or Element 
        whose tag contains the given string.

        This is useful for ignoring XML namespace, 
        e.g. to find "Speed" when the element tag is "ns3:Speed"
    '''

    return [elem for elem in tree.iter() if name in elem.tag]

def get_speed_conversions():
    '''
        Return unit conversions to m/s
    '''

    return {
        "km/h"   :  0.277778,
        "m/s"    :  1.0,
        "min/mi" : 26.8224,
        "min/km" : 16.6666667,
        "mi/h"   :  0.44704
    }

def get_seconds_conversions():
    '''
        Return the multiplier to convert 
        the time component of the given unit to seconds
    '''

    return {
        "km/h"   : 3600, # 1h == 3600s
        "m/s"    : 1.0,
        "min/mi" : 0.01666666666, # = 1/60s
        "min/km" : 0.01666666666, # = 1/60s
        "mi/h"   : 3600
    }

def get_speed_conversion(unit):
    '''
        Return the value which converts the given unit to m/s
    '''

    conversions = get_speed_conversions()

    if not unit in conversions:
        raise ValueError(f'Unsupported unit conversion "{unit}"')

    return conversions[unit]


def convert_to_seconds(unit):
    '''
        Return the multiplier to convert 
        the time component of the given unit to seconds
    '''

    conversions = get_seconds_conversions()

    if not unit in conversions:
        raise ValueError(f'Unsupported unit conversion "{unit}"')

    return conversions[unit]

class TrackpointWindow:

    def __init__(self, start_time, start_dist, speed, distance, units):
        self.start_time = start_time
        self.start_dist = start_dist
        self.speed = speed
        self.distance = distance
        self.duration = self.distance / self.speed * convert_to_seconds(units)
        self.end_time = self.start_time + timedelta(seconds=self.duration)

    def find(self, laps):
        '''
            Find trackpoints in the time window,
            and find laps containing any of those trackpoints.
        '''

        window_trackpoints = []
        window_laps = []

        for lap in laps:
            lap_trackpoint_elems = get_elems_of_name(lap, 'Trackpoint')

            for trackpoint in lap_trackpoint_elems:
                time_elem = get_elems_of_name(trackpoint, 'Time')[0]
                trackpoint_time = datetime.strptime(time_elem.text, tcx_time_format)

                if trackpoint_time >= self.start_time and trackpoint_time <= self.end_time:
                    window_trackpoints.append(trackpoint)
            
            if len(window_trackpoints) > 0:
                window_laps.append(lap)

        return window_laps, window_trackpoints

    def recalc_trackpoints(self, laps, units, loglevel):

        window_laps, window_trackpoints = self.find(laps)

        if (loglevel > 1):
            print(f'Found {len(window_trackpoints)} trackpoint(s) '
                  f'and {len(window_laps)} lap(s) '
                  f'for speed {self.speed:.2f} {units} '
                  f'and distance {self.distance} '
                  f'starting at {self.start_time} '
                  f'and ending at {self.end_time} '
                  f'({self.duration:.2f}s)')
        
        dist = self.start_dist
        time = self.start_time
        
        for trackpoint in window_trackpoints:
            dist, time = recalc_trackpoint_from_speed(trackpoint, 
                                                    self.speed * get_speed_conversion(units),
                                                    dist,
                                                    time, 
                                                    loglevel)

        return self.end_time, dist

def recalc_laps_from_speed_and_distance(laps, speeds, distances, units, loglevel):
    '''
        From the given workout structure (sequential speed/distance pairs), 
        recalculate the lap and trackpoint distances and speeds.
        Assumes each distance was run at the corresponding constant speed.
    '''

    if (len(laps) == 0 ):
        raise ValueError(f'Found no laps but requre at least 1')

    if (len(distances) != len(speeds)):
        raise ValueError(f'Found {len(distances)} distances but {len(speeds)} speeds')

    start_time = datetime.strptime(laps[0].get('StartTime'), tcx_time_format)
    start_dist = 0.0

    for speed, distance in zip(speeds, distances):
        window = TrackpointWindow(start_time, start_dist, speed, distance, units)
        start_time, start_dist = window.recalc_trackpoints(laps, units, loglevel)

    recalc_laps(laps, loglevel)

def recalc_laps(laps, loglevel):
    '''
        Recalculate lap DistanceMeters by summing trackpoint distances.
        Recalculate lap MaximumSpeed from the fastest trackpoint.
    '''

    for lap in laps:

        trackpoints = get_elems_of_name(lap, 'Trackpoint')
        distances = get_elems_of_name(lap, 'DistanceMeters')
        maxSpeeds = get_elems_of_name(lap, 'MaximumSpeed')

        lap_max_speed, lap_distance = get_max_speed_and_distance(trackpoints)

        distances[0].text = str(lap_distance)
        maxSpeeds[0].text = str(lap_max_speed)

def get_max_speed_and_distance(trackpoints):
    '''
        Return the maximum speed from and distance traveled over the given trackpoints
    '''

    max_speed = 0.0

    # Get total distance and max speed
    for trackpoint in trackpoints:
        trackpoint_distance_elem = get_elems_of_name(trackpoint, 'DistanceMeters')[0]
        trackpoint_speed_elem = get_elems_of_name(trackpoint, 'Speed')[0]

        distance = float(trackpoint_distance_elem.text)
        trackpoint_speed = float(trackpoint_speed_elem.text)
        max_speed = max_speed if trackpoint_speed < max_speed else trackpoint_speed

    return max_speed, distance

def recalc_laps_from_speed(laps, speeds, units, loglevel):
    '''
        Recalculate the all of the given laps' distances.
        Assumes each lap was run at the corresponding constant speed.
    '''

    if (len(laps) != len(speeds)):
        raise ValueError(f'Found {len(laps)} laps but {len(speeds)} speeds')
    
    dist = 0.0 # Cumulative distance
    time = None # Lap completion datetime
    
    for speed, lap in zip(speeds, laps):
        dist, time = recalc_lap_from_speed(lap, 
                                           speed * get_speed_conversion(units), 
                                           dist, 
                                           time,
                                           loglevel)

def recalc_lap_from_speed(lap, speed, dist, time, loglevel):
    '''
        Recalculate the given lap's distances.
        Assumes each lap was run at the given constant speed.

        Results depend on previously accumulated lap distances and times.
    '''

    trackpoints = get_elems_of_name(lap, 'Trackpoint')
    distances = get_elems_of_name(lap, 'DistanceMeters')
    maxSpeeds = get_elems_of_name(lap, 'MaximumSpeed')

    new_dist = dist
    new_time = time

    # Edit each trackpoint
    for trackpoint in trackpoints:
        new_dist, new_time = recalc_trackpoint_from_speed(trackpoint, speed, new_dist, new_time, loglevel)

    # Update lap total distance
    distances[0].text = str(new_dist - dist)
    
    # Update lap max speed
    maxSpeeds[0].text = str(speed)

    if (loglevel > 0):
        print_lap(new_dist, dist, speed, new_time)

    return new_dist, new_time

def print_lap(new_dist, dist, speed, new_time):

    lap = {
        "Distance": f'{new_dist - dist:.0f}m',
        "Cumulative": f'{new_dist:.0f}m',
        "Speed": f'{speed:.2f} m/s',
        "Completed": f'{new_time}'
    }

    print(f'{{"Lap": {json.dumps(lap)}}}')

def recalc_trackpoint_from_speed(trackpoint, speed, dist, time, loglevel):
    '''
        Recalculate the trackpoint's distance as if it occured at the given speed.
        Also update the trackpoint's speed field to the given speed.
    '''

    # Assume the device was paused if 
    # a trackpoint lasts longer than this duration.
    # The trackpoint will not contribute to lap distance.
    assume_paused_duration_s = 10

    new_dist = dist
    new_time = datetime.strptime(get_elems_of_name(trackpoint, 'Time')[0].text, tcx_time_format)

    # Get time in seconds since the previous trackpoint
    time_diff = 0
    if time is not None: # Not yet set for first trackpoint
        time_diff = (new_time - time).total_seconds()
    
    if (time_diff > assume_paused_duration_s):
        print(f"Warning: assuming the device was paused during trackpoint with very long duration {time_diff}s")
        speed = 0

    # Set trackpoint distance to the distance that would 
    # be traveled at the given speed
    trackpoint_distance = get_elems_of_name(trackpoint, 'DistanceMeters')[0]
    new_dist += speed*time_diff
    trackpoint_distance.text = str(new_dist)

    if (loglevel > 2):
        print(f"  Trackpoint:")
        print(f"    Old Distance: {dist:.0f}m")
        print(f"    New Distance: {new_dist:.0f}m")
        print(f"    Duration:     {time_diff:.1f}s")

    # Set trackpoint speed to the given speed
    for trackpoint_speed in get_elems_of_name(trackpoint, 'Speed'):
        trackpoint_speed.text = str(speed)

    return new_dist, new_time

def add_distance(tree, delta):
    trackpoints = get_elems_of_name(tree, "Trackpoint")
    
    # Edit each trackpoint
    for trackpoint in trackpoints:
        trackpoint_distance_elem = get_elems_of_name(trackpoint, 'DistanceMeters')[0]
        distance = float(trackpoint_distance_elem.text)
        distance += delta
        trackpoint_distance_elem.text = str(distance)
        
def read(file):
    return ET.parse(file)

def write(tree, file):
    
    encoding = 'utf-8'

    # Write to fake file since ElementTree.tostring doesn't include xml declaration
    f = BytesIO()
    tree.write(f, encoding=encoding, xml_declaration=True)

    # Decode byte stream to a string
    s = f.getvalue().decode(encoding)

    # Strava doesn't like namespaces. Remove "<ns2:...>" etc
    s = re.sub(r'ns\d+:', '', s)

    with open(file, "w") as f2:
        print(s, file=f2)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Recalculate tcx lap and trackpoint distances from lap treadmill speeds',
        epilog=f'Example: {sys.argv[0]} activity.tcx --speeds 11.5 14.0 11.5 --units mi/h')

    parser.add_argument('input',                                                   help='input tcx file')
    parser.add_argument('-s', '--speeds',    nargs='+', type=float,                help='List of speeds')
    parser.add_argument('-d', '--distances', nargs='+', type=float,                help='List of distances. Use this when laps representing workout structure are not available.')
    parser.add_argument('-o', '--output',    nargs='?',                            help='output tcx file. Default output file for "<file>.tcx " is "<file>-edited.tcx"')
    parser.add_argument('-u', '--units',     nargs='?',             default='m/s', help=f"lap speed units. Supported: {', '.join(str(key) for key in get_speed_conversions().keys())}")
    parser.add_argument('-v', '--verbosity', nargs='?', type=int,   default='1',   help=f'Level of detailed output (0=no detail, 1=some detail, >2=verbose)')
    parser.add_argument('-a', '--add',       nargs='?', type=float,                help=f'Add the given value to each trackpoint')

    return parser.parse_args()

def get_output(input, output):
    if output is not None:
        return output

    split = input.split('.')
    return f'{split[0]}-edited.{split[-1]}'

def main():
    args = parse_args()
    tree = read(args.input)
    laps = get_elems_of_name(tree, 'Lap')
    
    if args.add is not None:
        add_distance(tree, args.add)
    elif args.speeds is not None:
        if args.distances is not None:
            recalc_laps_from_speed_and_distance(laps, args.speeds, args.distances, args.units, args.verbosity)
        else:
            recalc_laps_from_speed(laps, args.speeds, args.units, args.verbosity)

    write(tree, get_output(args.input, args.output))

if __name__ == '__main__':
    main()