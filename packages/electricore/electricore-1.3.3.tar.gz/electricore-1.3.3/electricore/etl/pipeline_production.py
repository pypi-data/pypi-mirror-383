"""
Pipeline de production avec l'architecture refactorisée.
Traite tous les flux configurés avec des options flexibles.
"""

import dlt
import yaml
from pathlib import Path
from sources.sftp_enedis import flux_enedis

def run_production_pipeline(
    flux_selection=None,
    max_files=None,
    destination="duckdb",
    dataset_name="flux_enedis"
):
    """
    Lance le pipeline de production avec l'architecture modulaire refactorisée.
    
    Args:
        flux_selection: Liste des flux à traiter (ex: ['R151', 'C15']) ou None pour tous
        max_files: Limitation du nombre de fichiers par resource (pour tests)
        destination: Destination DLT (duckdb, postgres, etc.)
        dataset_name: Nom du dataset de destination
    """
    
    print("="*80)
    print("🚀 PIPELINE PRODUCTION - ARCHITECTURE REFACTORISÉE")
    print("="*80)
    
    # Charger la configuration des flux
    config_path = Path("config/flux.yaml")
    if not config_path.exists():
        raise FileNotFoundError("Configuration flux.yaml non trouvée")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        all_flux_config = yaml.safe_load(f)
    
    # Filtrer les flux si spécifié
    if flux_selection:
        flux_config = {k: v for k, v in all_flux_config.items() if k in flux_selection}
        print(f"📋 Flux sélectionnés: {list(flux_config.keys())}")
    else:
        flux_config = all_flux_config
        print(f"📋 Tous les flux configurés: {list(flux_config.keys())}")
    
    if not flux_config:
        print("❌ Aucun flux à traiter!")
        return
    
    # Calculer le nombre total de tables
    total_tables = 0
    for flux_name, config in flux_config.items():
        if 'xml_configs' in config:
            total_tables += len(config['xml_configs'])
        if 'csv_configs' in config:
            total_tables += len(config['csv_configs'])
    
    print(f"📊 {len(flux_config)} flux → {total_tables} tables cibles")
    if max_files:
        print(f"⚡ Mode test: max {max_files} fichiers par resource")
    
    # Créer le pipeline
    pipeline = dlt.pipeline(
        pipeline_name="flux_enedis_pipeline",
        destination=destination,
        dataset_name=dataset_name
    )
    
    print(f"🎯 Destination: {destination} → dataset '{dataset_name}'")
    print()
    
    # Créer la source avec l'architecture modulaire
    print("🏗️ CRÉATION SOURCE MODULAIRE...")
    source = flux_enedis(flux_config, max_files=max_files)
    print()
    
    # Exécution du pipeline
    print("🚀 EXÉCUTION PIPELINE...")
    print("-" * 50)
    
    try:
        # Pipeline complet: Extract + Normalize + Load
        load_info = pipeline.run(source)

        print()
        print("="*80)
        print("✅ PIPELINE RÉUSSI!")
        print("="*80)

        # Extraire les statistiques depuis le trace
        trace = pipeline.last_trace
        total_rows = 0

        if trace and trace.last_normalize_info:
            table_metrics = trace.last_normalize_info.row_counts

            print("\n📊 STATISTIQUES DU CHARGEMENT:")
            for table_name, row_count in table_metrics.items():
                if not table_name.startswith("_dlt"):  # Ignorer les tables système
                    print(f"   - {table_name}: {row_count} nouveaux enregistrements")
                    total_rows += row_count

            if total_rows == 0:
                print("   ⚠️ Aucune nouvelle donnée à traiter")
            else:
                print(f"   ✅ Total: {total_rows} enregistrements ajoutés")
        else:
            print("\n📊 Pas de métriques disponibles dans le trace")

        # Afficher les informations de timing
        print(f"\n📦 Load info: {load_info}")

        # Résumé simple
        packages_count = len(load_info.load_packages) if hasattr(load_info, 'load_packages') else 1
        print(f"📋 {packages_count} package(s) traité(s) avec succès")

        print()
        print("🎉 ARCHITECTURE REFACTORISÉE OPÉRATIONNELLE!")
        
    except Exception as e:
        print(f"❌ Erreur pipeline: {e}")
        raise

def main():
    """Point d'entrée principal avec différents modes"""
    
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "test":
            # Mode test rapide - seulement R151 avec 2 fichiers
            print("🧪 MODE TEST RAPIDE")
            run_production_pipeline(
                flux_selection=['R151', 'C15', 'F15', 'R64'],
                max_files=2,
                dataset_name="flux_enedis_test"
            )
            
        elif mode == "r151":
            # Mode R151 complet
            print("📊 MODE R151 COMPLET") 
            run_production_pipeline(
                flux_selection=['R151'],
                dataset_name="flux_enedis_r151"
            )
            
        elif mode == "all":
            # Mode production complète
            print("🌟 MODE PRODUCTION COMPLÈTE")
            run_production_pipeline(
                dataset_name="flux_enedis"
            )
            
        else:
            print(f"❌ Mode inconnu: {mode}")
            print("Usage: python pipeline_production.py [test|r151|all]")
            sys.exit(1)
    else:
        # Mode par défaut - test rapide  
        print("🧪 MODE PAR DÉFAUT: TEST RAPIDE")
        run_production_pipeline(
            flux_selection=['R151'],
            max_files=2,
            dataset_name="flux_enedis_default"
        )

if __name__ == "__main__":
    main()