# tcxmill

Blog entry: https://www.sltr.us/2019/10/tcxmill.html

    usage: tcxmill.py [-h] [-s SPEEDS [SPEEDS ...]] [-d DISTANCES [DISTANCES ...]]
                    [-o [OUTPUT]] [-u [UNITS]] [-v [VERBOSITY]] [-a [ADD]]
                    input

    Recalculate tcx lap and trackpoint distances from lap treadmill speeds

    positional arguments:
    input                 input tcx file

    optional arguments:
    -h, --help            show this help message and exit
    -s SPEEDS [SPEEDS ...], --speeds SPEEDS [SPEEDS ...]
                            List of speeds
    -d DISTANCES [DISTANCES ...], --distances DISTANCES [DISTANCES ...]
                            List of distances. Use this when laps representing
                            workout structure are not available.
    -o [OUTPUT], --output [OUTPUT]
                            output tcx file. Default output file for "<file>.tcx "
                            is "<file>-edited.tcx"
    -u [UNITS], --units [UNITS]
                            lap speed units. Supported: km/h, m/s, min/mi, min/km,
                            mi/h
    -v [VERBOSITY], --verbosity [VERBOSITY]
                            Level of detailed output (0=no detail, 1=some detail,
                            >2=verbose)
    -a [ADD], --add [ADD]
                            Add the given value to each trackpoint

    Example: tcxmill.py activity.tcx --speeds 11.5 14.0 11.5 --units mi/h

# Features

* Read and write tcx format
* Supports a variety of units
* Handles device pauses (if they last longer than 10s)
* Handle Strava peculiarities, i.e. XML namespaces

# Requirements

* python3

# Assumptions

The assumptions behind tcxmill are:

* You use a treadmill
* You use Garmin Connect and Strava
* You don't use your device's lap key, and:
    * You know the treadmill speed of each segment of your workout.
    * You know the treadmill distance of each segment of your workout.
* (Optional) You use your device's lap key to transition through your structured workout, and
    * You know the treadmill speed of each segment of your workout.
    * The treadmill speed of each lap is constant
        * i.e. if you need to change the treadmill speed, press the lap key on your device. It does not matter if you press the lap key before, during, or after the change in speed; the acceleration will not be accounted for.

# Example 1

A workout where the lap key was used. Export your workout from Garmin Connect to TCX.

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

    python3 tcxmill.py activity.tcx --speeds 11.5 14.0 11.5 14.1 11.5 14.2 11.5 14.3 11.5 14.4 11.5 14.5 11.5 -u km/h
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

Another workout where the lap key was used. Strava before tcxmill: 
![alt text][10km-charts-before]

    python3 tcxmill.py activity.tcx --speeds 11.5 -u km/h                         
    Warning: assuming the device was paused during trackpoint with very long duration 114.0s
    {"Lap": {"Distance": "10002m", "Cumulative": "10002m", "Speed": "3.19 m/s", "Completed": "2019-10-18 10:41:20"}}

**Note** The warning above shows that tcxmill detected a device pause. The device is assumed paused if a trackpoint lasts longer than 30s. tcxmill assumes zero speed during a device pause. This is useful if you need to jump off the treadmill for e.g. a bathroom break or your workout has rest intervals.

[Processed TCX workout](./res/10km-2019-10-18/activity-edited.tcx)

Strava after tcxmill: 
![alt text][10km-charts-after]

# Example 3

[Original TCX workout](./res/8mi-progression-2019-12-13/activity.tcx)

