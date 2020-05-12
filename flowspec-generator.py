#!/usr/bin/env python3

# Import stuff.
from __future__ import print_function
from sys import stdout
from time import sleep
from random import getrandbits
from ipaddress import IPv4Network, IPv4Address, IPv6Network, IPv6Address
import random

# Set this to the number of flowspec rules you want to generate/announce.
# The script will create this number of rules for both IPv4 and IPv6. (So double this number will be generated total.)
count = 10

# Function to generate a random IPv4 address within the given prefix.
def genipv4():
	subnet = IPv4Network("192.168.0.0/16") 
	bits = getrandbits(subnet.max_prefixlen - subnet.prefixlen)
	addr = IPv4Address(subnet.network_address + bits)
	addr_str = str(addr)
	return addr_str

def genipv6():
	subnet6 = IPv6Network("2001:DB8:beef::/64")
	bits6 = getrandbits(subnet6.max_prefixlen - subnet6.prefixlen)
	addr6 = IPv6Address(subnet6.network_address + bits6)
	addr_str6 = str(addr6)
	return addr_str6


# Function to generate a list of flowspec rules based on random data.
def genflows():
	flow_types = []
	flow_types.append(
		"announce flow route { match { source " + genipv4() + "/32; destination 192.168.255.10/32; destination-port =" + str(random.randint(1024, 65530)) + "; protocol tcp; } then { rate-limit " + str(random.randint(9600, 51200)) + "; } }")
	flow_types.append("announce flow route { match { source " + genipv4() + "/32; } then { discard; } }")
	flow_types.append("announce flow route { match { source " + genipv4() + "/32; } then { redirect 666:666; } }")
	flow_types.append("announce flow route { match { destination " + genipv4() + "/32; } then { discard; } }")
	flow_types.append("announce flow route { match { source " + genipv4() + "/32; tcp-flags [ urgent rst ]; } then { redirect 666:666; } }")
	flow_types.append("announce flow route { match { source " + genipv4() + "/32; } then { redirect 192.168.255.254:666; } }")
	flow_types.append("announce flow route { match { destination " + genipv4() + "/32; fragment not-a-fragment;} then { discard; } }")
	flow_types.append("announce flow route { match { source " + genipv4() + "/32; packet-length >200&<500; } then { discard; } }")
	flow_types.append("announce flow route { match { destination " + genipv4() + "/32; icmp-type [ unreachable echo-request echo-reply ];} then { discard; } }")
	flow_types.append("announce flow route { match { source " + genipv4() + "/32; } then { rate-limit " + str(random.randint(9600, 51200)) + "; } }")
	return flow_types

def genflows6():
	flow_types6 = []
	flow_types6.append(
		"announce flow route { match { source " + genipv6() + "/128; destination 2001:DB8:beef:cafe::1/128; destination-port =" + str(random.randint(1024, 65530)) + "; protocol tcp; } then { rate-limit " + str(random.randint(9600, 51200)) + "; } }")
	flow_types6.append("announce flow route { match { source " + genipv6() + "/128; } then { discard; } }")
	flow_types6.append("announce flow route { match { source " + genipv6() + "/128; } then { redirect 666:666; } }")
	flow_types6.append("announce flow route { match { destination " + genipv6() + "/128; } then { discard; } }")
	flow_types6.append("announce flow route { match { source " + genipv6() + "/128; tcp-flags [ urgent rst ]; } then { redirect 666:666; } }")
	flow_types6.append("announce flow route { match { destination " + genipv6() + "/128; fragment not-a-fragment;} then { discard; } }")
	flow_types6.append("announce flow route { match { source " + genipv6() + "/128; packet-length >200&<500; } then { discard; } }")
	flow_types6.append("announce flow route { match { destination " + genipv6() + "/128; icmp-type [ unreachable echo-request echo-reply ];} then { discard; } }")
	flow_types6.append("announce flow route { match { source " + genipv6() + "/128; } then { rate-limit " + str(random.randint(9600, 51200)) + "; } }")
	return flow_types6

# Initialize empty flow list.
messages = []

# Append a randomly chosen item from the flow_types list to the messages list to be sent to exabgp.
# This is probably overly complicated, but it does what I want it to do.
for x in range(0, count):
	flows = genflows()
	messages.append(random.choice(flows))

for x in range(0, count):
	flows6 = genflows6()
	messages.append(random.choice(flows6))

# Let the BGP session come up before we bombard it with BGP updates.
sleep(5)

# Iterate through messages list.
for message in messages:
	stdout.write(message + '\n')
	stdout.flush()
	#print(message)
	sleep(0.001) # If you're running more than a few dozen flows, you'll want this set pretty low.

#Loop endlessly to allow ExaBGP to continue running
while True:
    sleep(1)
