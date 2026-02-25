
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
  name                  = "data"
  storage_account_id    = azurerm_storage_account.user.id
  container_access_type = "private"
}

resource "azurerm_storage_blob" "json_data" {
  for_each               = local.data_json_files
  name                   = each.value
  storage_account_name   = azurerm_storage_account.user.name
  storage_container_name = azurerm_storage_container.data.name
  type                   = "Block"
  source                 = "${path.module}/../../../../data/${each.value}"
  content_type           = "application/json"
}
