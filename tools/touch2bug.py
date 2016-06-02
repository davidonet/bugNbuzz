#!/usr/bin/env python2
#from subprocess import Popen, PIPE

from liblo import *
target = Address("localhost",10000)


def touch2bug(dst, path, args):
	""" TODO
	
	 dst: Str
	 path: Str
	 args: List(str)
	"""
	if dst == "ardour":
		splited = path.split("/")
#		print('###', splited)
		ard_path = "/" + splited[1] + "/" + splited[2] + "/" + splited[3]
#		print('### path ###', ard_path)

		
		
		if splited[3] == "gainabs":
			multiple = int(splited[4]) - 1
			if multiple == 317:
				track = 318
			else:
				track = multiple * 8 + int(splited[5]) + multiple
			arg = float(args[0]),

		
		elif splited[3] == "mute":
			multiple = int(splited[4]) - 1
			track = multiple * 8 + int(splited[6]) + multiple
			arg = int(args[0]), 
		
#	 	Adrour      REGISTER_CALLBACK (serv, "/ardour/routes/plugin/parameter", "iiif", route_plugin_parameter);
#					params are Route-ID Plugin-Number Parameter-Number Value */
#		Touchosc	/ardour/route/plugin/parameter/[tracknumer]/[Plugin-number]/[Parameter-number] [arg]
		elif splited[3] == "plugin":
#			print('### plugin ###')
			ard_path = ard_path + "/" + splited[4]
#			print('### newpath ###', ard_path)
			track = int(splited[7])+1
			plugin = int(splited[6])
			parm = int(splited[5])
			arg = plugin, parm, 0.9999*float(args[0])
#			print('###', ard_path, track, arg)
		
		return ard_path, track, arg,
		
	if dst =="carla":
		splited = path.split("/")
		carla_path = "/" + splited[1] + "/" + str(int(splited[4]) - 1) + "/" + splited[2]
		arg = int(args[0])
		return carla_path, arg
		
if __name__ == '__main__':
	touch2bug()
