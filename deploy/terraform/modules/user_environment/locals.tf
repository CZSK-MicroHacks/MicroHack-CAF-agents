locals {
  user_name            = split("@", var.user)[0]
  storage_user_name    = join("", regexall("[0-9a-z]", lower(local.user_name)))
  resolved_search_location = coalesce(var.search_location, var.location)
  rg_name              = "rg-${local.user_name}"
  storage_account_name = "st${local.storage_user_name}${random_string.unique_suffix.result}"
  search_service_name  = "srch-${local.user_name}-${random_string.unique_suffix.result}"
  foundry_account_name = "aif-${local.user_name}${random_string.unique_suffix.result}"
  openai_account_name  = "oai${local.storage_user_name}${random_string.unique_suffix.result}"
  foundry_project_name = "project-${local.user_name}"
  document_audio_files = fileset("${path.module}/../../../../data/documents", "*.mp3")
  document_pdf_files   = fileset("${path.module}/../../../../data/documents", "*.pdf")
}

resource "random_string" "unique_suffix" {
  length  = 6
  lower   = true
  upper   = false
  numeric = false
  special = false
}

