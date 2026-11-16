"""Vérification de trois affirmations du comparatif des supports, pour SQLite (bibliothèque standard).

    python3 research/experiences/technique/dossier_maison/verif_sqlite.py

Ce n'est pas un portage du dossier : seulement de quoi ne pas affirmer de mémoire.
"""
import os
import sqlite3
import tempfile

chemin = os.path.join(tempfile.mkdtemp(prefix="dossier_maison_sqlite_"), "dossier.db")
a, b = sqlite3.connect(chemin), sqlite3.connect(chemin)  # deux écrivains
a.execute("PRAGMA journal_mode=WAL")
a.executescript("""
CREATE TABLE journal (branche TEXT, n INTEGER, prolonge TEXT, evenement TEXT, PRIMARY KEY (branche, n));
CREATE TRIGGER journal_sans_modification BEFORE UPDATE ON journal BEGIN SELECT RAISE(ABORT, 'ajout seul'); END;
CREATE TRIGGER journal_sans_suppression BEFORE DELETE ON journal BEGIN SELECT RAISE(ABORT, 'ajout seul'); END;
CREATE TABLE derive (piece TEXT, entree TEXT);
""")
a.execute("INSERT INTO journal VALUES ('principale', 0, NULL, '{}')")
a.execute("INSERT INTO journal VALUES ('principale', 1, 'h0', '{\"de\": \"a\"}')")
a.commit()

try:  # 1. la seconde écriture au même rang d'une branche est refusée par le moteur
    b.execute("INSERT INTO journal VALUES ('principale', 1, 'h0', '{\"de\": \"b\"}')")
    b.commit()
    raise SystemExit("ÉCHEC : seconde écriture acceptée")
except sqlite3.IntegrityError as erreur:
    print("1. seconde écriture au même rang refusée :", erreur)
    b.rollback()  # sans cela, l'écrivain refusé garde le verrou et bloque les autres (constaté au premier passage)

for requete in ("UPDATE journal SET evenement = '{}' WHERE n = 0", "DELETE FROM journal WHERE n = 0"):
    try:  # 2. l'ajout seul n'est pas natif : il faut des déclencheurs, et ils tiennent
        a.execute(requete)
        raise SystemExit(f"ÉCHEC : {requete}")
    except sqlite3.DatabaseError as erreur:
        assert "ajout seul" in str(erreur), f"refus venu d'ailleurs que du déclencheur : {erreur}"
        print("2.", requete.split()[0], "refusé par déclencheur :", erreur)

a.executemany("INSERT INTO derive VALUES (?, ?)", [("plan", "horizon"), ("calculs", "plan"), ("objections", "calculs"),
                                                  ("restitution", "objections"), ("restitution", "prenom")])
aval = sorted(r[0] for r in a.execute(
    "WITH RECURSIVE aval(p) AS (SELECT piece FROM derive WHERE entree = 'horizon' "
    "UNION SELECT piece FROM derive JOIN aval ON entree = p) SELECT p FROM aval"))
assert aval == ["calculs", "objections", "plan", "restitution"], aval
print("3. aval de « horizon » en une requête récursive :", aval)
print("SQLite", sqlite3.sqlite_version, "; module sqlite3 de la bibliothèque standard")
