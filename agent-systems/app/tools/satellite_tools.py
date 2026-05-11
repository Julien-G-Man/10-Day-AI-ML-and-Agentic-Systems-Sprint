
import json, math
from langchain.tools import tool
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

# Mock satellite database (in production: call space-track.org or celestrak.com)
SATELLITE_DB = {
    'iss': {'norad':25544,'name':'International Space Station','altitude_km':420,
    'inclination_deg':51.6,'velocity_kms':7.66,'operator':'NASA/Roscosmos/JAXA/ESA/CSA',
        'launched':'1998-11-20','mass_kg':444615,'purpose':'crewed research station'},
    'hubble': {'norad':20580,'name':'Hubble Space Telescope','altitude_km':547,
        'inclination_deg':28.5,'velocity_kms':7.59,'operator':'NASA',
        'launched':'1990-04-24','mass_kg':11110,'purpose':'optical/UV astronomy'},
    'jwst': {'norad':None,'name':'James Webb Space Telescope','altitude_km':1500000,
        'inclination_deg':None,'velocity_kms':0.5,'operator':'NASA/ESA/CSA',
        'launched':'2021-12-25','mass_kg':6500,'purpose':'infrared astronomy'},
    'sentinel3b': {'norad':43226,'name':'Sentinel-3B','altitude_km':814,
        'inclination_deg':98.6,'velocity_kms':7.40,'operator':'ESA',
        'launched':'2018-04-25','mass_kg':1150,'purpose':'Earth observation'},
    'starlink': {'norad':'48274+','name':'Starlink Constellation','altitude_km':550,
        'inclination_deg':53,'velocity_kms':7.61,'operator':'SpaceX',
        'launched':'2019-present','mass_kg':310,'purpose':'broadband internet'},
}

@tool
def lookup_satellite_database(satellite_name: str) -> str:
    """
    Look up orbital and technical parameters for a satellite from the internal database.
    Use this FIRST when asked about any satellite. Supports: ISS, Hubble, JWST,
    Sentinel-3B, Starlink. Returns JSON with altitude, inclination, operator, purpose.
    """
    key = satellite_name.lower().replace('-','').replace(' ','').replace('_','')
    # Fuzzy matching
    for db_key, data in SATELLITE_DB.items():
        if db_key in key or key in db_key or satellite_name.lower() in data['name'].lower():
            return json.dumps(data, indent=2)
    return json.dumps({'error': f'Satellite "{satellite_name}" not found.',
                        'available': list(SATELLITE_DB.keys())})

class OrbitalCalcInput(BaseModel):
    altitude_km: float = Field(..., description='Orbital altitude above Earth surface in km')
    mass_kg: float     = Field(None, description='Optional satellite mass in kg')

def _calc_orbital(altitude_km: float, mass_kg: float = None) -> str:
    R_earth = 6371.0
    mu      = 398600.4418
    a       = R_earth + altitude_km
    T_min   = round(2 * math.pi * math.sqrt(a**3 / mu) / 60, 2)
    v_kms   = round(math.sqrt(mu / a), 3)
    orbits_per_day = round(1440 / T_min, 2)
    result = {
        'altitude_km': altitude_km,
        'semi_major_axis_km': round(a, 1),
        'orbital_period_min': T_min,
        'orbital_period_hrs': round(T_min/60, 3),
        'orbital_velocity_kms': v_kms,
        'orbital_velocity_kmh': round(v_kms*3600, 0),
        'orbits_per_day': orbits_per_day,
    }
    return json.dumps(result, indent=2)

calculate_orbital_params = StructuredTool.from_function(
    func=_calc_orbital,
    name='calculate_orbital_params',
    description=(
        'Calculate orbital mechanics parameters given altitude. '
        'Returns period, velocity, and orbits per day. '
        'Use when you need to compute or verify orbital values.'
    ),
    args_schema=OrbitalCalcInput,
)
