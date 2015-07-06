#!bin/sh
source ./func.sh
source ../conf/dump_mysql_data.conf

#dump common data
table_list=(regions ages categories classification devices groups industries network operators os sizes age_idea ban_idea category_idea classify_idea device_idea  idea_industry idea_network idea_operator idea_os idea_region size_type)
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
where a.id='7' and a.status='0'"
${MYSQL} -h${HOST} -u${USER} -p${PASSWD} -P${PORT} -e"$sql"  > ../data/users.txt
if [ $? -ne 0 ]
then
    WriteLog "dump user file failed" "Warning" ${LOG_FILE}
    exit 1   
fi

#dump plans
sql="set names utf8;use mis;select id as plan_id,name,user_id,budget from plans where status='0'"
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
sql="set names utf8;use mis;select * from ideas where status='0'"
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


