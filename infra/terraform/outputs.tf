output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app.id
}

output "public_ip" {
  description = "EC2 public IP"
  value       = aws_instance.app.public_ip
}

output "public_dns" {
  description = "EC2 public DNS"
  value       = aws_instance.app.public_dns
}

output "ssh_command" {
  description = "Ready-to-paste SSH command (assumes ~/.ssh/letter-poc.pem)"
  value       = "ssh -i ~/.ssh/${var.key_pair_name}.pem ubuntu@${aws_instance.app.public_ip}"
}

output "api_url" {
  description = "Transcription API URL"
  value       = "http://${aws_instance.app.public_ip}:8000"
}

output "prometheus_url" {
  description = "Prometheus UI"
  value       = "http://${aws_instance.app.public_ip}:9090"
}

output "grafana_url" {
  description = "Grafana UI"
  value       = "http://${aws_instance.app.public_ip}:3000"
}

output "ssh_allowed_from" {
  description = "CIDR currently authorized for SSH"
  value       = var.ssh_allowed_cidr
}