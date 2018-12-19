variable "GCP_PROJECT" {
  default = "sentish"
}

variable "GCP_REGION" {
  default = "europe-west2"
}

variable "GCP_ZONE" {
  default = "europe-west2-a"
}

variable "GCP_GKE_NAME" {
  default = "gke-sentish"
}

variable "GCP_SQL_INSTANCE_NAME" {
  default = "sentish-master"
}

variable "GCP_SQL_DB_NAME" {
  default = "sentish"
}

variable "GCP_SQL_USER_NAME" {
  default = "sentish"
}

variable "GCP_SQL_USER_PASSWORD" {}

variable "GCP_REDIS_NAME" {
  default = "sentish-redis"
}
