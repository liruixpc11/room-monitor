#!/usr/bin/env bash

mkdir -p dist/ 2>/dev/null >/dev/null
cd $(dirname "$0")
cd ..

rm -f dist/room-monitor.tar.gz 2>/dev/null >/dev/null
tar zcvf dist/room-monitor.tar.gz roomonitor/*.py static/index.html static/main.bin.js

ssh root@115.28.100.161 "service uwsgi stop; rm -rf /opt/room-monitor; mkdir /opt/room-monitor/"
scp dist/room-monitor.tar.gz root@115.28.100.161:/opt/room-monitor/
ssh root@115.28.100.161 "cd /opt/room-monitor/; tar xvf room-monitor.tar.gz; rm room-monitor.tar.gz; mkdir /var/room-monitor/; service uwsgi start"

