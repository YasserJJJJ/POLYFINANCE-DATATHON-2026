"""Le script de vérification ne plante pas sous Windows et explique l'échec (aucun appel réseau)."""
import os
import subprocess
import sys
from pathlib import Path


def test_sans_identifiants_message_clair_sans_trace_meme_en_cp1252(tmp_path):
    vide = tmp_path / "vide"
    vide.write_text("")
    env = {**os.environ, "AWS_PROFILE": "profil_inexistant_audit", "AWS_CONFIG_FILE": str(vide),
           "AWS_SHARED_CREDENTIALS_FILE": str(vide), "PYTHONIOENCODING": "cp1252"}
    for cle in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
        env.pop(cle, None)
    r = subprocess.run([sys.executable, "verifier_bedrock.py"], cwd=Path(__file__).parents[1], env=env,
                       capture_output=True, timeout=60)
    sortie = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    assert r.returncode == 1, sortie
    assert "ÉCHEC identifiants AWS" in sortie and "Traceback" not in sortie
