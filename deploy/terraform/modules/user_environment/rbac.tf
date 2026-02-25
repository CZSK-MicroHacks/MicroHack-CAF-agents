locals {
  owner_role_definition_id                          = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
  blob_reader_role_definition_id                    = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/2a2b9908-6ea1-4ae2-8e65-a410df84e7d1"
  search_service_contributor_role_definition_id     = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/7ca78c08-252a-4471-8644-bb5ff32d4ba0"
  search_index_data_contributor_role_definition_id  = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/8ebe5a00-799e-43f5-93ac-243d3dce84a7"
  cognitive_services_openai_user_role_definition_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/5e0bd9bd-7b93-4f28-af87-19fc36ad61bd"
  role_assignment_ns                                = "b24988ac-6180-42a0-ab88-20f7382dd24c"
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

resource "azurerm_role_assignment" "foundry_project_search_service_contributor" {
  scope              = azurerm_search_service.user.id
  role_definition_id = local.search_service_contributor_role_definition_id
  principal_id       = azapi_resource.foundry_project.identity[0].principal_id
  principal_type     = "ServicePrincipal"

  depends_on = [
    azapi_resource.foundry_project,
    azurerm_search_service.user
  ]
}

resource "azurerm_role_assignment" "foundry_project_search_index_data_contributor" {
  scope              = azurerm_search_service.user.id
  role_definition_id = local.search_index_data_contributor_role_definition_id
  principal_id       = azapi_resource.foundry_project.identity[0].principal_id
  principal_type     = "ServicePrincipal"

  depends_on = [
    azapi_resource.foundry_project,
    azurerm_search_service.user
  ]
}

resource "azurerm_role_assignment" "search_foundry_openai_user" {
  scope              = azapi_resource.foundry_account.id
  role_definition_id = local.cognitive_services_openai_user_role_definition_id
  principal_id       = azurerm_search_service.user.identity[0].principal_id
  principal_type     = "ServicePrincipal"

  depends_on = [
    azapi_resource.foundry_account,
    azurerm_search_service.user
  ]
}
