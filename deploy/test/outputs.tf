output "resource_group_name" {
  description = "Resource group name for the test user environment."
  value       = module.user_environment.resource_group_name
}

output "storage_account_name" {
  description = "Storage account name for the test user environment."
  value       = module.user_environment.storage_account_name
}

output "search_service_name" {
  description = "Azure AI Search service name for the test user environment."
  value       = module.user_environment.search_service_name
}

output "storage_container_names" {
  description = "Blob container names created for the test user environment."
  value       = module.user_environment.storage_container_name
}

output "foundry_account_name" {
  description = "Azure AI Foundry account name for the test user environment."
  value       = module.user_environment.foundry_account_name
}

output "foundry_project_name" {
  description = "Azure AI Foundry project name for the test user environment."
  value       = module.user_environment.foundry_project_name
}