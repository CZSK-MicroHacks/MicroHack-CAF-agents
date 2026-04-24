locals {
  owner_role_definition_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
  role_assignment_ns       = "b24988ac-6180-42a0-ab88-20f7382dd24c"
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

# --- Foundry account roles for the assigned user ---

resource "azurerm_role_assignment" "user_foundry_ai_user" {
  count                = var.create_role_assignment ? 1 : 0
  scope                = azapi_resource.foundry_account.id
  role_definition_name = "Azure AI User"
  principal_id         = var.assigned_user_object_id
  principal_type       = "User"
}

resource "azurerm_role_assignment" "user_foundry_ai_project_manager" {
  count                = var.create_role_assignment ? 1 : 0
  scope                = azapi_resource.foundry_account.id
  role_definition_name = "Azure AI Project Manager"
  principal_id         = var.assigned_user_object_id
  principal_type       = "User"
}

resource "azurerm_role_assignment" "user_foundry_cognitive_services_user" {
  count                = var.create_role_assignment ? 1 : 0
  scope                = azapi_resource.foundry_account.id
  role_definition_name = "Cognitive Services User"
  principal_id         = var.assigned_user_object_id
  principal_type       = "User"
}

resource "azurerm_role_assignment" "user_foundry_openai_user" {
  count                = var.create_role_assignment ? 1 : 0
  scope                = azapi_resource.foundry_account.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = var.assigned_user_object_id
  principal_type       = "User"
}

resource "azurerm_role_assignment" "user_openai_openai_user" {
  count                = var.create_role_assignment ? 1 : 0
  scope                = azapi_resource.openai_account.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = var.assigned_user_object_id
  principal_type       = "User"
}

# --- Foundry account role for the project managed identity ---

resource "azurerm_role_assignment" "foundry_project_ai_user" {
  scope                = azapi_resource.foundry_account.id
  role_definition_name = "Azure AI User"
  principal_id         = azapi_resource.foundry_project.identity[0].principal_id
  principal_type       = "ServicePrincipal"

  depends_on = [azapi_resource.foundry_project]
}

# --- Search and storage roles ---

resource "azurerm_role_assignment" "search_storage_blob_reader" {
  scope                = azurerm_storage_account.user.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_search_service.user.identity[0].principal_id

  depends_on = [
    azurerm_search_service.user,
    azurerm_storage_account.user
  ]
}

resource "azurerm_role_assignment" "user_storage_blob_data_owner" {
  count                = var.create_role_assignment ? 1 : 0
  scope                = azurerm_storage_account.user.id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = var.assigned_user_object_id
  principal_type       = "User"

  depends_on = [azurerm_storage_account.user]
}

resource "azurerm_role_assignment" "user_search_service_contributor" {
  count                = var.create_role_assignment ? 1 : 0
  scope                = azurerm_search_service.user.id
  role_definition_name = "Search Service Contributor"
  principal_id         = var.assigned_user_object_id
  principal_type       = "User"

  depends_on = [azurerm_search_service.user]
}

resource "azurerm_role_assignment" "user_search_index_data_contributor" {
  count                = var.create_role_assignment ? 1 : 0
  scope                = azurerm_search_service.user.id
  role_definition_name = "Search Index Data Contributor"
  principal_id         = var.assigned_user_object_id
  principal_type       = "User"

  depends_on = [azurerm_search_service.user]
}

resource "azurerm_role_assignment" "user_search_index_data_reader" {
  count                = var.create_role_assignment ? 1 : 0
  scope                = azurerm_search_service.user.id
  role_definition_name = "Search Index Data Reader"
  principal_id         = var.assigned_user_object_id
  principal_type       = "User"

  depends_on = [azurerm_search_service.user]
}

resource "azurerm_role_assignment" "foundry_project_search_service_contributor" {
  scope                = azurerm_search_service.user.id
  role_definition_name = "Search Service Contributor"
  principal_id         = azapi_resource.foundry_project.identity[0].principal_id
  principal_type       = "ServicePrincipal"

  depends_on = [
    azapi_resource.foundry_project,
    azurerm_search_service.user
  ]
}

resource "azurerm_role_assignment" "foundry_project_search_reader" {
  scope                = azurerm_search_service.user.id
  role_definition_name = "Reader"
  principal_id         = azapi_resource.foundry_project.identity[0].principal_id
  principal_type       = "ServicePrincipal"

  depends_on = [
    azapi_resource.foundry_project,
    azurerm_search_service.user
  ]
}

resource "azurerm_role_assignment" "foundry_project_search_index_data_contributor" {
  scope                = azurerm_search_service.user.id
  role_definition_name = "Search Index Data Contributor"
  principal_id         = azapi_resource.foundry_project.identity[0].principal_id
  principal_type       = "ServicePrincipal"

  depends_on = [
    azapi_resource.foundry_project,
    azurerm_search_service.user
  ]
}

resource "azurerm_role_assignment" "foundry_project_search_index_data_reader" {
  scope                = azurerm_search_service.user.id
  role_definition_name = "Search Index Data Reader"
  principal_id         = azapi_resource.foundry_project.identity[0].principal_id
  principal_type       = "ServicePrincipal"

  depends_on = [
    azapi_resource.foundry_project,
    azurerm_search_service.user
  ]
}

resource "azurerm_role_assignment" "search_foundry_openai_user" {
  scope                = azapi_resource.openai_account.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_search_service.user.identity[0].principal_id
  principal_type       = "ServicePrincipal"

  depends_on = [
    azapi_resource.openai_account,
    azurerm_search_service.user
  ]
}

resource "azurerm_role_assignment" "search_foundry_cognitive_services_user" {
  scope                = azapi_resource.foundry_account.id
  role_definition_name = "Cognitive Services User"
  principal_id         = azurerm_search_service.user.identity[0].principal_id
  principal_type       = "ServicePrincipal"

  depends_on = [
    azapi_resource.foundry_account,
    azurerm_search_service.user
  ]
}
