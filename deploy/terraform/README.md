# Terraform Workshop Infrastructure

This Terraform configuration deploys per-user workshop environments in Azure.

## What gets deployed per user
- Resource Group: `rg-userNNN`
- Storage Account (Blob-capable): `stuserNNNxxxxxx`
- Azure AI Search (Standard): `srch-userNNN-xxxxxx`
- Optional Entra user, membership in the shared `MicroHackUsers` security group, and Owner RBAC on the resource group (when `manage_entra_users=true`)

`NNN` is a zero-padded user index and `xxxxxx` is a generated random 6-character lowercase suffix.

## Naming and uniqueness
Some Azure resources must be globally unique. Each user environment generates one random suffix:
- 6 characters
- lowercase letters only (`a-z`)

That suffix is reused for globally unique resources in that user environment.

## Variables
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `n` | number | yes | Default number of seats when count overrides are unset. |
| `n_entra` | number | no | Optional override for the number of Entra users. Defaults to `n`. |
| `n_azure` | number | no | Optional override for the number of Azure user environments. Defaults to `n`. |
| `locations` | list(string) | yes | Azure regions used in round-robin distribution. |
| `subscription_id` | string | yes | Target Azure subscription ID. |
| `manage_azure_resources` | bool | no (default `true`) | Deploy per-user Azure resources. |
| `manage_entra_users` | bool | no (default `true`) | Create Entra users and assign Owner on each user RG. |
| `entra_user_domain` | string | conditional | Required when `manage_entra_users=true`. |
| `entra_user_password` | string | conditional | Required when `manage_entra_users=true`. |

Each user environment deploys chat models plus `text-embedding-3-large` on the Foundry account, and also deploys `text-embedding-3-large` on the dedicated Azure OpenAI account used for Search embeddings.

## Quick start
```pwsh
terraform init
terraform workspace select sub1
terraform plan -var-file="sub1.tfvars"
terraform apply -var-file="sub1.tfvars"
```

## Outputs
- `resource_group_names`
- `storage_account_names`
- `search_service_names`
- `entra_user_principal_names`
- `entra_user_object_ids`
- `entra_security_group_object_id`
- `entra_security_group_display_name`
- `region_assignment`
- `region_distribution`
