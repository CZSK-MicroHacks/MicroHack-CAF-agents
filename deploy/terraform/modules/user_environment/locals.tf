locals {
  padded               = format("%03d", var.user_index)
  rg_name              = "rg-user${local.padded}"
  storage_account_name = "stuser${local.padded}${random_string.unique_suffix.result}"
  search_service_name  = "srch-user${local.padded}-${random_string.unique_suffix.result}"
  foundry_account_name = "aif${local.padded}${random_string.unique_suffix.result}uk"
  foundry_project_name = "project-user${local.padded}"
  foundry_location     = "uksouth"
  data_json_files      = fileset("${path.module}/../../../../data", "*.json")
}

resource "random_string" "unique_suffix" {
  length  = 6
  lower   = true
  upper   = false
  numeric = false
  special = false
}

