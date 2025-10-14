from pandas import DataFrame

from openfisca_france_dotations_locales import (
    CountryTaxBenefitSystem as OpenFiscaFranceDotationsLocales,
)

from leximpact_dotations_back.load_configuration import load_configuration
from leximpact_dotations_back.computing.calculate import create_simulation_with_data
from leximpact_dotations_back.data_building.build_dotations_data import (
    load_criteres,
    adapt_criteres,
    build_data,
    get_previous_year_data
)


# TODO vérifier incohérences de période avec valeur dans .env ?
CURRENT_YEAR = 2024

# rattache DATA_DIRECTORY (et simulation_2024.py) au .env
simulation_2024_configuration = load_configuration()
DATA_DIRECTORY = simulation_2024_configuration['data_directory']


def buid_data_2023_for_2024(year=CURRENT_YEAR, data_directory=DATA_DIRECTORY):
    data = get_previous_year_data(year, data_directory)  # pour récupérer year - 1
    return data


def build_data_2024(year=CURRENT_YEAR, data_directory=DATA_DIRECTORY) -> DataFrame:
    data_2024 = build_data(year, data_directory)  # TODO inverser l'ordre des arguments pour avoir le même ordre dans toutes les fonctions ?
    return data_2024


def get_strates_2024(model):
    strates_scale = model.parameters(CURRENT_YEAR).population.groupes_demographiques
    # en 2024 : [0, 500, 1000, 2000, 3500, 5000, 7500, 10000, 15000, 20000, 35000, 50000, 75000, 100000, 200000]
    return strates_scale.thresholds


def build_simulation_2024(year, model, data_adapted_criteres_2024, data_selection_2023):
    # TODO vérifier la cohérence des données 2023 et 2024 associées ?
    simulation_2024 = create_simulation_with_data(
        model,
        year,
        data_adapted_criteres_2024,
        data_selection_2023
    )

    return simulation_2024

# TODO supprimer au bénéfice de DotationsSimulation ?


def get_simulation_2024(data_directory=DATA_DIRECTORY, year=CURRENT_YEAR):

    # charge les données DGCL 2024 et les adapte
    data_criteres_2024 = load_criteres(year, data_directory)
    data_adapted_criteres_2024 = adapt_criteres(year, data_criteres_2024)
    # data_adapted_criteres_2024.columns

    data_selection_2023 = buid_data_2023_for_2024(year, data_directory)
    # data_selection_2023.columns

    openfisca_france_dotations_locales_model = OpenFiscaFranceDotationsLocales()

    simulation_2024 = build_simulation_2024(
        year,
        openfisca_france_dotations_locales_model,
        data_adapted_criteres_2024,
        data_selection_2023
    )

    return simulation_2024
