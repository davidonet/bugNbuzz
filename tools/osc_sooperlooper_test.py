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
		self.stdscr.nodelay(False)
		self.stdscr.addstr(0,0,"******************************* SooperLooper ****************************",curses.A_REVERSE)
		self.stdscr.addstr(4,0,"All    ",curses.A_REVERSE)
		for l in range(4):
			self.stdscr.addstr(l+5,0,"loop "+str(l+1)+ " ",curses.A_REVERSE)
		self.stdscr.addstr(10,0,"q : quit / 1-4 : loop selection / a : all / r : RecPlayOver / u : UndoRedo / s : Stop and Clear",curses.A_DIM)
		self.ping()
		self.states = [0.0,0.0,0.0,0.0,0.0]
		self.stdscr.addstr(13,0,"********************************** Jacket *******************************",curses.A_REVERSE)
		self.stdscr.addstr(14, 0, "Host :  osc.udp://xosc:9000")
		for l in range(5):
			self.stdscr.addstr(l+16,0,"button "+str(l+1)+ " ",curses.A_REVERSE)

		self.stdscr.addstr(22,0,"record / play ",curses.A_REVERSE)
		self.stdscr.addstr(23,0,"     undo     ",curses.A_REVERSE)
		self.stdscr.addstr(24,0,"     stop     ",curses.A_REVERSE)
			
		for l in range(5):
			self.stdscr.addstr(l+16,20,"led "+str(l+1)+ " ",curses.A_REVERSE)
		for l in range(5):
			self.stdscr.addstr(l+16,32,"analog "+str(l+1)+ " ",curses.A_REVERSE)

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
		self.states[l]=s
		self.stdscr.addstr(l+5,10,self.getState(s))

	@make_method('/battery','f')
	def battery(self, path, args):
		self.battery = args	

	@make_method('/inputs/digital','iiiiiiiiiiiiiiii')
	def buttons(self, path, args):
		buttons = args	
		if buttons[15]==0:
			self.loopRecPlay()
		if buttons[14]==0:
			self.loopStop()
		if buttons[13]==0:
			self.loopUndo()

	@make_method('/inputs/analogue','ffffffffffffffff')
	def potar(self, path, args):
		potar = args

	@make_method(None, None)
	def fallback(self, path, args):
		print "received message '%s'" % path
		print args

	def ping(self):
		send(self.target,"/ping","osc.udp://localhost:8000/","/pong")
	
	def loopSelect(self,loopnum):
		self.loopnum=loopnum
		send(self.target,"/sl/set","selected_loop_num",int(self.loopnum))
		send(self.target,"/sl/-1/set","dry",0)
		send(self.target,"/sl/"+str(self.loopnum)+"/set","dry",1)
		for l in range(5):
			self.stdscr.addstr(l+4,8," ")	
		self.stdscr.addstr(self.loopnum+5,8,"*",curses.A_BOLD)

	def loopRecPlay(self):
		if self.states[self.loopnum]==0.0 or self.states[self.loopnum]==14.0:
			send(self.target,"/sl/"+str(self.loopnum)+"/hit","record")
		elif self.states[self.loopnum]==2.0:
			send(self.target,"/sl/"+str(self.loopnum)+"/hit","record")
		else:
			send(self.target,"/sl/"+str(self.loopnum)+"/hit","overdub")	

	def loopStop(self):
		send(self.target,"/sl/"+str(self.loopnum)+"/hit","pause")
		self.states[self.loopnum]=0.0

	def loopUndo(self):
		send(self.target,"/sl/"+str(self.loopnum)+"/hit","undo")


	def interact(self):
		c = self.stdscr.getch()
		if c==ord('q'):
			self.quit()
		elif c==ord('a'):
			self.loopSelect(-1)
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
