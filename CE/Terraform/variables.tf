variable "aws_access_key" {
  type        = string
  description = "AWS Access Key for authentication"
}

variable "aws_secret_key" {
  type        = string
  description = "AWS Secret Key for authentication"
}

variable "db_password" {
  type        = string
  description = "Password for the RDS PostgreSQL instance"
}

variable "private_subnet_cidrs" {
  type = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "aws_availability_zones" {
  type = list(string)
  default = ["eu-west-2a","eu-west-2b", "eu-west-2c"]
}

variable "user"{
type = string
}