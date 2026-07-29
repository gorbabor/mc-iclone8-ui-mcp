# Journal des limitations

## 2026-07-29 — Lot 0

- Aucun accès à une instance iClone 8 n'est disponible dans l'environnement de développement : les fonctionnalités de production restent `planned`.
- Le backend Win32 actuel détecte les fenêtres par titre. Il ne lit pas encore les contrôles UI Automation, le Scene Manager ou la Timeline.
- Les captures nécessitent `Pillow` et une session Windows interactive.
- Aucune action de clic, saisie, raccourci, menu ou RLPy n'est implémentée dans ce lot.
- La couverture de la matrice est une cartographie de planification, pas une preuve de support.
- Certains `automation_id` exposés par l'interface iClone 8 contiennent encore un préfixe Qt historique tel que `iClone6 MainWindow`. Le serveur ne l'utilise pas comme API : il ignore ce préfixe et ne matche que les suffixes UI sémantiques. Aucune fonction RLPy, API iClone 6 ou référence de manuel iClone 6 n'est utilisée.
