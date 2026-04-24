data "azurerm_client_config" "current" {}

module "user_environment" {
  source = "../terraform/modules/user_environment"

  user                    = var.user_name
  location                = var.location
  search_location         = var.search_location
  assigned_user_object_id = data.azurerm_client_config.current.object_id
  create_role_assignment  = true
}