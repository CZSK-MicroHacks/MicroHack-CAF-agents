variable "n" {
  type        = number
  default     = 5
  description = "Default number of seats to provision when n_entra or n_azure are not set. Must be >= 1."

  validation {
    condition     = var.n >= 1
    error_message = "n must be greater than or equal to 1."
  }
}

variable "n_entra" {
  type        = number
  default     = null
  description = "Optional override for the number of Entra ID users to provision. Defaults to n when unset."

  validation {
    condition     = var.n_entra == null ? true : var.n_entra >= 1
    error_message = "n_entra must be null or greater than or equal to 1."
  }
}

variable "n_azure" {
  type        = number
  default     = null
  description = "Optional override for the number of Azure user environments to provision. Defaults to n when unset."

  validation {
    condition     = var.n_azure == null ? true : var.n_azure >= 1
    error_message = "n_azure must be null or greater than or equal to 1."
  }
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
When true: creates n_entra users, or n users when n_entra is unset, and assigns Owner RBAC on each resource group.
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
When true: n_azure per-user resource groups, or n resource groups when n_azure is unset, are provisioned with optional RBAC.
When false: only Entra ID users are created (if manage_entra_users is true).
EOT
}

