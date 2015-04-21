#SANzone

SANzone is a script to pull Service Profile HBA info from UCS Manager and generate SAN zone configuration for Cisco MDS switches. This will not generate a full config. Array zones, and zonesets should already be created. This script is used to add new hosts to an existing SAN infrastructure.

An HBA input file can also be used if you want to generate MDS configs from HBA and WWPN addresses without connecting to a UCS Manager. The file should be in the format:
```
ServerName-HBA-A,00:00:00:00:00:00:00:00
ServerName-HBA-B,00:00:00:00:00:00:00:00
```
SSH implementation is planned for future revisions to push config directly to MDS switches.

Tweaking will definitely be required if you want to use this for your own environment.

---
Requirements:

- Python 2.7
- [Cisco UCS SDK](https://communities.cisco.com/docs/DOC-37174)

---
Usage
```
python SANzone.py --ucs [UCS IP's separated by space] --login [UCS login] --serviceprofile [Service Profile search string wildcard, or individual names separated by space] --array [array name in MDS]
```
