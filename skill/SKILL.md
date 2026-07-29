# mc-iclone8-ui-mcp — skill expert

Utiliser ce serveur uniquement pour des workflows **visibles, locaux et vérifiables** dans iClone 8.

## Règles d'appel

1. Appeler `ui.inspect_application`.
2. Si le résultat est `blocked`, arrêter et demander à l'utilisateur d'ouvrir iClone 8.
3. Appeler `ui.capture_screen` avant une séquence à risque.
4. Décrire une seule action UI par étape et vérifier l'état après chaque étape.
5. Appeler `workflow.stop_all` à la demande de l'utilisateur ou dès qu'une fenêtre inattendue apparaît.
6. Ne jamais annoncer le succès sans capture, lecture UIA ou preuve de fichier produite.

## Prompts d'exemple

```text
Inspecte iClone 8. Si sa fenêtre est détectée, capture l'état avant et lis uniquement l'état visible.
N'effectue aucune modification.
```

```text
Prépare un workflow de création de path dans iClone 8, mais arrête-toi avant le premier clic
et indique les contrôles visibles et la preuve attendue à chaque étape.
```

Les actions de production ne sont pas encore disponibles dans le lot 0. Voir `docs/limitations.md`.
