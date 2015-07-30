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
python charge_total.py  $last_update_time $time_now ../charge_log/$sql_file.${last_update_time}
if [ $? -ne 0 ]
then
    WriteLog "charge failed" "Warning" $LOG_PATH
    echo "0" > $lock_flag_file
    exit 1
fi

${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT}  < ../charge_log/$sql_file.${last_update_time}
if [ $? -ne 0 ]
then
    WriteLog "charge failed" "Warning" $LOG_PATH
    echo "0" > $lock_flag_file
    exit 1
fi

${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT} -e"use mis;select * from charge_record where charge_time>='${last_update_time}' and charge_time<='${time_now}'" > ../tmp/charge_record

python update_consumption.py ../tmp/charge_record ../charge_log/update_consumpton.sql.${last_update_time}  ${last_update_time}
if [ $? -ne 0 ]
then
    WriteLog "run update consumption python failed" "Warning" $LOG_PATH
    echo "0" > $lock_flag_file
    exit 1
fi

${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT}  < ../charge_log/update_consumpton.sql.${last_update_time}
if [ $? -ne 0 ]
then
    WriteLog "update consumption to db failed" "Warning" $LOG_PATH
    echo "0" > $lock_flag_file
    exit 1
fi


echo "0" > $lock_flag_file
exit 1
echo $time_now > timestamp

