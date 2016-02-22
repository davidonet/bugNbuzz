#!/usr/bin/env python2
# coding=utf8


from time import time, sleep
from liblo import *
import curses
import sys
import signal
import colorsys

# Useless with ardour
# try:
#    import patcher
# except ImportError:
#    print('patcher import failed')

try:
    import touch2bug
except ImportError:
    print('touch2bug import failed')


class MyServer(ServerThread):

    def __init__(self):
        ServerThread.__init__(self, 8000)

        self.states = [0.0] * 5
        self.buttons = [1] * 16
        self.led = [0] * 27
        self.ledState = [0] * 27
        self.loopnum = -1
        self.frame = 0

        try:
            self.sooperlooper = Address("localhost", 9951)
            self.ardour = Address("localhost", 3819)
            self.jacket = Address("192.168.1.30", 9000)  # in router config
            self.carla = Address("localhost", 17001)
        except liblo.AddressError as err:
            print(err)
            sys.exit()

        self.stdscr = curses.initscr()
        curses.cbreak()
        curses.noecho()
        self.stdscr.nodelay(True)
        self.stdscr.addstr(
            0, 0, "******************************* SooperLooper ****************************", curses.A_REVERSE)
        self.stdscr.addstr(4, 0, "All    ", curses.A_REVERSE)
        for l in range(4):
            self.stdscr.addstr(l + 5, 0, "loop " +
                               str(l + 1) + " ", curses.A_REVERSE)
        self.stdscr.addstr(
            10, 0, "q : quit / 1-4 : loop selection / a : all / r : RecPlayOver / u : UndoRedo / s : Stop and Clear", curses.A_DIM)

        self.ping()

    def quit(self):
        """ Trying to restore console """
        self.blank()
        self.refreshLed()
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        sys.exit(0)

########## OSC methods from SooperLooper ###########

    @make_method('/pong', 'ssi')
    def pong_callback(self, path, args):
        """ this message should be called throu osc by SooperLooper after a ping message"""
        h, v, l = args
        self.stdscr.addstr(1, 0, "Host : " + h + " version : " + v)
        self.stdscr.addstr(2, 0, str(l) + " loop(s) instancied")
        self.stdscr.refresh()

        if(l < 4):
            # Just in case
            send(self.sooperlooper, "/loop_add", l + 1, 1.0)
            send(self.sooperlooper, "/ping",
                 "osc.udp://localhost:8000/", "/pong")
        else:
            for l in range(4):
                send(self.sooperlooper, "/sl/" + str(l) + "/register_auto_update",
                     "state", 100, "osc.udp://localhost:8000/", "/update")
        self.blank()
        self.loopSelect(0)  # to be ready to receive command

#  Useless with ardour, tempo given by jack timebase
#        send(self.sooperlooper, "/register_auto_update",
#             "tempo", 100, "osc.udp://localhost:8000/", "/tempo")

#    @make_method('/tempo', 'isf')
#    def tempo(self, path, args):
#        """ when tempo changed in SooperLooper sync it to bitwig"""
#        send(self.bitwig, "/tempo/raw", args[2])
#        self.stdscr.addstr(2, 30, "BPM : " +
#                           "{0:.2f}".format(args[2]), curses.A_REVERSE)

    @make_method('/update', 'isf')
    def update(self, path, args):
        """ received a state change for a specific loop """
        l, c, s = args
        self.states[l] = s
        self.stdscr.addstr(l + 5, 10, self.getState(s))
        self.setColor(l, self.getColor(s))


########## OSC methods from OSC-X module ###########

    @make_method('/battery', 'f')
    def battery(self, path, args):
        """ battery voltage """
        self.battery = args  # TODO: handling low power

    @make_method('/inputs/digital', 'iiiiiiiiiiiiiiii')
    def buttons(self, path, args):
        """ Button handling
                An internal pull-up is active on each button :
                - press is 0
                - release is 1

                A basic debouncer is implemented by keeping the last buttons state
        """

        if (self.buttons != args):
            self.buttons = args
            self.stdscr.addstr(0, 0, "*", curses.A_REVERSE)
            self.loopRecPlay(self.buttons[15] == 0 or self.buttons[7])
            self.loopStop(self.buttons[14] == 0 or self.buttons[6])
            self.loopUndo(self.buttons[13] == 0)
            if self.buttons[12] == 0:
                self.loopSelect(-1)
            if self.buttons[8] == 0:
                self.loopSelect(3)
            if self.buttons[9] == 0:
                self.loopSelect(2)
            if self.buttons[10] == 0:
                self.loopSelect(1)
            if self.buttons[11] == 0:
                self.loopSelect(0)
        else:
                # Just to visualize the debouncing
            self.stdscr.addstr(0, 0, "#", curses.A_REVERSE)

    @make_method('/inputs/analogue', 'ffffffffffffffff')
    def potar(self, path, args):
        """ Receiving gain value from potentiometer

        Attributes:
            gain: contains 5 values : 0 is all then 1->4 channel

        TODO: 	send it back to right software.
                Don't forget channel 1 is index 0
        """
        gain = [0, 0, 0, 0, 0]
        for l in range(5):
            self.stdscr.addstr(l + 4, 30, str(int(100.0 * args[l])) + " % ")
            gain[l] = args[l]
            if l == 0:
                pass
#                send(self.bitwig, "/master/volume", int(gain[l]*100))
            else:
                send(self.sooperlooper, "/sl/" + str(l - 1) +
                     "/set", "wet", float(gain[l]))


########### wildcard ##########

    @make_method(None, None)
    def fallback(self, path, args):
        path_split = path.split("/")


