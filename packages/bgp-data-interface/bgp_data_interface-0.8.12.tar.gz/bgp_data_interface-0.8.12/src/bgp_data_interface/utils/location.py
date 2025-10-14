from typing import Any

ABP = 'ABP'
ABPR = 'ABPR'
BBO = 'BBO'
BHH = 'BHH'
BIH = 'BIH'
BIP = 'BIP'
BND = 'BND'
BTW = 'BTW'
BKKH = 'BKKH'
BPLC = 'BPLC'
CWD = 'CWD'
CWT = 'CWT'
GLB = 'GLB'
LKB = 'LKB'
NGC = 'NGC'
SAI = 'SAI'
SPG = 'SPG'
VHH = 'VHH'


CNX = 'CNX'
DMK = 'DMK'
KOP = 'KOP'
PHS = 'PHS'
SVB = 'SVB'
UTP = 'UTP'


_sites: dict[str, Any] = {
    ABP: {
        'name': 'Amata Chonburi',
        'abbreviation': ABP,
        'latitude': 13.438325247289432,
        'longitude': 101.03261043520196,
    },
    ABPR: {
        'name': 'Amata Rayong',
        'abbreviation': ABPR,
        'latitude': 12.967463192203619,
        'longitude': 101.10886287800753,
    },
    BBO: {
        'name': 'Bang Bo',
        'abbreviation': BBO,
        'latitude': 13.4916354486428,
        'longitude': 100.85609829815238,
    },
    BHH: {
        'name': 'Blueport Hua Hin',
        'abbreviation': BHH,
        'latitude': 12.54791708446621,
        'longitude': 99.96218792521458,
    },
    # BIH: {  # close to SPG
    #     'name': 'Bumrungrad International Hospital',
    #     'abbreviation': BIH,
    #     'latitude': 13.746793044020455, 
    #     'longitude': 100.55249747106282,
    # },
    BIP: {
        'name': 'Bangkadi',
        'abbreviation': BIP,
        'latitude': 13.981568940669403,
        'longitude': 100.56130494764083,
    },
    # BKKH: { # close to GLB
    #     'name': 'Bangkok Hospital',
    #     'abbreviation': BKKH,
    #     'latitude': 13.749001709309066, 
    #     'longitude': 100.58323779481869,
    # },
    BND: {
        'name': 'Ban Na Derm',
        'abbreviation': BND,
        'latitude': 8.856461,
        'longitude': 99.331357,
    },
    BPLC: {
        'name': 'Laem Chabang',
        'abbreviation': BPLC,
        'latitude': 13.088506958504015,
        'longitude': 100.90629722775577,
    },
    BTW: {
        'name': 'Bo Thong Wind Farm',
        'abbreviation': BTW,
        'latitude': 16.391435,
        'longitude': 104.416524,
    },
    # CWD: { # close to SPG
    #     'name': 'Central World Department Store',
    #     'abbreviation': CWD,
    #     'latitude': 13.746794224603907,
    #     'longitude': 100.53918098289748,
    # },
    CWT: {
        'name': 'CW Tower',
        'abbreviation': CWD,
        'latitude': 13.769935623362223,
        'longitude': 100.57372454764186,
    },
    GLB: {
        'name': 'Gerhard Link',
        'abbreviation': GLB,
        'latitude': 13.749774021289749,
        'longitude': 100.6470687945474,
        'fusion_solar_code': '49730507',
    },
    # LKB: { # close to SVB
    #     'name': 'Ladkrabang',
    #     'abbreviation': LKB,
    #     'latitude': 13.751965,
    #     'longitude': 100.825256,
    # },
    NGC: {
        'name': 'Nongchok',
        'abbreviation': NGC,
        'latitude': 13.911125,
        'longitude': 100.859104,
    },
    SAI: {
        'name': 'Sai Noi, Nonthaburi',
        'abbreviation': SAI,
        'latitude': 14.093072,
        'longitude': 100.28938,
    },
    SPG: {
        'name': 'Siam Paragon',
        'abbreviation': SPG,
        'latitude': 13.747353387161175,
        'longitude': 100.53387853680702,
    },
    VHH: {
        'name': 'Veranda Hua Hin',
        'abbreviation': VHH,
        'latitude': 12.740478045961716,
        'longitude': 99.96559233685912,
        'fusion_solar_code': '51085076',
    },
}

_airports: dict[str, Any] = {
    CNX: {
        'name': 'Chiang Mai International Airport',
        'abbreviation': CNX,
        'latitude': 18.7694865813824,
        'longitude': 98.96814618111513,
        'weather_underground_code': 'VTCC:9:TH',
    },
    DMK: {
        'name': 'Don Mueang Airport',
        'abbreviation': DMK,
        'latitude': 13.916006191931878,
        'longitude': 100.60539905456106,
        'weather_underground_code': 'VTBD:9:TH',
    },
    KOP: {
        'name': 'Nakhon Phanom Airport',
        'abbreviation': KOP,
        'latitude': 17.388842796606305,
        'longitude': 104.6448075345258,
        'weather_underground_code': 'VTUW:9:TH',
    },
    PHS: {
        'name': 'Phitsanulok Airport',
        'abbreviation': PHS,
        'latitude': 16.7717275230451,
        'longitude': 100.28138323875666,
        'weather_underground_code': 'VTPP:9:TH',
    },
    SVB: {
        'name': 'Suvarnabhumi Airport',
        'abbreviation': SVB,
        'latitude': 13.683402925860605,
        'longitude': 100.74685929073979,
        'weather_underground_code': 'VTBS:9:TH',
    },
    UTP: {
        'name': 'U-Tapao Pattaya Airport',
        'abbreviation': UTP,
        'latitude': 12.677823039377754, 
        'longitude': 100.99820270651894,
        'weather_underground_code': 'VTBU:9:TH',
    },
}

_locations: dict[str, Any] = {
    **_sites,
    **_airports,
}

def get_site_keys() -> list[str]:
    return list(_sites.keys())

def get_airport_keys() -> list[str]:
    return list(_airports.keys())

def get_location_keys() -> list[str]:
    return list(_locations.keys())

def get_site(name: str) -> dict[str, Any]:
    return _sites.get(name, {})

def get_airport(name: str) -> dict[str, Any]:
    return _airports.get(name, {})

def get_location(name: str) -> dict[str, Any]:
    return _locations.get(name, {})

def get_latlong(name: str) -> dict[str, float]:
    location = get_location(name)

    return {
        'latitude': location.get('latitude', 0.0),
        'longitude': location.get('longitude', 0.0)
    }