A workout where the lap key *was not* used. In lieu of using laps to indicate workout structure, txcmill is provided speeds and distances. Garmin before tcxmill: 
![alt text][8mi-charts-before]

    python3 tcxmill.py res/8mi-progression-2019-12-13/activity.tcx --speeds 7.5 7.6 7.7 7.8 7.9 8.0 8.1 8.2 8.3 8.4 8.5 8.6 8.7 8.8 8.9 9.0 --distances 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 -u mi/h --verbosity 2
    Found 238 trackpoint(s) and 1 lap(s) for speed 7.50 mi/h and distance 0.5 starting at 2019-12-13 11:59:25 and ending at 2019-12-13 12:03:25 (240.00s)
    Found 236 trackpoint(s) and 1 lap(s) for speed 7.60 mi/h and distance 0.5 starting at 2019-12-13 12:03:25 and ending at 2019-12-13 12:07:21.842105 (236.84s)
    Found 231 trackpoint(s) and 1 lap(s) for speed 7.70 mi/h and distance 0.5 starting at 2019-12-13 12:07:21.842105 and ending at 2019-12-13 12:11:15.608339 (233.77s)
    Found 229 trackpoint(s) and 1 lap(s) for speed 7.80 mi/h and distance 0.5 starting at 2019-12-13 12:11:15.608339 and ending at 2019-12-13 12:15:06.377570 (230.77s)
    Found 227 trackpoint(s) and 1 lap(s) for speed 7.90 mi/h and distance 0.5 starting at 2019-12-13 12:15:06.377570 and ending at 2019-12-13 12:18:54.225671 (227.85s)
    Found 223 trackpoint(s) and 1 lap(s) for speed 8.00 mi/h and distance 0.5 starting at 2019-12-13 12:18:54.225671 and ending at 2019-12-13 12:22:39.225671 (225.00s)
    Found 221 trackpoint(s) and 1 lap(s) for speed 8.10 mi/h and distance 0.5 starting at 2019-12-13 12:22:39.225671 and ending at 2019-12-13 12:26:21.447893 (222.22s)
    Found 218 trackpoint(s) and 1 lap(s) for speed 8.20 mi/h and distance 0.5 starting at 2019-12-13 12:26:21.447893 and ending at 2019-12-13 12:30:00.960088 (219.51s)
    Found 215 trackpoint(s) and 1 lap(s) for speed 8.30 mi/h and distance 0.5 starting at 2019-12-13 12:30:00.960088 and ending at 2019-12-13 12:33:37.827558 (216.87s)
    Found 213 trackpoint(s) and 1 lap(s) for speed 8.40 mi/h and distance 0.5 starting at 2019-12-13 12:33:37.827558 and ending at 2019-12-13 12:37:12.113272 (214.29s)
    Found 210 trackpoint(s) and 1 lap(s) for speed 8.50 mi/h and distance 0.5 starting at 2019-12-13 12:37:12.113272 and ending at 2019-12-13 12:40:43.877978 (211.76s)
    Found 207 trackpoint(s) and 1 lap(s) for speed 8.60 mi/h and distance 0.5 starting at 2019-12-13 12:40:43.877978 and ending at 2019-12-13 12:44:13.180304 (209.30s)
    Found 205 trackpoint(s) and 1 lap(s) for speed 8.70 mi/h and distance 0.5 starting at 2019-12-13 12:44:13.180304 and ending at 2019-12-13 12:47:40.076856 (206.90s)
    Found 203 trackpoint(s) and 1 lap(s) for speed 8.80 mi/h and distance 0.5 starting at 2019-12-13 12:47:40.076856 and ending at 2019-12-13 12:51:04.622311 (204.55s)
    Found 200 trackpoint(s) and 1 lap(s) for speed 8.90 mi/h and distance 0.5 starting at 2019-12-13 12:51:04.622311 and ending at 2019-12-13 12:54:26.869502 (202.25s)
    Found 193 trackpoint(s) and 1 lap(s) for speed 9.00 mi/h and distance 0.5 starting at 2019-12-13 12:54:26.869502 and ending at 2019-12-13 12:57:46.869502 (200.00s)

[Processed TCX workout](./res/8mi-progression-2019-12-13/activity-edited.tcx)

Strava after tcxmill: 
![alt text][8mi-charts-after]

# Example 4
A workout where the lap key was used and you know only the distance you run. Export your workout from Garmin Connect to TCX.

It was an Interval training following this structure:
* Warm up: 1km
* 16x
  * 400m run (15.5km/h ~ 16.5km/h)
  * 300m recover easy
* Cool down: 1km

