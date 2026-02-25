
resource "azurerm_storage_account" "user" {
  name                            = local.storage_account_name
  resource_group_name             = local.rg_name
  location                        = var.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = false
  min_tls_version                 = "TLS1_2"

  depends_on = [azapi_resource.rg]
}

resource "azurerm_storage_container" "data" {
  for_each              = toset(["audio", "documents", "wines", "reviews"])
  name                  = each.value
  storage_account_id    = azurerm_storage_account.user.id
  container_access_type = "private"
}

resource "azurerm_storage_blob" "audio_documents_mp3" {
  for_each               = local.document_audio_files
  name                   = each.value
  storage_account_name   = azurerm_storage_account.user.name
  storage_container_name = azurerm_storage_container.data["audio"].name
  type                   = "Block"
  source                 = "${path.module}/../../../../data/documents/${each.value}"
  content_type           = "audio/mpeg"
}

resource "azurerm_storage_blob" "documents_pdf" {
  for_each               = local.document_pdf_files
  name                   = each.value
  storage_account_name   = azurerm_storage_account.user.name
  storage_container_name = azurerm_storage_container.data["documents"].name
  type                   = "Block"
  source                 = "${path.module}/../../../../data/documents/${each.value}"
  content_type           = "application/pdf"
}

resource "azurerm_storage_blob" "wines_json" {
  name                   = "wines.json"
  storage_account_name   = azurerm_storage_account.user.name
  storage_container_name = azurerm_storage_container.data["wines"].name
  type                   = "Block"
  source                 = "${path.module}/../../../../data/wines.json"
  content_type           = "application/json"
}

resource "azurerm_storage_blob" "reviews_json" {
  name                   = "reviews.json"
  storage_account_name   = azurerm_storage_account.user.name
  storage_container_name = azurerm_storage_container.data["reviews"].name
  type                   = "Block"
  source                 = "${path.module}/../../../../data/reviews.json"
  content_type           = "application/json"
}
