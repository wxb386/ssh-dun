#!/usr/bin/python3.6

import sqlite3
import time, datetime

DB_PATH = "sshdun.db"
TABLES_NAME = "sshdun"
conn = sqlite3.connect(DB_PATH)


# 保存数据到Firewall表中
# 参数是包含(logintime,hostname,tablesname,ip)的列表
def save_firewall(rows):
    if len(rows) == 0: return False
    sql = "insert into sshdun_firewall values(?,?,?,?);"
    conn.executemany(sql, rows)
    conn.commit()
    return True


# 保存数据到Logs表中
# 参数是包含(logintime,hostname,username,ip)的列表
def save_logs(rows):
    if len(rows) == 0: return False
    sql = "insert into sshdun_logs values(?,?,?,?);"
    conn.executemany(sql, rows)
    conn.commit()
    return True


# 查询最近时间内超过N次登录失败的ip
# 参数是"%Y-%m-%d %H:%M:%S"格式的时间字符串,第二参数是失败次数
def load_logs(last_time, count=20):
    time_array = time.strptime(last_time, "%Y-%m-%d %H:%M:%S")
    seconds = int(time.mktime(time_array))
    sql = "select ip,count(ip) as c from sshdun_logs where logintime>? group by ip having c>?;"
    return conn.execute(sql, (seconds, count))


# 保存数据到Files表中
# 参数是包含(hostname,filename,position)的列表
def save_files(rows):
    if len(rows) == 0: return False
    sql = "insert into sshdun_files values(?,?,?);"
    print(rows)
    conn.executemany(sql, rows)
    conn.commit()
    return True


# 更新数据到Files表,参数是(hostname,filename,position)
def update_files(row):
    sql = "update sshdun_files set position=? where hostname=? and filename=?;"
    print(row)
    a, b, c = row
    conn.execute(sql, (c, a, b))
    conn.commit()
    return True


# 读取Files表的所有行
def load_files():
    sql = "select * from sshdun_files;"
    c = conn.execute(sql)
    return c


# 读取需要的日志内容
def read_log_file(hostname, filename, position):
    logs = []
    with open(filename, "r") as f:
        f.seek(position, 0)
        lines = f.readlines()
        for line in lines:
            month, day, now, _, _, message = line.split(" ", 5)

            if message.startswith("Failed password"):
                time_array = time.strptime("2018 %s %s %s" % (month, day, now), '%Y %b %d %H:%M:%S')
                logintime = int(time.mktime(time_array))
                _, _, _, field1, _, field2, _, field3, *_ = message.split(" ")

                if field1 == "invalid":
                    username, ip = field2, field3
                else:
                    username, ip = field1, field2

                logs.append((logintime, hostname, username, ip))
        position = f.tell()
    # 读完日志了,把状态保存一下(position)
    update_files((hostname, filename, position))
    return logs


# 初始化时建表
def create_table():
    files_create_tables_sql = """create table if not exists sshdun_files (
    hostname char(32) not null,
    filename char(255) not null,
    position int not null,
    primary key(hostname,filename)
);"""
    logs_create_tables_sql = """create table if not exists sshdun_logs (
    logintime int not null,
    hostname char(32) not null,
    username char(32) not null,
    ip char(15) not null
);"""
    firewall_create_tables_sql = """create table if not exists sshdun_firewall (
    logintime int not null,
    hostname char(32) not null,
    tablesname char(10) not null,
    ip char(15) not null,
    primary key(logintime,hostname)
);"""
    conn.execute(files_create_tables_sql)
    conn.execute(logs_create_tables_sql)
    conn.execute(firewall_create_tables_sql)
    conn.commit()


files_rows = ["localhost", "/var/log/secure", 0]
if __name__ == "__main__":
    create_table()
    # save_files((files_rows,))
    all_files = load_files()
    for hostname, filename, position in all_files:
        logs = read_log_file(hostname, filename, position)
        save_logs(logs)
    for i in load_logs("2018-10-01 0:0:0"):
        print(i)
    conn.close()
