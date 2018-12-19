provider "google" {
  credentials = "${file("gcp_credentials.json")}"
  project     = "${var.GCP_PROJECT}"
  region      = "${var.GCP_REGION}"
}
