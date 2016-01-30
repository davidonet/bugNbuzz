#!/bin/bash

# Script de lancement de la session "Bug'n'Buzz
# Exit codes :
# 10 : Erreur de lancement de Jack
# 11 : Erreur au lancement de Sooperlooper
# 12 : Erreur au lancement de Sooperlooper GUI
# 13 : Erreur au lancement du script OSC
# 14 : Erreur au lancement de bitwig


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


echo "Lancement de la session BugNbuzz..."

############## Jack ##############

jackdmp -d coreaudio >$DIR/log/jack.log 2>$DIR/log/jack_err.log &
JACK_PID=$!

if ps -eo pid | grep -q "^$JACK_PID$"
then
	echo "jack est lancé avec le PID $JACK_PID"
else
	echo "erreur au lancement de jack"
	exit 10
fi


#if ps -p $JACK_PID >/dev/null
#then
#	echo "jack est lancé avec le PID $JACK_PID"
#else
#	echo "erreur au lancement de jack"
#	exit 10
#fi

############## Sooperlooper #############

cd /Application/sooperlooper/content/MacOS/
./sooperlooper >$DIR/log/sl.log 2>$DIR/log/sl_err.log &
SL_PID=$!

if ps -eo pid | grep -q "^$SL_PID$"
then
	echo "SooperLooper est lancé avec le PID $SL_PID"
else
	echo "erreur au lancement de SooperLooper"
	exit 11
fi

./slgui >$DIR/log/slgui.log 2>$DIR/log/slgui_err.log &
SLGUI_PID=$!

if ps -eo pid | grep -q "^$SLGUI_PID$"
then
	echo "SooperLooper GUI est lancé avec le PID $SLGUI_PID"
else
	echo "erreur au lancement de SooperLooper GUI"
	exit 12
fi

############## Script OSC #############

cd $DIR/bugNbuzz/tools/
./osc_sooperlooper_test.py &
OSC_PID=$!

if ps -eo pid | grep -q "^$OSC_PID$"
then
	echo "Script OSC est lancé avec le PID $OSC_PID"
else
	echo "erreur au lancement du script OSC"
	exit 13
fi

############# Bitwig studio ##############

bitwig-studio "/user/adil/Bitwig Studio/Projects/Bug'n'Buzz.bwproject" &
BITWIG_PID=$!

if ps -eo pid | grep -q "^$BITWIG_PID$"
then
	echo "Bitwig est lancé avec le PID $BITWIG_PID"
else
	echo "erreur au lancement de Bitwig"
	exit 14
fi

############# Connections jack #############

cd $DIR
./patcher.py $
PATCH_PID=$!

#if ps -eo pid | grep -q "^$PATCH_PID$"
#then
#	echo "Bitwig est lancé avec le PID $BITWIG_PID"
#else
#	echo "erreur au lancement de Bitwig"
#	exit 14
#fi

############# Cloture de session ############

read -n1 -rsp 'Appuis espace pour quitter la session\n' touche

if [ "$touche" = ' ' ]
then
	echo "cloture de session"
	kill $PATCH_PID
	kill $BITWIG_PID
	kill $OSC_PID
	kill $SLGUI_PID
	kill $SL_PID
#	kill $JACK_PID
	exit 0

fi
