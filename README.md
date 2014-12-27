SANzone

by Bobby Watson

-----------------
Requirements:

Python 2.7
Cisco UcsSdk
-----------------

SANzone is a script to pull HBA info from UCS Manager and generate SAN zone configuration for Cisco MDS switches.

An HBA input file can also be used if you want to generate MDS configs from HBA and WWPN addresses without connecting to a UCS Manager. The file should be in the format:

HBA-A,00:00:00:00:00:00:00:00
HBA-B,00:00:00:00:00:00:00:00

SSH implementation is planned for future revisions to push config directly to MDS switches, as well as the ability to connect to multiple UCS Managers.

Tweaking will definitely be required if you want to use this for your own environment.

-----------------

Usage

python SANzone.py -u [UCS IP] -l [UCS login] -p [UCS password] -s [Service Profile name]