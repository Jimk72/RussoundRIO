
# russound-polyglot

This is the Russound Poly for the [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with  [Polyglot V2](https://github.com/Einstein42/udi-polyglotv2)
(c) 2020 James Knutson and Robert Paauwe
MIT license.

This node server is intended to support the Russound MCA series whole house audio controllers using RIO API(http://www.russound.com/).

## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web
4. Once running you will have to update IP to your Russound IP and change number of controllers and zones if needed.
5. click Save changes, wait till the first node is added(about 1 minute) 
6. stop and then restart RussoundRIO nodeserver. This will connect to your russound amp to get actual zone names and create the nodes.
7. Wait till all nodes are added(number of total zones plus 1 for the controller) 
for 6 zones 1 controller should be 7 nodes
for 6 zones 2 controllers should be 13 nodes
for 8 zones 1 controller should be 9 nodes
for 8 zones 2 controllers should be 17 nodes
8. Once all nodes are added you can open your ISY admin council and under RussoundRIO you should find all your zones by name.

### Node Settings
The settings for this node are:

#### Short Poll
   * Not used
#### Long Poll
   * Not used

#### IP Address
   * The IP Address of the serial device server conected to the Russound controller. 
#### Port
   * 9621 Russound RIO Port
#### Number of Zones per controller
   * 6 or 8
#### Number of controllers
   * Russound amps connected 1 or 2

## Requirements

1. Polyglot V2 itself should be run on Raspian Stretch.
  To check your version, ```cat /etc/os-release``` and the first line should look like
  ```PRETTY_NAME="Raspbian GNU/Linux 9 (stretch)"```. It is possible to upgrade from Jessie to
  Stretch, but I would recommend just re-imaging the SD card.  Some helpful links:
   * https://www.raspberrypi.org/blog/raspbian-stretch/
   * https://linuxconfig.org/raspbian-gnu-linux-upgrade-from-jessie-to-raspbian-stretch-9
2. This has only been tested with ISY 5.0.14 so it is not guaranteed to work with any other version.

# Upgrading

Open the Polyglot web page, go to nodeserver store and click "Update" for "RussoundRIO".

For Polyglot 2.0.35, hit "Cancel" in the update window so the profile will not be updated and ISY rebooted.  The install procedure will properly handle this for you.  This will change with 2.0.36, for that version you will always say "No" and let the install procedure handle it for you as well.

Then restart the RussoundRIO nodeserver by selecting it in the Polyglot dashboard and select Control -> Restart, then watch the log to make sure everything goes well.

The Roku nodeserver keeps track of the version number and when a profile rebuild is necessary.  The profile/version.txt will contain the Russound profile_version which is updated in server.json when the profile should be rebuilt.

# Release Notes

- 1.0.0 02/11/2021
   - Prepped for release to public github

 
