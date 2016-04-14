#!/usr/bin/env python2

from liblo import *
import sys

class MyServer(ServerThread):
	def __init__(self):
		ServerThread.__init__(self, 8000)

	@make_method(None, None)
	def fallback(self, path, args):
		print "received message '%s'" % path
		print args


try:
    server = MyServer()
except ServerError, err:
    print str(err)
    sys.exit()

server.start()
raw_input("press enter to quit...\n")