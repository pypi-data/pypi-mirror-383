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
