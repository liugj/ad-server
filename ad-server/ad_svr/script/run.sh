#!bin/sh
source ./func.sh
source ../conf/dump_mysql_data.conf

#dump common data
table_list=(regions ages categories classification devices groups industries network operators os sizes age_idea ban_idea category_idea classify_idea device_idea  idea_industry idea_network idea_operator idea_os idea_region size_type click_actions)
numvalues=${#table_list[@]}
for (( i=0; i < numvalues; i++ ));  
do
name=${table_list[i]}
sql="set names utf8;use mis;select * from ${name}"
${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT} -e"$sql"  > ../data/${name}.txt
if [ $? -ne 0 ]
then
    WriteLog "dump ${name} file failed" "Warning" ${LOG_FILE}
    exit 1   
fi
done

#dump user info
sql="set names utf8;use mis;select a.id as user_id,a.status,b.total,b.consumption_total
from users a 
left join
basics b
on a.id=b.id
where a.status='0'"
${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT} -e"$sql"  > ../data/users.txt
if [ $? -ne 0 ]
then
    WriteLog "dump user file failed" "Warning" ${LOG_FILE}
    exit 1   
fi

#dump plans
sql="set names utf8;use mis;select id as plan_id,name,user_id,budget,start_time,end_time from plans where status='0'"
${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT} -e"$sql"  > ../data/plans.txt
if [ $? -ne 0 ]
then
    WriteLog "dump user file failed" "Warning" ${LOG_FILE}
    exit 1   
fi

#dump consumption
today=`date +%Y-%m-%d`
sql="set names utf8;use mis;select id,user_id,idea_id,plan_id,smooth,price from consumptions where date='${today}'"
${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT} -e"$sql"  > ../data/consumption.txt
if [ $? -ne 0 ]
then
    WriteLog "dump consumption file failed" "Warning" ${LOG_FILE}
    exit 1   
fi

#dump ideas
sql="set names utf8;use mis;select * from ideas"
${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT} -e"$sql"  > ../data/ideas.txt
if [ $? -ne 0 ]
then
    WriteLog "dump ideas file failed" "Warning" ${LOG_FILE}
    exit 1   
fi

#dump ideas
sql="set names utf8;use mis;select a.*,b.size_id from 
types a 
left join 
size_type b
on 
a.id=b.type_id"
${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT} -e"$sql"  > ../data/type_size_join.txt
if [ $? -ne 0 ]
then
    WriteLog "dump ideas file failed" "Warning" ${LOG_FILE}
    exit 1   
fi

#update smooth charge 
python update_smooth_charge.py ../data/ideas.txt ../data/update_smooth_charge.sql
${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT}   < ../data/update_smooth_charge.sql
if [ $? -ne 0 ]
then
    WriteLog "update smooth failed" "Warning" ${LOG_FILE}
    exit 1   
fi

#create index
python create_index.py
if [ $? -ne 0 ]
then
    WriteLog "create index failed" "Warning" ${LOG_FILE}
    exit 1   
fi


#restart
pid_list=`ps ux | grep "ad_svr.py" | awk '{print $2}'`
echo "0" > ../data/init_done
nohup python ad_svr.py&
init_flag=`cat ../data/init_done`
while [ $init_flag -eq 0 ]
do
init_flag=`cat ../data/init_done`
sleep 1
done
kill -15 $pid_list

