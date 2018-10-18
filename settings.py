#!/usr/bin/python3.6

IPTABLES = "/usr/sbin/iptables"
TABLES_NAME = "sshdun"

DB_PATH = "sshdun.db"
DB_URL = "sqlite:////dev/shm/ssh-dun/sshdun.db"

LOGIN_FAIL_LONG_TIME = 5
LOGIN_FAIL_TIMES = 10

if __name__ == '__main__':
    pass
