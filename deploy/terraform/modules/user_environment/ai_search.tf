resource "azurerm_search_service" "user" {
  name                = local.search_service_name
  resource_group_name = local.rg_name
  location            = var.location
  sku                 = "standard"
  replica_count       = 1
  partition_count     = 1
  identity {
    type = "SystemAssigned"
  }

  depends_on = [azapi_resource.rg]
}
