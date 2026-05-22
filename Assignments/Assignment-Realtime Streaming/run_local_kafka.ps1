<#
run_local_kafka.ps1
Starts local Zookeeper and Kafka broker using a Kafka installation pointed to by KAFKA_HOME.
This script opens two new PowerShell windows (ZK and Kafka) and leaves them running.

Usage: set environment variable KAFKA_HOME to your Kafka installation root,
then run this script from the assignment folder.
#>

$kafkaHome = $env:KAFKA_HOME
if (-not $kafkaHome) {
    Write-Output "ERROR: Please set KAFKA_HOME environment variable to your Kafka installation folder."
    Write-Output "Example: setx KAFKA_HOME 'C:\kafka_2.13-3.5.1' (then re-open PowerShell)"
    exit 1
}

$zkScript = Join-Path $kafkaHome 'bin\windows\zookeeper-server-start.bat'
$zkConf = Join-Path $kafkaHome 'config\zookeeper.properties'
$kafkaScript = Join-Path $kafkaHome 'bin\windows\kafka-server-start.bat'
$kafkaConf = Join-Path $kafkaHome 'config\server.properties'

if (-not (Test-Path $zkScript)) { Write-Output "zookeeper-server-start.bat not found at $zkScript"; exit 1 }
if (-not (Test-Path $kafkaScript)) { Write-Output "kafka-server-start.bat not found at $kafkaScript"; exit 1 }

Write-Output "Starting Zookeeper in new window..."
Start-Process -FilePath "powershell" -ArgumentList @(
    '-NoExit',
    '-Command',
    "& `"$zkScript`" `"$zkConf`""
)

Start-Sleep -Seconds 2

Write-Output "Starting Kafka broker in new window..."
Start-Process -FilePath "powershell" -ArgumentList @(
    '-NoExit',
    '-Command',
    "& `"$kafkaScript`" `"$kafkaConf`""
)

Write-Output "Zookeeper and Kafka broker launched."
