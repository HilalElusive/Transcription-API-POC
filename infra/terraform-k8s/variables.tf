variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-3"
}

variable "project_name" {
  description = "Used as a prefix and tag value on all resources"
  type        = string
  default     = "letter-transcription-poc-k8s"
}

variable "environment" {
  description = "Environment label"
  type        = string
  default     = "poc"
}

variable "key_pair_name" {
  description = "Existing AWS EC2 key pair name (created out-of-band)"
  type        = string
  default     = "letter-poc"
}

variable "instance_type" {
  description = "EC2 instance type. K3s + Postgres + 6 API pods needs ~6GB RAM peak."
  type        = string
  default     = "t3.large"
}

variable "root_volume_size_gb" {
  description = "Root EBS size. K3s containerd cache + PVCs live here."
  type        = number
  default     = 30
}

variable "ssh_allowed_cidr" {
  description = "CIDR allowed for SSH. Open to world for CI runner reachability (see Phase 1 Incident #1)."
  type        = string
  default     = "0.0.0.0/0"
}

variable "kubectl_allowed_cidr" {
  description = "CIDR allowed to reach the Kubernetes API server (port 6443). Lock this to your IP."
  type        = string
}

variable "nodeport_range" {
  description = "K3s NodePort service port range opened to world."
  type        = object({ from = number, to = number })
  default     = { from = 30000, to = 32767 }
}