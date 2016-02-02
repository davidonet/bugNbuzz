#!/bin/bash

# Script de lancement de la session "Bug'n'Buzz
# Exit codes :
# 10 : Erreur de lancement de Jack
# 11 : Erreur au lancement de Sooperlooper
# 12 : Erreur au lancement de Sooperlooper GUI
# 14 : Erreur au lancement de bitwig

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

jackdmp -R -d coreaudio -r 44100 -p 256 -d SaffireAudioEngine:0 -H >/tmp/log/jack.log 2>/tmp/log/jack_err.log &
sleep 5s
verify $! 10 jack


############## Sooperlooper #############

cd /Applications/Audio/SooperLooper.app/Contents/MacOS
./sooperlooper -L "$DIR/../sessions/Bug'n'buzz SL.slsess" >/tmp/log/sl.log 2>/tmp/log/sl_err.log &
verify $! 11 sooperlooper

./slgui >/tmp/log/slgui.log 2>/tmp/log/slgui_err.log &
verify $! 12 sooperlooperGUI



############# Bitwig studio ##############

cd "/Applications/Audio/Bitwig Studio.app/Contents/MacOS"
./BitwigStudio /Users/cieconcordance/Documents/Bitwig\ Studio/Projects/Bug\'n\'buzz/Bug\'n\'buzz.bwproject >/tmp/log/bitwig.log 2>/tmp/log/bitwig_err.log &
verify $! 14 bitwig

############# Connections jack #############
sleep 5s
cd $DIR
./patcher.py > /tmp/log/patcher.log
PATCH_PID=$!


############## Script OSC #############

cd $DIR
./osc_sooperlooper_test.py

############# Cloture de session ############
close
exit 0
