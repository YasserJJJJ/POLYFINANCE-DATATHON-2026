# R03 — Cadres d'adéquation (KYC) et profilage : ce qui change une décision

Recherche déléguée (sous-agent researcher), 2026-11-14. **Rapport partiel** : PDF ESMA et ACVM illisibles par l'outil, EUR-Lex vide. Niveaux : TL texte lu ; RS résumé ou extrait secondaire ; NV non vérifié. Ne citer devant le jury que les éléments TL, ou après relecture du texte primaire.

## Constats

| Cadre | Constat | Accès |
|---|---|---|
| [FINRA Rule 2111](https://www.finra.org/rules-guidance/rulebooks/finra-rules/2111) | Profil : situation et besoins financiers, autres placements, horizon, besoins de liquidité, tolérance au risque, expérience ; diligence raisonnable pour obtenir et analyser ces facteurs (SM .04) | TL partiel |
| ACVM, Règlement 31-103 (art. 13.2, 13.3) et Avis 31-368 | Distinction explicite entre tolérance au risque (attitude) et capacité de perte (aptitude objective) ; des formulaires les fusionnaient. Une instruction du client ne remplace pas l'analyse d'adéquation ; proposer une alternative convenable et expliquer | RS ([FAQ ACVM](https://www.securities-administrators.ca/wp-content/uploads/2023/12/CFRsFAQsDecember2023EN.pdf)) |
| ESMA35-43-3172 (orientations 2022) et Q&R ESMA35-43-349 | Capacité à comprendre et à supporter financièrement les pertes ; signaler une évaluation faite sans information complète. Transaction à l'initiative du client contre l'avis : avertissement, hors protection d'adéquation | RS |
| Règl. délégué (UE) 2021/1253 | Préférences de durabilité : sujet confirmé, contenu non lu | NV |
| FSA 2011, FG11/5 « Assessing suitability » | Beaucoup de firmes négligent la capacité de perte | RS |

**Empirique**
- Klement 2015, *Investor Risk Profiling: An Overview*, CFA Institute Research Foundation, doi:10.2470/rfbr.v1.n1.1 — questionnaires jugés très peu fiables par la page de la fondation (TL partiel) ; Crossref sans métadonnées complètes (**à revérifier**).
- Grable et Lytton 1999, *Financial risk tolerance revisited*, Financial Services Review, [doi:10.1016/S1057-0810(99)00041-4](https://doi.org/10.1016/S1057-0810(99)00041-4) (vérifié Crossref) — échelle à 13 items jugée fiable (RS). Contradiction avec Klement non tranchée.

## Conséquences retenues pour le prototype

Schéma de profil minimal, chaque champ avec statut `déclaré` / `hypothèse` / `inconnu` :
horizon ; besoins de liquidité ; **capacité de perte** (distincte de la tolérance) ; tolérance déclarée ; rendement visé ; avoirs existants et concentration ; expérience ; préférences de durabilité ; **origine de la demande** (analyse proposée par l'outil ou initiative de la personne) ; fiabilité de chaque champ.

Règle de clarification (conception de l'équipe, non sourcée) :
1. Demander si le champ manquant peut faire basculer la conclusion (ex. capacité de perte de Robert) ou si deux champs se contredisent.
2. Avancer avec une hypothèse affichée et modifiable si le champ est utile sans changer le sens de la conclusion.
3. Présenter des scénarios si plusieurs inconnues subsistent ou sans réponse.
4. Demande incohérente avec le profil : ne pas acquiescer ; montrer l'écart chiffré ; proposer des alternatives ; consigner l'initiative de la personne.

## Reste à lire

ESMA 3172 et Instruction générale 31-103CP (texte intégral), EUR-Lex 2021/1253, FG11/5, CFA IPS, règles OCRI.
