#!/bin/sh

#sleep 10s

xterm -e ~/bugNbuzz/tools/madjack -p 10000 -d ~/bugNbuzz/mp3 -l "ardour:mp3/audio_in 1" -r "ardour:mp3/audio_in 2"
