#!/bin/bash
source /dev/shm/ssh-dun/venv/bin/activate
/dev/shm/ssh-dun/venv/bin/python3.6 /dev/shm/ssh-dun/start.py
echo $(date "+%F %T") > /dev/shm/ssh-dun/run.log

