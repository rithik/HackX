# Steps to Deploy onto AWS

## Create an EC2 Instance

- t2.micro
- Amazon Linux
- Security Group with HTTP, HTTPS and SSH

## Connect via SSH

ssh -i "keys/HackX.pem" ec2-user@ec2-3-83-1-229.compute-1.amazonaws.com

## Install python3 and git

`sudo yum install git python3`\

## EBS

sudo yum install postgresql-devel


`eb init -p python-3.6 hackx-main`
