<#
.SYNOPSIS
    Creates or deletes Microsoft Fabric workspaces using the Fabric CLI (fab).

.DESCRIPTION
    For each entry in the configuration, the script can:
      - create: Create a workspace, assign capacity, add Admin, set Spark settings
      - delete: Remove the workspace

.PARAMETER Action
    The operation to perform: create or delete. Defaults to create.

.PARAMETER ConfigFile
    Path to a JSON file with workspace definitions (see sample below).
    If omitted, uses the default $Workspaces array defined in the script.

.EXAMPLE
    # Create workspaces using built-in configuration
    .\create-workspaces.ps1

.EXAMPLE
    # Create workspaces from an external JSON config file
    .\create-workspaces.ps1 -ConfigFile .\workspaces.json

.EXAMPLE
    # Delete all workspaces defined in a JSON config file
    .\create-workspaces.ps1 -Action delete -ConfigFile .\workspaces.json

    # workspaces.json format:
    # [
    #   { "user_name": "alice@contoso.com", "workspace_name": "ws-alice", "capacity_name": "fabric01sc" },
    #   { "user_name": "bob@contoso.com",   "workspace_name": "ws-bob",   "capacity_name": "fabric02ne" }
    # ]
#>

[CmdletBinding()]
param(
    [ValidateSet("create", "delete")]
    [string]$Action = "create",

    [string]$ConfigFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

# -- Default configuration (edit here or supply a JSON file via -ConfigFile) ---
$DefaultWorkspaces = @(
    @{ user_name = "user1@contoso.com"; workspace_name = "ws-user1"; capacity_name = "fabric01sc" }
    @{ user_name = "user2@contoso.com"; workspace_name = "ws-user2"; capacity_name = "fabric02ne" }
    @{ user_name = "user3@contoso.com"; workspace_name = "ws-user3"; capacity_name = "fabric03wu3" }
    @{ user_name = "user4@contoso.com"; workspace_name = "ws-user4"; capacity_name = "fabric04we" }
)

# -- Load configuration -------------------------------------------------------
if ($ConfigFile) {
    if (-not (Test-Path $ConfigFile)) {
        Write-Error "Config file not found: $ConfigFile"
    }
    Write-Host "Loading configuration from $ConfigFile" -ForegroundColor Yellow
    $Workspaces = Get-Content $ConfigFile -Raw -Encoding UTF8 | ConvertFrom-Json
} else {
    Write-Host "Using built-in default configuration" -ForegroundColor Yellow
    $Workspaces = $DefaultWorkspaces
}

# -- Spark settings (max nodes = 1) -------------------------------------------
$SparkNodeCount = 1

# -- Helper: resolve user UPN to Entra object ID ------------------------------
function Get-UserObjectId {
    param([string]$Upn)
    $objectId = az ad user show --id $Upn --query id -o tsv 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Could not resolve object ID for '$Upn'. Skipping ACL assignment."
        return $null
    }
    return $objectId.Trim()
}

# -- Main ----------------------------------------------------------------------
Write-Host "`n==============================================" -ForegroundColor Magenta
Write-Host "   Fabric Workspace Manager - CAF2026"          -ForegroundColor Magenta
Write-Host "==============================================" -ForegroundColor Magenta

function Invoke-CreateWorkspaces {
    foreach ($entry in $Workspaces) {
        $userName      = $entry.user_name
        $workspaceName = $entry.workspace_name
        $capacityName  = $entry.capacity_name

        Write-Host "`n----------------------------------------------" -ForegroundColor DarkGray
        Write-Host "  User:      $userName"
        Write-Host "  Workspace: $workspaceName"
        Write-Host "  Capacity:  $capacityName"
        Write-Host "----------------------------------------------" -ForegroundColor DarkGray

        # 1. Create workspace with capacity
        Write-Host "`n  [1/3] Creating workspace '$workspaceName' on capacity '$capacityName'..." -ForegroundColor Cyan
        fab mkdir "$workspaceName.Workspace" -P "capacityName=$capacityName" 2>&1 | ForEach-Object { Write-Host "        $_" }
        if ($LASTEXITCODE -ne 0) {
            # Workspace may already exist - try reassigning capacity
            Write-Warning "  Create failed. Attempting to assign capacity to existing workspace..."
            fab assign ".capacities/$capacityName.Capacity" -W "$workspaceName.Workspace" 2>&1 | ForEach-Object { Write-Host "        $_" }
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "  Failed to create or assign capacity for '$workspaceName'. Skipping..."
                continue
            }
            Write-Host "        Capacity reassigned." -ForegroundColor Green
        } else {
            Write-Host "        Done." -ForegroundColor Green
        }

        # 2. Add user as Admin
        Write-Host "  [2/3] Adding '$userName' as Admin..." -ForegroundColor Cyan
        $objectId = Get-UserObjectId -Upn $userName
        if ($objectId) {
            fab acl set "$workspaceName.Workspace" -I $objectId -R Admin -f 2>&1 | ForEach-Object { Write-Host "        $_" }
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "  Failed to set ACL for '$userName'."
            } else {
                Write-Host "        Done." -ForegroundColor Green
            }
        }

        # 3. Set Spark starter pool max nodes
        Write-Host "  [3/3] Setting Spark max nodes to $SparkNodeCount..." -ForegroundColor Cyan
        fab set "$workspaceName.Workspace" -q sparkSettings.pool.starterPool.maxNodeCount -i $SparkNodeCount -f 2>&1 | ForEach-Object { Write-Host "        $_" }
        fab set "$workspaceName.Workspace" -q sparkSettings.pool.starterPool.maxExecutors -i $SparkNodeCount -f 2>&1 | ForEach-Object { Write-Host "        $_" }
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "  Failed to set Spark settings."
        } else {
            Write-Host "        Done." -ForegroundColor Green
        }
    }
}

function Invoke-DeleteWorkspaces {
    Write-Host "`n  Deleting $($Workspaces.Count) workspace(s)..." -ForegroundColor Yellow

    foreach ($entry in $Workspaces) {
        $workspaceName = $entry.workspace_name

        Write-Host "`n=== Deleting Workspace: $workspaceName ===" -ForegroundColor Cyan
        fab rm "$workspaceName.Workspace" -f 2>&1 | ForEach-Object { Write-Host "        $_" }

        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to delete workspace '$workspaceName'. It may not exist."
        } else {
            Write-Host "  ✓ Deleted." -ForegroundColor Green
        }
    }
}

switch ($Action) {
    "create" { Invoke-CreateWorkspaces }
    "delete" { Invoke-DeleteWorkspaces }
}

Write-Host "`n==============================================`n" -ForegroundColor Magenta
Write-Host "Action '$Action' complete.`n" -ForegroundColor Green
