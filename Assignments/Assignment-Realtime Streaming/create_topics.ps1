# PowerShell helper to create Kafka topics used by the demo
# Run from the Assignment-Realtime Streaming folder after docker compose up -d

Write-Output "Creating topics: raw-data and predictions"


Write-Output "Topics created (or already exist)."

# PowerShell helper to create Kafka topics used by the demo (local Kafka)
# Usage: set environment variable KAFKA_HOME to your Kafka installation root,
# then run this script from the Assignment-Realtime Streaming folder.

Write-Output "Creating topics: raw-data and predictions (local Kafka)"

$kafkaHome = $env:KAFKA_HOME
if (-not $kafkaHome) {
	Write-Output "ERROR: Please set KAFKA_HOME environment variable to your Kafka installation folder."
	Write-Output "Example: setx KAFKA_HOME 'C:\kafka_2.13-3.5.1' (then re-open PowerShell)"
	exit 1
}

$kafkaTopics = Join-Path $kafkaHome 'bin\windows\kafka-topics.bat'
if (-not (Test-Path $kafkaTopics)) {
	Write-Output "ERROR: kafka-topics.bat not found at $kafkaTopics"
	exit 1
}

;& $kafkaTopics --create --topic raw-data --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
;& $kafkaTopics --create --topic predictions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

Write-Output "Topics created (or already exist)."
