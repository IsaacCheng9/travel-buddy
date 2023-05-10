#!/bin/sh
sudo yum install -y python3-pip
sudo yum install -y git
cd /home/ec2-user/
git clone https://github.com/KPiatigorskii/travel-buddy
sudo pip3 install -r /home/ec2-user/travel-buddy/requirements.txt
    