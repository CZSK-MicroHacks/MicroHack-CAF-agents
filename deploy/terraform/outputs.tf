output "resource_group_names" {
  description = "List of provisioned resource group names."
  value       = [for k, m in module.user_environment : m.resource_group_name]
}

output "storage_account_names" {
  description = "List of provisioned storage account names."
  value       = [for k, m in module.user_environment : m.storage_account_name]
}

output "search_service_names" {
  description = "List of provisioned Azure AI Search service names."
  value       = [for k, m in module.user_environment : m.search_service_name]
}

output "storage_container_names" {
  description = "List of provisioned blob container names."
  value       = [for k, m in module.user_environment : m.storage_container_name]
}

output "foundry_account_names" {
  description = "List of provisioned Azure AI Foundry account names."
  value       = [for k, m in module.user_environment : m.foundry_account_name]
}

output "foundry_project_names" {
  description = "List of provisioned Azure AI Foundry project names."
  value       = [for k, m in module.user_environment : m.foundry_project_name]
}

output "entra_user_principal_names" {
  description = "List of Entra user principal names (when manage_entra_users=true)."
  value       = var.manage_entra_users ? [for k, u in module.entra_users : u.user_principal_name] : []
}

output "entra_user_object_ids" {
  description = "List of Entra user object ids (when manage_entra_users=true)."
  value       = var.manage_entra_users ? [for k, u in module.entra_users : u.object_id] : []
}

output "region_assignment" {
  description = "Map of user index -> region (round-robin assignment)."
  value       = { for i in local.user_indices : i => local.user_location_map[i] }
}

output "region_distribution" {
  description = "Count of environments per region."
  value       = { for r in var.locations : r => length([for i in local.user_indices : local.user_location_map[i] if local.user_location_map[i] == r]) }
}
