variable "vpc_id" {
  description = "Ecommerce VPC ID"
  type        = string
}

variable "db_password" {
  description = "RDS PostgreSQL password"
  type        = string
  sensitive   = true
}
