variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-3"
}

variable "project_name" {
  description = "Used as a prefix and tag value on all resources"
  type        = string
  default     = "letter-transcription-poc"
}

variable "environment" {
  description = "Environment label (poc, dev, prod)"
  type        = string
  default     = "poc"
}

variable "key_pair_name" {
  description = "Existing AWS EC2 key pair name (created out-of-band)"
  type        = string
  default     = "letter-poc"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "root_volume_size_gb" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 20
}

variable "ssh_allowed_cidr" {
  description = "CIDR allowed for SSH."
  type        = string
}

variable "app_ports" {
  description = "TCP ports open to the world for the app and observability"
  type        = list(number)
  default     = [8000, 9090, 3000]
}