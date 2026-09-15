terraform {
  backend "s3" {
    bucket       = "ecommerce-terraform-state-777000838263"
    key          = "ecommerce/rds/terraform.tfstate"
    region       = "ap-south-1"
    use_lockfile = true
  }

  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

data "aws_vpc" "ecommerce" {
  id = var.vpc_id
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.ecommerce.id]
  }

  tags = {
    Type = "private"
  }
}

resource "aws_security_group" "rds" {
  name        = "ecommerce-rds-sg"
  description = "Allow PostgreSQL access from EKS nodes"
  vpc_id      = data.aws_vpc.ecommerce.id

  ingress {
    description     = "PostgreSQL from EKS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = ["sg-0391d7a0910ec6b66"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "ecommerce-rds-sg"
    Project = "ecommerce"
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "ecommerce-rds-subnet-group"
  subnet_ids = data.aws_subnets.private.ids

  tags = {
    Name = "ecommerce-rds-subnet-group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier = "ecommerce-postgres"

  engine         = "postgres"
  engine_version = "16"

  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 30
  storage_type          = "gp3"

  db_name  = "ecommerce"
  username = "ecommerce"
  password = var.db_password
  port     = 5432

  db_subnet_group_name = aws_db_subnet_group.main.name

  vpc_security_group_ids = [
    aws_security_group.rds.id
  ]

  publicly_accessible = false

  skip_final_snapshot = true
  deletion_protection = false

  backup_retention_period = 1

  tags = {
    Name    = "ecommerce-postgres"
    Project = "ecommerce"
  }

  lifecycle {
    ignore_changes = [
      password
    ]
  }
}
