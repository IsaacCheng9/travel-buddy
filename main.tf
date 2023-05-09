variable vpc_cidr_block {}
variable subnet_cidr_block {}
variable avail_zone {}
variable env_prefix {}
variable ami_key {}

provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "travel-buddy-instance" {
  ami = var.ami_key 
  instance_type = "t2.micro"
  vpc_security_group_ids = [aws_security_group.travel-buddy-sgroup.id]
  subnet_id = aws_subnet.travel-buddy-subnet.id
  provisioner "remote-exec" {
    inline = [
      "sudo mkdir /home/ec2-user/travel-buddy"
    ]
  }

  provisioner "file" {
      source      = "install.sh"      
      destination = "/home/ec2-user/travel-buddy/install.sh" 
  }

  provisioner "remote-exec" {
    inline = [
      "./install.sh"
    ]
  }
}

resource "aws_vpc" "travel-buddy-vpc" {
    cidr_block = var.vpc_cidr_block
    tags = {
        Name: "${var.env_prefix}-travel-buddy-vpc"
    }
}

resource "aws_internet_gateway" "travel-buddy-gateway" {
  vpc_id = aws_vpc.travel-buddy-vpc.id

  tags = {
    Name = "main"
  }
}

resource "aws_subnet" "travel-buddy-subnet" {
    vpc_id = aws_vpc.travel-buddy-vpc.id
    cidr_block = var.subnet_cidr_block
    availability_zone = var.avail_zone
    tags = {
        Name: "${var.env_prefix}-travel-buddy-subnet"
    }
}

resource "aws_internet_gateway" "travel-buddy-igw" {
  vpc_id = aws_vpc.travel-buddy-vpc.id
  tags = {
    Name: "${var.env_prefix}-igw"
  }
}

resource "aws_route_table" "travel-buddy-route-table" {
  vpc_id = aws_vpc.travel-buddy-vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.travel-buddy-igw.id
  }
  tags = {
    Name: "${var.env_prefix}-rtb"
  }
}

resource "aws_security_group" "travel-buddy-sgroup" {
    vpc_id = aws_vpc.travel-buddy-vpc.id
    tags = {
        Name: "${var.env_prefix}-travel-buddy-sg"
    }
}

resource "aws_vpc_security_group_egress_rule" "egress-rule" {
    security_group_id = aws_security_group.travel-buddy-sgroup.id
    from_port = 0
    to_port = 0
    ip_protocol = "tcp"
    cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "http-rule" {
    security_group_id = aws_security_group.travel-buddy-sgroup.id
    from_port = 80
    to_port = 80
    ip_protocol = "tcp"
    cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "ssh-rule" {
    security_group_id = aws_security_group.travel-buddy-sgroup.id
    from_port = 22
    to_port = 22
    ip_protocol = "tcp"
    cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_key_pair" "deployer-key" {
    key_name   = "deployer-key"
    public_key = file("~/.ssh/id_rsa.pub")
}
# Konstantin Piatigorskii