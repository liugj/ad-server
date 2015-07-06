#!bin/sh
pid_list=`ps ux | grep ad_svr | awk '{print $2}'`
echo "0" > ../data/init_done
nohup python ad_svr.py&
init_flag=`cat ../data/init_done`
while [ $init_flag -eq 0 ]
do
init_flag=`cat ../data/init_done`
sleep 1
done
kill -15 $pid_list


