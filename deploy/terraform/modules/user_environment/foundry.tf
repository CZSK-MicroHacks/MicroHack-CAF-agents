resource "azapi_resource" "foundry_account" {
  type      = "Microsoft.CognitiveServices/accounts@2025-06-01"
  name      = local.foundry_account_name
  parent_id = azapi_resource.rg.id
  location  = var.location
  identity {
    type = "SystemAssigned"
  }

  body = {
    kind = "AIServices"
    sku = {
      name = "S0"
    }
    properties = {
      allowProjectManagement        = true
      customSubDomainName           = local.foundry_account_name
      disableLocalAuth              = false
      dynamicThrottlingEnabled      = false
      publicNetworkAccess           = "Enabled"
      restrictOutboundNetworkAccess = false
    }
  }

  schema_validation_enabled = false
}

resource "azapi_resource" "foundry_project" {
  type      = "Microsoft.CognitiveServices/accounts/projects@2025-07-01-preview"
  name      = local.foundry_project_name
  parent_id = azapi_resource.foundry_account.id
  location  = var.location
  identity {
    type = "SystemAssigned"
  }

  body = {
    properties = {
      displayName = local.foundry_project_name
      description = "Per-user Foundry project ${var.user}"
    }
  }

  schema_validation_enabled = false
}

resource "azapi_resource" "foundry_project_connection_ai_search" {
  type      = "Microsoft.CognitiveServices/accounts/projects/connections@2025-07-01-preview"
  name      = "ai-search"
  parent_id = azapi_resource.foundry_project.id

  body = {
    properties = {
      category                    = "CognitiveSearch"
      target                      = "https://${azurerm_search_service.user.name}.search.windows.net/"
      authType                    = "AAD"
      useWorkspaceManagedIdentity = true
    }
  }

  schema_validation_enabled = false

  depends_on = [
    azurerm_role_assignment.foundry_project_search_service_contributor,
    azurerm_role_assignment.foundry_project_search_index_data_contributor
  ]
}

resource "azapi_resource" "foundry_model_deployment_gpt52" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2025-06-01"
  name      = "gpt-5.2"
  parent_id = azapi_resource.foundry_account.id

  body = {
    sku = {
      name     = "GlobalStandard"
      capacity = 100
    }
    properties = {
      model = {
        format  = "OpenAI"
        name    = "gpt-5.2"
        version = "2025-12-11"
      }
      versionUpgradeOption = "OnceNewDefaultVersionAvailable"
    }
  }

  schema_validation_enabled = false

  depends_on = [azapi_resource.foundry_project]
}

resource "azapi_resource" "foundry_model_deployment_gpt5mini" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2025-06-01"
  name      = "gpt-5-mini"
  parent_id = azapi_resource.foundry_account.id

  body = {
    sku = {
      name     = "GlobalStandard"
      capacity = 100
    }
    properties = {
      model = {
        format  = "OpenAI"
        name    = "gpt-5-mini"
        version = "2025-08-07"
      }
      versionUpgradeOption = "OnceNewDefaultVersionAvailable"
    }
  }

  schema_validation_enabled = false
  depends_on                = [azapi_resource.foundry_model_deployment_gpt52]
}

resource "azapi_resource" "foundry_model_deployment_gpt5nano" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2025-06-01"
  name      = "gpt-5-nano"
  parent_id = azapi_resource.foundry_account.id

  body = {
    sku = {
      name     = "GlobalStandard"
      capacity = 300
    }
    properties = {
      model = {
        format  = "OpenAI"
        name    = "gpt-5-nano"
        version = "2025-08-07"
      }
      versionUpgradeOption = "OnceNewDefaultVersionAvailable"
    }
  }

  schema_validation_enabled = false
  depends_on                = [azapi_resource.foundry_model_deployment_gpt5mini]
}

resource "azapi_resource" "foundry_model_deployment_textembedding3large" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2025-06-01"
  name      = "text-embedding-3-large"
  parent_id = azapi_resource.foundry_account.id

  body = {
    sku = {
      name     = "GlobalStandard"
      capacity = 20
    }
    properties = {
      model = {
        format  = "OpenAI"
        name    = "text-embedding-3-large"
        version = "1"
      }
      versionUpgradeOption = "OnceNewDefaultVersionAvailable"
    }
  }

  schema_validation_enabled = false
  depends_on                = [azapi_resource.foundry_model_deployment_gpt5nano]
}
