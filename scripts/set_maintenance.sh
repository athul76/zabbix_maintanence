##!/bin/bash
#
# set permission to folder to allow mariadb to write files here
# chmod 777 /vision/awx-zabbix-maintenance-vi/logs

# run maintenance script
python3 /vision/awx-zabbix-maintenance-vi/scripts/setmaintenance.py 2> /vision/awx-zabbix-maintenance-vi/logs/maintenance_log.error

# push local repo back to git
cd /vision/awx-zabbix-maintenance-vi
git config --global user.name "AKG"
git config --global user.email athul.76@gmail.com
git add *
git commit -m "updated logs/log.txt (automated from deploy Server)"
git push origin master