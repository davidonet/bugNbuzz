#!/usr/bin/env python2

from time import time, sleep
from liblo import *
import curses
import sys
import signal

class MyServer(ServerThread):
	def __init__(self):
		ServerThread.__init__(self, 8000)
		print "Ready to receive (your order)"
		try:	
			self.target = Address("localhost",9951)
		except liblo.AddressError as err:
			print(err)
			sys.exit()
		self.stdscr = curses.initscr()
		curses.cbreak()
		curses.noecho()
		self.stdscr.nodelay(True)
		self.stdscr.addstr(0,0,"******** SooperLooper tester ********",curses.A_REVERSE)
		for l in range(4):
			self.stdscr.addstr(l+5,0,"loop "+str(l+1)+ " ",curses.A_REVERSE)
		self.stdscr.addstr(11,0,"q : quit / 1-4 : loop selection / r : RecPlayOver / u : UndoRedo / s : Stop",curses.A_DIM)
		self.ping()


	def quit(self):
		curses.nocbreak()
		curses.echo()
		curses.endwin()
		print("bye bye !!")
		sys.exit(0)

	@make_method('/pong', 'ssi')
	def pong_callback(self, path, args):
		h, v, l = args
		self.stdscr.addstr(1, 0, "Host : "+ h +" version : "+ v)
		self.stdscr.addstr(2, 0, str(l) +" loop(s) instancied")
		self.stdscr.refresh()
		if(l<4):
			send(self.target,"/loop_add",l+1,1.0)
			send(self.target,"/ping","osc.udp://localhost:8000/","/pong")
		else:
			for l in range(4):
				send(self.target,"/sl/"+str(l)+"/register_auto_update","state",100,"osc.udp://localhost:8000/","/update")

	def getState(self,s):
		if s == 0.0:
			return "Off         "
		if s == 1.0:
			return "WaitStart   "
		if s == 2.0:
			return "Recording   "
		if s == 3.0:
			return "WaitStop    "
		if s == 4.0:
			return "Playing     "
		if s == 5.0:
			return "Overdubbing "
		if s == 6.0:
			return "Multiplying "
		if s == 7.0:
			return "Inserting   "
		if s == 8.0:
			return "Replacing   "
		if s == 9.0:
			return "Delay       "
		if s == 10.0:
			return "Muted       "
		if s == 11.0:
			return "Scratching  "
		if s == 12.0:
			return "OneShot     "
		if s == 13.0:
			return "Substitute  "
		if s == 14.0:
			return "Paused      "

	@make_method('/update', 'isf')
	def update(self, path, args):
		l, c, s = args
		self.stdscr.addstr(l+5,10,self.getState(s))

	@make_method(None, None)
	def fallback(self, path, args):
		print "received message '%s'" % path
		print args

	def ping(self):
		send(self.target,"/ping","osc.udp://localhost:8000/","/pong")
	
	def loopSelect(self,loopnum):
		self.loopnum=loopnum
		for l in range(4):
			self.stdscr.addstr(l+5,8," ")	
		self.stdscr.addstr(self.loopnum+5,8,"*",curses.A_BOLD)

	def interact(self):
		c = self.stdscr.getch()
		if c==ord('q'):
			self.quit()
		elif c==ord('1'):
			self.loopSelect(0)
		elif c==ord('2'):
			self.loopSelect(1)
		elif c==ord('3'):
			self.loopSelect(2)
		elif c==ord('4'):
			self.loopSelect(3)
		elif c==ord('r'):
			self.loopRecPlay()
		elif c==ord('s'):
			self.loopStop()
		elif c==ord('u'):
			self.loopUndo()



try:
    server = MyServer()
except ServerError, err:
    print str(err)
    sys.exit()

server.start()

while True:
	server.interact()

server.quit()