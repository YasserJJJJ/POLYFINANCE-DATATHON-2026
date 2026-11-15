# Lance l'API et l'interface, chacune dans sa fenêtre, puis ouvre le navigateur.
# Prérequis (une seule fois) : python -m venv .venv ; .venv\Scripts\pip install -r backend\requirements.txt ;
#                             cd frontend ; npm install
# Agents IA : identifiants AWS dans le profil « datathon » (voir infra\enregistrer_identifiants.ps1).
# Sans identifiants, l'application marche quand même, en mode hors ligne.

$racine = $PSScriptRoot
$env:AWS_PROFILE = "datathon"
$env:AWS_REGION = "us-east-1"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$racine\backend'; ..\.venv\Scripts\python -m uvicorn api:app --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$racine\frontend'; npm run dev"
Start-Sleep -Seconds 4
Start-Process "http://localhost:5173"
