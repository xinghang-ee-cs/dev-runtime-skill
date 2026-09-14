param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $RunnerArguments
)

$ErrorActionPreference = "Stop"
$runner = Join-Path $PSScriptRoot "run_long_validation.py"
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $runner @RunnerArguments
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $runner @RunnerArguments
} else {
    Write-Error "Python 3 is required but neither 'py' nor 'python' is available."
    exit 127
}
exit $LASTEXITCODE
