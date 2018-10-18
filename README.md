# ssh-dun的使用说明

- 建议放在 /dev/shm/ 目录中运行
- 使用 python3.6 + sqlite3 环境

1.把脚本复制到服务器后,先初始化
```bash
# cd /dev/shm/
# python3.6
>>> import start
>>> start.init()
>>> exit()
```

2.添加到计划任务,每10分钟执行一次
```bash
# crontab -e
*/10 * * * * /usr/bin/python3.6 /dev/shm/start.py
```

3.查看防火墙规则
```bash
# iptables -vxnL | grep sshdun
```