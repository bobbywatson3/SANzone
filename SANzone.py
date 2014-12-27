import argparse
import time
import os.path
import re
from UcsSdk import *



parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', 
	help="Input file containing list of hosts and HBA's in the format \"host_hba_name,hba_wwpn\"")
parser.add_argument('-o', '--output',
	default="MDS_Config-" + time.strftime("%H:%M-%m-%d-%Y") +".txt",
	help='Destination file for MDS configuration. Default is "MDS_Config-date.txt"')
parser.add_argument('-a', '--array', required=True, help="Array to zone HBA's to.")
parser.add_argument('-u', '--ucs', help="Hostname or IP address of UCS Manager")
parser.add_argument('-l', '--login', help="Login for UCS Manager.")
parser.add_argument('-p', '--password', help="Password for UCS Manager.")
parser.add_argument('-s', '--serviceprofile', nargs='+', help="UCS Service Profile name. Multiple Service Profile names can be provided separated by a space.")
args = parser.parse_args()

print args.serviceprofile
array = args.array
vsanA = 5
vsanB = 50
zonesetA = 'zoneset name PCloud-A vsan %s\n' % vsanA
zonesetB = 'zoneset name PCloud-B vsan %s\n' % vsanB

def create_hba_dict_from_ucs(ucs, login, password):
	try:
		handle = UcsHandle()
		print "Connecting to UCS..."
		handle.Login(ucs, username=login, password=password)
		print "Connection Successful"
		output = {}
		print "Getting HBA information"
		getRsp = handle.GetManagedObject(None, None,{"Dn":"org-root/"}) # Last part is a key value pair to filter for a specific MO
		moList = handle.GetManagedObject(getRsp, "vnicFc")
		
		for serviceprofile in args.serviceprofile:
			for mo in moList:
				if str(mo.Addr) != 'derived' and serviceprofile in str(mo.Dn):
					print serviceprofile
					origDn = str(mo.Dn)
					origDn = origDn.replace('org-root/ls-','')
					origDn = origDn.replace('/fc','')
					output[origDn] = mo.Addr		
		handle.Logout()
		return output
		
	except Exception, err:
		print "Exception:", str(err)
		import traceback, sys
		print '-' * 60
		traceback.print_exc(file=sys.stdout)
		print '-' * 60

def create_hba_dict_from_file(file):	
	host_hbas_string = open(file).read() # open(args.input).read()
	# split host_hbas_string into list
	host_hbas_list = host_hbas_string.split('\n')

	# break out hosts and HBA's into dict
	output = {}
	for line in host_hbas_list:
		key, val = line.split(',')
		output[key] = str(val)
	return output

# Check that args are present/valid and then either create hba dict from file or UCS
if not (args.input or args.ucs):
	print 'HBA input file must be specified using -i option, or UCS must be specified using -u option'
	quit(0)
elif args.ucs and not (args.login and args.password and args.serviceprofile):
	print "Login, password, and service profile must be specified when using UCS as -l [login] -p [password] -s [service profile]"
	quit(0)
elif (args.input and not os.path.isfile(args.input)):
	print 'Input file "%s" does not exist.' % args.input
	quit(0)
elif args.input:
	host_hbas = create_hba_dict_from_file(args.input)
elif args.ucs and args.login and args.password:
	host_hbas = create_hba_dict_from_ucs(args.ucs, args.login, args.password)

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
print "Array:"
print array
print "Host HBA's:"
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