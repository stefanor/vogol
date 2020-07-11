#!/bin/bash

if [ -z "$2" ]; then
	echo "Usage: $0 roompath host"
	exit 2
fi

ROOM=$1
HOST=$2

t=`tempfile`
rm -f ${t} ${t}.jpg

ffmpeg=`which ffmpeg`
if ! [ $? -eq 0 ]; then
  echo No ffmpeg.
  exit 3
fi


function ff_fetch {
	# $0 host port file
	$ffmpeg -v quiet -y -i tcp://"$1":"$2"'?timeout=1000000' -map 0:v -s 320x180 -q 5 -an -vframes 1 "${t}".jpg && mv ${t}.jpg $3
}

mkdir -p ${ROOM}

while /bin/true; do
	ff_fetch $HOST 11000 ${ROOM}/room.jpg
	ff_fetch $HOST 13000 ${ROOM}/loop.jpg
	ff_fetch $HOST 13001 ${ROOM}/grabber.jpg
	ff_fetch $HOST 13002 ${ROOM}/recording.jpg
	ff_fetch $HOST 13003 ${ROOM}/jitsi.jpg
	sleep 1
done
