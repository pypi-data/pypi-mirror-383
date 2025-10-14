import logging
from numpy import full

from openfisca_core.errors.variable_not_found_error import VariableNotFoundError
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_core.simulations import Simulation


# tente de ne plus configurer de logger propre au fichier
# pour ne pas lire deux fois la configuration
# from leximpact_dotations_back.load_configuration import get_logging_level
# configured_logging_level = get_logging_level()
# logging.basicConfig(level=configured_logging_level)
# logger = logging.getLogger(__name__)
logger = logging.getLogger()


def set_simulation_inputs(simulation, data, period):
    for champ_openfisca in data.columns:
        try:
            simulation.tax_benefit_system.get_variable(champ_openfisca, check_existence=True)
            # oui c'est comme ça que je checke qu'une variable est openfisca ne me jugez pas
            # si exception, on choisit d'arrêter l'application
            simulation.set_input(
                champ_openfisca,
                period,
                data[champ_openfisca],
            )
        except VariableNotFoundError as vnfe:
            logger.fatal(f"Error while setting up this year data to '{champ_openfisca}'.")
            raise vnfe
        except ValueError as ve:  # Python buitin exception
            logger.fatal(f"Error while setting up '{champ_openfisca}' with this year data: {data[champ_openfisca]}")
            raise ve

    simulation = set_dotations_enveloppes_current_year(simulation, period)
    return simulation


def set_dotations_enveloppes_previous_year(simulation: Simulation, data, current_year: int):
    NOMBRE_TOTAL_COMMUNES_CURRENT_YEAR = len(data)
    PREVIOUS_YEAR = current_year - 1
    PARAMETERS_PREVIOUS_YEAR = simulation.tax_benefit_system.parameters(PREVIOUS_YEAR)

    # Fix bug NaN DSU
    dsu_montant_enveloppe_metropole_previous_year = PARAMETERS_PREVIOUS_YEAR.dotation_solidarite_urbaine.montant.metropole
    simulation.set_input('dsu_montant_total', PREVIOUS_YEAR, full(NOMBRE_TOTAL_COMMUNES_CURRENT_YEAR, dsu_montant_enveloppe_metropole_previous_year))
    # fin fix

    # Fix montant DSR
    dsr_cible_montant_enveloppe_metropole_previous_year = PARAMETERS_PREVIOUS_YEAR.dotation_solidarite_rurale.cible.montant  # métropole
    simulation.set_input('dsr_montant_total_fraction_cible', PREVIOUS_YEAR, full(NOMBRE_TOTAL_COMMUNES_CURRENT_YEAR, dsr_cible_montant_enveloppe_metropole_previous_year))
    # (constat 2024 : avec ce seul set_input enveloppe DSR 83% des communes ont une DSR calculée > 0)

    dsr_bourg_centre_montant_enveloppe_metropole_previous_year = PARAMETERS_PREVIOUS_YEAR.dotation_solidarite_rurale.bourg_centre.montant  # métropole
    simulation.set_input('dsr_montant_total_fraction_bourg_centre', PREVIOUS_YEAR, [dsr_bourg_centre_montant_enveloppe_metropole_previous_year])  # entité État
    # (constat 2024 : à l'ajout de ce set_input sans effet sur taux global DSR > 0)

    dsr_perequation_montant_enveloppe_metropole_previous_year = PARAMETERS_PREVIOUS_YEAR.dotation_solidarite_rurale.perequation.montant  # métropole
    simulation.set_input('dsr_montant_total_fraction_perequation', PREVIOUS_YEAR, full(NOMBRE_TOTAL_COMMUNES_CURRENT_YEAR, dsr_perequation_montant_enveloppe_metropole_previous_year))
    # (constat 2024 : à l'ajout ce set_input 95% des communes ont une DSR calculée > 0, soit +12%)
    # fin fix

    return simulation


def set_dotations_enveloppes_current_year(simulation: Simulation, current_year):
    # enveloppe écrêtement bloc communal - notes DGCL DF 2025 (page 5) et 2024 (page 5)
    if current_year == 2024:
        # warning : n'a pas été mis en production pour 2024
        # ajouté en 2025, postérieurement à la mise en production de la simulation 2024
        montant_total_ecretement_current_year = 42_096_834
        simulation.set_input('montant_total_ecretement', current_year, [montant_total_ecretement_current_year])

    if current_year == 2025:
        montant_total_ecretement_current_year = 190_023_687
        simulation.set_input('montant_total_ecretement', current_year, [montant_total_ecretement_current_year])

    return simulation


def set_simulation_previous_year_inputs(simulation: Simulation, data_current_year, data_previous_year, period):
    # data_previous_year est un dataframe dont toutes les colonnes
    # portent des noms de variables openfisca
    # et contiennent des valeurs de l'an dernier.

    if data_previous_year is not None:
        # on rassemble les informations de l'an dernier pour les communes
        # qui existent aussi cette année (les valeurs des nouvelles communes sont à zéro)

        # TODO vérifier qu'il ne s'agit pas d'une commune nouvelle ; exemple limite actuelle :
        # on se base sur le code INSEE qui peut être identique d'une année à l'autre
        # alors que la commune a fusionné avec une autre
        full_data = data_current_year.merge(
            data_previous_year,
            on="code_insee",
            how="left",
            suffixes=["_currentyear", ""],
        )

        for champ_openfisca in data_previous_year.columns:
            try:
                # oui c'est comme ça que je checke qu'une variable est openfisca ne me jugez pas
                # si exception, on choisit d'arrêter l'application
                simulation.tax_benefit_system.get_variable(champ_openfisca, check_existence=True)

                simulation.set_input(
                    champ_openfisca,
                    str(int(period) - 1),
                    full_data[champ_openfisca].fillna(0),
                )
            except VariableNotFoundError as vnfe:
                logger.fatal(f"Error while setting up previous year data to '{champ_openfisca}'.")
                raise vnfe
            except ValueError as ve:  # Python buitin exception
                logger.fatal(f"Error while setting up '{champ_openfisca}' with this previous data: {data_previous_year[champ_openfisca]}")
                raise ve

    # initialise les variables d'enveloppes N-1 grâce aux paramètres
    # (pour que N puisse être calculé en fonction de l'augmentation d'enveloppe)
    simulation = set_dotations_enveloppes_previous_year(simulation, data_current_year, period)

    return simulation


def create_simulation_with_data(model, period, data, data_previous_year=None):
    sb = SimulationBuilder()
    sb.create_entities(model)
    sb.declare_person_entity("commune", data.index)

    etat_instance = sb.declare_entity("etat", ["france"])
    nombre_communes = len(data.index)
    etat_communes = ["france"] * nombre_communes
    communes_etats_roles = [None] * nombre_communes  # no roles in our model
    sb.join_with_persons(etat_instance, etat_communes, communes_etats_roles)

    simulation: Simulation = sb.build(model)

    # TODO vérifier nécessité : simulation.max_spiral_loops = 10

    simulation = set_simulation_inputs(simulation, data, period)
    if data_previous_year is None:
        logger.warning("Creating simulation without previous year data.")
    else:
        simulation = set_simulation_previous_year_inputs(simulation, data, data_previous_year, period)

    return simulation
