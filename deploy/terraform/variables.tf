variable "n" {
  type        = number
  default     = 5
  description = "Number of user environments to provision. Each gets a resource group with optional RBAC. Must be >= 1."
}

variable "locations" {
  type        = list(string)
  description = <<EOT
List of Azure regions to distribute per-user resource groups across (round-robin).
Provide at least one region; empty list is invalid.
EOT
  validation {
    condition     = length(var.locations) > 0 && alltrue([for l in var.locations : length(trimspace(l)) > 0])
    error_message = "Provide at least one non-empty region name in locations."
  }
}

variable "manage_entra_users" {
  type        = bool
  default     = true
  description = <<EOT
Flag controlling whether temporary Entra ID user accounts are provisioned and granted Owner on each user resource group.
When true: creates n users and assigns Owner RBAC on each resource group.
When false: no Entra users are created and no role assignments are added.
EOT
}

variable "entra_user_domain" {
  type        = string
  default     = ""
  description = <<EOT
Custom domain (e.g. example.onmicrosoft.com) to append to generated user UPNs (user<index>@domain).
Required if manage_entra_users is true.
EOT
}

variable "entra_user_password" {
  type        = string
  sensitive   = true
  default     = ""
  description = <<EOT
Password to assign to all provisioned Entra ID users.
Provide via TF_VAR_entra_user_password env var.
If empty while manage_entra_users=true Terraform apply will fail in user module preconditions.
EOT
}

variable "subscription_id" {
  type        = string
  description = "Azure Subscription ID where all resources will be deployed."
}

variable "manage_azure_resources" {
  type        = bool
  default     = true
  description = <<EOT
Flag controlling whether user resource groups should be deployed.
When true: per-user resource groups with optional RBAC are provisioned.
When false: only Entra ID users are created (if manage_entra_users is true).
EOT
}

