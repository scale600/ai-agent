terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
  required_version = ">= 1.5"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ── Artifact Registry ──────────────────────────────────────────────────────────

resource "google_project_service" "artifact_registry" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "ai-agent"
  format        = "DOCKER"
  depends_on    = [google_project_service.artifact_registry]
}

# ── Service Account ────────────────────────────────────────────────────────────

resource "google_service_account" "app_sa" {
  account_id   = "ai-agent-sa"
  display_name = "AI Agent App Service Account"
}

# Static pages only — no IAM / Vertex AI permissions needed
# (All previous IAM roles intentionally removed to minimize attack surface and cost)

# ── Cloud Run ──────────────────────────────────────────────────────────────────

locals {
  image = "${var.region}-docker.pkg.dev/${var.project_id}/ai-agent/app:${var.image_tag}"
}

resource "google_cloud_run_v2_service" "app" {
  name     = "ai-agent"
  location = var.region

  deletion_protection = false

  template {
    service_account = google_service_account.app_sa.email

    containers {
      image = local.image

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.region
      }

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      startup_probe {
        http_get {
          path = "/_stcore/health"
          port = 8080
        }
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 5
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }
  }

  depends_on = [google_artifact_registry_repository.repo]
}

# Allow public (unauthenticated) access
resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.app.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
