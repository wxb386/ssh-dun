#!/usr/bin/python3.6

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# 文件表
class Files(Base):
    __tablename__ = "sshdun_files"

    hostname = Column(String(32), primary_key=True)
    inode = Column(Integer, primary_key=True)
    filename = Column(String(255))
    position = Column(Integer)

    def __str__(self):
        return "[%s:%s]文件名:%s,位置:%s" % (self.hostname, self.inode, self.filename, self.position)


# 日志信息表
class Logs(Base):
    __tablename__ = "sshdun_logs"

    id = Column(Integer, primary_key=True)
    hostname = Column(String(32))
    logintime = Column(DateTime)
    username = Column(String(32))
    ip = Column(String(15))

    def __str__(self):
        return "[%s,%s,%s,%s,%s]" % (self.id, self.hostname, self.logintime, self.username, self.ip)


def create_tables(engine):
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    pass