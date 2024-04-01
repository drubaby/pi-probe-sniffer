#!/usr/bin/sh
DATE=$(date +%m-%d-%Y)

echo "\e[91m Killing any running PiSniffer instances... \e[0m"
pkill -f PiSniffer
pkill -f airodump-ng

DEVICE=$(iw dev | awk '$1=="Interface"{print $2}')
if expr $DEVICE == 'wlan0mon'
then echo "\e[92m Wireless card already in monitor mode :) \n \e[0m"
else
echo "\e[91m No active monitor devices, setting up wlan0... \e[0m"
airmon-ng start wlan0
ifconfig wlan0 down
iwconfig wlan0 mode monitor
ifconfig wlan0 up
iwconfig wlan0
sleep 2
echo "iwconfig after all that: "
iwconfig
fi

echo "\e[91m Stopping active airmon devices... \e[0m"
airmon-ng check kill
sleep 2
DEVICE=$(iw dev | awk '$1=="Interface"{print $2}')
airmon-ng start $DEVICE

echo "\e[92m Starting airodump-ng on device: $DEVICE in background\e[0m"
airodump-ng -K 1 $DEVICE & >> /dev/null
sleep 2

echo "\e[92m Starting PiSniffer...'\e[0m"
touch "/usb/$DATE.csv"
echo "\e[92m PiSniffer.py -m $DEVICE -f /usb/${DATE} \e[0m"
python PiSniffer.py -m $DEVICE -f /usb/${DATE}
