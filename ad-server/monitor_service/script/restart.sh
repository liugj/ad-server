#!bin/sh
pid_list=`ps ux | grep monitor_svr | awk '{print $2}'`
nohup python monitor_svr.py&
kill -15 $pid_list