So the lap key was used to register the times I did run, but I don't know the speed, so the way to fix it is like this:


    python3 tcxmill.py ~/Downloads/activity_5039667047.tcx --distances 1000 400 300 400 300 400 300 400 300 400 300 400 300 400 300 400 300 400 300 400 300 400 300 400 300 400 300 400 300 400 300 400 300 1000
    {"Lap": {"Distance": "1000m", "Cumulative": "1000m", "Speed": "2.70 m/s", "Completed": "2020-06-04 16:13:30"}}
    {"Lap": {"Distance": "400m", "Cumulative": "1400m", "Speed": "4.04 m/s", "Completed": "2020-06-04 16:15:09"}}
    {"Lap": {"Distance": "300m", "Cumulative": "1700m", "Speed": "2.63 m/s", "Completed": "2020-06-04 16:17:03"}}
    {"Lap": {"Distance": "400m", "Cumulative": "2100m", "Speed": "4.71 m/s", "Completed": "2020-06-04 16:18:28"}}
    {"Lap": {"Distance": "300m", "Cumulative": "2400m", "Speed": "2.61 m/s", "Completed": "2020-06-04 16:20:23"}}
    {"Lap": {"Distance": "400m", "Cumulative": "2800m", "Speed": "4.26 m/s", "Completed": "2020-06-04 16:21:57"}}
    {"Lap": {"Distance": "300m", "Cumulative": "3100m", "Speed": "2.68 m/s", "Completed": "2020-06-04 16:23:49"}}
    {"Lap": {"Distance": "400m", "Cumulative": "3500m", "Speed": "4.35 m/s", "Completed": "2020-06-04 16:25:21"}}
    {"Lap": {"Distance": "300m", "Cumulative": "3800m", "Speed": "2.50 m/s", "Completed": "2020-06-04 16:27:21"}}
    {"Lap": {"Distance": "400m", "Cumulative": "4200m", "Speed": "4.30 m/s", "Completed": "2020-06-04 16:28:54"}}
    {"Lap": {"Distance": "300m", "Cumulative": "4500m", "Speed": "2.36 m/s", "Completed": "2020-06-04 16:31:01"}}
    {"Lap": {"Distance": "400m", "Cumulative": "4900m", "Speed": "4.35 m/s", "Completed": "2020-06-04 16:32:33"}}
    {"Lap": {"Distance": "300m", "Cumulative": "5200m", "Speed": "2.88 m/s", "Completed": "2020-06-04 16:34:17"}}
    {"Lap": {"Distance": "400m", "Cumulative": "5600m", "Speed": "4.49 m/s", "Completed": "2020-06-04 16:35:46"}}
    {"Lap": {"Distance": "300m", "Cumulative": "5900m", "Speed": "2.75 m/s", "Completed": "2020-06-04 16:37:35"}}
    {"Lap": {"Distance": "400m", "Cumulative": "6300m", "Speed": "4.26 m/s", "Completed": "2020-06-04 16:39:09"}}
    {"Lap": {"Distance": "300m", "Cumulative": "6600m", "Speed": "2.75 m/s", "Completed": "2020-06-04 16:40:58"}}
    {"Lap": {"Distance": "400m", "Cumulative": "7000m", "Speed": "4.44 m/s", "Completed": "2020-06-04 16:42:28"}}
    {"Lap": {"Distance": "300m", "Cumulative": "7300m", "Speed": "2.46 m/s", "Completed": "2020-06-04 16:44:30"}}
    {"Lap": {"Distance": "400m", "Cumulative": "7700m", "Speed": "4.44 m/s", "Completed": "2020-06-04 16:46:00"}}
    {"Lap": {"Distance": "300m", "Cumulative": "8000m", "Speed": "2.61 m/s", "Completed": "2020-06-04 16:47:55"}}
    {"Lap": {"Distance": "400m", "Cumulative": "8400m", "Speed": "4.40 m/s", "Completed": "2020-06-04 16:49:26"}}
    {"Lap": {"Distance": "300m", "Cumulative": "8700m", "Speed": "2.59 m/s", "Completed": "2020-06-04 16:51:22"}}
    {"Lap": {"Distance": "400m", "Cumulative": "9100m", "Speed": "4.40 m/s", "Completed": "2020-06-04 16:52:53"}}
    {"Lap": {"Distance": "300m", "Cumulative": "9400m", "Speed": "2.61 m/s", "Completed": "2020-06-04 16:54:48"}}
    {"Lap": {"Distance": "400m", "Cumulative": "9800m", "Speed": "4.44 m/s", "Completed": "2020-06-04 16:56:18"}}
    {"Lap": {"Distance": "300m", "Cumulative": "10100m", "Speed": "2.59 m/s", "Completed": "2020-06-04 16:58:14"}}
    {"Lap": {"Distance": "400m", "Cumulative": "10500m", "Speed": "4.44 m/s", "Completed": "2020-06-04 16:59:44"}}
    {"Lap": {"Distance": "300m", "Cumulative": "10800m", "Speed": "2.61 m/s", "Completed": "2020-06-04 17:01:39"}}
    {"Lap": {"Distance": "400m", "Cumulative": "11200m", "Speed": "4.40 m/s", "Completed": "2020-06-04 17:03:10"}}
    {"Lap": {"Distance": "300m", "Cumulative": "11500m", "Speed": "2.63 m/s", "Completed": "2020-06-04 17:05:04"}}
    {"Lap": {"Distance": "400m", "Cumulative": "11900m", "Speed": "4.55 m/s", "Completed": "2020-06-04 17:06:32"}}
    {"Lap": {"Distance": "300m", "Cumulative": "12200m", "Speed": "2.46 m/s", "Completed": "2020-06-04 17:08:34"}}
    {"Lap": {"Distance": "1000m", "Cumulative": "13200m", "Speed": "2.64 m/s", "Completed": "2020-06-04 17:14:53"}}



[export-tcx]: ./res/30km-progression-2019-09-25/export-tcx.png "Strava charts before running tcxmill"
[charts-before]: ./res/30km-progression-2019-09-25/charts-before.png "Strava charts before running tcxmill"
[charts-after]: ./res/30km-progression-2019-09-25/charts-after.png "Strava charts after running tcxmill"
[summary-before]: ./res/30km-progression-2019-09-25/summary-before.png "Strava summary before running tcxmill"
[summary-after]: ./res/30km-progression-2019-09-25/summary-after.png "Strava summary after running tcxmill"
[upload]: ./res/30km-progression-2019-09-25/upload.png "Strava upload"
[upload-file]: ./res/30km-progression-2019-09-25/upload-file.png "Strava file upload"

[10km-charts-before]: ./res/10km-2019-10-18/before.png "Strava charts before running tcxmill"
[10km-charts-after]: ./res/10km-2019-10-18/after.png "Strava charts before running tcxmill"

[8mi-charts-before]: ./res/8mi-progression-2019-12-13/before.png "Garmin charts after running tcxmill"
[8mi-charts-after]: ./res/8mi-progression-2019-12-13/after.png "Strava charts after running tcxmill"
