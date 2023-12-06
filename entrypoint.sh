#!/bin/bash

if [ ! -f /mnt/config_xhs.ini ]; then
  echo 'Error: /mnt/config_xhs.ini file not found. Please mount the /mnt/config_xhs.ini file and try again.'
  exit 1
fi

cp -f /mnt/config_xhs.ini /app/config_xhs.ini
python -u main.py
