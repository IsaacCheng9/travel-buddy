#!/bin/sh
sudo yum install -y git
git clone https://github.com/KPiatigorskii/travel-buddy.git /home/ec2-user/travel-buddy
sudo yum install -y python3-pip
sudo pip3 install -r /home/ec2-user/travel-buddy/requirements.txt
    