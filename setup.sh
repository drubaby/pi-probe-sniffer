#!/usr/bin/sh

# Only run this script once on startup

if [ $(id -u) != "0" ]; then
echo "You must be the superuser to run this script" >&2
exit 1
fi
apt-get update

# install dependencies: Aircrack, git, python3-pip
apt-get -y install aircrack-ng git python3-pip


# copy our systemd service to pi. This ensures that the script will start on every reboot
cp ./system/probe-sniffer.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable probe-sniffer.service
systemctl start probe-sniffer.service

# Add cron job to crontab. This will restart the systemd service and ensure that a new csv file is created each day to log probes

echo '# restart pi sniffer at midnight every day to generate new daily csv' >> /etc/crontab
echo '0 0 * * * sudo /usr/bin/systemctl try-restart probe-sniffer.service >> /usb/cron_log.log 2>&1' >> /etc/crontab
echo # run daily_csv script to convert yeserdays csv into a clean version and upload to supabase
echo 0 1 * * * sudo /usr/bin/python ~/wuds/scripts/daily_csv.py >> /usb/cron_log.log 2>&1
