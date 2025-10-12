# Announce that the range is closing.

** The application is designed to run on Raspberry Pi 3B or newer. **

Between Midnight and Noon the application synchronizes the time on the Raspberry Pi with an atomic time server.
It calculates the sunset for the day given the date from the OS and the longetude and latitude values provided in the ini file.
It calculates the amount of time between now and one hour, one minute before sunset then goes to sleep for that long an interval.


## Features

* Calculates the sunset for the current date and location.
* Uses a Shelly 1PM switch to turn the power on and off for an external amplifier.
* Plays recorded messages announcing impending range closure at:
  * 1 hour before sunset
  * 30 minutes before sunset
  * 15 minutes before sunset
  * 5 minutes before sunset
  * at sunset
* Can be started at any time and it will play the required messages.
* Loops indefinitely...start it once and let it run.
    * Note: The application spends almost all of the time performing a sleep operation so it is not using CPU or resources. 
* Logs information to Range_Announcer_Log.txt


## Requirements:

The application is intended to be run on Raspberry Pi 3B or newer with a wireless network interface and sound output jack.

The program requires inputs for:
1.  The longitude and latitude of the location.
2.  The IP address for the Shelly 1PM switch.
3.  The URLs to turn the Shelly switch on and off.
4.  A delay time to account for the delay between when the amp is powered on and when it is functioning.

These inputs are stored in the file rangeannouncer.json

## Installation
To install the application run the command:<br>
sudo pip install --upgrade range_announcer<br>
This will install the application launcher:  /usr/local/bin/RangeAnnouncer

## Usage

The application is intended to be run unattended on a Raspberry Pi and start automatically.<br>
To do that perform the following steps:
1. Open a terminal and type:  sudo nano /etc/rc.local
2. Add the following command before the '<b>exit 0</b>':<br>  sudo /usr/local/bin/RangeAnnouncer &<br>The trailing <b>&</b> must be in place to fork a new process...this program doesn't normally end.
3. In nano type Ctrl-x, then Y to save and exit.

This program will create a log in /srv/RangeAnnouncer logging informational, debug and error messages.

## Notes
On Raspberry Pi I had to edit /etc/pulse/daemon.conf to set<p>
 <b>alternate-sample-rate=48000<br>
 default-fragments=5<br>
 default-fragment-size-msec=12<br></b>

## History

Range Announcer is the first python application written and released by Michael J. Swenson.  Built using PyCharm 2022.3.1 Community edition.


## License

Range Announcer is licensed under the BSD-3-Clause license (see `LICENSE`).
