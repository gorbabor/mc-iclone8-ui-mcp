# Contrat de résultat

Chaque outil MCP retourne un objet `structuredContent` contenant exactement les champs suivants :

```json
{
  "status": "ok|failed|blocked",
  "action": "...",
  "target": "...",
  "screenshots": [],
  "observed_state_before": {},
  "observed_state_after": {},
  "verification": {},
  "warnings": [],
  "next_step": "..."
}
```

`ok` signifie seulement que l'opération demandée et sa vérification déclarée ont été exécutées. Une inspection sans preuve visuelle est explicitement marquée dans `verification`.