########### OSC methods for TouchOSC to ardour and carla ############
        if path_split[1] == "ardour":
            ard_path, track, arg = touch2bug.touch2bug("ardour", path, args)
            send(self.ardour, ard_path, track, arg)
        if path_split[1] == "Carla":
            carla_path, arg = touch2bug.touch2bug("carla", path, args)
            send(self.carla, carla_path, arg)


#		All other
        else:
            print >> sys.stderr, "received message '" + \
                str(path) + "' " + str(args)

########## osc-x Send methods ###########

    def setColor(self, l, c):
        i = l + 5
        if -1 < c:
            c = colorsys.hsv_to_rgb(c, 1, .1)
            self.ledState[i * 3] = int(c[0] * 150)
            self.ledState[i * 3 + 1] = int(c[1] * 200)
            self.ledState[i * 3 + 2] = int(c[2] * 255)
        else:
            self.ledState[i * 3] = 0
            self.ledState[i * 3 + 1] = 0
            self.ledState[i * 3 + 2] = 0

    def setSelect(self, l, c):
        i = l + 5
        if -1 < c:
            c = colorsys.hsv_to_rgb(c, 1, .01)
            self.led[i * 3] = int(c[0] * 150)
            self.led[i * 3 + 1] = int(c[1] * 200)
            self.led[i * 3 + 2] = int(c[2] * 255)
        else:
            self.led[i * 3] = 0
            self.led[i * 3 + 1] = 0
            self.led[i * 3 + 2] = 0

    def blank(self):
        self.led = [0] * (9 * 3)

    def refreshLed(self):
        self.frame = (self.frame + 1) % 25
        if 6 < self.frame:
            send(self.jacket, "/outputs/rgb/16", self.ledState)
        else:
            send(self.jacket, "/outputs/rgb/16", self.led)

########## Sooperlooper Send methods ###########

    def ping(self):
        """ Ping and ask for status """
        send(self.sooperlooper, "/ping", "osc.udp://localhost:8000/", "/pong")

    def loopSelect(self, loopnum):
        """ Select a channel on SooperLooper

                Args:
                        loopnum: channel number 0 based index
                """
        self.setSelect(self.loopnum, -1)
        self.loopnum = loopnum

        # Console interface
        for l in range(5):
            self.stdscr.addstr(l + 4, 8, " ")
        self.stdscr.addstr(self.loopnum + 5, 8, "*", curses.A_BOLD)

        # Sooperlooper command
        send(self.sooperlooper, "/sl/set",
             "selected_loop_num", int(self.loopnum))
        send(self.sooperlooper, "/sl/-1/set", "dry", 0)
        send(self.sooperlooper, "/sl/" + str(self.loopnum) + "/set", "dry", 1)
        self.setSelect(loopnum, .5)

    def loopRecPlay(self, press):
        """ Rec Play Overdub action 

        Depends on SooperLooper channel state send the right action
        """
        if press:
            action = "/down"
        else:
            action = "/up"

        if self.states[self.loopnum] == 0.0 or self.states[self.loopnum] == 14.0:
            send(self.sooperlooper, "/sl/" +
                 str(self.loopnum) + action, "record")
        elif self.states[self.loopnum] == 2.0:
            send(self.sooperlooper, "/sl/" +
                 str(self.loopnum) + action, "record")
        else:
            send(self.sooperlooper, "/sl/" +
                 str(self.loopnum) + action, "overdub")

    def loopStop(self, press):
        """ Stop Action """
        if press:
            action = "/down"
            self.states[self.loopnum] = 0.0
        else:
            action = "/up"
        send(self.sooperlooper, "/sl/" + str(self.loopnum) + action, "pause")

    def loopUndo(self,press):
        """ Undo Action 

        TODO: need to implement redo
                """
        if press:
            action = "/down"
        else:
            action = "/up"
        send(self.sooperlooper, "/sl/" + str(self.loopnum) + "/hit", "undo")

# useles with ardour
#    def connect(self):
#        patcher.connect_sl()

############ Bitwig config #############
# Useless with ardour
#
#    def bitwig_monitor(self):
#
#        for bank in range(27):
#            send(self.bitwig, "/track/bank/-")
#
#        for bank in range(4):
#            for track in range(7):
#                track += 1
#                send(self.bitwig, "/track/" + str(track) + "/monitor", 1)
#
#            send(self.bitwig, "/track/bank/page/+")
#            bank += 1

############ Interactions #############

    def interact(self):
        """ wait fo keypress

        Used to debug when the jacket is not available
        """
        c = self.stdscr.getch()
        if c == ord('q'):
            self.quit()
        elif c == ord('a'):
            self.loopSelect(-1)
        elif c == ord('1'):
            self.loopSelect(0)
        elif c == ord('2'):
            self.loopSelect(1)
        elif c == ord('3'):
            self.loopSelect(2)
        elif c == ord('4'):
            self.loopSelect(3)
        elif c == ord('r'):
            self.loopRecPlay()
        elif c == ord('s'):
            self.loopStop()
        elif c == ord('u'):
            self.loopUndo()
# Useless with ardour
#        elif c == ord('c'):
#            self.connect()
#        elif c == ord('m'):
#            self.bitwig_monitor()
        self.refreshLed()
        sleep(0.04)


############# Utilities #############

    def getState(self, s):
        """ Simple method to get a human readable state """
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

    def getColor(self, s):
        if s == 2.0:
            return 0
        if s == 4.0:
            return .25
        if s == 5.0:
            return .75
        if s == 14.0:
            return .15
        return -1

try:
    server = MyServer()
except ServerError, err:
    print str(err)
    sys.exit()

server.start()

while True:
    server.interact()
    # sleep(0.1) # TODO: Check if needed

server.quit()
