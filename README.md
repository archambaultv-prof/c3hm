# ✏️ `c3hm` : Corriger à 3 heures du matin

**Ici, on ne juge pas, sauf les travaux.**

Bienvenue dans le *sanctuaire obscur de la correction semi-automatisée*. Ce
projet Python fournit `c3hm`, une interface de ligne de commande conçue pour
les profs de cégep qui veulent survivre à la tempête de copies.

> [!WARNING]
> `c3hm` est actuellement en développement actif. Certaines
> fonctionnalités peuvent être instables ou sujettes à modification.

## 🔭 Juché sur les épaules de géants

Un grand merci à mes collègues du Collège de Maisonneuve, notamment Caroline
Houle pour avoir partagé ses grilles d'évaluation et macros Excel. Merci
également à Patrice Farand de l'École Polytechnique de Montréal pour m'avoir
appris à faire une grille d'évaluation. Le succès de `c3hm` leur revient en
bonne partie, toutes les erreurs sont les miennes.

## 🧰 Fonctionnalités

Pendant que tu regrettes ton choix de carrière face à la montagne de
copies à corriger, `c3hm` vient à ta rescousse. Il te permet de :

- `c3hm unpack` : Dézipper et nettoyer les remises des étudiants, comme un aspirateur numérique. Bye bye
  `node_modules`, `.venv` et autres joyeusetés. Ton OneDrive sera tellement content !
- `c3hm export` : Générer une grille d'évaluation à partir d'une description en YAML.
- `c3hm gradebook` : Générer un tableur Excel pour la correction.
- `c3hm feedback` : Ouf... il est 3 heures du matin et tu viens de finir
  ta correction. Bravo, le pire est derrière toi. Mais il te faut encore
  exporter une rétroaction pour chaque étudiant et remettre tout ça dans Omnivox. Tu en
  as de la chance, `c3hm` peut le faire pour toi ! Il va créer un fichier pour
  chaque étudiant, avec un nom qu'Omnivox comprend. Il va même te créer un
  tableur Excel avec les notes prêtes à être importées dans
  Omnivox.
- `c3hm template` : Le par cœur, ce n'est pas ton fort ? Pas de souci, `c3hm` peut
  générer un modèle de grille d'évaluation pour toi.
- `c3hm clean` : Nettoyer les fichiers temporaires et les artefacts de
  construction après la correction. Encore une fois, ton OneDrive te dira merci !

Pour l'instant, c'est tout, mais on a de grands projets pour l'avenir. Reste à l'écoute !

#### 😮 Quoi en anglais ?

Oui, les noms de commandes sont en anglais. Pourquoi ? Parce que c'est toujours
comme ça en informatique. Des termes et options comme `init`,
`--dry-run`, `--verbose`, `--help`, `--dir` et autres sont des classiques. On ne
va pas réinventer la roue.

Par contre, les messages d'erreur et les descriptions sont en français. Parce qu'on est au Québec, et qu'on aime bien
notre langue.

## 🪄 Installation

Clone le dépôt et installe `c3hm` en utilisant [`pipx`](https://github.com/pypa/pipx) :

```bash
git clone https://github.com/archambaultv-prof/c3hm.git
cd c3hm
pipx install .
```

### 🧪 Compatibilité

- Python ≥ 3.10
- Fonctionne mieux avec une bonne dose de désespoir
- Testé sous pression, entre deux réunions pédagogiques

## 🛡️ Licence

Plus généreux qu'un prof qui corrige avec des demi-points bonus : distribué
sous la licence MIT.