# Create Workspaces – Usage Guide

Script for provisioning and deleting Microsoft Fabric workspaces using the Fabric CLI (`fab`).

## Prerequisites

- [Fabric CLI (`fab`)](https://aka.ms/fabric-cli) installed and authenticated (`fab auth`)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) logged in (`az login`) — used to resolve user UPNs to Entra object IDs
- Fabric capacities already created (see `manage-fabric-help.md`)

## Actions

### Create workspaces

For each entry in the configuration, the script performs 3 steps:

| Step | Action | Command |
|------|--------|---------|
| 1 | Create workspace with capacity | `fab mkdir -P capacityName=...` |
| 2 | Add user as workspace Admin | `fab acl set` |
| 3 | Set Spark starter pool max nodes to 1 | `fab set` |

If the workspace already exists, step 1 falls back to `fab assign` to reassign the capacity.

```powershell
# Create using built-in defaults
.\create-workspaces.ps1

# Create using an external JSON config file
.\create-workspaces.ps1 -Action create -ConfigFile .\workspaces.json
```

### Delete workspaces

Removes all workspaces defined in the configuration. Uses `fab rm` with the `-f` (force) flag.

```powershell
# Delete using built-in defaults
.\create-workspaces.ps1 -Action delete

# Delete workspaces defined in a JSON config file
.\create-workspaces.ps1 -Action delete -ConfigFile .\workspaces.json
```

## Configuration

### Option 1 — Edit the script directly

Open `create-workspaces.ps1` and modify the `$DefaultWorkspaces` array:

```powershell
$DefaultWorkspaces = @(
    @{ user_name = "alice@contoso.com"; workspace_name = "ws-alice"; capacity_name = "fabric01sc" }
    @{ user_name = "bob@contoso.com";   workspace_name = "ws-bob";   capacity_name = "fabric02ne" }
)
```

Then run without parameters:

```powershell
.\create-workspaces.ps1
```

### Option 2 — Use a JSON config file

Create a JSON file (e.g. `workspaces.json`):

```json
[
  { "user_name": "alice@contoso.com", "workspace_name": "ws-alice", "capacity_name": "fabric01sc" },
  { "user_name": "bob@contoso.com",   "workspace_name": "ws-bob",   "capacity_name": "fabric02ne" },
  { "user_name": "carol@contoso.com", "workspace_name": "ws-carol", "capacity_name": "fabric03wu3" },
  { "user_name": "dave@contoso.com",  "workspace_name": "ws-dave",  "capacity_name": "fabric04we" }
]
```

Then pass it as a parameter:

```powershell
.\create-workspaces.ps1 -ConfigFile .\workspaces.json
```

## Parameters

| Parameter     | Required | Description                                              |
|---------------|----------|----------------------------------------------------------|
| `-Action`     | No       | `create` (default) or `delete`                           |
| `-ConfigFile` | No       | Path to a JSON file with workspace definitions. If omitted, uses the built-in `$DefaultWorkspaces` array. |

## Configuration fields

| Field            | Description                              | Example          |
|------------------|------------------------------------------|------------------|
| `user_name`      | User UPN to add as workspace Admin       | `alice@contoso.com` |
| `workspace_name` | Name of the Fabric workspace to create   | `ws-alice`       |
| `capacity_name`  | Name of the Fabric capacity to assign    | `fabric01sc`     |

## Available capacities

| Capacity Name  | Region         |
|----------------|----------------|
| `fabric01sc`   | Sweden Central |
| `fabric02ne`   | North Europe   |
| `fabric03wu3`  | West US 3      |
| `fabric04we`   | West Europe    |

## Running from cmd

```cmd
powershell -ExecutionPolicy Bypass -File .\create-workspaces.ps1
powershell -ExecutionPolicy Bypass -File .\create-workspaces.ps1 -ConfigFile .\workspaces.json
powershell -ExecutionPolicy Bypass -File .\create-workspaces.ps1 -Action delete -ConfigFile .\workspaces.json
```
