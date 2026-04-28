output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.k8s.id
}

output "public_ip" {
  description = "EC2 public IP"
  value       = aws_instance.k8s.public_ip
}

output "public_dns" {
  description = "EC2 public DNS"
  value       = aws_instance.k8s.public_dns
}

output "ssh_command" {
  description = "Ready-to-paste SSH command"
  value       = "ssh -i ~/.ssh/${var.key_pair_name}.pem ubuntu@${aws_instance.k8s.public_ip}"
}

output "api_url_nodeport" {
  description = "Transcription API URL via K3s NodePort (port assigned in manifests, Step 3)"
  value       = "http://${aws_instance.k8s.public_ip}:30080"
}

output "kubectl_server_url" {
  description = "Kubernetes API server URL (used in kubeconfig)"
  value       = "https://${aws_instance.k8s.public_ip}:6443"
}

output "kubeconfig_fetch_command" {
  description = "Run after Step 3 to fetch kubeconfig locally"
  value = join(" && ", [
    "scp -i ~/.ssh/${var.key_pair_name}.pem ubuntu@${aws_instance.k8s.public_ip}:/home/ubuntu/k3s.yaml ~/.kube/config-letter-poc",
    "sed -i 's|127.0.0.1|${aws_instance.k8s.public_ip}|g' ~/.kube/config-letter-poc",
    "export KUBECONFIG=~/.kube/config-letter-poc"
  ])
}