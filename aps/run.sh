#!/bin/bash

function usage {
  echo "usage: $0 <config_file> [extra args]"
}

if [ $# -lt 1 ]; then
  echo "not enough arguments"
  usage
  exit -1
fi

config_file=$1
config=$(cat $config_file)
shift
extra_args=$@

python aps.py $config $extra_args
