# rt-docker.ps1
#
# Wrapper for RazTodo that delegates `rt` commands to a persistent Docker
# container named "raztodo" so you can use the tool without installing it
# on your host machine.
#
# Usage (PowerShell):
#
#   Import-Module /path/to/raztodo/docker/rt-docker.ps1
#
# To make it available in every new PowerShell session, add that line to
# your PowerShell profile (see $PROFILE). Then use `rt` as usual. When
# imported, rt always runs inside the container (it is started on demand if
# it is not already running):
#
#   rt add "Prepare weekly groceries" --priority H
#   rt list
#   rt done 1
#
# Container lifecycle management:
#
#   Start-RtDocker       # create (if needed) and start the container
#   Stop-RtDocker        # stop and remove the container
#   Get-RtDockerStatus   # show whether the container is running
#   Invoke-RtDocker      # manage lifecycle via subcommand: start|stop|status|rebuild
#
# Configuration (environment variables, all optional):
#   RAZTODO_DOCKER_IMAGE       Image name (default: raztodo:local)
#   RAZTODO_DOCKER_CONTAINER   Container name (default: raztodo)
#   RAZTODO_DATA_DIR           Host data directory mounted at /data (default: $HOME\raztodo-data)

$script:RtDockerProjectDir = Split-Path (Split-Path $PSCommandPath -Parent) -Parent
$script:RtDockerImage = if ($env:RAZTODO_DOCKER_IMAGE)   { $env:RAZTODO_DOCKER_IMAGE }   else { "raztodo:local" }
$script:RtDockerContainer = if ($env:RAZTODO_DOCKER_CONTAINER) { $env:RAZTODO_DOCKER_CONTAINER } else { "raztodo" }
$script:RtDataDir = if ($env:RAZTODO_DATA_DIR) { $env:RAZTODO_DATA_DIR } else { Join-Path $HOME "raztodo-data" }

function Get-RtDockerRunning {
    $names = docker ps --format "{{.Names}}"
    $names -contains $script:RtDockerContainer
}

function Get-RtDockerExists {
    $names = docker ps -a --format "{{.Names}}"
    $names -contains $script:RtDockerContainer
}

function Start-RtDocker {
    if (Get-RtDockerRunning) {
        Write-Output "RazTodo container `"$($script:RtDockerContainer)`" is already running."
        return 0
    }

    $imageExists = docker image inspect $script:RtDockerImage 2>$null
    if (-not $imageExists) {
        Write-Error "Image `"$($script:RtDockerImage)`" not found. Build it first:"
        Write-Error "  docker build -t $($script:RtDockerImage) $($script:RtDockerProjectDir)"
        return 1
    }

    if (Get-RtDockerExists) {
        docker start $script:RtDockerContainer | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to start container `"$($script:RtDockerContainer)`"."
            return 1
        }
        Write-Output "Started RazTodo container `"$($script:RtDockerContainer)`"."
        return 0
    }

    New-Item -ItemType Directory -Force -Path $script:RtDataDir | Out-Null
    docker run -d `
        --name $script:RtDockerContainer `
        -v "$($script:RtDataDir):/data" `
        --entrypoint sleep `
        $script:RtDockerImage `
        infinity | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create container `"$($script:RtDockerContainer)`"."
        return 1
    }

    Write-Output "Created and started RazTodo container `"$($script:RtDockerContainer)`"."
    Write-Output "Database is persisted at $($script:RtDataDir)\tasks.db"
    return 0
}

function Stop-RtDocker {
    if (Get-RtDockerExists) {
        docker rm -f $script:RtDockerContainer | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to remove container `"$($script:RtDockerContainer)`"."
            return 1
        }
        Write-Output "Stopped and removed RazTodo container `"$($script:RtDockerContainer)`"."
    } else {
        Write-Output "RazTodo container `"$($script:RtDockerContainer)`" does not exist."
    }
}

function Get-RtDockerStatus {
    if (Get-RtDockerRunning) {
        Write-Output "RazTodo container `"$($script:RtDockerContainer)`" is running."
        Write-Output "Host data directory: $($script:RtDataDir)"
    } else {
        Write-Output "RazTodo container `"$($script:RtDockerContainer)`" is not running."
    }
}

function Invoke-RtDockerRebuild {
    Stop-RtDocker | Out-Host
    docker build `
        -t $script:RtDockerImage `
        $script:RtDockerProjectDir
    if ($LASTEXITCODE -ne 0) { return 1 }
    Start-RtDocker | Out-Host
}

function Invoke-RtDocker {
    param(
        [Parameter(Position = 0)]
        [ValidateSet("start", "stop", "status", "rebuild")]
        [string]$Command = "status"
    )
    switch ($Command) {
        "start"   { Start-RtDocker }
        "stop"    { Stop-RtDocker }
        "status"  { Get-RtDockerStatus }
        "rebuild" { Invoke-RtDockerRebuild }
    }
}

function rt {
    if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is required to run raztodo via the $($script:RtDockerImage) container but was not found."
        Write-Error "Install Docker first, or install raztodo natively (pipx install raztodo)."
        return 1
    }

    if (-not (Get-RtDockerRunning)) {
        Start-RtDocker | Out-Host
        if (-not (Get-RtDockerRunning)) { return 1 }
    }

    $execArgs = @("exec", "-i")
    if ([Console]::IsOutputRedirected -eq $false) { $execArgs += "-t" }
    $execArgs += @($script:RtDockerContainer, "rt") + @args
    docker exec @execArgs
    return $LASTEXITCODE
}

Export-ModuleMember -Function rt, Start-RtDocker, Stop-RtDocker, Get-RtDockerStatus, Invoke-RtDocker
