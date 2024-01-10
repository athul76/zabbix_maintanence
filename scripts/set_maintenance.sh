##!/bin/bash
#
# set permission to folder to allow mariadb to write files here
# chmod 777 /repo/awx-zabbix-maintenance/logs

# run maintenance script
python3 /repo/awx-zabbix-maintenance/scripts/setmaintenance.py 2> /repo/awx-zabbix-maintenance/logs/maintenance_log.error

# push local repo back to git
cd /repo/awx-zabbix-maintenance
git config --global user.name "AKG"
git config --global user.email athul.76@gmail.com
git add *
git commit -m "updated logs/log.txt (automated from deploy Server)"
git push origin master