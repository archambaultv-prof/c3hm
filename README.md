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

## 🛡️ Licence

Plus généreux qu'un prof qui corrige avec des demi-points bonus : distribué
sous la licence MIT.
