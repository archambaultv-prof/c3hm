# Tests pour c3hm

## Exécuter les tests

```bash
# Tous les tests
uv run pytest

# Tests du module data uniquement
uv run pytest tests/data/

# Un fichier de test spécifique
uv run pytest tests/data/test_utils.py
```

## Avec nox (tests multi-versions Python)

```bash
# Tests sur toutes les versions Python (3.11-3.14)
uv run nox

# Tests sur une version spécifique
uv run nox -s tests-3.13

# Linter
uv run nox -s lint

# Vérifier le formatage
uv run nox -s format_check

# Formater le code
uv run nox -s format
```
