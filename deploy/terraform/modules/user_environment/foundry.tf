resource "azapi_resource" "foundry_account" {
  type      = "Microsoft.CognitiveServices/accounts@2025-06-01"
  name      = local.foundry_account_name
  parent_id = azapi_resource.rg.id
  location  = local.foundry_location
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
  location  = local.foundry_location
  identity {
    type = "SystemAssigned"
  }

  body = {
    properties = {
      displayName = local.foundry_project_name
      description = "Per-user Foundry project ${local.padded}"
    }
  }

  schema_validation_enabled = false
}

resource "azapi_resource" "foundry_model_deployment_gpt52" {
  count     = var.deploy_gpt52 ? 1 : 0
  type      = "Microsoft.CognitiveServices/accounts/deployments@2025-06-01"
  name      = "dep-gpt52"
  parent_id = azapi_resource.foundry_account.id

  body = {
    sku = {
      name     = "GlobalProvisionedManaged"
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
  name      = "dep-gpt5mini"
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
  depends_on                = [azapi_resource.foundry_project]
}

resource "azapi_resource" "foundry_model_deployment_gpt5nano" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2025-06-01"
  name      = "dep-gpt5nano"
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
