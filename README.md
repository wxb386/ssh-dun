# ssh-dun的使用说明

- 建议放在 /dev/shm/ 目录中运行
- 使用 python3.6 + sqlite3 环境

1.把脚本复制到服务器后,先初始化
```bash
# cd /dev/shm/ssh-dun/
# virtualenv -p /usr/bin/python3.6 --no-site-packages venv
# source venv/bin/activate
# pip install sqlalchemy==1.2.12
# python3.6
>>> import start
>>> start.init()
>>> exit()
```

2.启动脚本
```bash
# echo '#!/bin/bash
source /dev/shm/ssh-dun/venv/bin/activate
/dev/shm/ssh-dun/venv/bin/python3.6 /dev/shm/ssh-dun/start.py
echo $(date "+%F %T") > /dev/shm/ssh-dun/run.log
' > sshdun.sh
# chmod 755 sshdun.sh
```

3.添加到计划任务,每10分钟执行一次
```bash
# crontab -e
*/10 * * * * /dev/shm/ssh-dun/sshdun.sh
```

4.查看防火墙规则
```bash
# iptables -vxnL | grep sshdun
```

5.手动运行脚本
```bash
# /dev/shm/ssh-dun/sshdun.sh
```