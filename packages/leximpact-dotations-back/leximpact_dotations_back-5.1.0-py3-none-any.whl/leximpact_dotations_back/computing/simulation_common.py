# les fonctions stables d'une année à une autre
# pour la construction de simulation sur les dotations

from pandas import DataFrame

from openfisca_france_dotations_locales import CountryTaxBenefitSystem as OpenFiscaFranceDotationsLocales

from leximpact_dotations_back.computing.calculate import create_simulation_with_data
from leximpact_dotations_back.data_building.build_dotations_data import (
    get_insee_communes_1943_file_path,
    load_criteres,
    load_insee_communes_history
)


def get_insee_communes_history(year, data_directory):
    '''
    Charge les dates de création des communes depuis 1943 selon l'INSEE.
    Un seul fichier issu du code officiel géographique mis à jour chaque année.
    '''
    insee_communes_1943_to_current_year_file_path = get_insee_communes_1943_file_path(data_directory, year)
    communes_history_current_year = load_insee_communes_history(insee_communes_1943_to_current_year_file_path)
    return communes_history_current_year


def get_criteres(year, data_directory) -> DataFrame:
    '''
    Charge les critères DGCL de l'année spécifiée.
    À l'initialisation d'une simulation, on charge typiquement les critères de l'année courante.
    '''
    dotations_criteres = load_criteres(year, data_directory)
    # dotations_criteres.columns
    return dotations_criteres


def calculate_dotations(simulation, dotations_criteres_data, year):  # adapted data

    # DF

    dotation_forfaitaire = simulation.calculate(
        "dotation_forfaitaire", year
    )

    # DSR

    dsr_fraction_bourg_centre = simulation.calculate(
        "dsr_fraction_bourg_centre", year
    )
    dsr_fraction_perequation = simulation.calculate(
        "dsr_fraction_perequation", year
    )
    dsr_fraction_cible = simulation.calculate(
        "dsr_fraction_cible", year
    )

    dotation_solidarite_rurale = simulation.calculate("dotation_solidarite_rurale", year)

    # DSU

    dsu_montant = simulation.calculate("dsu_montant", year)

    # DCN

    dotation_communes_nouvelles_part_amorcage = simulation.calculate("dotation_communes_nouvelles_part_amorcage", year)
    dotation_communes_nouvelles_part_garantie = simulation.calculate("dotation_communes_nouvelles_part_garantie", year)

    dotation_communes_nouvelles = simulation.calculate(
        "dotation_communes_nouvelles", year
    )

    # stockage des résultats même si accès aussi possible via
    # simulation.commune.get_holder('dotation_forfaitaire').get_array(2024)

    simulated_data = dotations_criteres_data.copy()

    simulated_data["dotation_forfaitaire"] = dotation_forfaitaire

    simulated_data["dsu_montant"] = dsu_montant

    simulated_data["dsr_fraction_bourg_centre"] = dsr_fraction_bourg_centre
    simulated_data["dsr_fraction_perequation"] = dsr_fraction_perequation
    simulated_data["dsr_fraction_cible"] = dsr_fraction_cible
    simulated_data["dotation_solidarite_rurale"] = dotation_solidarite_rurale

    simulated_data["dotation_communes_nouvelles_part_amorcage"] = dotation_communes_nouvelles_part_amorcage
    simulated_data["dotation_communes_nouvelles_part_garantie"] = dotation_communes_nouvelles_part_garantie
    simulated_data["dotation_communes_nouvelles"] = dotation_communes_nouvelles

    return simulated_data


def build_france_dotations_simulation(
    year: int,
    model: OpenFiscaFranceDotationsLocales,
    data_adapted_criteres_year: DataFrame,
    data_selection_previous_year: DataFrame
):
    # TODO vérifier la cohérence des données année N-1 et N associées ?
    current_year_simulation = create_simulation_with_data(
        model,
        year,
        data_adapted_criteres_year,
        data_selection_previous_year
    )

    return current_year_simulation
