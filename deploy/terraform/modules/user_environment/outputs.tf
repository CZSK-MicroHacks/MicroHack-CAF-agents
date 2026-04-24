output "resource_group_name" { value = local.rg_name }
output "storage_account_name" { value = azurerm_storage_account.user.name }
output "search_service_name" { value = azurerm_search_service.user.name }
output "storage_container_name" { value = sort([for c in azurerm_storage_container.data : c.name]) }
output "foundry_account_name" { value = azapi_resource.foundry_account.name }
output "openai_account_name" { value = azapi_resource.openai_account.name }
output "foundry_project_name" { value = azapi_resource.foundry_project.name }
