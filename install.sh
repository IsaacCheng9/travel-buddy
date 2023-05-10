#!/bin/sh
sudo yum install -y python3-pip
sudo yum install -y git
cd /home/ec2-user/
git clone https://github.com/KPiatigorskii/travel-buddy
cd travel-buddy/
python3 -m venv env
source env/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
pip3 install -e .
sudo chown -R ec2-user:ec2-user /home/ec2-user/travel-buddy/src/travel_buddy.egg-info
pip3 install -e .
    