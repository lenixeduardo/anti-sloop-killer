[CmdletBinding()]
param(
    [ValidateSet('codex','claude','cursor','agents','all')][string]$Agent = 'codex',
    [ValidateSet('project','global')][string]$Scope = 'project',
    [string]$ProjectPath = '.',
    [switch]$Force,
    [switch]$DryRun,
    [switch]$Verify
)
$ErrorActionPreference = 'Stop'
$installer = Join-Path $PSScriptRoot 'install.py'
if (Get-Command py -ErrorAction SilentlyContinue) {
    $python = 'py'
    $argsList = @('-3', $installer)
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $python = 'python'
    $argsList = @($installer)
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $python = 'python3'
    $argsList = @($installer)
} else {
    Write-Error 'Python 3 nao encontrado. Instale Python 3 antes de continuar.'
    exit 127
}
$argsList += @('--agent', $Agent, '--scope', $Scope, '--project', $ProjectPath)
if ($Force) { $argsList += '--force' }
if ($DryRun) { $argsList += '--dry-run' }
if ($Verify) { $argsList += '--verify' }
& $python @argsList
exit $LASTEXITCODE
