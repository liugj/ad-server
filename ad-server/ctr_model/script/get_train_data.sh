#!bin/sh
date=$1

python join_log.py /opt/userhome/superyc/ad_mobile/online/monitor_service/log/ad_show.log.${date} /opt/userhome/superyc/ad_mobile/online/monitor_service/log/ad_click.log.${date} /opt/userhome/superyc/ad_mobile/online/ad_server_new/log/ad_svr_python.log.${date} /opt/userhome/superyc/ad_mobile/online/rtb_web_service/charge_log/charge_log_detail_history.${date}  ../log/join_log.${date}
