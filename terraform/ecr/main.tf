terraform {
  backend "s3" {
    bucket       = "ecommerce-terraform-state-777000838263"
    key          = "ecommerce/ecr/terraform.tfstate"
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

locals {
  services = [
    "user-service",
    "product-service",
    "cart-service",
    "order-service",
    "payment-service",
    "inventory-service"
  ]
}

resource "aws_ecr_repository" "services" {
  for_each = toset(local.services)

  name                 = "ecommerce-${each.value}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = "ecommerce"
    Service = each.value
  }
}
