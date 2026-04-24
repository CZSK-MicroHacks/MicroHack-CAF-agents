resource "azurerm_search_service" "user" {
  name                = local.search_service_name
  resource_group_name = local.rg_name
  location            = local.resolved_search_location
  sku                 = "standard"
  semantic_search_sku = "free"
  local_authentication_enabled = true
  authentication_failure_mode  = "http401WithBearerChallenge"
  replica_count       = 1
  partition_count     = 1
  identity {
    type = "SystemAssigned"
  }

  depends_on = [azapi_resource.rg]
}
