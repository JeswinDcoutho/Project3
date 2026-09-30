variable "vpc_id" {
  description = "Ecommerce VPC ID"
  type        = string
}

variable "eks_security_group_id" {
  description = "EKS cluster security group ID allowed to access RDS"
  type        = string
}

variable "db_password" {
  description = "RDS PostgreSQL password"
  type        = string
  sensitive   = true
}
