# Appels réels de vérification — tranche 3

Sources : dossiers JSON complets adjacents. Les latences sont celles retournées par Bedrock, en millisecondes. Les jetons sont entrée / sortie. Une ligne représente un appel Converse, y compris les essais refusés par le contrôle en code.

## robert local sans Guardrail

| Agent | Modèle | Identifiant de requête | Jetons entrée | Jetons sortie | Latence ms | Fin / Guardrail |
|---|---|---|---:|---:|---:|---|
| Profileur | `global.amazon.nova-2-lite-v1:0` | `347b16af-eef1-4d9d-baaa-8abeedb7ee5e` | 735 | 124 | 856 | end_turn / absent |
| Sceptique | `global.anthropic.claude-sonnet-5` | `eee21b55-aa77-4bf2-91f3-20629bff67ed` | 1081 | 197 | 3135 | end_turn / absent |
| Rédacteur | `global.anthropic.claude-sonnet-5` | `ec5d6410-c14d-46ec-806e-d8b7268266f7` | 3456 | 442 | 4646 | end_turn / absent |

Total : **3 appels**, **6035 jetons**.

## amira local sans Guardrail

| Agent | Modèle | Identifiant de requête | Jetons entrée | Jetons sortie | Latence ms | Fin / Guardrail |
|---|---|---|---:|---:|---:|---|
| Profileur | `global.amazon.nova-2-lite-v1:0` | `558ab2e7-1d65-4792-93ec-b4df6cd68942` | 729 | 125 | 774 | end_turn / absent |
| Sceptique | `global.anthropic.claude-sonnet-5` | `9ad2a00e-6f51-4636-b78e-d796bba2bd2f` | 1026 | 245 | 3930 | end_turn / absent |
| Rédacteur | `global.anthropic.claude-sonnet-5` | `d9ce0e29-8db9-4002-b23d-679c298beebf` | 3109 | 469 | 5059 | end_turn / absent |

Total : **3 appels**, **5703 jetons**.

## contradictoire local sans Guardrail

| Agent | Modèle | Identifiant de requête | Jetons entrée | Jetons sortie | Latence ms | Fin / Guardrail |
|---|---|---|---:|---:|---:|---|
| Profileur | `global.amazon.nova-2-lite-v1:0` | `2c215bd5-a86c-4e81-9141-bf09ba54cef7` | 751 | 125 | 890 | end_turn / absent |
| Sceptique | `global.anthropic.claude-sonnet-5` | `53567ace-6b93-4c3d-afdc-894f02e67e94` | 1076 | 235 | 3878 | end_turn / absent |
| Rédacteur | `global.anthropic.claude-sonnet-5` | `fc1296c9-c820-4180-bf62-8e519d0f9991` | 3137 | 1267 | 12192 | end_turn / absent |
| Rédacteur | `global.anthropic.claude-sonnet-5` | `20db9e3b-ddd4-476e-9e61-6ad80d09f388` | 3203 | 577 | 5967 | end_turn / absent |

Total : **4 appels**, **10371 jetons**.

## Robert local Guardrail corrigé

| Agent | Modèle | Identifiant de requête | Jetons entrée | Jetons sortie | Latence ms | Fin / Guardrail |
|---|---|---|---:|---:|---:|---|
| Profileur | `global.amazon.nova-2-lite-v1:0` | `27fb5400-cde4-4727-a8f1-6654b43f0ba2` | 735 | 124 | 755 | end_turn / absent |
| Sceptique | `global.anthropic.claude-sonnet-5` | `3e0f35fa-19b3-4527-b27c-063c991683cb` | 1081 | 211 | 3608 | end_turn / absent |
| Rédacteur | `global.anthropic.claude-sonnet-5` | `fde12caa-8814-4fa1-a16d-589c1ea4ce5a` | 6361 | 521 | 6678 | end_turn / configure |
| Rédacteur | `global.anthropic.claude-sonnet-5` | `70694299-7553-4d29-8791-129eeaf14142` | 6417 | 609 | 7388 | end_turn / configure |

Total : **4 appels**, **16059 jetons**.

## Robert public Lambda

| Agent | Modèle | Identifiant de requête | Jetons entrée | Jetons sortie | Latence ms | Fin / Guardrail |
|---|---|---|---:|---:|---:|---|
| Profileur | `global.amazon.nova-2-lite-v1:0` | `839f7abd-ae30-406d-9e80-72509112f2f0` | 735 | 124 | 796 | end_turn / absent |
| Sceptique | `global.anthropic.claude-sonnet-5` | `974e5068-27a4-4451-a91d-0efc02b9aafe` | 1081 | 219 | 3437 | end_turn / absent |
| Rédacteur | `global.anthropic.claude-sonnet-5` | `16278046-bfd1-484f-8c1b-a44fc7e71247` | 6361 | 539 | 6499 | end_turn / configure |
| Rédacteur | `global.anthropic.claude-sonnet-5` | `b7ff6a7d-2cf9-4b86-81c2-971ba2ff7c14` | 6415 | 613 | 6729 | end_turn / configure |

Total : **4 appels**, **16087 jetons**.

## Conseil bloqué, Rédacteur réel

| Agent | Modèle | Identifiant de requête | Jetons entrée | Jetons sortie | Latence ms | Fin / Guardrail |
|---|---|---|---:|---:|---:|---|
| Rédacteur | `global.anthropic.claude-sonnet-5` | `2a3210a5-4b7e-44d2-9cbc-2733a949fcb7` | 0 | 0 | 419 | guardrail_intervened / bloque |

Total : **1 appels**, **0 jetons**.

## Diagnostics conservés avant correction du raccordement Guardrail

`guardrail-normal/robert-bedrock.json`, `guardrail-conseil.json` et `guardrail-diagnostic.json` conservent les essais initiaux : blocage du Profileur et requête d’ancrage trop longue. Ils ne décrivent pas le code publié. Aucun appel de diagnostic n’est présenté comme une validation réussie.
