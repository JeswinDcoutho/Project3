variable "vpc_id" {
  description = "Ecommerce VPC ID"
  type        = string

  default = "vpc-0fc6946872e7c4db1"
}

variable "db_password" {
  description = "RDS PostgreSQL password"
  type        = string
  sensitive   = true
}
