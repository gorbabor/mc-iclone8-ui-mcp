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

### Prérequis

- Windows avec une session utilisateur interactive.
- iClone 8 installé et ouvert pour les tests UI.
- Python 3.10 ou plus récent.
- Le serveur doit rester local : il ne se connecte pas à Internet pendant son exécution.

### Installation depuis GitHub

```powershell
git clone https://github.com/gorbabor/mc-iclone8-ui-mcp.git
cd mc-iclone8-ui-mcp
```

Si `python` pointe vers un environnement sans `pip`, utiliser le Python système (`py -3`) ou le chemin Python fourni par Codex :

```powershell
$py = "C:\Users\Christian Bwanakawa\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $py -m pip install -e ".[windows-ui,screenshots]"
```

La configuration setuptools inclut uniquement le paquet `mc_iclone8_ui_mcp`; les dossiers `skill/`, `docs/` et `screenshots/` ne sont pas installés comme paquets Python.

### Vérification

```powershell
& $py tests\smoke_test.py
& $py -m compileall -q mc_iclone8_ui_mcp
```

Résultat attendu : `smoke test: ok`.

### Configuration MCP stdio

Le serveur est lancé par le client MCP, pas comme un serveur HTTP :

```json
{
  "mcpServers": {
    "mc-iclone8-ui-mcp": {
      "command": "C:\\Users\\Christian Bwanakawa\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe",
      "args": ["-m", "mc_iclone8_ui_mcp"],
      "cwd": "C:\\chemin\\vers\\mc-iclone8-ui-mcp"
    }
  }
}
```

Le processus MCP utilise stdin/stdout pour JSON-RPC et stderr pour les journaux. Ne pas utiliser le panneau HTTP d'un autre plugin iClone comme remplacement de ce serveur.

### Gestion des instances iClone

Pour une session interactive, le client peut suivre cette séquence :

```text
ui.list_instances
→ ui.activate_instance(handle)
→ ui.get_active_instance
→ ui.set_interaction_mode("interact" ou "session")
→ action UI
→ vérification avant/après
```

Le mode `observe` ne prend pas le focus. Le mode `interact` autorise les primitives UI après vérification du focus. Le mode `session` indique qu’une instance doit rester la cible pendant la séquence, tout en vérifiant le focus avant chaque action.

Toute action UI doit passer par le garde-fou de focus : instance cible détectée, fenêtre restaurée si nécessaire, premier plan confirmé avant l’action, puis focus revérifié avant la preuve après action.

Note UI Automation : iClone 8 peut exposer des identifiants Qt historiques contenant `iClone6 MainWindow`. Ce sont des métadonnées d'accessibilité de l'interface observée, pas des appels à iClone 6. Le code matche uniquement les suffixes sémantiques et n'utilise ni RLPy ni API d'une autre version.

### Lancement manuel

```powershell
& $py -m mc_iclone8_ui_mcp
```

## Lancement

```powershell
python -m mc_iclone8_ui_mcp
```

Le processus utilise JSON-RPC sur stdin/stdout. Les logs vont sur stderr.

## Outils MCP read-only

- `ui.inspect_application` : détecte les fenêtres iClone 8 visibles et rapporte le focus.
- `ui.list_instances` : liste les fenêtres iClone 8 avec handle, PID, projet et focus.
- `ui.get_active_instance` : lit l’instance cible et l’état du focus.
- `ui.activate_instance` : restaure et place une instance cible au premier plan.
- `ui.set_interaction_mode` : configure `observe`, `interact` ou `session`.
- `ui.inspect_accessibility_tree` : lit les contrôles directs Windows UI Automation en lecture seule si `.[windows-ui]` est installé.
- `ui.inspect_named_control` : inspecte un contrôle nommé, par exemple `Scene`, et ses enfants directs.
- `ui.inspect_automation_control` : inspecte un contrôle par `automation_id`, par exemple le conteneur du Scene Manager.
- `scene.read_manager` : lit un sous-arbre borné du Scene Manager, sans modification.
- `scene.list_items` : extrait les noms des objets `TreeItem` visibles, sans sélection.
- `scene.select_item` : sélectionne un objet par nom accessible, uniquement avec `confirm=true` et iClone 8 au premier plan. `screenshot_dir` peut produire les captures avant/après.
- `scene.read_modify` : lit le sous-arbre du panneau Modify pour vérifier l’état après une action.
- `workflow.catalog` : expose l’état progressif des huit familles de workflows.
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
