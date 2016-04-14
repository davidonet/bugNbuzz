#!/bin/bash

# Script de lancement de la session "Bug'n'Buzz
# Exit codes :
# 10 : Erreur de lancement de Jack
# 11 : Erreur au lancement de Sooperlooper
# 12 : Erreur au lancement de Sooperlooper GUI
# 13 : Erreur au lancement de Madjack
# 14 : Erreur au lancement de ardour

PIDS=()
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
mkdir /tmp/log

function close {
	for pid in "${PIDS[@]}"
	do
		:
		echo "Sus au pid $pid !"
		kill -15 $pid
	done
	killall -s 15 jackdmp
}

# verify : pid exit_code name
function verify {
	echo "Verification du pid $1"
	sleep 1
	if ps -eo pid | grep -q "$1$"
	then
		echo "$3 est lancé avec le PID $1"
		PIDS+=($1)
	else
		echo "erreur au lancement de $3"
		close
		exit $2
fi
}


echo "Lancement de la session BugNbuzz..."

############## Jack ##############

jackdmp -S -R -X coremidi -d coreaudio -r 48000 -p 256 -d SaffireAudioEngine:0 --hog >/tmp/log/jack.log 2>/tmp/log/jack_err.log &
sleep 10s
verify $! 10 jack


############## Sooperlooper #############

cd /Applications/Audio/SooperLooper.app/Contents/MacOS
./sooperlooper -L "$DIR/../sessions/Bug'n'buzz SL.slsess" >/tmp/log/sl.log 2>/tmp/log/sl_err.log &
verify $! 11 sooperlooper

./slgui >/tmp/log/slgui.log 2>/tmp/log/slgui_err.log &
verify $! 12 sooperlooperGUI

############# Carla #############
#export CARLA_OSC_UDP_PORT=17001
#/Applications/Audio/Carla.app/Contents/MacOS/Carla /Users/cieconcordance/BugNBuzz/bugNbuzz/sessions/bugnbuzz.carxp >/tmp/log/carla.log 2>/tmp/log/carla.log &
#verify $! 13 carla
#
# Useless with X42's onset trigger 

############ Lancement MadJack #############
exec /Users/cieconcordance/BugNBuzz/src/madjack/src/madjack -p 10000 -d /Users/cieconcordance/BugNBuzz/mp3/ > /dev/null 2> /tmp/log/madjack_err.log < /dev/null &
verify $! 13 madjack


############# Ardour 4 ##############

ARDOUR_BUNDLED=1 /Applications/Audio/Ardour4.app/Contents/MacOS/Ardour4 --no-splash /Users/cieconcordance/BugNBuzz/bugNbuzz/sessions/Ardour/BugNBuzz/BugNBuzz.ardour > /tmp/log/ardour.log 2>/tmp/log/ardour_err.log &
verify $! 14 Ardour


############# Connections jack #############
# Useless with ardour
# sleep 5s
# cd $DIR
# ./patcher.py > /tmp/log/patcher.log
# PATCH_PID=$!



############## Script OSC #############

cd $DIR
./osc_sooperlooper_test.py 2> /tmp/log/osc_sl.log

############# Cloture de session ############
close
exit 0
