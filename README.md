# mc-iclone8-ui-mcp

Serveur MCP local pour piloter **l'interface visible d'iClone 8** comme un utilisateur humain.

> État actuel : lot 0, lecture seule. Le serveur sait inspecter la fenêtre iClone 8, gérer le focus sans action destructive, capturer l'écran, lire les métadonnées Win32 accessibles et interrompre un workflow. Aucune action de production n'est déclarée réussie sans vérification.

## Principes

- Les actions de production passent par `ui_driver`, jamais par RLPy.
- RLPy n'est pas importé dans ce projet.
- Les coordonnées seules sont interdites : les futurs sélecteurs devront combiner titre, rôle, nom accessible et position comme dernier recours.
- Les résultats MCP ont toujours le contrat documenté dans [`docs/protocol.md`](docs/protocol.md).
- Le serveur reste local : transport stdio uniquement, sans appel réseau.

## Installation

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

Les dépendances UI sont optionnelles. Le socle Win32 fonctionne avec la bibliothèque standard ; `Pillow` améliore les captures d'écran.

## Lancement

```powershell
python -m mc_iclone8_ui_mcp
```

Le processus utilise JSON-RPC sur stdin/stdout. Les logs vont sur stderr.

## Outils MCP read-only

- `ui.inspect_application` : détecte les fenêtres iClone 8 visibles et rapporte le focus.
- `ui.inspect_accessibility_tree` : lit l'arbre Windows UI Automation en lecture seule si `.[windows-ui]` est installé.
- `ui.capture_screen` : capture l'écran ou la fenêtre iClone 8.
- `scene.read_visible_state` : lit l'état visible connu sans modifier la scène.
- `workflow.stop_all` : arrête le workflow local courant.

## Références

- [Manuel officiel iClone 8](https://manual.reallusion.com/iclone-8/Content/ENU/8.0/01-Welcome/Welcome.htm)
- [Scene Manager](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/03-Introducing-the-User-Interface/Scene_manager.htm)
- [Launching Timeline](https://manual.reallusion.com/iclone-8/Content/ENU/8.7/51-Animation-Timeline-Editing/Launching-Timeline.htm)
- [Utilizing Path](https://manual.reallusion.com/iclone-8/content/ENU/8.0/50-Animation/Path/Utilizing_Path.htm)
- [Creating Path](https://manual.reallusion.com/iclone-8/content/enu/8.0/50-Animation/Path/Creating_New_Path.htm)
- [Setting Position Keys on Path](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/50-Animation/Path/Setting_Position_Keys_on_Path.htm)
- [Preference Panel](https://manual.reallusion.com/iClone-8/Content/ENU/8.2/03-Introducing-the-User-Interface/Preference_Panel.htm)

## Roadmap

Voir [`docs/implementation-plan.md`](docs/implementation-plan.md), [`docs/feature-matrix.csv`](docs/feature-matrix.csv) et [`docs/limitations.md`](docs/limitations.md).

Skill expert : [`skill/SKILL.md`](skill/SKILL.md). Référence de procédure manuelle : [https://manual.reallusion.com/iclone-8](https://manual.reallusion.com/iclone-8).
