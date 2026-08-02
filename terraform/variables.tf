variable "project_id" {
  description = "GCP Project ID — must be provided via -var or tfvars"
  type        = string
  # No default — caller must explicitly provide the project ID
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}
