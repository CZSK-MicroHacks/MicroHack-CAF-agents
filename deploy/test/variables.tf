variable "subscription_id" {
  type        = string
  description = "Azure Subscription ID where the test user environment will be deployed."
}

variable "location" {
  type        = string
  description = "Azure region where rg-user-test and its resources will be created."
}

variable "search_location" {
  type        = string
  default     = "germanywestcentral"
  description = "Azure region for the Azure AI Search service when the primary location has no search capacity."
}

variable "user_name" {
  type        = string
  default     = "user-test"
  description = "Logical user name used to derive rg-user-test and related resource names."
}