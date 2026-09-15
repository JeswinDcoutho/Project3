terraform {
  backend "s3" {
    bucket       = "ecommerce-terraform-state-777000838263"
    key          = "ecommerce/redis/terraform.tfstate"
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

resource "aws_security_group" "redis" {
  name        = "ecommerce-redis-sg"
  description = "Allow Redis access from EKS nodes"
  vpc_id      = data.aws_vpc.ecommerce.id

  ingress {
    description     = "Redis from EKS"
    from_port       = 6379
    to_port         = 6379
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
    Name    = "ecommerce-redis-sg"
    Project = "ecommerce"
  }
}

resource "aws_elasticache_subnet_group" "redis" {
  name       = "ecommerce-redis-subnet-group"
  subnet_ids = data.aws_subnets.private.ids
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = "ecommerce-redis"
  description          = "Ecommerce Redis"

  engine             = "redis"
  node_type          = "cache.t4g.micro"
  num_cache_clusters = 1

  port = 6379

  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]

  automatic_failover_enabled = false
  multi_az_enabled           = false

  tags = {
    Name    = "ecommerce-redis"
    Project = "ecommerce"
  }
}
