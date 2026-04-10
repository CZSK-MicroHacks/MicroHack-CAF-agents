<#
.SYNOPSIS
    Manages Microsoft Fabric capacities in Azure – create, start, pause, scale, and status.

.DESCRIPTION
    Creates a resource group and 4 Fabric F2 capacities across different regions,
    with commands to start (resume), pause (suspend), scale, and check status of each capacity.

.PARAMETER Action
    The operation to perform: create, start, pause, scale, or status.

.PARAMETER CapacityName
    Target a specific capacity by name. If omitted, the action applies to ALL capacities.

.PARAMETER Sku
    New SKU for the scale action (e.g. F2, F4, F8, F16, F32, F64, F128, F256, F512, F1024, F2048).

.PARAMETER AdminUpn
    UPN of the Fabric capacity administrator (required for create).

.PARAMETER ConfigFile
    Path to a JSON file with capacity definitions. If omitted, uses the built-in defaults.
    JSON format:
    [
      { "CapacityName": "fabric01sc", "Location": "swedencentral", "SKU": "F2" },
      { "CapacityName": "fabric02ne", "Location": "northeurope",   "SKU": "F2" }
    ]

.EXAMPLE
    # Create everything (resource group + all capacities)
    .\manage-fabric.ps1 -Action create -AdminUpn "admin@contoso.com"

.EXAMPLE
    # Create from an external JSON config file
    .\manage-fabric.ps1 -Action create -AdminUpn "admin@contoso.com" -ConfigFile .\capacities.json

.EXAMPLE
    # Pause a single capacity
    .\manage-fabric.ps1 -Action pause -CapacityName fabric02ne

.EXAMPLE
    # Start all capacities
    .\manage-fabric.ps1 -Action start

.EXAMPLE
    # Scale a specific capacity to F4
    .\manage-fabric.ps1 -Action scale -CapacityName fabric01sc -Sku F4

.EXAMPLE
    # Scale all capacities to F8
    .\manage-fabric.ps1 -Action scale -Sku F8

.EXAMPLE
    # Show status of all capacities
    .\manage-fabric.ps1 -Action status

.EXAMPLE
    # Show status of a specific capacity
    .\manage-fabric.ps1 -Action status -CapacityName fabric01sc
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet("create", "start", "pause", "scale", "status")]
    [string]$Action,

    [string]$CapacityName,

    [ValidateSet("F2", "F4", "F8", "F16", "F32", "F64", "F128", "F256", "F512", "F1024", "F2048")]
    [string]$Sku,

    [string]$AdminUpn,

    [string]$ConfigFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Configuration ────────────────────────────────────────────────────────────
$ResourceGroup = "rg-caf2026-fabric"
$RgLocation    = "swedencentral"

$DefaultCapacities = @(
    @{ CapacityName = "fabric01sc";  Location = "swedencentral"; SKU = "F2" }
    @{ CapacityName = "fabric02ne";  Location = "northeurope";   SKU = "F2" }
    @{ CapacityName = "fabric03wu3"; Location = "westus3";       SKU = "F2" }
    @{ CapacityName = "fabric04we";  Location = "westeurope";    SKU = "F2" }
)

# ── Load configuration ──────────────────────────────────────────────────────
if ($ConfigFile) {
    if (-not (Test-Path $ConfigFile)) {
        Write-Error "Config file not found: $ConfigFile"
    }
    Write-Host "Loading configuration from $ConfigFile" -ForegroundColor Yellow
    $Capacities = Get-Content $ConfigFile -Raw -Encoding UTF8 | ConvertFrom-Json
} else {
    Write-Host "Using built-in default configuration" -ForegroundColor Yellow
    $Capacities = $DefaultCapacities
}

# ── Helper functions ─────────────────────────────────────────────────────────
function Get-TargetCapacities {
    if ($CapacityName) {
        $match = $Capacities | Where-Object { $_.CapacityName -eq $CapacityName }
        if (-not $match) {
            Write-Error "Capacity '$CapacityName' not found. Valid names: $($Capacities.CapacityName -join ', ')"
        }
        return @($match)
    }
    return $Capacities
}

function Ensure-AzFabricExtension {
    $ext = az extension list --query "[?name=='microsoft.fabric'].name" -o tsv 2>$null
    if (-not $ext) {
        Write-Host "Installing Azure CLI 'microsoft.fabric' extension..." -ForegroundColor Yellow
        az extension add --name microsoft.fabric --yes
    }
}

