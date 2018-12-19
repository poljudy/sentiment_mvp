resource "google_redis_instance" "cache" {
  name           = "${var.GCP_REDIS_NAME}"
  tier           = "BASIC"
  memory_size_gb = 1

  location_id = "${var.GCP_ZONE}"

  redis_version = "REDIS_3_2"
  display_name  = "Sentish Redis Instance"
}

output "google_redis_instance_host" {
  value = "${google_redis_instance.cache.host}"
}
