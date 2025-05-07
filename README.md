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
Houle pour avoir partagé ses grilles d'évaluation et macros Excel.

Merci également à Patrice Farand de l'École Polytechnique de Montréal pour m'avoir 
appris à faire une grille d'évaluation. 

Le succès de `c3hm` leur revient en bonne partie, toutes les erreurs sont les miennes.

## 🧰 Fonctionnalités

Pendant que tu regrettes ton choix de carrière face à la montagne de
copies à corriger, `c3hm` vient à ta rescousse. Il te permet de :

- `c3hm clean` : Nettoyer les remises des étudiants, comme un aspirateur numérique. Bye bye
  `node_modules`, `.git`, `.venv` et autres joyeusetés. Ton OneDrive sera tellement content !
- `c3hm rubric generate` : Générer une grille d'évaluation à partir d'une description en YAML. Tu peux la
  générer en Word, PDF, Excel ou Markdown. Tu peux générer une version pour les étudiants et une
  version pour les correcteurs.
- `c3hm rubric export` : Ouf... il est 3 heures du matin et tu viens de finir
  ta correction. Bravo, le pire est derrière toi. Mais il te faut encore
  exporter un PDF pour chaque étudiant et remettre tout ça dans Omnivox. Tu en
  as de la chance, `c3hm` peut le faire pour toi ! Il va créer un PDF pour
  chaque étudiant, avec un nom qu'Omnivox comprend. Il va même te créer un
  tableur Excel avec les notes et les commentaires prêts à être importés dans
  Omnivox. Et comme `c3hm` est vraiment gentil, il va même mettre dans le
  tableur Excel une grille récapitulative pour que tu puisses voir globalement
  quelles parties du travail ont été bien comprises et lesquelles ont été
  ratées.

Pour l'instant, c'est tout, mais on a de grands projets pour l'avenir. Reste à l'écoute !

#### 😮 Quoi en anglais ?

Oui, les noms de commandes sont en anglais. Pourquoi ? Parce que c'est toujours
comme ça en informatique. Des termes et options comme `clean`, `init`,
`--dryrun`, `--verbose`, `--help`, `--dir` et autres sont des classiques. On ne
va pas réinventer la roue ici.

Par contre, les messages d'erreur et les descriptions sont en français. Parce que
on est au Québec, et qu'on aime bien notre langue.

## 🪄 Installation

Si tu es du genre à aimer les outils modernes comme
[`uv`](https://docs.astral.sh/uv/), tu peux utiliser `c3hm` directement, sans
te casser la tête avec des installations compliquées. Oui, c'est presque
magique.

Par exemple, pour générer ta grille d'évaluation `tp2` et impressionner tes
collègues :

```bash
uvx c3hm rubric generate tp2.yaml
```

Si tu préfères les méthodes plus classiques (ou si tu es nostalgique des années
2000), pas de panique. `c3hm` est un package Python, et tu peux l'installer sur ta
machine avec `pip`. Tu connais les environnements virtuels, non ?


### 🧪 Compatibilité

- Python ≥ 3.10
- Fonctionne mieux avec une bonne dose de désespoir
- Testé sous pression, entre deux réunions pédagogiques

## ⚙️ Comment ça marche ?

Je sais, je sais, comme les étudiants tu voudrais une vidéo TikTok pour tout t'expliquer en moins de
30 secondes. Mais ici, on fait les choses à l'ancienne. Alors va lire le [guide de démarrage](guide-demarrage.md) et
ensuite plonge dans le code, il est super bien commenté (c'est dans les critères des grilles de Caroline).

## 🛡️ Licence

Plus généreux qu’un prof qui corrige avec des demi-points bonus.

- Distribué sous la licence MIT.
- Tu peux aussi utiliser le matériel de ce projet sous la licence [Creative
Commons Attribution 4.0 International (CC BY
4.0)](https://creativecommons.org/licenses/by/4.0/deed.fr). Cette dernière
pourrait être mieux adaptée pour le matériel pédagogique.
- La [banque de grilles d'évaluation](gabarits_grilles/) est mise dans le domaine public via [CC0
  1.0](https://creativecommons.org/publicdomain/zero/1.0/deed.fr). Pas besoin
  de dire à tes étudiants que tu travailles en équipe !

Juste pour clarifier, évidemment tout travail généré par `c3hm` est ta propriété, ici
on parle du code source de ce dépôt et de la banque de grilles d'évaluation.