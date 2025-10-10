# ETL ElectriCore

Pipeline ETL pour les flux énergétiques Enedis avec architecture modulaire DLT.

## 🏗️ Architecture Refactorisée

```
electricore/etl/
├── transformers/            # Transformers DLT modulaires
│   ├── crypto.py           # Déchiffrement AES + transformer
│   ├── archive.py          # Extraction ZIP + transformer  
│   └── parsers.py          # Parsing XML/CSV + transformers
│
├── sources/                 # Sources DLT (@dlt.source)
│   └── sftp_enedis.py      # Source SFTP multi-ressources refactorisée
│
├── config/                  # Configuration centralisée
│   ├── settings.py         # Chargement YAML et constantes
│   └── flux.yaml           # Configuration des flux (C15, F12, F15, R15, R151, R64)
│
├── pipeline_production.py   # Pipeline de production avec modes
└── .dlt/                   # Configuration DLT
    ├── config.toml
    └── secrets.toml
```

## 🚀 Utilisation

### Pipeline de Production

```bash
# Test rapide (2 fichiers) - quelques secondes
poetry run python pipeline_production.py test

# R151 complet - environ 6 secondes  
poetry run python pipeline_production.py r151

# Tous les flux - production complète
poetry run python pipeline_production.py all

# Mode par défaut - test rapide
poetry run python pipeline_production.py
```

### Développement et Tests

```bash
# Test avec limitation personnalisée
from sources.sftp_enedis import sftp_flux_enedis_multi
source = sftp_flux_enedis_multi(flux_config, max_files=5)
```

### Commandes DLT Utiles

```bash
# Vérifier l'état du pipeline
poetry run dlt pipeline enedis_data info

# Reset complet si nécessaire  
poetry run dlt pipeline enedis_data drop --drop-all

# Logs détaillés
poetry run dlt pipeline enedis_data trace
```

## 📊 Flux Supportés

| Flux | Description | Tables générées |
|------|-------------|-----------------|
| **C15** | Changements contractuels | `flux_c15` |
| **F12** | Facturation distributeur | `flux_f12` |
| **F15** | Facturation détaillée | `flux_f15_detail` |
| **R15** | Relevés index | `flux_r15`, `flux_r15_acc` |
| **R151** | Relevés courbe de charge | `flux_r151` |
| **R64** | Relevés CSV (Polars) | `flux_r64` |

## 🔧 Configuration

### Secrets DLT (`.dlt/secrets.toml`)
```toml
[sftp]
url = "sftp://user:pass@host/path/"
file_pattern = "**/*.zip"

[aes]
key = "hex_encoded_key"
iv = "hex_encoded_iv"
```

### Configuration des Flux (`config/flux.yaml`)
Chaque flux définit :
- `zip_pattern` : Pattern des fichiers ZIP à traiter
- `xml_configs` : Configurations XML avec row_level, data_fields, nested_fields
- `csv_configs` : Configurations CSV avec délimiteurs et clés primaires

## 🎯 Avantages de l'Architecture Modulaire

✅ **Transformers réutilisables** : crypto | archive | parsers  
✅ **Tests ultra-rapides** : max_files pour éviter 15min d'attente  
✅ **Pipeline flexible** : modes test/production/personnalisé  
✅ **Consolidation DRY** : Suppression duplications lib/transformers  
✅ **Performance optimisée** : R151 complet en 6.3 secondes  

## ⚡ Performance

- **Test rapide** : 2 fichiers en ~3 secondes
- **R151 complet** : 108k enregistrements en 6.3 secondes  
- **Incrémental DLT** : Évite le retraitement automatiquement

## ⚠️ Attention : État Incrémental DLT et Nommage

### Problème caché de l'état incrémental

DLT maintient un état incrémental basé sur la **combinaison unique** de :
- Nom du pipeline (`pipeline_name`)
- Nom de la source (`@dlt.source(name="...")`)
- Nom du dataset (`dataset_name`)

**⚠️ IMPORTANT** : Si vous changez un de ces noms sans nettoyer l'état, DLT peut :
- Utiliser l'ancien état incrémental avec le nouveau nom → données manquantes
- Créer un nouvel état → rechargement complet non voulu
- Mélanger les états → comportements imprévisibles

### Où est stocké l'état ?

1. **Local** : `~/.dlt/pipelines/{pipeline_name}/state.json`
2. **DuckDB** : `{dataset_name}._dlt_pipeline_state`

### Comment éviter les problèmes ?

Lors d'un changement de nom :

```bash
# 1. Nettoyer l'état local
rm -rf ~/.dlt/pipelines/ancien_nom_pipeline/

# 2. Nettoyer dans DuckDB (optionnel si nouveau dataset)
poetry run python -c "
import duckdb
conn = duckdb.connect('flux_enedis.duckdb')
conn.execute('DROP SCHEMA IF EXISTS ancien_dataset CASCADE')
"

# 3. Relancer avec les nouveaux noms
poetry run python pipeline_production.py all
```

### Exemple de migration propre

Si vous renommez `enedis_production` → `flux_enedis` :

```python
# AVANT
pipeline = dlt.pipeline(
    pipeline_name="flux_enedis",  # ⚠️ Incohérent !
    dataset_name="enedis_production"
)
source = sftp_flux_enedis_multi(...)  # Ancien nom

# APRÈS (cohérent)
pipeline = dlt.pipeline(
    pipeline_name="flux_enedis_pipeline",  # Nouveau nom
    dataset_name="flux_enedis"  # Nouveau schema
)
source = flux_enedis(...)  # Source renommée aussi !
```

**Règle d'or** : En cas de doute sur l'état incrémental, utilisez `--replace` ou supprimez `~/.dlt/pipelines/`.

## 🔄 Architecture Modulaire

```python
# Pipeline avec chaînage de transformers
encrypted_files | decrypt_transformer | unzip_transformer | parse_transformer
```

Chaque transformer est :
- **Isolé** : Testable indépendamment
- **Réutilisable** : Partagé entre flux
- **Composable** : Chaînable avec l'opérateur |

## 🔮 Extensions Futures

- `sources/api_enedis.py` : API REST Enedis
- `sources/sftp_axpo.py` : SFTP Axpo
- `transformers/validators.py` : Validation Pandera des données

## 🔌 Intégrations

### Connecteurs disponibles

Les connecteurs Odoo ont été déplacés vers les modules Core pour une meilleure séparation des responsabilités :

- **Lecture** : `electricore.core.loaders` (OdooReader, OdooQuery)
- **Écriture** : `electricore.core.writers` (OdooWriter)

Voir [docs/odoo-query-builder.md](../../docs/odoo-query-builder.md) pour plus de détails.