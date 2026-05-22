<#
run_demo.ps1
Automates starting Kafka (docker compose), creating topics, and launching
Faust worker, producer, and consumer in separate PowerShell windows. Logs are
saved to faust.log, producer.log, consumer.log in the same folder.

Run this script from the assignment folder after Docker Desktop is installed.
#>


$base = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $base

Write-Output "Starting local Kafka processes (requires KAFKA_HOME environment variable)..."

$kafkaHome = $env:KAFKA_HOME
if (-not $kafkaHome) {
    Write-Output "ERROR: Please set KAFKA_HOME environment variable to your Kafka installation folder before running this script."
    Write-Output "Example: setx KAFKA_HOME 'C:\kafka_2.13-3.5.1' (then re-open PowerShell)"
    Pop-Location
    exit 1
}

$zkScript = Join-Path $kafkaHome 'bin\windows\zookeeper-server-start.bat'
$zkConf = Join-Path $kafkaHome 'config\zookeeper.properties'
$kafkaScript = Join-Path $kafkaHome 'bin\windows\kafka-server-start.bat'
$kafkaConf = Join-Path $kafkaHome 'config\server.properties'

Write-Output "Launching Zookeeper (new window)..."
Start-Process -FilePath "powershell" -ArgumentList @(
    '-NoExit',
    '-Command',
    "& `"$zkScript`" `"$zkConf`""
)

Start-Sleep -Seconds 2

Write-Output "Launching Kafka broker (new window)..."
Start-Process -FilePath "powershell" -ArgumentList @(
    '-NoExit',
    '-Command',
    "& `"$kafkaScript`" `"$kafkaConf`""
)

Start-Sleep -Seconds 4

Write-Output "Creating topics..."
& "$base\create_topics.ps1"

Write-Output "Launching Faust worker (new window)..."
Start-Process -FilePath "powershell" -ArgumentList @(
    '-NoExit',
    '-Command',
    "cd `"$base`"; faust -A faust_app worker -l info *>&1 | Tee-Object -FilePath faust.log"
)

Start-Sleep -Seconds 2

Write-Output "Launching Producer (new window)..."
Start-Process -FilePath "powershell" -ArgumentList @(
    '-NoExit',
    '-Command',
    "cd `"$base`"; python producer.py *>&1 | Tee-Object -FilePath producer.log"
)

Start-Sleep -Seconds 1

Write-Output "Launching Consumer (new window)..."
Start-Process -FilePath "powershell" -ArgumentList @(
    '-NoExit',
    '-Command',
    "cd `"$base`"; python consumer.py *>&1 | Tee-Object -FilePath consumer.log"
)

Write-Output "Demo launched. Check faust.log, producer.log, consumer.log in $base"
Pop-Location
