import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from leximpact_dotations_back.computing.calculate_impact import calculate_impact_base, calculate_impact_reform
from leximpact_dotations_back.computing.calculate_impact_commune import format_commune_impact
from leximpact_dotations_back.computing.compare import add_reform_to_base_strates_trends
from leximpact_dotations_back.computing.dotations_simulation import DotationsSimulation

from leximpact_dotations_back.computing.reform import (
    get_reformed_dotations_simulation,
    reform_from_amendement,
    reform_from_plf
)
from leximpact_dotations_back.configure_logging import formatter
from leximpact_dotations_back.main_types import (
    ApiCommuneRequest, ApiCommuneResponse,
    ApiCalculateRequest, ApiCalculateResponse
)
from leximpact_dotations_back.preload import configuration, MODEL_OFDL_BASE
from importlib.metadata import version, distributions


# configure _root_ logger
logger = logging.getLogger()
logging.basicConfig(level=configuration['logging_level'])
if logger.hasHandlers():
    logger.handlers.clear()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


@asynccontextmanager
async def lifespan_logic(app: FastAPI):
    '''
    Manage lifespan stratup and shutdown logic.
    Allows for async preload during app initialisation.
    '''
    # code à exécuter à l'entrée dans le contexte
    # avant que l'application ne démarre le traitement de toute requête
    simulation_year = configuration['year_period']

    logger.info(f"▶️  Démarrage de l'API web pour une simulation de l'année {simulation_year}. Préchargement des données...")
    dotations_simulation = DotationsSimulation(
        data_directory=configuration['data_directory'],
        model=MODEL_OFDL_BASE,
        annee=simulation_year
    )

    app.state.dotations_simulation = dotations_simulation

    # TODO conserver les informations du département
    logger.debug(f"Nombre de communes identifiées: { dotations_simulation.adapted_criteres.shape[0] }")

    yield
    # à faire suivre de tout code à exécuter à la sortie du contexte


app = FastAPI(lifespan=lifespan_logic)

try:
    origins = configuration['api_origins']
except ValueError:
    origins = ["https://leximpact.an.fr"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*.leximpact.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    logger.debug("GET /")
    leximpact_dotations_back_version = version('leximpact-dotations-back')
    return {
        "INFO": f"Bienvenue sur le service d'API web de leximpact-dotations-back v.{leximpact_dotations_back_version} ! Pour en savoir plus, consulter la page /docs"
    }


@app.get("/dependencies")
def read_dependencies():
    logger.debug("GET /dependencies")

    # limit to a specific list of packages
    selected_dependencies = [
        'leximpact-dotations-back',
        'OpenFisca-Core', 'OpenFisca-France-Dotations-Locales',
        'numpy', 'fastapi'
    ]
    # get the distribution objects for all installed packages
    packages_info = {}
    for dist in distributions():
        dependency_name = dist.metadata["Name"]
        if dependency_name in selected_dependencies:
            packages_info[dependency_name] = dist.version
    return packages_info


@app.post("/commune", response_model=ApiCommuneResponse)
async def commune(commune: ApiCommuneRequest):
    logger.debug("POST /commune")

    dotations_simulation_base = app.state.dotations_simulation
    response_body: ApiCommuneResponse = format_commune_impact(commune, dotations_simulation_base)

    return response_body


@app.post("/calculate", response_model=ApiCalculateResponse)
async def calculate(request: ApiCalculateRequest):
    logger.debug("POST /calculate")

    YEAR = configuration['year_period']
    dotations_simulation_base = app.state.dotations_simulation  # TODO adapter à configuration['year_period']

    CONFIGURED_PLF = configuration['next_year_plf']
    activatePlf = CONFIGURED_PLF is not None and CONFIGURED_PLF != ""  # TODO adapter à la valeur de PLF configurée

    # construit la réponse en enrichissant le contenu de la requete
    base_response = calculate_impact_base(
        dotations_simulation_base,
        request.base,
        YEAR
    )  # conserve request.base.dotations

    response_body: ApiCalculateResponse = {
        "base": base_response
    }

    MODEL_OFDL_PLF = None
    if activatePlf and request.plf and request.plf.dotations:
        MODEL_OFDL_PLF = reform_from_plf(MODEL_OFDL_BASE, request.plf.dotations)
        NEXT_YEAR = YEAR + 1

        dotations_simulation_plf_next_year = get_reformed_dotations_simulation(
            MODEL_OFDL_PLF,
            configuration['data_directory'],
            NEXT_YEAR,
            # reformed_parameters = request.plf.dotations
        )

        plf_response = calculate_impact_reform(
            dotations_simulation_plf_next_year,
            request.plf,
            NEXT_YEAR
        )  # conserve request.plf.dotations

        response_body['plf'] = plf_response

    if request.amendement and request.amendement.dotations:
        if MODEL_OFDL_PLF is None:
            logger.debug("En l'absence de PLF, calcule l'amendement sur la base de la loi en vigueur...")
            amendement_model = reform_from_amendement(MODEL_OFDL_BASE, request.amendement.dotations, YEAR)
        else:
            logger.debug("Un PLF a été défini, calcule l'amendement sur la base du PLF...")
            amendement_model = reform_from_amendement(MODEL_OFDL_PLF, request.amendement.dotations, NEXT_YEAR)

        dotations_simulation_amendement_current_year = get_reformed_dotations_simulation(
            amendement_model,
            configuration['data_directory'],
            YEAR,
            # reformed_parameters = request.amendement.dotations
        )

        amendement_response = calculate_impact_reform(
            dotations_simulation_amendement_current_year,
            request.amendement,
            YEAR
        )  # conserve request.amendement.dotations

        # par strate, ajoute la comparaison de la réforme par rapport à 'base'
        amendement_response["strates"] = add_reform_to_base_strates_trends(base_response.strates, amendement_response.strates)

        response_body["amendement"] = amendement_response

    return response_body
