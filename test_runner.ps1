<#
.SYNOPSIS
Test runner for isolated module testing in AstroToon project

.DESCRIPTION
Allows testing individual components without starting dependent services
#>

param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("planets", "script", "tts", "animation")]
    [string]$module
)

$basePath = "d:\AI\nebles"

# Module-specific test configurations
$testConfig = @{
    planets = @{
        Image = "planets-processor:test"
        Command = @("pytest", "tests/")
        BuildContext = "planets/"
        Dockerfile = "planets/Dockerfile"
        Volumes = @(
            "-v", "${basePath}\planets\tests:/app/tests",
            "-v", "${basePath}\planets\planet-alignments:/app/planet-alignments"
        )
    }
    llm_script = @{
        Image = "llm-script-test"  
        Command = @("python", "script_generator.py", "--input-mock", "test_mock.json")
        Volumes = @("${basePath}/ollama-script/test_mock.json:/app/test_mock.json")
    }
    tts = @{
        Image = "tts-test"
        Command = @("python", "-m", "pytest", "tests/")
        Volumes = @("${basePath}/tts/tests:/app/tests")
    }
    animation = @{
        Image = "animation-test"
        Command = @("node", "validate_scene.js", "--test")
        Volumes = @("${basePath}/animation/test_scenes:/app/test_scenes")
    }
}

# Build test image
docker build `
    -t $testConfig[$module].Image `
    -f $testConfig[$module].Dockerfile `
    $testConfig[$module].BuildContext `
    --no-cache

# Run isolated test container
# Validate required files exist
if (-not (Test-Path $testConfig[$module].Dockerfile)) {
    Write-Error "Missing Dockerfile: $($testConfig[$module].Dockerfile)"
    exit 1
}

$image = "${module}-processor:test"
$volumes = $testConfig[$module].Volumes
$command = $testConfig[$module].Command

docker run --rm `
    -v "${basePath}\batch:/app/batch" `
    @volumes `
    $image `
    @command

if ($LASTEXITCODE -ne 0) {
    Write-Error "Tests failed for $module module"
    exit 1
}

Write-Host "✅ $module tests completed successfully"