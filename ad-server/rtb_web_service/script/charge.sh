#!bin/sh

source ./func.sh
source ../conf/charge.conf

time_now=`date +'%Y-%m-%d %H:%M:%S'`
prefix=`date +'%Y-%m-%d_%H:%M:%S'`
time_start=`cat ${TIME_STAMP}`
charge_log_name=${CHARGE_PATH}
grep "win_notice id=" ../log/rtb_new.log | awk -v time_now="$time_now" -v time_start="$time_start" '{time=$1" "$2;if(time>=time_start && time<time_now) {split($7,array,"=");print array[2]"\t"$0}}' > $charge_log_name

./decrypter ${charge_log_name} ../charge_log/charge_log_detail
${PYTHON} charge.py ../charge_log/charge_log_detail
if [ $? -ne 0 ]
then
    WriteLog "charge failed" "Warning" $LOG_PATH
    exit 1
fi
WriteLog "charge success" "Notice" $LOG_PATH
cat ../charge_log/charge_log_detail >> ../charge_log/charge_log_detail_history 
echo $time_now > ${TIME_STAMP}
