#!/usr/bin/python3.6

import settings as conf
import time, os
from datetime import datetime
import subprocess
from modules import Files, Logs
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

IPTABLES = "/usr/sbin/iptables"
GREP = "/usr/bin/grep"
DB_PATH = "sshdun.db"
TABLES_NAME = "sshdun"

engine = create_engine(conf.DB_URL, encoding="utf8", echo=True)
DBSession = sessionmaker(bind=engine)
session = DBSession()


def create_iptables():
    subprocess.call([IPTABLES, "-N", TABLES_NAME])
    subprocess.call([IPTABLES, "-I", "INPUT", "3", "-p", "tcp", "-m", "tcp", "--dport", "22", "-j", "sshdun"])


def insert_rule(hostname):
    subprocess.call([IPTABLES, "-F", TABLES_NAME])
    for row in load_logs(hostname, conf.LOGIN_FAIL_LONG_TIME,conf.LOGIN_FAIL_TIMES):
        subprocess.call([IPTABLES, "-A", TABLES_NAME, "-s", row[0], "-j", "DROP"])


# 查询最近时间内超过N次登录失败的ip
# 第一参数表示多少天之前,第二参数是失败次数
def load_logs(hostname, days, times):
    seconds = time.time() - days * 86400
    last_time = datetime.fromtimestamp(seconds)
    logs_rows = session.query(Logs.ip, func.count(Logs.ip)) \
        .filter(Logs.logintime > last_time) \
        .filter(Logs.hostname == hostname) \
        .group_by(Logs.ip) \
        .having(func.count(Logs.ip) > times)
    print("=" * 30, ">", logs_rows)
    return logs_rows


# 保存数据到Logs表中
# 参数是包含(logintime,hostname,username,ip)的列表
def save_logs_to_db(rows):
    session.add_all(rows)
    session.commit()


# 读取需要的日志内容
def read_log_file(row):
    logs_rows = []

    with open(row.filename, "r") as f:
        # 移动到最后的偏移位置
        f.seek(row.position, 0)
        # 读出所有行
        lines = f.readlines()
        year = time.localtime(time.time())[0]
        logintime, hostname, username, ip = None, row.hostname, None, None
        _, month, day, now, message, field1, field2, field3 = None, None, None, None, None, None, None, None
        for line in lines:
            # 每行日志以开头5个空格分隔成6段
            month, day, now, _, _, message = line.split(" ", 5)
            # 当第6段以"Failed password"开头时进行处理
            if message.startswith("Failed password"):
                logintime = datetime.strptime("%s %s %s %s" % (year, month, day, now), '%Y %b %d %H:%M:%S')
                # 对日志信息进行分隔并处理
                _, _, _, field1, _, field2, _, field3, *_ = message.split(" ")
                if field1 == "invalid":
                    username, ip = field2, field3
                else:
                    username, ip = field1, field2
                # 添加到结果列表
                logs_rows.append(Logs(logintime=logintime, hostname=hostname, username=username, ip=ip))
        # 读完日志了,把状态保存一下(position)
        row.position = f.tell()
        session.commit()

    return logs_rows


# 检查文件的inode是否一致,不一致时需要把position重置为0
def check_file(row):
    inode = os.stat(row.filename).st_ino
    if row.inode != inode:
        row.inode = inode
        row.position = 0
        session.commit()


# 初始化函数,进行建表和写入初始测试数据
def init():
    import modules
    modules.create_tables(engine)
    hostname = "127.0.0.1"
    filename = "/var/log/secure"
    inode = os.stat(filename).st_ino
    position = 0
    files_row = Files(
        hostname=hostname,
        inode=inode,
        filename=filename,
        position=position
    )
    try:
        session.add(files_row)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
    create_iptables()


if __name__ == "__main__":
    # init()
    all_files = session.query(Files)
    for row in all_files:
        check_file(row)
        logs = read_log_file(row)
        save_logs_to_db(logs)
        insert_rule(row.hostname)

    session.close()
