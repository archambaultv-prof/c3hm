# ✏️ `c3hm` : Corriger à 3 heures du matin

![Tests](https://github.com/archambaultv-prof/c3hm/actions/workflows/tests.yml/badge.svg?branch=main)

**Ici, on ne juge pas, sauf les travaux.**

Bienvenue dans le *sanctuaire obscur de la correction semi-automatisée*. Ce
projet Python fournit `c3hm`, une interface de ligne de commande conçue pour
les profs de cégep qui veulent survivre à la tempête de copies.

> [!WARNING]
> `c3hm` est actuellement en développement actif. Certaines
> fonctionnalités peuvent être instables ou sujettes à modification.

## 🧰 Fonctionnalités

Pendant que tu regrettes ton choix de carrière face à la montagne de
copies à corriger, `c3hm` vient à ta rescousse. Il te permet de :

- `c3hm template` : Le par cœur, ce n'est pas ton fort ? Pas de souci, `c3hm` peut
  générer un modèle de configuration pour toi.
- `c3hm rubric` : Crée un `PDF` de la grille d'évaluation à partir du fichier
  de configuration. Parfait pour l'afficher en classe, l'imprimer ou en faire
  ton avatar.
- `c3hm unpack` : Dézipper et nettoyer les remises des étudiants, comme un aspirateur numérique. Bye-bye
  `node_modules`, `.venv` et autres joyeusetés. Ton OneDrive sera tellement content !
- `c3hm gradebook` : Générer des grilles d'évaluation. Tu n'auras qu'à remplir
  les notes et les commentaires.
- `c3hm feedback` : Ouf... il est 3 heures du matin et tu viens de finir ta
  correction. Bravo, le pire est derrière toi. Mais il te faut encore exporter
  une rétroaction pour chaque étudiant et remettre tout ça dans Omnivox. Tu en
  as de la chance, `c3hm` peut le faire pour toi ! À partir des grilles
  d'évaluation générées par `c3hm gradebook`, il va créer un
  tableur Excel avec les notes prêtes à être importées dans Omnivox.
- `c3hm clean` : Nettoyer les fichiers temporaires et les artefacts de
  construction après la correction. Encore une fois, ton OneDrive te dira merci !
- `c3hm server` : Lancer un serveur web local pour une interface de correction plus conviviale. Parce que
  corriger via des fichiers JSON c'est trop pour les humains.

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

## �️ Développement

### Configuration de l'environnement

Pour contribuer au projet, clonez le dépôt et installez les dépendances de développement:

```bash
git clone https://github.com/archambaultv-prof/c3hm.git
cd c3hm
pip install -e ".[dev]"
```

### Exécuter les tests

Le projet utilise [nox](https://nox.thea.codes/) pour orchestrer les tests sur plusieurs versions de Python (3.11-3.14):

```bash
# Exécuter tous les tests sur toutes les versions
nox

# Exécuter les tests sur Python 3.13 uniquement
nox -s tests-3.13

# Exécuter le linter
nox -s lint

# Vérifier le formatage
nox -s format_check
```

Ou directement avec pytest:

```bash
pytest tests/data/
```

**Couverture de code:** Le projet vise une couverture d'au moins 80% pour le module `c3hm.data`. Un rapport détaillé est généré dans `htmlcov/index.html` après chaque exécution.

Pour plus de détails sur les tests, consultez [tests/README.md](tests/README.md).

### Formatage du code

Le projet utilise [ruff](https://docs.astral.sh/ruff/) pour le linting et le formatage:

```bash
# Formater le code
nox -s format

# Vérifier le code
nox -s lint
```

### CI/CD

Les tests sont automatiquement exécutés via GitHub Actions sur chaque pull request vers `main`. Le workflow teste le code sur Python 3.11, 3.12, 3.13 et 3.14 et vérifie la couverture de code.

## �🛡️ Licence

Plus généreux qu'un prof qui corrige avec des demi-points bonus : distribué
sous la licence MIT.
