# Fabric Capacity Manager – Usage Guide

Script for managing Microsoft Fabric capacities in Azure (resource group `rg-caf2026-fabric`).

## Prerequisites

- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and logged in (`az login`)
- The `microsoft.fabric` extension is installed automatically on first run

## Configuration

Capacities can be defined in two ways:

1. **Built-in defaults** — used when `-ConfigFile` is omitted
2. **External JSON file** — passed via `-ConfigFile .\capacities.json`

### JSON format (`capacities.json`)

```json
[
  { "CapacityName": "fabric01sc",  "Location": "swedencentral", "SKU": "F2" },
  { "CapacityName": "fabric02ne",  "Location": "northeurope",   "SKU": "F2" },
  { "CapacityName": "fabric03wu3", "Location": "westus3",       "SKU": "F2" },
  { "CapacityName": "fabric04we",  "Location": "westeurope",    "SKU": "F2" }
]
```

### Default capacities

| CapacityName     | Location       | SKU |
|------------------|----------------|-----|
| `fabric01sc`     | swedencentral  | F2  |
| `fabric02ne`     | northeurope    | F2  |
| `fabric03wu3`    | westus3        | F2  |
| `fabric04we`     | westeurope     | F2  |

## Actions

### Create resource group and capacities

```powershell
# Using built-in defaults
.\manage-fabric.ps1 -Action create -AdminUpn "admin@contoso.com"

# Using an external JSON config file
.\manage-fabric.ps1 -Action create -AdminUpn "admin@contoso.com" -ConfigFile .\capacities.json
```

The `-AdminUpn` parameter is **required** for `create` — it sets the Fabric capacity administrator.

### Start (resume) capacities

```powershell
# Start all capacities
.\manage-fabric.ps1 -Action start

# Start a specific capacity
.\manage-fabric.ps1 -Action start -CapacityName fabric02ne
```

### Pause (suspend) capacities

```powershell
# Pause all capacities
.\manage-fabric.ps1 -Action pause

# Pause a specific capacity
.\manage-fabric.ps1 -Action pause -CapacityName fabric01sc
```

### Scale capacities

```powershell
# Scale all capacities to F8
.\manage-fabric.ps1 -Action scale -Sku F8

# Scale a specific capacity to F4
.\manage-fabric.ps1 -Action scale -CapacityName fabric03wu3 -Sku F4
```

### Check capacity status

```powershell
# Show status of all capacities
.\manage-fabric.ps1 -Action status

# Show status of a specific capacity
.\manage-fabric.ps1 -Action status -CapacityName fabric01sc
```

Displays name, location, SKU, and state (Active/Paused) for each capacity.

Supported SKUs: `F2`, `F4`, `F8`, `F16`, `F32`, `F64`, `F128`, `F256`, `F512`, `F1024`, `F2048`.

## Parameters

| Parameter        | Required    | Description                                         |
|------------------|-------------|-----------------------------------------------------|
| `-Action`        | Yes         | `create`, `start`, `pause`, `scale`, or `status`    |
| `-CapacityName`  | No          | Target a single capacity; omit to target all         |
| `-Sku`           | Scale only  | New SKU to scale to                                  |
| `-AdminUpn`      | Create only | UPN of the Fabric capacity administrator             |
| `-ConfigFile`    | No          | Path to a JSON file with capacity definitions        |
