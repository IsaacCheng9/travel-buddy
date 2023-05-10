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
  associate_public_ip_address = true
  key_name =  "${aws_key_pair.deployer-key.key_name}"

  provisioner "remote-exec" { 
    connection {
      host = self.public_ip
      type     = "ssh"
      user     = "ec2-user"
      private_key = "${file("~/.ssh/id_rsa")}"
    }
    inline = [
      "touch /home/ec2-user/install.sh"
    ]
  }

  provisioner "file" {
    connection {
      host = self.public_ip
      type     = "ssh"
      user     = "ec2-user"
      private_key = "${file("~/.ssh/id_rsa")}"
    }
    source      = "install.sh"      
    destination = "/home/ec2-user/install.sh" 
  }

  provisioner "remote-exec" { 
    connection {
      host = self.public_ip
      type     = "ssh"
      user     = "ec2-user"
      private_key = "${file("~/.ssh/id_rsa")}"
    }
    inline = [
      "chmod +x /home/ec2-user/install.sh",
      "source /home/ec2-user/install.sh"
    ]
  }

  provisioner "remote-exec" { 
    connection {
      host = self.public_ip
      type     = "ssh"
      user     = "ec2-user"
      private_key = "${file("~/.ssh/id_rsa")}"
    }
    inline = [
      "chmod +x /home/ec2-user/travel-buddy/start.sh",
      "source /home/ec2-user/travel-buddy/start.sh"
    ]
  }
}


 output "public_ip" {
  value = aws_instance.travel-buddy-instance.public_ip  
 }

  output "public_dns" {
  value = aws_instance.travel-buddy-instance.public_dns  
 }

resource "aws_vpc" "travel-buddy-vpc" {
    cidr_block = var.vpc_cidr_block
    tags = {
        Name: "${var.env_prefix}-travel-buddy-vpc"
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

resource "aws_route_table_association" "travel-buddy-route-ta" {
  route_table_id = aws_route_table.travel-buddy-route-table.id
  subnet_id = aws_subnet.travel-buddy-subnet.id
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
# 5000
resource "aws_route_table_association" "travel-buddy-rtba" {
  subnet_id = aws_subnet.travel-buddy-subnet.id
  route_table_id = aws_route_table.travel-buddy-route-table.id
}

resource "aws_security_group" "travel-buddy-sgroup" {
    vpc_id = aws_vpc.travel-buddy-vpc.id
    tags = {
        Name: "${var.env_prefix}-travel-buddy-sg"
    }
}

resource "aws_vpc_security_group_egress_rule" "egress-rule" {
    security_group_id = aws_security_group.travel-buddy-sgroup.id
    ip_protocol = -1
    cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "travel-buddy-rule" {
    security_group_id = aws_security_group.travel-buddy-sgroup.id
    from_port = 5000
    to_port = 5000
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