# ── Actions ──────────────────────────────────────────────────────────────────
function Invoke-Create {
    if (-not $AdminUpn) {
        Write-Error "Parameter -AdminUpn is required for the 'create' action."
    }

    Ensure-AzFabricExtension

    # Create resource group
    Write-Host "`n=== Creating Resource Group ===" -ForegroundColor Cyan
    Write-Host "  Name:     $ResourceGroup"
    Write-Host "  Location: $RgLocation"
    az group create --name $ResourceGroup --location $RgLocation --output table
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create resource group." }

    # Create each capacity
    $targets = Get-TargetCapacities
    foreach ($cap in $targets) {
        Write-Host "`n=== Creating Fabric Capacity ===" -ForegroundColor Cyan
        Write-Host "  Name:     $($cap.CapacityName)"
        Write-Host "  Location: $($cap.Location)"
        Write-Host "  SKU:      $($cap.SKU)"
        Write-Host "  Admin:    $AdminUpn"

        az fabric capacity create `
            --resource-group $ResourceGroup `
            --capacity-name $cap.CapacityName `
            --location $cap.Location `
            --sku name="$($cap.SKU)" tier="Fabric" `
            --administration members="['$AdminUpn']" `
            --output table

        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to create capacity '$($cap.CapacityName)'. Continuing..."
        } else {
            Write-Host "  ✓ Created successfully." -ForegroundColor Green
        }
    }
}

function Invoke-Start {
    Ensure-AzFabricExtension
    $targets = Get-TargetCapacities

    foreach ($cap in $targets) {
        Write-Host "`n=== Resuming Capacity: $($cap.CapacityName) ===" -ForegroundColor Cyan
        az fabric capacity resume `
            --resource-group $ResourceGroup `
            --capacity-name $cap.CapacityName `
            --output table

        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to resume capacity '$($cap.CapacityName)'."
        } else {
            Write-Host "  ✓ Resumed." -ForegroundColor Green
        }
    }
}

function Invoke-Pause {
    Ensure-AzFabricExtension
    $targets = Get-TargetCapacities

    foreach ($cap in $targets) {
        Write-Host "`n=== Suspending Capacity: $($cap.CapacityName) ===" -ForegroundColor Cyan
        az fabric capacity suspend `
            --resource-group $ResourceGroup `
            --capacity-name $cap.CapacityName `
            --output table

        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to suspend capacity '$($cap.CapacityName)'."
        } else {
            Write-Host "  ✓ Suspended." -ForegroundColor Green
        }
    }
}

function Invoke-Scale {
    if (-not $Sku) {
        Write-Error "Parameter -Sku is required for the 'scale' action (e.g. -Sku F4)."
    }

    Ensure-AzFabricExtension
    $targets = Get-TargetCapacities

    foreach ($cap in $targets) {
        Write-Host "`n=== Scaling Capacity: $($cap.CapacityName) → $Sku ===" -ForegroundColor Cyan
        az fabric capacity update `
            --resource-group $ResourceGroup `
            --capacity-name $cap.CapacityName `
            --sku name="$Sku" tier="Fabric" `
            --output table

        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to scale capacity '$($cap.CapacityName)'."
        } else {
            Write-Host "  ✓ Scaled to $Sku." -ForegroundColor Green
        }
    }
}

function Invoke-Status {
    Ensure-AzFabricExtension
    $targets = Get-TargetCapacities

    foreach ($cap in $targets) {
        Write-Host "`n=== Status: $($cap.CapacityName) ===" -ForegroundColor Cyan
        $info = az fabric capacity show `
            --resource-group $ResourceGroup `
            --capacity-name $cap.CapacityName `
            --output json 2>&1

        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to get status for '$($cap.CapacityName)'. It may not exist yet."
        } else {
            $parsed = $info | ConvertFrom-Json
            Write-Host "  Name:     $($parsed.name)"
            Write-Host "  Location: $($parsed.location)"
            Write-Host "  SKU:      $($parsed.sku.name)"
            Write-Host "  State:    $($parsed.state)"
        }
    }
}

# ── Main ─────────────────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║   Fabric Capacity Manager – CAF2026  ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════╝`n" -ForegroundColor Magenta

switch ($Action) {
    "create" { Invoke-Create }
    "start"  { Invoke-Start }
    "pause"  { Invoke-Pause }
    "scale"  { Invoke-Scale }
    "status" { Invoke-Status }
}

Write-Host "`n✅ Action '$Action' completed.`n" -ForegroundColor Green
