resource "google_container_cluster" "primary" {
  name               = "${var.GCP_GKE_NAME}"
  zone               = "${var.GCP_ZONE}"
  initial_node_count = 3

  ip_allocation_policy = {
    cluster_ipv4_cidr_block = "10.2.0.0/19"
  }
}

output "cluster_endpoint" {
  value = "${google_container_cluster.primary.endpoint}"
}
