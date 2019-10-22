import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET

from datetime import datetime
from io import BytesIO

def get_elems_of_name(tree, name):
    '''
        Recursively find Elements of the given ElementTree or Element 
        whose tag contains the given string.

        This is useful for ignoring XML namespace, 
        e.g. to find "Speed" when the element tag is "ns3:Speed"
    '''

    return [elem for elem in tree.iter() if name in elem.tag]

def get_speed_conversions():
    return {
        "km/h"   :  0.277778,
        "m/s"    :  1.0,
        "min/mi" : 26.8224,
        "min/km" : 16.6666667,
        "mi/h"   : 0.44704
    }

def get_speed_conversion(unit):
    '''
        Return the value which converts the given unit to m/s
    '''

    conversions = get_speed_conversions()

    if not unit in conversions:
        raise ValueError(f'Unsupported unit conversion "{unit}"')

    return conversions[unit]

def edit_laps(laps, speeds, units, loglevel):
    '''
        Recalculate the all of the given laps' distances.
        Assumes each lap was run at the corresponding constant speed.
    '''

    if (len(laps) != len(speeds)):
        raise ValueError(f'Found {len(laps)} laps but {len(speeds)} speeds')
    
    dist = 0.0 # Cumulative distance
    time = None # Lap completion datetime
    
    for speed, lap in zip(speeds, laps):
        dist, time = edit_lap(lap, 
                              speed * get_speed_conversion(units), 
                              dist, 
                              time,
                              loglevel)

def edit_lap(lap, speed, dist, time, loglevel):
    '''
        Recalculate the given lap's distances.
        Assumes each lap was run at the given constant speed.

        Results depend on previously accumulated lap distances and times.
    '''

    trackpoints = get_elems_of_name(lap, 'Trackpoint')
    new_dist = dist
    new_time = time

    # Edit each trackpoint
    for trackpoint in trackpoints:
        new_dist, new_time = edit_trackpoint(trackpoint, speed, new_dist, new_time, loglevel)

    # Update lap total distance
    distances = get_elems_of_name(lap, 'DistanceMeters')
    distances[0].text = str(new_dist - dist)
    
    # Update lap max speed
    maxSpeeds = get_elems_of_name(lap, 'MaximumSpeed')
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


def edit_trackpoint(trackpoint, speed, dist, time, loglevel):
    '''
        Recalculate the trackpoint's distance as if it occured at the given speed.
        Also update the trackpoint's speed field to the given speed.
    '''

    tcx_time_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    # Assume the device was paused if 
    # a trackpoint lasts longer than this duration.
    # The trackpoint will not contribute to lap distance.
    assume_paused_duration_s = 30

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
    # be traveled at the given speed since the previous trackpoint
    trackpoint_distance = get_elems_of_name(trackpoint, 'DistanceMeters')[0]
    new_dist += speed*time_diff
    trackpoint_distance.text = str(new_dist)

    if (loglevel > 1):
        print(f"  Trackpoint:")
        print(f"    Old Distance: {dist:.0f}m")
        print(f"    New Distance: {new_dist:.0f}m")
        print(f"    Duration:     {time_diff:.1f}s")

    # Set trackpoint speed to the given speed
    for trackpoint_speed in get_elems_of_name(trackpoint, 'Speed'):
        trackpoint_speed.text = str(speed)

    return new_dist, new_time

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
        epilog=f'Example: {sys.argv[0]} activity.tcx 11.5 14.0 11.5')

    parser.add_argument('input', help='input tcx file')
    parser.add_argument('speeds', nargs='+', type=float, help='List of lap treadmill speeds')
    parser.add_argument('-o', '--output', nargs='?', help='output tcx file. Default output file for "<file>.tcx " is "<file>-edited.tcx"')
    parser.add_argument('-u', '--units', nargs='?', default='ms', help=f"lap speed units. Supported: {', '.join(str(key) for key in get_speed_conversions().keys())}")
    parser.add_argument('-v', '--verbosity', nargs='?', type=int, default='1', help=f'Level of detailed output (0=no detail, 1=some detail, >2=verbose)')
    
    return parser.parse_args()

def get_output(args):
    if args.output is not None:
        return args.output

    split = args.input.split('.')
    return f'{split[0]}-edited.{split[-1]}'

def main():
    args = parse_args()
    tree = read(args.input)
    laps = get_elems_of_name(tree, 'Lap')

    edit_laps(laps, args.speeds, args.units, args.verbosity)

    write(tree, get_output(args))

if __name__ == '__main__':
    main()