# Plan d'implémentation

## Lot 0 — lecture seule (présent)

- [x] Transport MCP stdio local.
- [x] Détection Win32 des fenêtres dont le titre contient `iClone 8`.
- [x] Lecture du focus et des limites de fenêtre.
- [x] Capture d'écran facultative avec Pillow.
- [x] Contrat de résultat commun et journalisation stderr.
- [x] Arrêt global coopératif.

## Lot 1 — accessibilité et état visible

- [ ] Backend UI Automation (UIA) avec rôles, noms accessibles et arborescence.
- [ ] Sélecteurs bilingues FR/EN et tolérance aux variations de panneaux.
- [ ] Lecture réelle du Scene Manager, de la Timeline, de Modify et du Content Manager.
- [ ] Tests contre une scène de test iClone 8 en interface anglaise et française.

## Lot 2 — actions UI non destructives

- [ ] Focus explicite et restauration après perte de focus.
- [ ] Sélection d'un objet par nom accessible.
- [ ] Ouverture de panneaux et navigation de menus.
- [ ] Prévisualisation avant/après et blocage si l'état attendu n'est pas visible.

## Lot 3 — workflows verticaux

- [ ] Projet : nouveau, ouvrir, enregistrer sous avec confirmation.
- [ ] Scène : primitive, import, transformation, Scene Manager.
- [ ] Path : création, points, attachement, clés Path Position (%), transition et vérification de mouvement.
- [ ] Caméra : cadrage, capture avant/après et caméra active.
- [ ] Rendu : paramètres, confirmation avant long rendu et vérification du fichier.

## Lot 4 — couverture avancée

- [ ] Animation, avatars, Motion Director, facial, matériaux, lumières, physique et effets.
- [ ] Documentation de chaque limitation observée.
- [ ] Exemples de prompts et skill expert Markdown.

## Risques

| Risque | Mitigation |
| --- | --- |
| iClone absent ou non focalisable | Retour `blocked`, aucune action aveugle |
| Contrôles non exposés par UIA | Capture + état partiel, limitation documentée |
| Variations FR/EN | Sélecteurs sémantiques multilingues, jamais coordonnées seules |
| Opération destructive | Confirmation obligatoire et sauvegarde proposée |
