# tcxmill

Blog entry: https://blog.sltr.us/2019/10/tcxmill.html

    usage: tcxmill.py [-h] [-o [OUTPUT]] [-u [UNITS]] [-v [VERBOSITY]]
                    input speeds [speeds ...]

    Recalculate tcx lap and trackpoint distances from lap treadmill speeds

    positional arguments:
    input                 input tcx file
    speeds                List of lap treadmill speeds

    optional arguments:
    -h, --help            show this help message and exit
    -o [OUTPUT], --output [OUTPUT]
                            output tcx file. Default output file for "<file>.tcx "
                            is "<file>-edited.tcx"
    -u [UNITS], --units [UNITS]
                            lap speed units. Supported: {'km/h': 0.277778, 'm/s':
                            1.0, 'min/mi': 26.8224, 'min/km': 16.6666667}
    -v [VERBOSITY], --verbosity [VERBOSITY]
                            Level of detailed output (0=no detail, 1=some detail,
                            >2=verbose)

    Example: tcxmill.py activity.tcx 11.5 14.0 11.5

# Features

* Read and write tcx format
* Supports a variety of units
* Handles device pauses (if they last longer than 30s)
* Handle Strava peculiarities, i.e. XML namespaces

# Requirements

* python3

# Assumptions

The assumptions behind tcxmill are:

* You use Garmin Connect and Strava
* You use your device's lap key to transition through your structured workout
* The treadmill speed of each lap is constant
  * i.e. if you need to change the treadmill speed, press the lap key on your device. It does not matter if you press the lap key before, during, or after the change in speed; the acceleration will not be accounted for.
* You know the treadmill speed of each lap

# Example 1

Export your workout from Garmin Connect to TCX.

![alt text][export-tcx]
[Original TCX workout](./res/30km-progression-2019-09-25/activity.tcx)

Strava charts for the above workout: 
![alt text][summary-before]
![alt text][charts-before]

If the activity has been previously uploaded to Strava, you must delete it or you will get a duplicate activity error. 

* **Warning**  Deleting an activity will delete all kudos and comments for that activity. 

* **Warning** TCX does not have temperature data. If your activity with temperature data automatically synced from Garmin Connect, you will lose this field on Strava.

Run tcxmill, passing in the workout structure. The structure of the above workout is

* 3km at 11.5km/h
* 6km at 14.0km/h
* 1km at 11.5km/h
* 5km at 14.1km/h
* 1km at 11.5km/h
* 4km at 14.2km/h
* 1km at 11.5km/h
* 3km at 14.3km/h
* 1km at 11.5km/h
* 2km at 14.4km/h
* 1km at 11.5km/h
* 1km at 14.5km/h
* 1km at 11.5km/h

Here is the call to produce the tcx file and chart below:

    python3 tcxmill.py activity.tcx 11.5 14.0 11.5 14.1 11.5 14.2 11.5 14.3 11.5 14.4 11.5 14.5 11.5 -u km/h
    {"Lap": {"Distance": "2990m", "Cumulative": "2990m", "Speed": "3.19 m/s", "Completed": "2019-09-25 08:53:31"}}
    {"Lap": {"Distance": "5985m", "Cumulative": "8975m", "Speed": "3.89 m/s", "Completed": "2019-09-25 09:19:10"}}
    {"Lap": {"Distance": "1003m", "Cumulative": "9978m", "Speed": "3.19 m/s", "Completed": "2019-09-25 09:24:24"}}
    {"Lap": {"Distance": "4998m", "Cumulative": "14976m", "Speed": "3.92 m/s", "Completed": "2019-09-25 09:45:40"}}
    {"Lap": {"Distance": "1000m", "Cumulative": "15976m", "Speed": "3.19 m/s", "Completed": "2019-09-25 09:50:53"}}
    {"Lap": {"Distance": "4000m", "Cumulative": "19975m", "Speed": "3.94 m/s", "Completed": "2019-09-25 10:07:47"}}
    {"Lap": {"Distance": "1003m", "Cumulative": "20978m", "Speed": "3.19 m/s", "Completed": "2019-09-25 10:13:01"}}
    {"Lap": {"Distance": "3003m", "Cumulative": "23981m", "Speed": "3.97 m/s", "Completed": "2019-09-25 10:25:37"}}
    {"Lap": {"Distance": "1003m", "Cumulative": "24984m", "Speed": "3.19 m/s", "Completed": "2019-09-25 10:30:51"}}
    {"Lap": {"Distance": "2004m", "Cumulative": "26988m", "Speed": "4.00 m/s", "Completed": "2019-09-25 10:39:12"}}
    {"Lap": {"Distance": "1000m", "Cumulative": "27988m", "Speed": "3.19 m/s", "Completed": "2019-09-25 10:44:25"}}
    {"Lap": {"Distance": "1003m", "Cumulative": "28991m", "Speed": "4.03 m/s", "Completed": "2019-09-25 10:48:34"}}
    {"Lap": {"Distance": "1000m", "Cumulative": "29991m", "Speed": "3.19 m/s", "Completed": "2019-09-25 10:53:47"}}

[Processed TCX workout](./res/30km-progression-2019-09-25/activity-edited.tcx)

Upload the tcx file to Strava
![alt text][upload]
![alt text][upload-file]

Strava charts for the above workout: 
![alt text][summary-after]
![alt text][charts-after]

# Example 2

[Original TCX workout](./res/10km-2019-10-18/activity.tcx)

Strava before tcxmill: 
![alt text][10km-charts-before]

    python3 tcxmill.py activity.tcx 11.5 -u km/h                         
    Warning: assuming the device was paused during trackpoint with very long duration 114.0s
    {"Lap": {"Distance": "10002m", "Cumulative": "10002m", "Speed": "3.19 m/s", "Completed": "2019-10-18 10:41:20"}}

**Note** The warning above shows that tcxmill detected a device pause. The device is assumed paused if a trackpoint lasts longer than 30s. tcxmill assumes zero speed during a device pause. This is useful if you need to jump off the treadmill for e.g. a bathroom break or your workout has rest intervals.

[Processed TCX workout](./res/10km-2019-10-18/activity-edited.tcx)

Strava after tcxmill: 
![alt text][10km-charts-after]

[export-tcx]: ./res/30km-progression-2019-09-25/export-tcx.png "Strava charts before running tcxmill"
[charts-before]: ./res/30km-progression-2019-09-25/charts-before.png "Strava charts before running tcxmill"
[charts-after]: ./res/30km-progression-2019-09-25/charts-after.png "Strava charts after running tcxmill"
[summary-before]: ./res/30km-progression-2019-09-25/summary-before.png "Strava summary before running tcxmill"
[summary-after]: ./res/30km-progression-2019-09-25/summary-after.png "Strava summary after running tcxmill"
[upload]: ./res/30km-progression-2019-09-25/upload.png "Strava upload"
[upload-file]: ./res/30km-progression-2019-09-25/upload-file.png "Strava file upload"

[10km-charts-before]: ./res/10km-2019-10-18/before.png "Strava charts before running tcxmill"
[10km-charts-after]: ./res/10km-2019-10-18/after.png "Strava charts before running tcxmill"
