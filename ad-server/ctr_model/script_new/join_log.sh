#!bin/sh
CHARGE_LOG_PATH="/opt/log/charge"
NGINX_LOG_PATH="/opt/log/nginx"
AD_SVR_LOG_PATH="/opt/userhome/superyc/ad_mobile/online/ad_server/log"

date=$1
python merge_log.py $CHARGE_LOG_PATH $NGINX_LOG_PATH $AD_SVR_LOG_PATH $date ../train_data


