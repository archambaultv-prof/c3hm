# Tutoriel `c3hm`

Mise à jour : 2025-08-17

> [!NOTE]
> Pour obtenir de l'aide pour une commande, utilisez l'option `--help`.

## Installation

Voir la [page principale](../README.md) pour les instructions d'installation.

## Le fichier de configuration

Le programme `c3hm` utilise un fichier de configuration au format YAML pour
personnaliser son comportement. Si vous utilisez `c3hm` pour la première fois,
le plus simple est d'utiliser la fonction `c3hm template --full` pour générer
un fichier de configuration complet et rigolo nommé `grille.yaml`. Celui-ci doit être accompagné
d'un fichier `étudiants.csv` que vous pouvez trouver ici :
[étudiants.csv](étudiants.csv)

Le fichier de configuration généré par `c3hm template --full` contient des
commentaires explicatifs pour vous aider à le personnaliser.

## Générer la grille

Utilisez ensuite la fonction `c3hm rubric grille.yaml` pour créer la grille
d'évaluation à partir du fichier de configuration et du fichier
`étudiants.csv`. Cela va créer un fichier Word nommé `grille.docx`.

## Corriger des copies

Pour corriger des copies, utilisez la fonction `c3hm gradebook grille.yaml` qui
va générer un fichier Excel nommé `grille.xlsx`. Pour chaque critère et chaque
indicateur, vous pouvez entrer les notes soit en pourcentage ou en points. Il
est aussi possible de laisser des commentaires. Le fichier d'exemple simule un
travail fait en équipe, notez qu'une fois la correction faite pour le premier
élève, les autres élèves de son équipe seront automatiquement notés de la même
manière. Il est bien sûr possible de modifier la note ou le commentaire
attribué à un élève en particulier.

## Rétroactions et notes dans Omnivox

Une fois la grille remplie, vous pouvez générer une rétroaction individuelle
pour chaque étudiant en utilisant la fonction `c3hm feedback grille.yaml grille.xlsx`. Cela
va créer un dossier nommé `rétroaction` contenant les rétroactions et
les notes à importer dans Omnivox.

> [!WARNING]
> Pour l'instant les messages d'erreur sont assez ... disons ... bruts. Vous devez remplir
> la grille au grand complet pour tous les étudiants avant de générer les rétroactions.

## Autres fonctionnalités

### Unpack

Si vous téléchargez vos copies depuis Omnivox, vous pouvez utiliser la fonction
`c3hm unpack nom_archive_omnivox.zip` pour extraire les dossiers ou fichiers
des étudiants. La fonction unpack s'occupe notamment de :

- Décompresser l'archive téléchargée depuis Omnivox si elle est encore au format zip.
- Décompresser tous les fichiers `.zip` trouvés dans le dossier Omnivox.
- Supprimer les dossiers et fichiers inutiles comme `__MACOSX`, `node_modules`, etc.
- Raccourcir les noms de fichiers/dossiers trop longs générés par Omnivox.
- Aplatir la structure des dossiers si nécessaire.


### Clean

La fonctionnalité `c3hm clean folder_path` permet de nettoyer les fichiers
générés par les programmes des étudiants comme les `node_modules` et autres
fichiers temporaires. À utiliser lorsque la correction nécessite d'exécuter du
code.
