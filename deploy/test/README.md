# Test User Environment

This Terraform root deploys a single user environment into the dedicated resource group `rg-user-test`.

It intentionally does not create or modify any Entra ID users, groups, or role assignments.

## Usage

```powershell
terraform -chdir=deploy/test init
terraform -chdir=deploy/test plan --var-file .\sub1.tfvars
terraform -chdir=deploy/test apply --var-file .\sub1.tfvars --auto-approve
```

## Inputs

- `subscription_id`: Azure subscription ID for the deployment.
- `location`: Azure region for the resource group and contained services.
- `search_location`: Optional Azure region for Azure AI Search when the primary region has no search capacity.
- `user_name`: Defaults to `user-test`; keep this value if you want the resource group to remain `rg-user-test`.