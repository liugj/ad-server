#!bin/sh
pid_list=`ps ux | grep cpa_monitor | awk '{print $2}'`
nohup python cpa_monitor.py&
kill -15 $pid_list
