# Import indépendant de l’implémentation Codex

Copie du projet `Datathon_AlphaForge`, comprenant les modifications locales non commitées (dont Folio), destinée à la comparaison puis à la fusion des implémentations. Aucun composant de l’application à la racine n’a été remplacé. Ceci est un import de fichiers, pas une fusion fonctionnelle.

- Code, tests, données du défi, prototypes, recherches et preuves visuelles sont conservés dans leur arborescence.
- Voir [README du projet](README.md) pour son fonctionnement et son installation; exécuter les commandes depuis ce dossier.
- [Manifeste](IMPORT_MANIFEST.json) : origine, empreinte SHA-256 de chaque fichier et liste des exclusions.
- Les environnements, identifiants et états locaux ne sont pas transférés. Les liens du README vers des dossiers de démonstration locaux peuvent nécessiter de recréer ces dossiers. Les accès AWS doivent être configurés sur la machine destinataire.
- Le lanceur AWS personnel, une archive dérivée et quatre collectes présentant des chaînes sensibles potentielles sont exclus. Les originaux restent intacts sur le Mac. Certaines références documentaires vers ces exclusions restent donc uniquement disponibles dans la copie source.
- Les chemins absolus présents dans les rapports historiques décrivent la machine d’origine; ils n’ont pas été réécrits pour conserver les preuves telles quelles.

Contrôle de cet import : identité des empreintes de tous les fichiers copiés. L’import ne constitue pas une nouvelle validation fonctionnelle ni scientifique de leurs contenus. Aucun serveur, déploiement ou appel d’inférence n’a été lancé.
