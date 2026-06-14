output "cloud_run_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.app.uri
}

output "service_account_email" {
  description = "Service Account email for Cloud Run"
  value       = google_service_account.app_sa.email
}

output "image_registry" {
  description = "Artifact Registry image path"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/ai-agent/app"
}
