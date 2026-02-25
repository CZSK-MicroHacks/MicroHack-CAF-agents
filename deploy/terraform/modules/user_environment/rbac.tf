locals {
  owner_role_definition_id       = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
  blob_reader_role_definition_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/2a2b9908-6ea1-4ae2-8e65-a410df84e7d1"
  role_assignment_ns             = "b24988ac-6180-42a0-ab88-20f7382dd24c"
}

resource "azapi_resource" "rg_owner_role_assignment" {
  count     = var.create_role_assignment ? 1 : 0
  type      = "Microsoft.Authorization/roleAssignments@2022-04-01"
  name      = uuidv5(local.role_assignment_ns, "${data.azurerm_client_config.current.subscription_id}/${local.rg_name}/${var.assigned_user_object_id}")
  parent_id = azapi_resource.rg.id
  body = {
    properties = {
      roleDefinitionId = local.owner_role_definition_id
      principalId      = var.assigned_user_object_id
      principalType    = "User"
    }
  }

  lifecycle {
    precondition {
      condition     = !var.create_role_assignment || (var.create_role_assignment && var.assigned_user_object_id != null)
      error_message = "create_role_assignment=true requires non-null assigned_user_object_id"
    }
  }
}

resource "azurerm_role_assignment" "search_storage_blob_reader" {
  scope              = azurerm_storage_account.user.id
  role_definition_id = local.blob_reader_role_definition_id
  principal_id       = azurerm_search_service.user.identity[0].principal_id

  depends_on = [
    azurerm_search_service.user,
    azurerm_storage_account.user
  ]
}
