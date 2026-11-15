# Enregistre les identifiants AWS temporaires du datathon dans le profil « datathon ».
# Étape 1 : dans le même terminal PowerShell, colle le bloc « Windows (PowerShell) »
#           de Workshop Studio (les lignes $Env:AWS_...).
# Étape 2 : colle ce script (ou exécute-le). Il lit les variables du terminal et
#           écrit ~/.aws/credentials. Aucune clé n'est stockée dans le dépôt.

foreach ($v in "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN") {
    if (-not (Test-Path "Env:$v")) {
        Write-Host "Il manque $v : colle d'abord le bloc PowerShell de Workshop Studio dans ce terminal."
        return
    }
}
$dossier = Join-Path $HOME ".aws"
New-Item -ItemType Directory -Force $dossier | Out-Null
@"
[datathon]
aws_access_key_id = $env:AWS_ACCESS_KEY_ID
aws_secret_access_key = $env:AWS_SECRET_ACCESS_KEY
aws_session_token = $env:AWS_SESSION_TOKEN
"@ | Set-Content -Encoding ascii (Join-Path $dossier "credentials")
@"
[profile datathon]
region = us-east-1
"@ | Set-Content -Encoding ascii (Join-Path $dossier "config")
Write-Host "Identifiants enregistrés dans $dossier\credentials (profil datathon, région us-east-1)."
