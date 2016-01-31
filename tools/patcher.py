#!/usr/bin/env python2

import jackpatch

client = jackpatch.Client("patcher")

nport = 0

for out_port in client.get_ports(flags=jackpatch.JackPortIsOutput, name_pattern="Bitwig Studio:SL *"):
	nport += 1
	namepattern = "sooperlooper:loop.*_" + str(nport)
	for in_port in client.get_ports(flags=jackpatch.JackPortIsInput, name_pattern=namepattern):
		client.connect(out_port, in_port)
