#!/bin/bash
# to run the flask website

if [ "$1" == "-ext" ]
then
    # for external connections
    screen -S urban -dm flask --app flaskr --debug run --host=0.0.0.0

else
    # for local only connections
    flask --app flaskr --debug run
fi
