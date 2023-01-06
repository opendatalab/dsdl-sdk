#!/usr/bin/env bash

if [ $1 == "cd" ]; then
     export  DS_NAME=xxx
else
     odl  $*
fi
