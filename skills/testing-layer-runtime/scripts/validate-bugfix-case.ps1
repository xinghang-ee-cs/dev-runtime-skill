param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ValidatorArguments
)

$ErrorActionPreference = "Stop"
$validator = Join-Path $PSScriptRoot "validate_bugfix_case.py"
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $validator @ValidatorArguments
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $validator @ValidatorArguments
} else {
    Write-Error "Python 3 is required but neither 'py' nor 'python' is available."
    exit 127
}
exit $LASTEXITCODE
