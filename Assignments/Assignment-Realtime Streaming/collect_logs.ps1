<#
collect_logs.ps1
Prints the last lines of the faust/producer/consumer logs to the console for quick verification.
#>

$base = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $base

Write-Output "--- faust.log (last 100 lines) ---"
if (Test-Path faust.log) { Get-Content faust.log -Tail 100 } else { Write-Output "faust.log not found" }

Write-Output "--- producer.log (last 50 lines) ---"
if (Test-Path producer.log) { Get-Content producer.log -Tail 50 } else { Write-Output "producer.log not found" }

Write-Output "--- consumer.log (last 50 lines) ---"
if (Test-Path consumer.log) { Get-Content consumer.log -Tail 50 } else { Write-Output "consumer.log not found" }

Pop-Location
