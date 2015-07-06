#!bin/sh
pid_list=`ps ux | grep rtb_svr_new | awk '{print $2}'`
nohup python rtb_svr_new.py&
kill -15 $pid_list
