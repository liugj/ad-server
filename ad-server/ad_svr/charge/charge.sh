#!bin/sh

source ./func.sh
source ../conf/charge.conf
lock_flag=`cat lock_flag`
if [ ${lock_flag} -ne 0 ]
then
    WriteLog "one process is working on charging" "Warning" $LOG_PATH
    exit 0
fi

echo "1" > $lock_flag_file
time_now=`date +'%Y-%m-%d-%H:%M:%S'`
last_update_time=`cat timestamp`
python charge.py  $last_update_time $time_now $sql_file.${last_update_time}
if [ $? -ne 0 ]
then
    WriteLog "charge failed" "Warning" $LOG_PATH
    echo "0" > $lock_flag_file
    exit 1
fi

#${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT}  < $sql_file.${last_update_time}
if [ $? -ne 0 ]
then
    WriteLog "charge failed" "Warning" $LOG_PATH
    echo "0" > $lock_flag_file
    exit 1
fi

echo "0" > $lock_flag_file
echo $time_now > timestamp

