### c3hm poubelle

```bash
uvx c3hm clean --help
```

Cette commande nettoie les remises des étudiant·e·s en supprimant les fichiers et
dossiers inutiles. Pour l'instant elle supprime

- `__pycache__`
- `.DS_Store`
- `.git`
- `.idea`
- `.pytest_cache`
- `.venv`
- `venv`
- `.vscode`
- `node_modules`

Le nom de chaque dossier d'étudiant·e doit être conforme à celui
généré par Omnivox. Par exemple : `NOM1_NOM2_123456789_`.

> [!NOTE]
> `node_modules` peut être très long à supprimer, surtout s'il est sur OneDrive.

### c3hm rubric generate

```bash
uvx c3hm rubric generate --help
```

Cette commande génère une grille d'évaluation à partir d'une description en
YAML. Elle prend en entrée un fichier YAML et par défaut génère

- Un fichier Word qui contient la grille d'évaluation pour les étudiant·e·s. Il
  existe aussi une option pour générer un fichier PDF directement.
- Un fichier Excel qui contient la grille d'évaluation pour les correcteur·trice·s. Si tu fournis
  une liste d'étudiant, `c3hm` va générer une feuille Excel par étudiant. Il prend aussi en 
  charge le travail en équipe.


### c3hm rubric export

```bash
uvx c3hm rubric export --help
```

Bravo, tu as finis de corriger, le pire est derrière toi. Mais avant de te
coucher, il te reste une dernière étape : exporter ton travail pour chaque
étudiant·e. 

`c3hm` va prendre ton fichier Excel avec une feuille par étudiant·e et
générer un PDF (ou Word si tu insistes) pour chaque étudiant·e avec un nom de fichier que Omnivox
comprend.