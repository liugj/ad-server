#!bin/sh
function WriteLog
{
    message=$1
    log_type=$2
    log_path=$3
    time=`date "+%Y-%m-%d %H:%M:%S"`
    echo "[$time][$log_type]$message" >> $log_path
}
