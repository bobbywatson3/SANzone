import argparse
import time
import os.path

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', 
	help="Input file containing list of hosts and HBA's in the format \"host_hba_name,hba_wwpn\"")
parser.add_argument('-o', '--output',
	default="MDS_Config-" + time.strftime("%H:%M-%m-%d-%Y") +".txt",
	help='Destination file for MDS configuration. Default is "MDS_Config-date.txt"')
parser.add_argument('-a', '--array', 
	default='VNX5800-A',
	help="Array to zone HBA's to. Default is VNX5800-A")
args = parser.parse_args()

if not args.input:
	print 'HBA input file must be specified using -i option.'
	quit(0)
elif os.path.isfile(args.input) == False:
	print 'Input file "%s" does not exist.' % args.input
	quit(0)
	
host_hbas_string = open(args.input).read()

# split host_hbas_string into list
host_hbas_list = host_hbas_string.split('\n')

# break out hosts and HBA's into dict
host_hbas = {}
for line in host_hbas_list:
	key, val = line.split(',')
	host_hbas[key] = str(val)

array = args.array
vsanA = 5
vsanB = 50
zonesetA = 'zoneset name PCloud-A vsan %s\n' % vsanA
zonesetB = 'zoneset name PCloud-B vsan %s\n' % vsanB

#Create fcalias
def create_fcalias(switch):
	output = '' # Create empty string that fcaliases will be appended too
	if switch == 'A':
		for host, hba in host_hbas.items():
			if host.endswith(switch): # Checks the end of each host for "A"
				output += "fcalias name %s vsan %d\nmember pwwn %s\n" % (host, vsanA, hba)
		return output
	elif switch == 'B':
		for host, hba in host_hbas.items():
			if host.endswith(switch): # Checks the end of each host for "B"
				output += "fcalias name %s vsan %d\nmember pwwn %s\n" % (host, vsanB, hba)
		return output
	else:
		print 'Valid switch parameter not provided to fcalias function.'

def create_zones(switch):
	output = '' # Create empty string that zones will be appended to
	global zonesetA # Use global variable, don't create local
	global zonesetB # Use global variable, don't create local
	if switch == 'A':
		for host in host_hbas.keys():
			if host.endswith(switch):
				zonesetA += "member %s_%s\n" % (host, array) # Add zone to zoneset
				output += "zone name %s_%s vsan %d\n" % (host, array, vsanA)
				output += "member fcalias %s\n" % host
				output += "member fcalias %s\n" % array
		return output
	elif switch == 'B':
		for host in host_hbas.keys():
			if host.endswith(switch):
				zonesetB += "member %s_%s\n" % (host, array) # Add zone to zoneset
				output += "zone name %s_%s vsan %d\n" % (host, array, vsanB)
				output += "member fcalias %s\n" % host
				output += "member fcalias %s\n" % array
		return output
print "Creating zone config"
print "Array:", array
print "Hosts:"
for host in host_hbas.keys():
	print host
# create fcaliases
fcaliases_for_A = create_fcalias('A')
fcaliases_for_B = create_fcalias('B')

# create zones and zonesets
zones_for_A = create_zones('A')
zones_for_B = create_zones('B')

config = ''
config += '-' * 20
config += 'MDS A Config'
config += '-' * 20 #, '\n'
config += '\n\n'
config += fcaliases_for_A
config += '\n'
config += zones_for_A
config += '\n'
config += zonesetA
config += '\n'
config += 'zoneset activate name PCloud-A vsan %d' % vsanA # '\n'
config += '\n\n'
config += '-' * 20
config += 'MDS B Config'
config += '-' * 20 #, '\n'
config += '\n\n'
config += fcaliases_for_B
config += '\n'
config += zones_for_B
config += '\n'
config += zonesetB
config += '\n'
config += 'zoneset activate name PCloud-B vsan %d' % vsanB

output = open(args.output, 'w')
output.write(config)
output.close

"""
# Print out the config commands
print '-' * 20
print 'MDS A Config'
print '-' * 20, '\n'
print fcaliases_for_A
print zones_for_A
print zonesetA
print 'zoneset activate name PCloud-A vsan %d' % vsanA, '\n'
print '-' * 20
print 'MDS B Config'
print '-' * 20, '\n'
print fcaliases_for_B
print zones_for_B
print zonesetB
print 'zoneset activate name PCloud-B vsan %d' % vsanB
"""