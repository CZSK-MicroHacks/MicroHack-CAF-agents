variable "user_index" {
  type        = number
  description = "Numeric user index (1..n) used to derive naming (rg-userNNN)."
}

variable "location" {
  type        = string
  description = "Azure region where the resource group is created."
}

variable "assigned_user_object_id" {
  type        = string
  default     = null
  description = <<EOT
Optional Entra ID user object ID to receive Owner role on this resource group.
If null, no role assignment resource is created.
Supplied by root when `manage_entra_users=true`.
EOT
}

variable "create_role_assignment" {
  type        = bool
  default     = false
  description = <<EOT
Explicit switch controlling creation of the Owner role assignment.
Set true only when an assigned_user_object_id is also provided.
EOT
}

variable "deploy_gpt52" {
  type        = bool
  default     = false
  description = "Deploy gpt-5.2 model. Requires Global Provisioned Managed throughput quota."
}
