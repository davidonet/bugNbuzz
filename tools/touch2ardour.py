#!/usr/bin/env python2

def touch2ardour(path, args):
	splited = path.split("/")
	ard_path = "/" + splited[1] + "/" + splited[2] + "/" + splited[3]
	multiple = int(splited[4]) - 1
	if splited[3] == "gainabs":
		track = multiple * 8 + int(splited[5]) + multiple
		arg = float(args[0])
	if splited[3] == "mute":
		track = multiple * 8 + int(splited[6]) + multiple
		arg = int(args[0])
	
	return ard_path, track, arg


if __name__ == '__main__':
	touch2ardour()
