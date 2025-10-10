import polars as pl
import pandera.polars as pa
from pandera.typing.polars import DataFrame
from pandera.engines.polars_engine import DateTime
from typing import Optional, Annotated

class RelevéIndex(pa.DataFrameModel):
    """
    📌 Modèle Pandera pour les relevés d'index issus de différentes sources - Version Polars.

    Ce modèle permet de valider les relevés de compteurs avec leurs métadonnées
    en utilisant Polars pour des performances optimales.
    """
    
    # 📆 Date du relevé - Utilisation du type DateTime Polars avec timezone
    date_releve: DateTime = pa.Field(nullable=False, dtype_kwargs={"time_unit": "us", "time_zone": "Europe/Paris"})
    ordre_index: pl.Boolean = pa.Field(default=False)

    # 🔹 Identifiant du Point de Livraison (PDL)
    pdl: pl.Utf8 = pa.Field(nullable=False)
    ref_situation_contractuelle: Optional[pl.Utf8] = pa.Field(nullable=True)
    formule_tarifaire_acheminement: Optional[pl.Utf8] = pa.Field(nullable=True)

    # 🏢 Références Fournisseur & Distributeur
    id_calendrier_fournisseur: Optional[pl.Utf8] = pa.Field(nullable=True)
    id_calendrier_distributeur: Optional[pl.Utf8] = pa.Field(nullable=True)
    id_affaire: Optional[pl.Utf8] = pa.Field(nullable=True)

    # Source des données
    source: pl.Utf8 = pa.Field(nullable=False, isin=["flux_R151", "flux_R15", "flux_C15", "flux_R64", "FACTURATION"])

    # 📏 Unité de mesure
    unite: pl.Utf8 = pa.Field(nullable=False, isin=["kWh", "Wh", "MWh"])
    precision: pl.Utf8 = pa.Field(nullable=False, isin=["kWh", "Wh", "MWh"])

    # ⚡ Index de compteurs (valeurs cumulées en kWh)
    index_hp_kwh: Optional[pl.Float64] = pa.Field(nullable=True)
    index_hc_kwh: Optional[pl.Float64] = pa.Field(nullable=True)
    index_hch_kwh: Optional[pl.Float64] = pa.Field(nullable=True)
    index_hph_kwh: Optional[pl.Float64] = pa.Field(nullable=True)
    index_hpb_kwh: Optional[pl.Float64] = pa.Field(nullable=True)
    index_hcb_kwh: Optional[pl.Float64] = pa.Field(nullable=True)
    index_base_kwh: Optional[pl.Float64] = pa.Field(nullable=True)

    # 🔌 Métadonnées spécifiques R64 (optionnelles)
    type_releve: Optional[pl.Utf8] = pa.Field(nullable=True, isin=["AQ", "AM", "AC"])
    contexte_releve: Optional[pl.Utf8] = pa.Field(nullable=True, isin=["COL", "IND"])
    etape_metier: Optional[pl.Utf8] = pa.Field(nullable=True, isin=["BRUT", "CORR", "VALID"])
    grandeur_physique: Optional[pl.Utf8] = pa.Field(nullable=True, isin=["EA", "ER"])
    grandeur_metier: Optional[pl.Utf8] = pa.Field(nullable=True, isin=["CONS", "PROD"])

    @pa.dataframe_check
    def verifier_presence_mesures(cls, data) -> pl.LazyFrame:
        """
        Vérifie que les mesures attendues sont présentes selon l'Id_Calendrier_Distributeur.
        Utilise les expressions Polars natives pour la validation.
        """
        df_lazy = data.lazyframe
        
        # Créer des conditions pour chaque type de calendrier
        conditions = []
        
        # DI000001: index_base_kwh doit être non-null
        cond_d1 = (
            pl.when(pl.col("id_calendrier_distributeur") == "DI000001")
            .then(pl.col("index_base_kwh").is_not_null())
            .otherwise(pl.lit(True))
        )
        conditions.append(cond_d1)

        # DI000002: index_hp_kwh et index_hc_kwh doivent être non-null
        cond_d2 = (
            pl.when(pl.col("id_calendrier_distributeur") == "DI000002")
            .then(pl.col("index_hp_kwh").is_not_null() & pl.col("index_hc_kwh").is_not_null())
            .otherwise(pl.lit(True))
        )
        conditions.append(cond_d2)

        # DI000003: index_hph_kwh, index_hch_kwh, index_hpb_kwh, index_hcb_kwh doivent être non-null
        cond_d3 = (
            pl.when(pl.col("id_calendrier_distributeur") == "DI000003")
            .then(
                pl.col("index_hph_kwh").is_not_null() &
                pl.col("index_hch_kwh").is_not_null() &
                pl.col("index_hpb_kwh").is_not_null() &
                pl.col("index_hcb_kwh").is_not_null()
            )
            .otherwise(pl.lit(True))
        )
        conditions.append(cond_d3)
        
        # Combiner toutes les conditions
        combined_condition = conditions[0]
        for cond in conditions[1:]:
            combined_condition = combined_condition & cond
        
        return df_lazy.select(combined_condition.alias("mesures_valides"))

    class Config:
        """Configuration du modèle."""
        strict = False  # Permet les colonnes supplémentaires durant la migration


class RequêteRelevé(pa.DataFrameModel):
    """
    📌 Modèle Pandera pour les requêtes d'interrogation des relevés d'index - Version Polars.

    Assure que les requêtes sont bien formatées avant d'interroger le DataFrame `RelevéIndex`.
    """
    # 📆 Date du relevé demandée
    date_releve: DateTime = pa.Field(nullable=False, dtype_kwargs={"time_unit": "ns", "time_zone": "Europe/Paris"})

    # 🔹 Identifiant du Point de Livraison (PDL)
    pdl: pl.Utf8 = pa.Field(nullable=False)