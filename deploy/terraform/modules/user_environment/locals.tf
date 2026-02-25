locals {
  user_name            = split("@", var.user)[0]
  rg_name              = "rg-${local.user_name}"
  storage_account_name = "st${local.user_name}${random_string.unique_suffix.result}"
  search_service_name  = "srch-${local.user_name}-${random_string.unique_suffix.result}"
  foundry_account_name = "aif-${local.user_name}${random_string.unique_suffix.result}"
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

