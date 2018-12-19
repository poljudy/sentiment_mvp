resource "google_sql_database_instance" "master" {
  name             = "${var.GCP_SQL_INSTANCE_NAME}"
  database_version = "POSTGRES_9_6"
  region           = "${var.GCP_REGION}"

  settings {
    tier = "db-f1-micro"
  }
}

resource "google_sql_database" "database" {
  name     = "${var.GCP_SQL_DB_NAME}"
  instance = "${google_sql_database_instance.master.name}"
}

resource "google_sql_user" "users" {
  name     = "${var.GCP_SQL_USER_NAME}"
  instance = "${google_sql_database_instance.master.name}"
  host     = "*"
  password = "${var.GCP_SQL_USER_PASSWORD}"
}
