from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy as sa
from db.database import SessionLocal

from fastapi.staticfiles import StaticFiles
from pathlib import Path
from routers import competitions, payments, judges, certificates, divisions, athletes, ranking, disciplines, participants, results, auth, judges, organizers, coaches, teams, matches, asl


WSM_COUNTRIES = {
    "AFG": {"name": "Afghanistan", "iso": "af"},
    "ALB": {"name": "Albania", "iso": "al"},
    "ALG": {"name": "Algeria", "iso": "dz"},
    "AND": {"name": "Andorra", "iso": "ad"},
    "ANG": {"name": "Angola", "iso": "ao"},
    "ANT": {"name": "Antigua & Barbuda", "iso": "ag"},
    "ARG": {"name": "Argentina", "iso": "ar"},
    "ARM": {"name": "Armenia", "iso": "am"},
    "ARU": {"name": "Aruba", "iso": "aw"},
    "AUS": {"name": "Australia", "iso": "au"},
    "AUT": {"name": "Austria", "iso": "at"},
    "AZE": {"name": "Azerbaijan", "iso": "az"},
    "BAH": {"name": "Bahamas", "iso": "bs"},
    "BHR": {"name": "Bahrain", "iso": "bh"},
    "BAN": {"name": "Bangladesh", "iso": "bd"},
    "BAR": {"name": "Barbados", "iso": "bb"},
    "BLR": {"name": "Belarus", "iso": "by"},
    "BEL": {"name": "Belgium", "iso": "be"},
    "BIZ": {"name": "Belize", "iso": "bz"},
    "BEN": {"name": "Benin", "iso": "bj"},
    "BHU": {"name": "Bhutan", "iso": "bt"},
    "BOL": {"name": "Bolivia", "iso": "bo"},
    "BIH": {"name": "Bosnia & Herzegovina", "iso": "ba"},
    "BOT": {"name": "Botswana", "iso": "bw"},
    "BRA": {"name": "Brazil", "iso": "br"},
    "BRN": {"name": "Brunei", "iso": "bn"},
    "BUL": {"name": "Bulgaria", "iso": "bg"},
    "BUR": {"name": "Burkina Faso", "iso": "bf"},
    "BDI": {"name": "Burundi", "iso": "bi"},
    "CAM": {"name": "Cambodia", "iso": "kh"},
    "CMR": {"name": "Cameroon", "iso": "cm"},
    "CAN": {"name": "Canada", "iso": "ca"},
    "CPV": {"name": "Cape Verde", "iso": "cv"},
    "CAF": {"name": "Central African Rep.", "iso": "cf"},
    "CHA": {"name": "Chad", "iso": "td"},
    "CHI": {"name": "Chile", "iso": "cl"},
    "CHN": {"name": "China", "iso": "cn"},
    "COL": {"name": "Colombia", "iso": "co"},
    "COM": {"name": "Comoros", "iso": "km"},
    "CGO": {"name": "Congo", "iso": "cg"},
    "COD": {"name": "DR Congo", "iso": "cd"},
    "CRC": {"name": "Costa Rica", "iso": "cr"},
    "CRO": {"name": "Croatia", "iso": "hr"},
    "CUB": {"name": "Cuba", "iso": "cu"},
    "CYP": {"name": "Cyprus", "iso": "cy"},
    "CZE": {"name": "Czech Republic", "iso": "cz"},
    "DEN": {"name": "Denmark", "iso": "dk"},
    "DJI": {"name": "Djibouti", "iso": "dj"},
    "DOM": {"name": "Dominican Republic", "iso": "do"},
    "ECU": {"name": "Ecuador", "iso": "ec"},
    "EGY": {"name": "Egypt", "iso": "eg"},
    "ESA": {"name": "El Salvador", "iso": "sv"},
    "GEQ": {"name": "Equatorial Guinea", "iso": "gq"},
    "ERI": {"name": "Eritrea", "iso": "er"},
    "EST": {"name": "Estonia", "iso": "ee"},
    "ETH": {"name": "Ethiopia", "iso": "et"},
    "FIJ": {"name": "Fiji", "iso": "fj"},
    "FIN": {"name": "Finland", "iso": "fi"},
    "FRA": {"name": "France", "iso": "fr"},
    "GAB": {"name": "Gabon", "iso": "ga"},
    "GAM": {"name": "Gambia", "iso": "gm"},
    "GEO": {"name": "Georgia", "iso": "ge"},
    "GER": {"name": "Germany", "iso": "de"},
    "GHA": {"name": "Ghana", "iso": "gh"},
    "GBR": {"name": "Great Britain", "iso": "gb"},
    "GRE": {"name": "Greece", "iso": "gr"},
    "GRN": {"name": "Grenada", "iso": "gd"},
    "GUA": {"name": "Guatemala", "iso": "gt"},
    "GUI": {"name": "Guinea", "iso": "gn"},
    "GBS": {"name": "Guinea-Bissau", "iso": "gw"},
    "GUY": {"name": "Guyana", "iso": "gy"},
    "HAI": {"name": "Haiti", "iso": "ht"},
    "HON": {"name": "Honduras", "iso": "hn"},
    "HKG": {"name": "Hong Kong", "iso": "hk"},
    "HUN": {"name": "Hungary", "iso": "hu"},
    "ISL": {"name": "Iceland", "iso": "is"},
    "IND": {"name": "India", "iso": "in"},
    "INA": {"name": "Indonesia", "iso": "id"},
    "IRI": {"name": "Iran", "iso": "ir"},
    "IRQ": {"name": "Iraq", "iso": "iq"},
    "IRL": {"name": "Ireland", "iso": "ie"},
    "ISR": {"name": "Israel", "iso": "il"},
    "ITA": {"name": "Italy", "iso": "it"},
    "CIV": {"name": "Ivory Coast", "iso": "ci"},
    "JAM": {"name": "Jamaica", "iso": "jm"},
    "JPN": {"name": "Japan", "iso": "jp"},
    "JOR": {"name": "Jordan", "iso": "jo"},
    "KAZ": {"name": "Kazakhstan", "iso": "kz"},
    "KEN": {"name": "Kenya", "iso": "ke"},
    "PRK": {"name": "North Korea", "iso": "kp"},
    "KOR": {"name": "South Korea", "iso": "kr"},
    "KUW": {"name": "Kuwait", "iso": "kw"},
    "KGZ": {"name": "Kyrgyzstan", "iso": "kg"},
    "LAO": {"name": "Laos", "iso": "la"},
    "LAT": {"name": "Latvia", "iso": "lv"},
    "LIB": {"name": "Lebanon", "iso": "lb"},
    "LES": {"name": "Lesotho", "iso": "ls"},
    "LBR": {"name": "Liberia", "iso": "lr"},
    "LBA": {"name": "Libya", "iso": "ly"},
    "LIE": {"name": "Liechtenstein", "iso": "li"},
    "LTU": {"name": "Lithuania", "iso": "lt"},
    "LUX": {"name": "Luxembourg", "iso": "lu"},
    "MAD": {"name": "Madagascar", "iso": "mg"},
    "MAW": {"name": "Malawi", "iso": "mw"},
    "MAS": {"name": "Malaysia", "iso": "my"},
    "MDV": {"name": "Maldives", "iso": "mv"},
    "MLI": {"name": "Mali", "iso": "ml"},
    "MLT": {"name": "Malta", "iso": "mt"},
    "MTN": {"name": "Mauritania", "iso": "mr"},
    "MRI": {"name": "Mauritius", "iso": "mu"},
    "MEX": {"name": "Mexico", "iso": "mx"},
    "MDA": {"name": "Moldova", "iso": "md"},
    "MON": {"name": "Monaco", "iso": "mc"},
    "MGL": {"name": "Mongolia", "iso": "mn"},
    "MNE": {"name": "Montenegro", "iso": "me"},
    "MAR": {"name": "Morocco", "iso": "ma"},
    "MOZ": {"name": "Mozambique", "iso": "mz"},
    "MYA": {"name": "Myanmar", "iso": "mm"},
    "NAM": {"name": "Namibia", "iso": "na"},
    "NEP": {"name": "Nepal", "iso": "np"},
    "NED": {"name": "Netherlands", "iso": "nl"},
    "NZL": {"name": "New Zealand", "iso": "nz"},
    "NCA": {"name": "Nicaragua", "iso": "ni"},
    "NIG": {"name": "Niger", "iso": "ne"},
    "NGR": {"name": "Nigeria", "iso": "ng"},
    "NOR": {"name": "Norway", "iso": "no"},
    "OMA": {"name": "Oman", "iso": "om"},
    "PAK": {"name": "Pakistan", "iso": "pk"},
    "PAN": {"name": "Panama", "iso": "pa"},
    "PNG": {"name": "Papua New Guinea", "iso": "pg"},
    "PAR": {"name": "Paraguay", "iso": "py"},
    "PER": {"name": "Peru", "iso": "pe"},
    "PHI": {"name": "Philippines", "iso": "ph"},
    "PLE": {"name": "Palestine", "iso": "ps"},
    "POL": {"name": "Poland", "iso": "pl"},
    "POR": {"name": "Portugal", "iso": "pt"},
    "PUR": {"name": "Puerto Rico", "iso": "pr"},
    "QAT": {"name": "Qatar", "iso": "qa"},
    "ROU": {"name": "Romania", "iso": "ro"},
    "RUS": {"name": "Russia", "iso": "ru"},
    "RWA": {"name": "Rwanda", "iso": "rw"},
    "SKN": {"name": "Saint Kitts & Nevis", "iso": "kn"},
    "STP": {"name": "Sao Tome & Principe", "iso": "st"},
    "KSA": {"name": "Saudi Arabia", "iso": "sa"},
    "SEN": {"name": "Senegal", "iso": "sn"},
    "SRB": {"name": "Serbia", "iso": "rs"},
    "SEY": {"name": "Seychelles", "iso": "sc"},
    "SLE": {"name": "Sierra Leone", "iso": "sl"},
    "SGP": {"name": "Singapore", "iso": "sg"},
    "SVK": {"name": "Slovakia", "iso": "sk"},
    "SLO": {"name": "Slovenia", "iso": "si"},
    "SOL": {"name": "Solomon Islands", "iso": "sb"},
    "SOM": {"name": "Somalia", "iso": "so"},
    "RSA": {"name": "South Africa", "iso": "za"},
    "ESP": {"name": "Spain", "iso": "es"},
    "SRI": {"name": "Sri Lanka", "iso": "lk"},
    "SUD": {"name": "Sudan", "iso": "sd"},
    "SUR": {"name": "Suriname", "iso": "sr"},
    "SWZ": {"name": "Eswatini", "iso": "sz"},
    "SWE": {"name": "Sweden", "iso": "se"},
    "SUI": {"name": "Switzerland", "iso": "ch"},
    "SYR": {"name": "Syria", "iso": "sy"},
    "TPE": {"name": "Chinese Taipei", "iso": "tw"},
    "TJK": {"name": "Tajikistan", "iso": "tj"},
    "TAN": {"name": "Tanzania", "iso": "tz"},
    "THA": {"name": "Thailand", "iso": "th"},
    "TLS": {"name": "Timor-Leste", "iso": "tl"},
    "TOG": {"name": "Togo", "iso": "tg"},
    "TTO": {"name": "Trinidad & Tobago", "iso": "tt"},
    "TUN": {"name": "Tunisia", "iso": "tn"},
    "TUR": {"name": "Turkey", "iso": "tr"},
    "TKM": {"name": "Turkmenistan", "iso": "tm"},
    "UGA": {"name": "Uganda", "iso": "ug"},
    "UKR": {"name": "Ukraine", "iso": "ua"},
    "UAE": {"name": "UAE", "iso": "ae"},
    "GBR": {"name": "United Kingdom", "iso": "gb"},
    "USA": {"name": "USA", "iso": "us"},
    "URU": {"name": "Uruguay", "iso": "uy"},
    "UZB": {"name": "Uzbekistan", "iso": "uz"},
    "VAN": {"name": "Vanuatu", "iso": "vu"},
    "VEN": {"name": "Venezuela", "iso": "ve"},
    "VIE": {"name": "Vietnam", "iso": "vn"},
    "YEM": {"name": "Yemen", "iso": "ye"},
    "ZAM": {"name": "Zambia", "iso": "zm"},
    "ZIM": {"name": "Zimbabwe", "iso": "zw"},
}

def country_flag_html(code):
    if not code:
        return "—"
    c = WSM_COUNTRIES.get(code.upper())
    if c:
        return f'<img src="https://flagcdn.com/w20/{c["iso"]}.png" width="20" height="14" title="{c["name"]}" style="vertical-align:middle;margin-right:4px;"> {code}'
    return code

def country_flag_html(code):
    if not code:
        return "—"
    c = WSM_COUNTRIES.get(code.upper())
    if c:
        return f'<img src="https://flagcdn.com/w20/{c["iso"]}.png" width="20" height="14" title="{c["name"]}" style="vertical-align:middle;margin-right:4px;"> {code}'
    return code


WSM_COUNTRIES = {
    "AFG": {"name": "Afghanistan", "iso": "af"},
    "ALB": {"name": "Albania", "iso": "al"},
    "ALG": {"name": "Algeria", "iso": "dz"},
    "AND": {"name": "Andorra", "iso": "ad"},
    "ANG": {"name": "Angola", "iso": "ao"},
    "ANT": {"name": "Antigua & Barbuda", "iso": "ag"},
    "ARG": {"name": "Argentina", "iso": "ar"},
    "ARM": {"name": "Armenia", "iso": "am"},
    "ARU": {"name": "Aruba", "iso": "aw"},
    "AUS": {"name": "Australia", "iso": "au"},
    "AUT": {"name": "Austria", "iso": "at"},
    "AZE": {"name": "Azerbaijan", "iso": "az"},
    "BAH": {"name": "Bahamas", "iso": "bs"},
    "BHR": {"name": "Bahrain", "iso": "bh"},
    "BAN": {"name": "Bangladesh", "iso": "bd"},
    "BAR": {"name": "Barbados", "iso": "bb"},
    "BLR": {"name": "Belarus", "iso": "by"},
    "BEL": {"name": "Belgium", "iso": "be"},
    "BIZ": {"name": "Belize", "iso": "bz"},
    "BEN": {"name": "Benin", "iso": "bj"},
    "BHU": {"name": "Bhutan", "iso": "bt"},
    "BOL": {"name": "Bolivia", "iso": "bo"},
    "BIH": {"name": "Bosnia & Herzegovina", "iso": "ba"},
    "BOT": {"name": "Botswana", "iso": "bw"},
    "BRA": {"name": "Brazil", "iso": "br"},
    "BRN": {"name": "Brunei", "iso": "bn"},
    "BUL": {"name": "Bulgaria", "iso": "bg"},
    "BUR": {"name": "Burkina Faso", "iso": "bf"},
    "BDI": {"name": "Burundi", "iso": "bi"},
    "CAM": {"name": "Cambodia", "iso": "kh"},
    "CMR": {"name": "Cameroon", "iso": "cm"},
    "CAN": {"name": "Canada", "iso": "ca"},
    "CPV": {"name": "Cape Verde", "iso": "cv"},
    "CAF": {"name": "Central African Rep.", "iso": "cf"},
    "CHA": {"name": "Chad", "iso": "td"},
    "CHI": {"name": "Chile", "iso": "cl"},
    "CHN": {"name": "China", "iso": "cn"},
    "COL": {"name": "Colombia", "iso": "co"},
    "COM": {"name": "Comoros", "iso": "km"},
    "CGO": {"name": "Congo", "iso": "cg"},
    "COD": {"name": "DR Congo", "iso": "cd"},
    "CRC": {"name": "Costa Rica", "iso": "cr"},
    "CRO": {"name": "Croatia", "iso": "hr"},
    "CUB": {"name": "Cuba", "iso": "cu"},
    "CYP": {"name": "Cyprus", "iso": "cy"},
    "CZE": {"name": "Czech Republic", "iso": "cz"},
    "DEN": {"name": "Denmark", "iso": "dk"},
    "DJI": {"name": "Djibouti", "iso": "dj"},
    "DOM": {"name": "Dominican Republic", "iso": "do"},
    "ECU": {"name": "Ecuador", "iso": "ec"},
    "EGY": {"name": "Egypt", "iso": "eg"},
    "ESA": {"name": "El Salvador", "iso": "sv"},
    "GEQ": {"name": "Equatorial Guinea", "iso": "gq"},
    "ERI": {"name": "Eritrea", "iso": "er"},
    "EST": {"name": "Estonia", "iso": "ee"},
    "ETH": {"name": "Ethiopia", "iso": "et"},
    "FIJ": {"name": "Fiji", "iso": "fj"},
    "FIN": {"name": "Finland", "iso": "fi"},
    "FRA": {"name": "France", "iso": "fr"},
    "GAB": {"name": "Gabon", "iso": "ga"},
    "GAM": {"name": "Gambia", "iso": "gm"},
    "GEO": {"name": "Georgia", "iso": "ge"},
    "GER": {"name": "Germany", "iso": "de"},
    "GHA": {"name": "Ghana", "iso": "gh"},
    "GBR": {"name": "Great Britain", "iso": "gb"},
    "GRE": {"name": "Greece", "iso": "gr"},
    "GRN": {"name": "Grenada", "iso": "gd"},
    "GUA": {"name": "Guatemala", "iso": "gt"},
    "GUI": {"name": "Guinea", "iso": "gn"},
    "GBS": {"name": "Guinea-Bissau", "iso": "gw"},
    "GUY": {"name": "Guyana", "iso": "gy"},
    "HAI": {"name": "Haiti", "iso": "ht"},
    "HON": {"name": "Honduras", "iso": "hn"},
    "HKG": {"name": "Hong Kong", "iso": "hk"},
    "HUN": {"name": "Hungary", "iso": "hu"},
    "ISL": {"name": "Iceland", "iso": "is"},
    "IND": {"name": "India", "iso": "in"},
    "INA": {"name": "Indonesia", "iso": "id"},
    "IRI": {"name": "Iran", "iso": "ir"},
    "IRQ": {"name": "Iraq", "iso": "iq"},
    "IRL": {"name": "Ireland", "iso": "ie"},
    "ISR": {"name": "Israel", "iso": "il"},
    "ITA": {"name": "Italy", "iso": "it"},
    "CIV": {"name": "Ivory Coast", "iso": "ci"},
    "JAM": {"name": "Jamaica", "iso": "jm"},
    "JPN": {"name": "Japan", "iso": "jp"},
    "JOR": {"name": "Jordan", "iso": "jo"},
    "KAZ": {"name": "Kazakhstan", "iso": "kz"},
    "KEN": {"name": "Kenya", "iso": "ke"},
    "PRK": {"name": "North Korea", "iso": "kp"},
    "KOR": {"name": "South Korea", "iso": "kr"},
    "KUW": {"name": "Kuwait", "iso": "kw"},
    "KGZ": {"name": "Kyrgyzstan", "iso": "kg"},
    "LAO": {"name": "Laos", "iso": "la"},
    "LAT": {"name": "Latvia", "iso": "lv"},
    "LIB": {"name": "Lebanon", "iso": "lb"},
    "LES": {"name": "Lesotho", "iso": "ls"},
    "LBR": {"name": "Liberia", "iso": "lr"},
    "LBA": {"name": "Libya", "iso": "ly"},
    "LIE": {"name": "Liechtenstein", "iso": "li"},
    "LTU": {"name": "Lithuania", "iso": "lt"},
    "LUX": {"name": "Luxembourg", "iso": "lu"},
    "MAD": {"name": "Madagascar", "iso": "mg"},
    "MAW": {"name": "Malawi", "iso": "mw"},
    "MAS": {"name": "Malaysia", "iso": "my"},
    "MDV": {"name": "Maldives", "iso": "mv"},
    "MLI": {"name": "Mali", "iso": "ml"},
    "MLT": {"name": "Malta", "iso": "mt"},
    "MTN": {"name": "Mauritania", "iso": "mr"},
    "MRI": {"name": "Mauritius", "iso": "mu"},
    "MEX": {"name": "Mexico", "iso": "mx"},
    "MDA": {"name": "Moldova", "iso": "md"},
    "MON": {"name": "Monaco", "iso": "mc"},
    "MGL": {"name": "Mongolia", "iso": "mn"},
    "MNE": {"name": "Montenegro", "iso": "me"},
    "MAR": {"name": "Morocco", "iso": "ma"},
    "MOZ": {"name": "Mozambique", "iso": "mz"},
    "MYA": {"name": "Myanmar", "iso": "mm"},
    "NAM": {"name": "Namibia", "iso": "na"},
    "NEP": {"name": "Nepal", "iso": "np"},
    "NED": {"name": "Netherlands", "iso": "nl"},
    "NZL": {"name": "New Zealand", "iso": "nz"},
    "NCA": {"name": "Nicaragua", "iso": "ni"},
    "NIG": {"name": "Niger", "iso": "ne"},
    "NGR": {"name": "Nigeria", "iso": "ng"},
    "NOR": {"name": "Norway", "iso": "no"},
    "OMA": {"name": "Oman", "iso": "om"},
    "PAK": {"name": "Pakistan", "iso": "pk"},
    "PAN": {"name": "Panama", "iso": "pa"},
    "PNG": {"name": "Papua New Guinea", "iso": "pg"},
    "PAR": {"name": "Paraguay", "iso": "py"},
    "PER": {"name": "Peru", "iso": "pe"},
    "PHI": {"name": "Philippines", "iso": "ph"},
    "PLE": {"name": "Palestine", "iso": "ps"},
    "POL": {"name": "Poland", "iso": "pl"},
    "POR": {"name": "Portugal", "iso": "pt"},
    "PUR": {"name": "Puerto Rico", "iso": "pr"},
    "QAT": {"name": "Qatar", "iso": "qa"},
    "ROU": {"name": "Romania", "iso": "ro"},
    "RUS": {"name": "Russia", "iso": "ru"},
    "RWA": {"name": "Rwanda", "iso": "rw"},
    "SKN": {"name": "Saint Kitts & Nevis", "iso": "kn"},
    "STP": {"name": "Sao Tome & Principe", "iso": "st"},
    "KSA": {"name": "Saudi Arabia", "iso": "sa"},
    "SEN": {"name": "Senegal", "iso": "sn"},
    "SRB": {"name": "Serbia", "iso": "rs"},
    "SEY": {"name": "Seychelles", "iso": "sc"},
    "SLE": {"name": "Sierra Leone", "iso": "sl"},
    "SGP": {"name": "Singapore", "iso": "sg"},
    "SVK": {"name": "Slovakia", "iso": "sk"},
    "SLO": {"name": "Slovenia", "iso": "si"},
    "SOL": {"name": "Solomon Islands", "iso": "sb"},
    "SOM": {"name": "Somalia", "iso": "so"},
    "RSA": {"name": "South Africa", "iso": "za"},
    "ESP": {"name": "Spain", "iso": "es"},
    "SRI": {"name": "Sri Lanka", "iso": "lk"},
    "SUD": {"name": "Sudan", "iso": "sd"},
    "SUR": {"name": "Suriname", "iso": "sr"},
    "SWZ": {"name": "Eswatini", "iso": "sz"},
    "SWE": {"name": "Sweden", "iso": "se"},
    "SUI": {"name": "Switzerland", "iso": "ch"},
    "SYR": {"name": "Syria", "iso": "sy"},
    "TPE": {"name": "Chinese Taipei", "iso": "tw"},
    "TJK": {"name": "Tajikistan", "iso": "tj"},
    "TAN": {"name": "Tanzania", "iso": "tz"},
    "THA": {"name": "Thailand", "iso": "th"},
    "TLS": {"name": "Timor-Leste", "iso": "tl"},
    "TOG": {"name": "Togo", "iso": "tg"},
    "TTO": {"name": "Trinidad & Tobago", "iso": "tt"},
    "TUN": {"name": "Tunisia", "iso": "tn"},
    "TUR": {"name": "Turkey", "iso": "tr"},
    "TKM": {"name": "Turkmenistan", "iso": "tm"},
    "UGA": {"name": "Uganda", "iso": "ug"},
    "UKR": {"name": "Ukraine", "iso": "ua"},
    "UAE": {"name": "UAE", "iso": "ae"},
    "GBR": {"name": "United Kingdom", "iso": "gb"},
    "USA": {"name": "USA", "iso": "us"},
    "URU": {"name": "Uruguay", "iso": "uy"},
    "UZB": {"name": "Uzbekistan", "iso": "uz"},
    "VAN": {"name": "Vanuatu", "iso": "vu"},
    "VEN": {"name": "Venezuela", "iso": "ve"},
    "VIE": {"name": "Vietnam", "iso": "vn"},
    "YEM": {"name": "Yemen", "iso": "ye"},
    "ZAM": {"name": "Zambia", "iso": "zm"},
    "ZIM": {"name": "Zimbabwe", "iso": "zw"},
}

def country_flag_html(code):
    if not code:
        return "—"
    c = WSM_COUNTRIES.get(code.upper())
    if c:
        return f'<img src="https://flagcdn.com/w20/{c["iso"]}.png" width="20" height="14" title="{c["name"]}" style="vertical-align:middle;margin-right:4px;"> {code}'
    return code

def country_flag_html(code):
    if not code:
        return "—"
    c = WSM_COUNTRIES.get(code.upper())
    if c:
        return f'<img src="https://flagcdn.com/w20/{c["iso"]}.png" width="20" height="14" title="{c["name"]}" style="vertical-align:middle;margin-right:4px;"> {code}'
    return code

app = FastAPI(title="World Strongman Platform API", version="2.0.0")

@app.get("/google6810233f6ed024b3.html", include_in_schema=False)
async def google_verification():
    from fastapi.responses import HTMLResponse
    return HTMLResponse("google-site-verification: google6810233f6ed024b3.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.ranking.worldstrongman.org", "https://ranking.worldstrongman.org", "https://events.worldstrongman.org"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("uploads/athletes").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(competitions.router)
app.include_router(payments.router)
app.include_router(divisions.router)
app.include_router(athletes.router)
app.include_router(ranking.router)
app.include_router(disciplines.router)
app.include_router(participants.router)
app.include_router(results.router)
app.include_router(auth.router)
app.include_router(judges.router)
app.include_router(certificates.router)
app.include_router(judges.router)
app.include_router(certificates.router)
app.include_router(organizers.router)
app.include_router(coaches.router)
app.include_router(teams.router)
app.include_router(matches.router)
app.include_router(asl.router)


@app.get("/")
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/competitions-list")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-test")
async def db_test():
    async with SessionLocal() as session:
        result = await session.execute(sa.text("SELECT 1"))
        return {"database": "connected", "result": result.scalar()}

from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy import select, desc
from models.athlete import Athlete

templates = Jinja2Templates(directory="templates")
templates.env.globals["WSM_COUNTRIES"] = WSM_COUNTRIES

@app.get("/countries")
async def get_countries():
    return [{"code": k, "name": v["name"], "iso": v["iso"]} for k, v in sorted(WSM_COUNTRIES.items(), key=lambda x: x[1]["name"])]

@app.get("/athletes/{athlete_id}/profile")
async def athlete_profile(athlete_id: str, request: Request):
    from db.database import SessionLocal
    import uuid
    async with SessionLocal() as db:
        athlete = await db.get(Athlete, uuid.UUID(athlete_id))
        if not athlete:
            return {"error": "Athlete not found"}

        # Ranking
        ranking = None
        try:
            from models.ranking import Ranking
            r = await db.execute(
                select(Ranking).where(Ranking.athlete_id == uuid.UUID(athlete_id))
            )
            ranking = r.scalar_one_or_none()
        except:
            pass

        # Achievements - топ результаты
        achievements = []
        try:
            from models.result import Result
            from models.participant import Participant
            from models.competition_division import CompetitionDivision
            from models.competition import Competition
            from sqlalchemy.orm import selectinload
            res = await db.execute(
                select(Result)
                .join(Participant, Result.participant_id == Participant.id)
                .where(Participant.athlete_id == uuid.UUID(athlete_id))
                .order_by(desc(Result.points))
                .limit(5)
            )
            raw = res.scalars().all()
            for r in raw:
                participant = await db.get(Participant, r.participant_id)
                div = await db.get(CompetitionDivision, participant.competition_division_id)
                comp = await db.get(Competition, div.competition_id)
                achievements.append({
                    "competition_name": comp.name,
                    "division_name": div.name if hasattr(div, 'name') else "Division",
                    "result": r.points,
                })
        except:
            pass

        # Upcoming competitions
        upcoming = []
        try:
            from models.participant import Participant
            from models.competition_division import CompetitionDivision
            from models.competition import Competition
            import datetime
            parts = await db.execute(
                select(Participant).where(Participant.athlete_id == uuid.UUID(athlete_id))
            )
            for p in parts.scalars().all():
                div = await db.get(CompetitionDivision, p.competition_division_id)
                if div:
                    comp = await db.get(Competition, div.competition_id)
                    if comp and hasattr(comp, 'date') and comp.date and comp.date >= datetime.date.today():
                        upcoming.append({
                            "competition_name": comp.name,
                            "location": getattr(comp, 'location', ''),
                            "division_name": getattr(div, 'name', 'Division'),
                            "date": comp.date,
                        })
        except:
            pass

        # Sponsors
        sponsors = []
        try:
            from models.athlete_sponsor import AthleteSponsor
            sp = await db.execute(
                select(AthleteSponsor).where(AthleteSponsor.athlete_id == uuid.UUID(athlete_id)).limit(3)
            )
            sponsors_raw = sp.scalars().all()
            sponsors = [{'id': str(s.id), 'name': s.name, 'logo_url': s.logo_url or '', 'mc_text': getattr(s, 'mc_text', '') or '', 'website_url': getattr(s, 'website_url', '') or ''} for s in sponsors_raw]
        except:
            pass

        # Competition history для графика
        competition_history = []
        try:
            from models.participant import Participant
            from models.competition_division import CompetitionDivision
            from models.competition import Competition
            from models.overall_standing import OverallStanding
            from sqlalchemy import select as sa_select

            parts_res = await db.execute(
                sa_select(Participant).where(Participant.athlete_id == uuid.UUID(athlete_id))
            )
            for p in parts_res.scalars().all():
                div = await db.get(CompetitionDivision, p.competition_division_id)
                if not div: continue
                comp = await db.get(Competition, div.competition_id)
                if not comp: continue
                overall_res = await db.execute(
                    sa_select(OverallStanding).where(
                        OverallStanding.competition_division_id == div.id,
                        OverallStanding.participant_id == p.id
                    )
                )
                overall = overall_res.scalar_one_or_none()
                if overall:
                    q = float(comp.coefficient_q or 1.0)
                    competition_history.append({
                        "comp_name": comp.name,
                        "date": str(comp.date_start) if comp.date_start else "2026-01-01",
                        "place": overall.overall_place,
                        "points": float(overall.total_points or 0),
                        "weighted": round(float(overall.total_points or 0) * q, 1),
                        "division": div.division_key,
                        "q": q,
                    })
            competition_history.sort(key=lambda x: x["date"])
        except Exception as e:
            print(f"History error: {e}")

        return templates.TemplateResponse("athlete_profile.html", {
            "request": request,
            "athlete": athlete,
            "ranking": ranking,
            "achievements": achievements,
            "upcoming": upcoming,
            "upcoming_count": len(upcoming),
            "sponsors": sponsors,
            "competition_history": competition_history,
        })


@app.get("/api/athletes/search")
async def api_athletes_search(q: str = ""):
    from sqlalchemy import select, or_
    from models.athlete import Athlete
    async with SessionLocal() as db:
        query = select(Athlete).order_by(Athlete.last_name).limit(20)
        if q:
            like = f"%{q}%"
            query = query.where(or_(
                Athlete.first_name.ilike(like),
                Athlete.last_name.ilike(like),
                Athlete.country.ilike(like)
            ))
        result = await db.execute(query)
        athletes = result.scalars().all()
    return [{"id": str(a.id), "first_name": a.first_name or "", "last_name": a.last_name or "", "name": f"{a.first_name} {a.last_name}", "country": a.country or "", "photo": a.photo_url or ""} for a in athletes]

@app.get("/api/coaches/search")
async def api_coaches_search(q: str = ""):
    from sqlalchemy import select, or_
    from models.coach import Coach
    async with SessionLocal() as db:
        query = select(Coach).order_by(Coach.last_name).limit(20)
        if q:
            like = f"%{q}%"
            query = query.where(or_(
                Coach.first_name.ilike(like),
                Coach.last_name.ilike(like),
                Coach.country.ilike(like)
            ))
        result = await db.execute(query)
        coaches = result.scalars().all()
    return [{"id": str(c.id), "name": f"{c.first_name} {c.last_name}", "country": c.country or "", "photo": c.photo_url or ""} for c in coaches]

@app.get("/athletes-list")
async def athletes_list(request: Request):
    from sqlalchemy import select
    from models.athlete import Athlete
    async with SessionLocal() as db:
        result = await db.execute(select(Athlete).order_by(Athlete.last_name))
        athletes = result.scalars().all()
    return templates.TemplateResponse("athletes_list.html", {
        "request": request,
        "athletes": athletes,
    })


@app.get("/judges/{judge_id}/profile")
async def judge_profile(judge_id: str, request: Request):
    import uuid
    from models.judge import Judge
    from models.judge_certificate import JudgeCertificate
    from models.judge_competition import JudgeCompetition
    from models.judge_levels import JudgeLevel, JUDGE_LEVEL_LABELS
    from models.competition import Competition
    from sqlalchemy import select
    async with SessionLocal() as db:
        judge = await db.get(Judge, uuid.UUID(judge_id))
        if not judge:
            return {"error": "Judge not found"}
        certs = await db.execute(
            select(JudgeCertificate).where(JudgeCertificate.judge_id == uuid.UUID(judge_id))
        )
        certificates = certs.scalars().all()
        comps_result = await db.execute(
            select(JudgeCompetition).where(JudgeCompetition.judge_id == uuid.UUID(judge_id))
        )
        comp_assignments = comps_result.scalars().all()
        competitions = []
        for ca in comp_assignments:
            comp = await db.get(Competition, ca.competition_id)
            if comp:
                competitions.append({"competition_name": comp.name, "role": ca.role})
        level_label = JUDGE_LEVEL_LABELS.get(JudgeLevel(judge.level)) if judge.level else None
    return templates.TemplateResponse("judge_profile.html", {
        "request": request,
        "judge": judge,
        "certificates": certificates,
        "competitions": competitions,
        "level_label": level_label,
    })


@app.get("/organizers/{organizer_id}/profile")
async def organizer_profile(organizer_id: str, request: Request):
    import uuid
    from models.organizer import Organizer
    from models.organizer_sponsor import OrganizerSponsor
    from models.competition import Competition
    from sqlalchemy import select
    async with SessionLocal() as db:
        org = await db.get(Organizer, uuid.UUID(organizer_id))
        if not org:
            return {"error": "Organizer not found"}
        sponsors_result = await db.execute(
            select(OrganizerSponsor).where(OrganizerSponsor.organizer_id == uuid.UUID(organizer_id))
            .order_by(OrganizerSponsor.tier)
        )
        sponsors = sponsors_result.scalars().all()
        comps_result = await db.execute(
            select(Competition).where(Competition.organizer_id == uuid.UUID(organizer_id))
            .order_by(Competition.date_start.desc())
        )
        competitions = comps_result.scalars().all()
    return templates.TemplateResponse("organizer_profile.html", {
        "request": request,
        "organizer": org,
        "sponsors": sponsors,
        "competitions": competitions,
    })


@app.get("/judges-list")
async def judges_list(request: Request):
    from sqlalchemy import select
    from models.judge import Judge
    async with SessionLocal() as db:
        result = await db.execute(select(Judge).order_by(Judge.last_name))
        judges = result.scalars().all()
    return templates.TemplateResponse("judges_list.html", {
        "request": request,
        "judges": judges,
    })


@app.get("/organizers-list")
async def organizers_list(request: Request):
    from sqlalchemy import select
    from models.organizer import Organizer
    async with SessionLocal() as db:
        result = await db.execute(select(Organizer).order_by(Organizer.name))
        organizers = result.scalars().all()
    return templates.TemplateResponse("organizers_list.html", {
        "request": request,
        "organizers": organizers,
    })


@app.get("/teams/{team_id}/room")
async def team_room(team_id: str, request: Request):
    from sqlalchemy import select
    from models.team import Team
    from models.team_member import TeamMember
    from models.team_sponsor import TeamSponsor
    from models.athlete import Athlete
    from models.coach import Coach
    from models.match import Match
    import uuid
    tid = uuid.UUID(team_id)
    async with SessionLocal() as db:
        team = await db.get(Team, tid)
        if not team:
            return {"error": "Team not found"}
        members_result = await db.execute(
            select(TeamMember).where(TeamMember.team_id == tid)
        )
        members = members_result.scalars().all()
        for m in members:
            if m.athlete_id:
                m.athlete = await db.get(Athlete, m.athlete_id)
        sponsors_result = await db.execute(
            select(TeamSponsor).where(TeamSponsor.team_id == tid)
        )
        sponsors = sponsors_result.scalars().all()
        coach = await db.get(Coach, team.coach_id) if team.coach_id else None
        matches_result = await db.execute(
            select(Match).where(
                (Match.home_team_id == tid) | (Match.away_team_id == tid)
            ).order_by(Match.round_number, Match.match_date)
        )
        matches = matches_result.scalars().all()
    return templates.TemplateResponse("team_room.html", {
        "request": request,
        "team": team,
        "members": members,
        "sponsors": sponsors,
        "coach": coach,
        "matches": matches,
    })


@app.get("/sitemap.xml")
async def sitemap():
    from fastapi.responses import FileResponse
    return FileResponse("/var/www/wsm-platform/static/sitemap.xml", media_type="application/xml")

@app.get("/robots.txt")
async def robots():
    from fastapi.responses import PlainTextResponse
    content = """User-agent: *
Allow: /
Disallow: /admin
Disallow: /organizer
Sitemap: https://ranking.worldstrongman.org/sitemap.xml"""
    return PlainTextResponse(content)

@app.get("/register/organizer/complete")
async def register_organizer_complete(request: Request):
    return templates.TemplateResponse("register_organizer_complete.html", {"request": request})

@app.get("/register/judge/complete")
async def register_judge_complete(request: Request):
    return templates.TemplateResponse("register_judge_complete.html", {"request": request})

@app.get("/register/team/complete")
async def register_team_complete(request: Request):
    return templates.TemplateResponse("register_team_complete.html", {"request": request})

@app.get("/register/athlete/complete")
async def register_athlete_complete(request: Request):
    return templates.TemplateResponse("register_athlete_complete.html", {"request": request})

@app.get("/competitions/{competition_id}/mc")
async def mc_screen(competition_id: str, request: Request):
    from fastapi import HTTPException
    from models.competition import Competition
    from models.organizer import Organizer
    from models.competition_sponsor import CompetitionSponsor
    import uuid

    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            raise HTTPException(404)

        # Live data
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"http://localhost:8000/competitions/{competition_id}/live-data")
                live_data = r.json()
        except:
            live_data = None

        # Organizer
        organizer = None
        if comp.organizer_id:
            organizer = await db.get(Organizer, comp.organizer_id)

        # Sponsors
        sponsors = []
        from sqlalchemy import select
        sp = await db.execute(select(CompetitionSponsor).where(CompetitionSponsor.competition_id == uuid.UUID(competition_id)))
        sponsors_raw = sp.scalars().all()
        sponsors = [{'id': str(s.id), 'name': s.name, 'logo_url': s.logo_url or '', 'mc_text': getattr(s, 'mc_text', '') or '', 'website_url': getattr(s, 'website_url', '') or ''} for s in sponsors_raw]

        # Program
        program = []
        try:
            from sqlalchemy import select, text
            pr = await db.execute(text("SELECT time_slot, type, title, description, person_name, person_role FROM competition_program WHERE competition_id=:cid ORDER BY order_no, time_slot"), {"cid": competition_id})
            program = [{"time_slot": r[0], "type": r[1], "title": r[2], "description": r[3], "person_name": r[4], "person_role": r[5]} for r in pr.fetchall()]
        except:
            pass

        # Guests
        guests = []
        try:
            from sqlalchemy import text
            gr = await db.execute(text("SELECT name, title, country, photo_url, bio FROM competition_guests WHERE competition_id=:cid ORDER BY order_no"), {"cid": competition_id})
            guests = [{"name": r[0], "title": r[1], "country": r[2], "photo_url": r[3], "bio": r[4]} for r in gr.fetchall()]
        except:
            pass

    return templates.TemplateResponse("mc_screen.html", {
        "request": request,
        "competition": comp,
        "live_data": live_data,
        "organizer": organizer,
        "sponsors": sponsors,
        "program": program,
        "guests": guests,
        "division_name": (live_data.get("divisions") or [{}])[0].get("division_name", "") if live_data else "",
    })

@app.get("/privacy-policy")
async def privacy_policy(request: Request):
    return templates.TemplateResponse("privacy_policy.html", {"request": request})

@app.get("/cookie-policy")
async def cookie_policy(request: Request):
    return templates.TemplateResponse("cookie_policy.html", {"request": request})

@app.get("/asl/divisions/{division_id}")
async def asl_division_page(division_id: str, request: Request):
    from sqlalchemy import select
    from models.asl_league import ASLLeague
    from models.asl_division import ASLDivision
    from models.team_standing import TeamStanding
    from models.team import Team
    from models.match import Match
    from models.match_discipline_result import MatchDisciplineResult
    from collections import defaultdict
    import uuid
    did = uuid.UUID(division_id)
    async with SessionLocal() as db:
        division = await db.get(ASLDivision, did)
        if not division:
            return {"error": "Division not found"}
        league = await db.get(ASLLeague, division.league_id)
        standings_result = await db.execute(
            select(TeamStanding)
            .where(TeamStanding.asl_division_id == did)
            .order_by(TeamStanding.points.desc(), TeamStanding.disciplines_won.desc())
        )
        standings = standings_result.scalars().all()
        team_map = {}
        for s in standings:
            t = await db.get(Team, s.team_id)
            s.team = t
            if t:
                team_map[str(s.team_id)] = t
        matches_result = await db.execute(
            select(Match)
            .where(Match.asl_division_id == did)
            .order_by(Match.round_number, Match.match_date)
        )
        matches = matches_result.scalars().all()
        for m in matches:
            for tid in [m.home_team_id, m.away_team_id]:
                if str(tid) not in team_map:
                    t = await db.get(Team, tid)
                    if t:
                        team_map[str(tid)] = t
        matches_by_round = defaultdict(list)
        for m in matches:
            matches_by_round[m.round_number or 1].append(m)
        discipline_results = {}
        for m in matches:
            if m.status == 'completed':
                dr_result = await db.execute(
                    select(MatchDisciplineResult).where(MatchDisciplineResult.match_id == m.id)
                )
                discipline_results[str(m.id)] = dr_result.scalars().all()
        completed_count = sum(1 for m in matches if m.status == 'completed')
        rounds_order = sorted(matches_by_round.keys())
    return templates.TemplateResponse("asl_division.html", {
        "request": request,
        "league": league,
        "division": division,
        "standings": standings,
        "matches": matches,
        "matches_by_round": dict(matches_by_round),
        "rounds_order": rounds_order,
        "team_map": team_map,
        "discipline_results": discipline_results,
        "completed_count": completed_count,
    })


@app.get("/asl/help")
async def asl_help(request: Request):
    return templates.TemplateResponse("asl_help.html", {"request": request})

@app.get("/asl/match-help")
async def asl_match_help(request: Request):
    return templates.TemplateResponse("asl_match_help.html", {"request": request})

@app.get("/asl/{league_id}")
async def asl_home(league_id: str, request: Request):
    from sqlalchemy import select
    from models.asl_league import ASLLeague
    from models.asl_division import ASLDivision
    from models.asl_team_division import ASLTeamDivision
    from models.team_standing import TeamStanding
    from models.team import Team
    from models.match import Match
    import uuid
    lid = uuid.UUID(league_id)
    async with SessionLocal() as db:
        league = await db.get(ASLLeague, lid)
        if not league:
            return {"error": "League not found"}
        divs_result = await db.execute(
            select(ASLDivision).where(ASLDivision.league_id == lid).order_by(ASLDivision.name)
        )
        divisions = divs_result.scalars().all()
        standings_by_division = {}
        total_teams = 0
        for div in divisions:
            td_result = await db.execute(
                select(ASLTeamDivision).where(ASLTeamDivision.division_id == div.id)
            )
            total_teams += len(td_result.scalars().all())
            s_result = await db.execute(
                select(TeamStanding)
                .where(TeamStanding.asl_division_id == div.id)
                .order_by(TeamStanding.points.desc(), TeamStanding.disciplines_won.desc())
            )
            standings = s_result.scalars().all()
            for s in standings:
                s.team = await db.get(Team, s.team_id)
            standings_by_division[str(div.id)] = standings
        matches_result = await db.execute(
            select(Match).where(Match.asl_division_id.in_([d.id for d in divisions]))
            .order_by(Match.match_date.desc()).limit(20)
        )
        recent_matches = matches_result.scalars().all()
        team_names = {}
        div_names = {str(d.id): d.name for d in divisions}
        for m in recent_matches:
            for tid in [m.home_team_id, m.away_team_id]:
                if str(tid) not in team_names:
                    t = await db.get(Team, tid)
                    if t:
                        team_names[str(tid)] = t.name
        matches_count_result = await db.execute(
            select(Match).where(Match.asl_division_id.in_([d.id for d in divisions]))
        )
        total_matches = len(matches_count_result.scalars().all())
    return templates.TemplateResponse("asl_home.html", {
        "request": request,
        "league": league,
        "divisions": divisions,
        "standings_by_division": standings_by_division,
        "recent_matches": recent_matches,
        "team_names": team_names,
        "div_names": div_names,
        "total_teams": total_teams,
        "total_matches": total_matches,
    })


@app.get("/asl/{league_id}/final-four")
async def asl_final_four(league_id: str, request: Request):
    from sqlalchemy import select
    from models.asl_league import ASLLeague
    from models.asl_division import ASLDivision
    from models.team_standing import TeamStanding
    from models.team import Team
    from models.match import Match
    import uuid
    lid = uuid.UUID(league_id)
    async with SessionLocal() as db:
        league = await db.get(ASLLeague, lid)
        if not league:
            return {"error": "League not found"}
        divs_result = await db.execute(
            select(ASLDivision).where(ASLDivision.league_id == lid).order_by(ASLDivision.name)
        )
        divisions = divs_result.scalars().all()
        # Лидеры каждого дивизиона
        qualifiers = {}
        for div in divisions:
            s_result = await db.execute(
                select(TeamStanding)
                .where(TeamStanding.asl_division_id == div.id)
                .order_by(TeamStanding.points.desc(), TeamStanding.disciplines_won.desc())
                .limit(1)
            )
            top = s_result.scalar_one_or_none()
            if top:
                qualifiers[str(div.id)] = await db.get(Team, top.team_id)
        # Final Four матчи по типу
        ff_matches = await db.execute(
            select(Match).where(
                Match.asl_division_id == None,
                Match.competition_division_id == None
            )
        )
        # Пока финальные матчи хранятся отдельно — упрощённая версия
        sf1 = sf2 = final = third = None
        sf1_teams = sf2_teams = final_teams = third_teams = []
        champion = None
    return templates.TemplateResponse("asl_final_four.html", {
        "request": request,
        "league": league,
        "divisions": divisions,
        "qualifiers": qualifiers,
        "sf1": sf1, "sf1_teams": sf1_teams,
        "sf2": sf2, "sf2_teams": sf2_teams,
        "final": final, "final_teams": final_teams,
        "third": third, "third_teams": third_teams,
        "champion": champion,
    })




@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import FileResponse
    return FileResponse("static/logo.jpg")


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/register/coach")
async def register_coach_page(request: Request):
    return templates.TemplateResponse("register_coach.html", {"request": request})

@app.get("/register/athlete")
async def register_athlete_page(request: Request):
    return templates.TemplateResponse("register_athlete.html", {"request": request})

@app.get("/register/judge")
async def register_judge_page(request: Request):
    return templates.TemplateResponse("register_judge.html", {"request": request})

@app.get("/register/team")
async def register_team_page(request: Request):
    return templates.TemplateResponse("register_team.html", {"request": request})

@app.get("/register/coach")
async def register_coach_page(request: Request):
    return templates.TemplateResponse("register_coach.html", {"request": request})

@app.get("/register/athlete")
async def register_athlete_page(request: Request):
    return templates.TemplateResponse("register_athlete.html", {"request": request})

@app.get("/register/judge")
async def register_judge_page(request: Request):
    return templates.TemplateResponse("register_judge.html", {"request": request})

@app.get("/register/team")
async def register_team_page(request: Request):
    return templates.TemplateResponse("register_team.html", {"request": request})

@app.get("/register/organizer")
async def register_organizer_page(request: Request):
    return templates.TemplateResponse("register_organizer.html", {"request": request})


@app.get("/competitions-list")
async def competitions_list(request: Request):
    from sqlalchemy import select
    from models.competition import Competition
    async with SessionLocal() as db:
        result = await db.execute(select(Competition).where(Competition.status == 'PUBLISHED').order_by(Competition.date_start.desc()))
        competitions = result.scalars().all()
    return templates.TemplateResponse("competitions_list.html", {
        "request": request,
        "competitions": competitions,
    })


@app.get("/teams-list")
async def teams_list_page(request: Request):
    from models.team import Team
    from sqlalchemy import select
    async with SessionLocal() as db:
        result = await db.execute(select(Team).order_by(Team.name))
        teams = result.scalars().all()
    return templates.TemplateResponse("teams_list.html", {
        "request": request,
        "teams": teams,
    })


@app.get("/competitions/{competition_id}/page")
async def competition_page(competition_id: str, request: Request):
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.athlete import Athlete
    from models.discipline_result import DisciplineResult
    from models.discipline_standing import DisciplineStanding
    from models.overall_standing import OverallStanding
    from sqlalchemy import select
    import uuid

    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            return templates.TemplateResponse("404.html", {"request": request})

        # Дивизионы
        divs_result = await db.execute(
            select(CompetitionDivision).where(CompetitionDivision.competition_id == uuid.UUID(competition_id))
        )
        divisions = divs_result.scalars().all()

        divisions_data = []
        for div in divisions:
            # Дисциплины
            discs_result = await db.execute(
                select(CompetitionDiscipline)
                .where(CompetitionDiscipline.competition_division_id == div.id)
                .order_by(CompetitionDiscipline.order_no)
            )
            disciplines = discs_result.scalars().all()

            # Участники
            parts_result = await db.execute(
                select(Participant).where(Participant.competition_division_id == div.id)
                .order_by(Participant.lot_number, Participant.bib_no)
            )
            participants = parts_result.scalars().all()

            # Атлеты
            athlete_map = {}
            for p in participants:
                ath = await db.get(Athlete, p.athlete_id)
                if ath:
                    athlete_map[str(p.id)] = ath

            # Результаты по дисциплинам
            results_map = {}  # discipline_id -> {participant_id -> result}
            standings_map = {}  # discipline_id -> {participant_id -> standing}
            for disc in disciplines:
                res_result = await db.execute(
                    select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc.id)
                )
                results_map[str(disc.id)] = {str(r.participant_id): r for r in res_result.scalars().all()}

                st_result = await db.execute(
                    select(DisciplineStanding).where(DisciplineStanding.competition_discipline_id == disc.id)
                )
                standings_map[str(disc.id)] = {str(s.participant_id): s for s in st_result.scalars().all()}

            # Overall standings
            overall_result = await db.execute(
                select(OverallStanding).where(OverallStanding.competition_division_id == div.id)
                .order_by(OverallStanding.overall_place)
            )
            overall_standings = {str(o.participant_id): o for o in overall_result.scalars().all()}

            # Порядок старта для каждой дисциплины
            start_orders = {}
            for i, disc in enumerate(disciplines):
                if i == 0:
                    # Первая - по жеребьёвке
                    ordered = sorted(participants, key=lambda p: (p.lot_number or 999, p.bib_no or 999))
                elif disc.is_final or i == len(disciplines) - 1:
                    # Финальная - реверс по очкам
                    def get_points(p):
                        o = overall_standings.get(str(p.id))
                        return float(o.total_points) if o else 0
                    ordered = sorted(participants, key=get_points)
                else:
                    # Остальные - реверс по месту в предыдущей
                    prev_disc = disciplines[i-1]
                    def get_prev_place(p):
                        st = standings_map.get(str(prev_disc.id), {}).get(str(p.id))
                        return st.place if st and hasattr(st, 'place') else 999
                    ordered = sorted(participants, key=get_prev_place, reverse=True)
                start_orders[str(disc.id)] = {str(p.id): idx+1 for idx, p in enumerate(ordered)}

            sorted_participants = sorted(
                participants,
                key=lambda p: overall_standings[str(p.id)].overall_place
                    if overall_standings.get(str(p.id)) and overall_standings[str(p.id)].overall_place
                    else 999
            )
            divisions_data.append({
                "division": div,
                "disciplines": disciplines,
                "participants": sorted_participants,
                "athlete_map": athlete_map,
                "results_map": results_map,
                "standings_map": standings_map,
                "overall_standings": overall_standings,
                "start_orders": start_orders,
            })

        # Organizer
        organizer = None
        if comp.organizer_id:
            from models.organizer import Organizer
            organizer = await db.get(Organizer, comp.organizer_id)

        # Competition sponsors (model may not exist yet)
        sponsors = []
        try:
            from models.competition_sponsor import CompetitionSponsor as CS
            sponsors_result = await db.execute(
                select(CS).where(CS.competition_id == uuid.UUID(competition_id))
            )
            sponsors = sponsors_result.scalars().all()
        except Exception:
            pass

    # Competition judges
    judges = []
    try:
        from models.judge_competition import JudgeCompetition
        from models.judge import Judge
        judges_result = await db.execute(
            select(JudgeCompetition, Judge)
            .join(Judge, JudgeCompetition.judge_id == Judge.id)
            .where(JudgeCompetition.competition_id == uuid.UUID(competition_id))
        )
        judges = [
            {"role": jc.role, "first_name": j.first_name, "last_name": j.last_name, "country": j.country}
            for jc, j in judges_result.all()
        ]
    except Exception:
        pass

    return templates.TemplateResponse("competition_page.html", {
        "request": request,
        "competition": comp,
        "divisions_data": divisions_data,
        "organizer": organizer,
        "sponsors": sponsors,
        "judges": judges,
    })


# ─── ADMIN PANEL ────────────────────────────────────────────────────────────

@app.get("/competitions/{competition_id}/admin")
async def competition_admin(competition_id: str, request: Request):
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.athlete import Athlete
    from models.discipline_result import DisciplineResult
    from models.overall_standing import OverallStanding
    from sqlalchemy import select
    import uuid

    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            return templates.TemplateResponse("404.html", {"request": request})

        divs_result = await db.execute(
            select(CompetitionDivision).where(CompetitionDivision.competition_id == uuid.UUID(competition_id))
        )
        divisions = divs_result.scalars().all()

        divisions_data = []
        for div in divisions:
            discs_result = await db.execute(
                select(CompetitionDiscipline)
                .where(CompetitionDiscipline.competition_division_id == div.id)
                .order_by(CompetitionDiscipline.order_no)
            )
            disciplines = discs_result.scalars().all()

            parts_result = await db.execute(
                select(Participant).where(Participant.competition_division_id == div.id)
                .order_by(Participant.lot_number, Participant.bib_no)
            )
            participants = parts_result.scalars().all()

            athlete_map = {}
            for p in participants:
                ath = await db.get(Athlete, p.athlete_id)
                if ath:
                    athlete_map[str(p.id)] = ath

            results_map = {}
            for disc in disciplines:
                res_result = await db.execute(
                    select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc.id)
                )
                results_map[str(disc.id)] = {str(r.participant_id): r for r in res_result.scalars().all()}

            overall_result = await db.execute(
                select(OverallStanding).where(OverallStanding.competition_division_id == div.id)
            )
            overall_standings = {str(o.participant_id): o for o in overall_result.scalars().all()}

            divisions_data.append({
                "division": div,
                "disciplines": disciplines,
                "participants": participants,
                "athlete_map": athlete_map,
                "results_map": results_map,
                "overall_standings": overall_standings,
            })

    return templates.TemplateResponse("competition_admin.html", {
        "request": request,
        "competition": comp,
        "divisions_data": divisions_data,
    })


@app.post("/competitions/{competition_id}/admin/save-result")
async def save_result(competition_id: str, request: Request):
    from models.discipline_result import DisciplineResult
    from sqlalchemy import select
    import uuid

    data = await request.json()
    discipline_id = uuid.UUID(data["discipline_id"])
    participant_id = uuid.UUID(data["participant_id"])
    primary_value = data.get("primary_value")
    secondary_value = data.get("secondary_value")
    reps = data.get("reps")
    status_flag = data.get("status_flag")

    async with SessionLocal() as db:
        existing = await db.execute(
            select(DisciplineResult).where(
                DisciplineResult.competition_discipline_id == discipline_id,
                DisciplineResult.participant_id == participant_id
            )
        )
        result = existing.scalar_one_or_none()

        if result:
            if primary_value is not None:
                result.primary_value = primary_value if primary_value != "" else None
            if secondary_value is not None:
                result.secondary_value = secondary_value if secondary_value != "" else None
            if reps is not None:
                result.reps = reps if reps != "" else None
            if status_flag is not None:
                result.status_flag = status_flag if status_flag != "" else None
        else:
            result = DisciplineResult(
                competition_discipline_id=discipline_id,
                participant_id=participant_id,
                primary_value=primary_value if primary_value != "" else None,
                secondary_value=secondary_value if secondary_value != "" else None,
                reps=reps if reps != "" else None,
                status_flag=status_flag if status_flag != "" else None,
            )
            db.add(result)

        await db.commit()
    return {"ok": True}


@app.post("/competitions/{competition_id}/admin/recalculate/{division_id}")
async def recalculate_standings(competition_id: str, division_id: str, request: Request):
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.discipline_result import DisciplineResult
    from models.discipline_standing import DisciplineStanding
    from models.overall_standing import OverallStanding
    from sqlalchemy import select, delete
    import uuid
    from decimal import Decimal

    div_id = uuid.UUID(division_id)

    async with SessionLocal() as db:
        # Дисциплины
        discs_result = await db.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == div_id)
            .order_by(CompetitionDiscipline.order_no)
        )
        disciplines = discs_result.scalars().all()

        # Участники
        parts_result = await db.execute(
            select(Participant).where(Participant.competition_division_id == div_id)
        )
        participants = parts_result.scalars().all()
        n = len(participants)

        total_points = {str(p.id): Decimal("0") for p in participants}

        for disc in disciplines:
            # Результаты этой дисциплины
            res_result = await db.execute(
                select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc.id)
            )
            results = {str(r.participant_id): r for r in res_result.scalars().all()}

            # Определяем режим сортировки по discipline_mode
            mode = disc.discipline_mode or "AMRAP_REPS"
            reverse = mode in ("AMRAP_REPS", "MAX_WEIGHT_WITHIN_CAP", "AMRAP_DISTANCE")

            def sort_key(p):
                r = results.get(str(p.id))
                if not r:
                    return (-1, 0) if reverse else (999999, 0)
                if r.reps is not None:
                    return (r.reps, 0)
                if r.primary_value is not None:
                    sec = float(r.secondary_value) if r.secondary_value else 0
                    return (float(r.primary_value), sec)
                return (-1, 0) if reverse else (999999, 0)

            sorted_parts = sorted(participants, key=sort_key, reverse=reverse)

            # Удаляем старые standings этой дисциплины
            await db.execute(
                delete(DisciplineStanding).where(DisciplineStanding.competition_discipline_id == disc.id)
            )

            # Записываем новые standings
            place = 1
            for p in sorted_parts:
                r = results.get(str(p.id))
                has_result = r and (r.primary_value is not None or r.reps is not None)
                pts = Decimal(str(n - place + 1)) if has_result else Decimal("0")
                st = DisciplineStanding(
                    competition_discipline_id=disc.id,
                    participant_id=p.id,
                    place=place if has_result else n,
                    points_for_discipline=pts,
                )
                db.add(st)
                if has_result:
                    total_points[str(p.id)] += pts
                    place += 1

        # Overall standings
        await db.execute(
            delete(OverallStanding).where(OverallStanding.competition_division_id == div_id)
        )

        sorted_overall = sorted(participants, key=lambda p: total_points[str(p.id)], reverse=True)
        for i, p in enumerate(sorted_overall):
            o = OverallStanding(
                competition_division_id=div_id,
                participant_id=p.id,
                total_points=total_points[str(p.id)],
                overall_place=i + 1,
            )
            db.add(o)

        await db.commit()

    return {"ok": True, "recalculated": len(participants)}


# ─── REFEREE APP API ─────────────────────────────────────────────────────────

@app.get("/results/discipline/{discipline_id}/sheet")
async def get_discipline_sheet(discipline_id: str):
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.athlete import Athlete
    from models.discipline_result import DisciplineResult
    from sqlalchemy import select
    import uuid

    disc_id = uuid.UUID(discipline_id)

    async with SessionLocal() as db:
        disc = await db.get(CompetitionDiscipline, disc_id)
        if not disc:
            from fastapi import HTTPException
            raise HTTPException(404, "Discipline not found")

        parts_result = await db.execute(
            select(Participant).where(Participant.competition_division_id == disc.competition_division_id)
            .order_by(Participant.lot_number, Participant.bib_no)
        )
        participants = parts_result.scalars().all()

        res_result = await db.execute(
            select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc_id)
        )
        results = {str(r.participant_id): r for r in res_result.scalars().all()}

        sheet = []
        for p in participants:
            ath = await db.get(Athlete, p.athlete_id)
            r = results.get(str(p.id))
            sheet.append({
                "participant_id": str(p.id),
                "bib_no": p.bib_no,
                "lot_number": p.lot_number,
                "first_name": ath.first_name if ath else "",
                "last_name": ath.last_name if ath else "",
                "country": ath.country if ath else "",
                "primary_value": float(r.primary_value) if r and r.primary_value is not None else None,
                "secondary_value": float(r.secondary_value) if r and r.secondary_value is not None else None,
                "reps": r.reps if r else None,
                "status_flag": r.status_flag if r else "OK",
            })

    return sheet


@app.post("/results/discipline/{discipline_id}")
async def upsert_discipline_result(discipline_id: str, request: Request):
    from models.discipline_result import DisciplineResult
    from sqlalchemy import select
    import uuid

    disc_id = uuid.UUID(discipline_id)
    data = await request.json()
    participant_id = uuid.UUID(data["participant_id"])

    async with SessionLocal() as db:
        existing = await db.execute(
            select(DisciplineResult).where(
                DisciplineResult.competition_discipline_id == disc_id,
                DisciplineResult.participant_id == participant_id
            )
        )
        result = existing.scalar_one_or_none()

        pv = data.get("primary_value")
        sv = data.get("secondary_value")
        reps = data.get("reps")
        flag = data.get("status_flag", "OK")

        if result:
            result.primary_value = pv
            result.secondary_value = sv
            result.reps = reps
            result.status_flag = flag
        else:
            result = DisciplineResult(
                competition_discipline_id=disc_id,
                participant_id=participant_id,
                primary_value=pv,
                secondary_value=sv,
                reps=reps,
                status_flag=flag,
            )
            db.add(result)

        await db.commit()
    return {"ok": True}


@app.post("/disciplines/{discipline_id}/calculate-standings")
async def calculate_discipline_standings(discipline_id: str):
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.discipline_result import DisciplineResult
    from models.discipline_standing import DisciplineStanding
    from models.overall_standing import OverallStanding
    from sqlalchemy import select, delete
    import uuid
    from decimal import Decimal

    disc_id = uuid.UUID(discipline_id)

    async with SessionLocal() as db:
        disc = await db.get(CompetitionDiscipline, disc_id)
        if not disc:
            from fastapi import HTTPException
            raise HTTPException(404, "Discipline not found")

        parts_result = await db.execute(
            select(Participant).where(Participant.competition_division_id == disc.competition_division_id)
        )
        participants = parts_result.scalars().all()
        n = len(participants)

        res_result = await db.execute(
            select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc_id)
        )
        results = {str(r.participant_id): r for r in res_result.scalars().all()}

        mode = disc.discipline_mode or "AMRAP_REPS"
        reverse = mode in ("AMRAP_REPS", "MAX_WEIGHT_WITHIN_CAP", "AMRAP_DISTANCE")

        def sort_key(p):
            r = results.get(str(p.id))
            if not r or (r.primary_value is None and r.reps is None):
                return (-1, 0) if reverse else (999999, 0)
            if r.reps is not None:
                return (r.reps, 0)
            sec = float(r.secondary_value) if r.secondary_value else 0
            return (float(r.primary_value), sec)

        sorted_parts = sorted(participants, key=sort_key, reverse=reverse)

        await db.execute(
            delete(DisciplineStanding).where(DisciplineStanding.competition_discipline_id == disc_id)
        )

        place = 1
        for p in sorted_parts:
            r = results.get(str(p.id))
            has_result = r and (r.primary_value is not None or r.reps is not None)
            if r and r.status_flag in ("DNS", "DNF", "DSQ"):
                has_result = False
            pts = Decimal(str(n - place + 1)) if has_result else Decimal("0")
            st = DisciplineStanding(
                competition_discipline_id=disc_id,
                participant_id=p.id,
                place=place if has_result else n,
                points_for_discipline=pts,
            )
            db.add(st)
            if has_result:
                place += 1

        # Пересчёт overall standings для всего дивизиона
        div_id = disc.competition_division_id
        all_discs_result = await db.execute(
            select(CompetitionDiscipline).where(CompetitionDiscipline.competition_division_id == div_id)
        )
        all_discs = all_discs_result.scalars().all()

        total_points = {str(p.id): Decimal("0") for p in participants}
        for d in all_discs:
            st_result = await db.execute(
                select(DisciplineStanding).where(DisciplineStanding.competition_discipline_id == d.id)
            )
            for st in st_result.scalars().all():
                if str(st.participant_id) in total_points:
                    total_points[str(st.participant_id)] += st.points_for_discipline

        await db.execute(
            delete(OverallStanding).where(OverallStanding.competition_division_id == div_id)
        )

        sorted_overall = sorted(participants, key=lambda p: total_points[str(p.id)], reverse=True)
        for i, p in enumerate(sorted_overall):
            o = OverallStanding(
                competition_division_id=div_id,
                participant_id=p.id,
                total_points=total_points[str(p.id)],
                overall_place=i + 1,
            )
            db.add(o)

        await db.commit()

    return {"ok": True, "discipline": discipline_id}


@app.get("/results/discipline/{discipline_id}/standings")
async def get_discipline_standings(discipline_id: str):
    from models.discipline_standing import DisciplineStanding
    from sqlalchemy import select
    import uuid

    disc_id = uuid.UUID(discipline_id)

    async with SessionLocal() as db:
        result = await db.execute(
            select(DisciplineStanding)
            .where(DisciplineStanding.competition_discipline_id == disc_id)
            .order_by(DisciplineStanding.place)
        )
        standings = result.scalars().all()

    return [
        {
            "participant_id": str(s.participant_id),
            "place": s.place,
            "points_for_discipline": float(s.points_for_discipline),
        }
        for s in standings
    ]


# ─── REFEREE APP — Division/Discipline endpoints ─────────────────────────────

@app.get("/competition-divisions/{division_id}")
async def get_division(division_id: str):
    from models.competition_division import CompetitionDivision
    from fastapi import HTTPException
    import uuid
    async with SessionLocal() as db:
        div = await db.get(CompetitionDivision, uuid.UUID(division_id))
        if not div:
            raise HTTPException(404, "Division not found")
        return {
            "id": str(div.id),
            "competition_id": str(div.competition_id),
            "division_key": div.division_key,
            "age_group": div.age_group,
            "status": div.status,
        }

@app.get("/competition-divisions/{division_id}/disciplines")
async def get_division_disciplines(division_id: str):
    from models.competition_discipline import CompetitionDiscipline
    from sqlalchemy import select
    import uuid
    async with SessionLocal() as db:
        result = await db.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == uuid.UUID(division_id))
            .order_by(CompetitionDiscipline.order_no)
        )
        discs = result.scalars().all()
        return [
            {
                "id": str(d.id),
                "discipline_name": d.discipline_name,
                "discipline_mode": d.discipline_mode,
                "result_unit": d.result_unit,
                "time_cap_seconds": d.time_cap_seconds,
                "is_final": d.is_final,
                "order_no": d.order_no,
            }
            for d in discs
        ]

@app.get("/competition-disciplines/{discipline_id}")
async def get_discipline(discipline_id: str):
    from models.competition_discipline import CompetitionDiscipline
    from fastapi import HTTPException
    import uuid
    async with SessionLocal() as db:
        d = await db.get(CompetitionDiscipline, uuid.UUID(discipline_id))
        if not d:
            raise HTTPException(404, "Discipline not found")
        return {
            "id": str(d.id),
            "competition_division_id": str(d.competition_division_id),
            "discipline_name": d.discipline_name,
            "discipline_mode": d.discipline_mode,
            "result_unit": d.result_unit,
            "time_cap_seconds": d.time_cap_seconds,
            "is_final": d.is_final,
            "order_no": d.order_no,
        }


# ─── PRINT PROTOCOL ──────────────────────────────────────────────────────────

@app.get("/competitions/{competition_id}/protocol")
async def competition_protocol(competition_id: str, request: Request):
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.athlete import Athlete
    from models.discipline_result import DisciplineResult
    from models.discipline_standing import DisciplineStanding
    from models.overall_standing import OverallStanding
    from sqlalchemy import select
    import uuid

    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            return templates.TemplateResponse("404.html", {"request": request})

        divs_result = await db.execute(
            select(CompetitionDivision).where(CompetitionDivision.competition_id == uuid.UUID(competition_id))
        )
        divisions = divs_result.scalars().all()

        divisions_data = []
        for div in divisions:
            discs_result = await db.execute(
                select(CompetitionDiscipline)
                .where(CompetitionDiscipline.competition_division_id == div.id)
                .order_by(CompetitionDiscipline.order_no)
            )
            disciplines = discs_result.scalars().all()

            parts_result = await db.execute(
                select(Participant).where(Participant.competition_division_id == div.id)
                .order_by(Participant.lot_number, Participant.bib_no)
            )
            participants = parts_result.scalars().all()

            athlete_map = {}
            for p in participants:
                ath = await db.get(Athlete, p.athlete_id)
                if ath:
                    athlete_map[str(p.id)] = ath

            results_map = {}
            standings_map = {}
            for disc in disciplines:
                res_result = await db.execute(
                    select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc.id)
                )
                results_map[str(disc.id)] = {str(r.participant_id): r for r in res_result.scalars().all()}

                st_result = await db.execute(
                    select(DisciplineStanding).where(DisciplineStanding.competition_discipline_id == disc.id)
                )
                standings_map[str(disc.id)] = {str(s.participant_id): s for s in st_result.scalars().all()}

            overall_result = await db.execute(
                select(OverallStanding).where(OverallStanding.competition_division_id == div.id)
                .order_by(OverallStanding.overall_place)
            )
            overall_standings = {str(o.participant_id): o for o in overall_result.scalars().all()}

            sorted_participants = sorted(
                participants,
                key=lambda p: overall_standings[str(p.id)].overall_place
                    if overall_standings.get(str(p.id)) and overall_standings[str(p.id)].overall_place
                    else 999
            )

            # Start orders
            start_orders = {}
            for i, disc in enumerate(disciplines):
                if i == 0:
                    ordered = sorted(participants, key=lambda p: (p.lot_number or 999, p.bib_no or 999))
                elif disc.is_final:
                    def get_points(p):
                        o = overall_standings.get(str(p.id))
                        return float(o.total_points) if o else 0
                    ordered = sorted(participants, key=get_points)
                else:
                    prev_disc = disciplines[i-1]
                    def get_prev_place(p):
                        st = standings_map.get(str(prev_disc.id), {}).get(str(p.id))
                        return st.place if st and hasattr(st, 'place') else 999
                    ordered = sorted(participants, key=get_prev_place, reverse=True)
                start_orders[str(disc.id)] = {str(p.id): idx+1 for idx, p in enumerate(ordered)}

            divisions_data.append({
                "division": div,
                "disciplines": disciplines,
                "participants": sorted_participants,
                "athlete_map": athlete_map,
                "results_map": results_map,
                "standings_map": standings_map,
                "overall_standings": overall_standings,
                "start_orders": start_orders,
            })

        # Организатор
        organizer = None
        if comp.organizer_id:
            from models.organizer import Organizer
            organizer = await db.get(Organizer, comp.organizer_id)

    return templates.TemplateResponse("competition_protocol.html", {
        "request": request,
        "competition": comp,
        "divisions_data": divisions_data,
        "organizer": organizer,
    })


# ─── WSM ADMIN PANEL ─────────────────────────────────────────────────────────

@app.get("/admin/pending-organizers")
async def admin_pending(request: Request):
    return templates.TemplateResponse("admin_pending.html", {"request": request})

@app.get("/admin/api/pending-organizers")
async def api_pending_organizers(request: Request):
    from models.user import User
    from models.organizer import Organizer
    from sqlalchemy import select
    from auth.dependencies import get_current_user
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from auth.security import decode_token
    from jose import JWTError

    # Проверяем токен из заголовка
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        from fastapi import HTTPException
        raise HTTPException(403, "Not authorized")
    token = auth.split(" ")[1]
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except:
        from fastapi import HTTPException
        raise HTTPException(403, "Invalid token")

    async with SessionLocal() as db:
        user = await db.get(User, int(user_id))
        if not user or user.role != "WSM_ADMIN":
            from fastapi import HTTPException
            raise HTTPException(403, "WSM_ADMIN role required")

        result = await db.execute(
            select(User, Organizer)
            .join(Organizer, Organizer.user_id == User.id, isouter=True)
            .where(User.role == "PENDING")
        )
        rows = result.all()
        return [
            {
                "user_id": u.id,
                "email": u.email,
                "organizer_id": str(o.id) if o else None,
                "name": o.name if o else "—",
                "type": o.type if o else "—",
                "country": o.country if o else "—",
                "city": o.city if o else "—",
                "phone": o.phone if o else "—",
                "website": o.website if o else "—",
                "photo_url": o.photo_url if o else None,
            }
            for u, o in rows
        ]

@app.post("/admin/api/approve-organizer/{user_id}")
async def api_approve_organizer(user_id: int, request: Request):
    from models.user import User
    from auth.security import decode_token

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        from fastapi import HTTPException
        raise HTTPException(403, "Not authorized")
    token = auth.split(" ")[1]
    try:
        payload = decode_token(token)
        admin_id = payload.get("sub")
    except:
        from fastapi import HTTPException
        raise HTTPException(403, "Invalid token")

    async with SessionLocal() as db:
        admin = await db.get(User, int(admin_id))
        if not admin or admin.role != "WSM_ADMIN":
            from fastapi import HTTPException
            raise HTTPException(403, "WSM_ADMIN role required")

        user = await db.get(User, user_id)
        if not user:
            from fastapi import HTTPException
            raise HTTPException(404, "User not found")

        user.role = "ORGANIZER"
        await db.commit()
    return {"ok": True, "user_id": user_id, "new_role": "ORGANIZER"}

@app.post("/admin/api/reject-organizer/{user_id}")
async def api_reject_organizer(user_id: int, request: Request):
    from models.user import User
    from auth.security import decode_token

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        from fastapi import HTTPException
        raise HTTPException(403, "Not authorized")
    token = auth.split(" ")[1]
    try:
        payload = decode_token(token)
        admin_id = payload.get("sub")
    except:
        from fastapi import HTTPException
        raise HTTPException(403, "Invalid token")

    async with SessionLocal() as db:
        admin = await db.get(User, int(admin_id))
        if not admin or admin.role != "WSM_ADMIN":
            from fastapi import HTTPException
            raise HTTPException(403, "WSM_ADMIN role required")

        user = await db.get(User, user_id)
        if not user:
            from fastapi import HTTPException
            raise HTTPException(404, "User not found")

        user.role = "REJECTED"
        await db.commit()
    return {"ok": True, "user_id": user_id, "new_role": "REJECTED"}


# ─── CERTIFICATES ────────────────────────────────────────────────────────────

@app.get("/competitions/{competition_id}/certificates")
async def competition_certificates(competition_id: str, request: Request):
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.participant import Participant
    from models.athlete import Athlete
    from models.overall_standing import OverallStanding
    from models.organizer import Organizer
    from sqlalchemy import select
    import uuid

    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            return templates.TemplateResponse("404.html", {"request": request})

        organizer = None
        if comp.organizer_id:
            organizer = await db.get(Organizer, comp.organizer_id)

        divs_result = await db.execute(
            select(CompetitionDivision).where(CompetitionDivision.competition_id == uuid.UUID(competition_id))
        )
        divisions = divs_result.scalars().all()

        certificates = []
        for div in divisions:
            parts_result = await db.execute(
                select(Participant).where(Participant.competition_division_id == div.id)
            )
            participants = parts_result.scalars().all()

            overall_result = await db.execute(
                select(OverallStanding).where(OverallStanding.competition_division_id == div.id)
                .order_by(OverallStanding.overall_place)
            )
            overall_standings = {str(o.participant_id): o for o in overall_result.scalars().all()}

            for p in participants:
                ath = await db.get(Athlete, p.athlete_id)
                overall = overall_standings.get(str(p.id))
                if overall:
                    certificates.append({
                        "athlete": ath,
                        "participant": p,
                        "overall": overall,
                        "division": div,
                    })

        certificates.sort(key=lambda x: (x["division"].division_key, x["overall"].overall_place))

    return templates.TemplateResponse("competition_certificates.html", {
        "request": request,
        "competition": comp,
        "organizer": organizer,
        "certificates": certificates,
    })


# ─── SEND CERTIFICATE EMAIL ──────────────────────────────────────────────────

@app.post("/competitions/{competition_id}/certificates/send")
async def send_certificate(competition_id: str, request: Request):
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.participant import Participant
    from models.athlete import Athlete
    from models.overall_standing import OverallStanding
    from models.organizer import Organizer
    from sqlalchemy import select
    from fastapi import HTTPException
    import uuid, os, resend

    data = await request.json()
    participant_id = data.get("participant_id")
    if not participant_id:
        raise HTTPException(400, "participant_id required")

    resend.api_key = os.getenv("RESEND_API_KEY")

    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            raise HTTPException(404, "Competition not found")

        organizer = None
        if comp.organizer_id:
            organizer = await db.get(Organizer, comp.organizer_id)

        p = await db.get(Participant, uuid.UUID(participant_id))
        if not p:
            raise HTTPException(404, "Participant not found")

        ath = await db.get(Athlete, p.athlete_id)
        if not ath or not ath.email:
            raise HTTPException(400, "Athlete has no email")

        overall_result = await db.execute(
            select(OverallStanding).where(
                OverallStanding.competition_division_id == p.competition_division_id,
                OverallStanding.participant_id == p.id
            )
        )
        overall = overall_result.scalar_one_or_none()
        if not overall:
            raise HTTPException(400, "No standings found for this athlete")

        div = await db.get(CompetitionDivision, p.competition_division_id)

        place = overall.overall_place
        suffix = "st" if place == 1 else "nd" if place == 2 else "rd" if place == 3 else "th"
        place_color = "#c9a84c" if place == 1 else "#aaa" if place == 2 else "#cd7f32" if place == 3 else "#666"

        org_block = ""
        if organizer and organizer.photo_url:
            org_block = f'<img src="{organizer.photo_url}" style="height:40px;max-width:100px;object-fit:contain;">'
        elif organizer:
            org_block = f'<span style="font-size:12px;color:#888;">{organizer.name}</span>'

        html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f0f0f0;font-family:Arial,sans-serif;">
<div style="max-width:600px;margin:40px auto;background:#fff;border:2px solid #c9a84c;padding:40px;">

  <!-- Header -->
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;border-bottom:2px solid #c9a84c;padding-bottom:16px;">
    <div style="display:flex;align-items:center;gap:12px;">
      <img src="https://psychic-eureka-pjxr6r56g5vwc6x59-8000.app.github.dev/static/logo.jpg" style="height:48px;width:48px;border-radius:50%;">
      <div>
        <div style="font-size:13px;font-weight:900;letter-spacing:2px;color:#111;text-transform:uppercase;">World Strongman</div>
        <div style="font-size:9px;color:#888;letter-spacing:2px;text-transform:uppercase;">International Union</div>
      </div>
    </div>
    {org_block}
  </div>

  <!-- Body -->
  <div style="text-align:center;padding:24px 0;">
    <div style="font-size:10px;letter-spacing:4px;color:#c9a84c;text-transform:uppercase;margin-bottom:8px;">Certificate of Achievement</div>
    <div style="font-size:24px;font-weight:900;text-transform:uppercase;letter-spacing:3px;color:#111;margin-bottom:4px;">{comp.name}</div>
    <div style="font-size:11px;color:#888;letter-spacing:2px;margin-bottom:24px;">
      {(comp.city or '') + (', ' + comp.country if comp.country else '')} · {comp.date_start or ''}
    </div>

    <div style="font-size:11px;color:#aaa;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">This certificate is presented to</div>
    <div style="font-size:28px;font-weight:900;text-transform:uppercase;letter-spacing:3px;color:#111;margin-bottom:4px;">{ath.first_name} {ath.last_name}</div>
    <div style="font-size:12px;color:#888;letter-spacing:3px;text-transform:uppercase;margin-bottom:24px;">{ath.country or ''}</div>

    <div style="margin-bottom:16px;">
      <span style="font-size:64px;font-weight:900;color:{place_color};line-height:1;">{place}</span>
      <span style="font-size:24px;font-weight:700;color:{place_color};vertical-align:super;">{suffix}</span>
      <div style="font-size:11px;letter-spacing:2px;color:#888;text-transform:uppercase;">Place</div>
    </div>

    <div style="font-size:14px;font-weight:700;letter-spacing:2px;color:#333;text-transform:uppercase;">{div.division_key} {div.age_group}</div>
    <div style="font-size:12px;color:#c9a84c;margin-top:4px;">{overall.total_points} points</div>
  </div>

  <!-- Footer -->
  <div style="display:flex;justify-content:space-between;border-top:1px solid #e0e0e0;padding-top:16px;margin-top:24px;">
    <div style="text-align:center;min-width:130px;">
      <div style="border-top:1px solid #333;margin-bottom:4px;"></div>
      <div style="font-size:9px;color:#888;letter-spacing:1px;text-transform:uppercase;">Chief Referee</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:11px;font-weight:700;color:#333;text-transform:uppercase;">{comp.name}</div>
      <div style="font-size:9px;color:#aaa;margin-top:2px;">{comp.date_end or comp.date_start or ''} · Q × {comp.coefficient_q}</div>
    </div>
    <div style="text-align:center;min-width:130px;">
      <div style="border-top:1px solid #333;margin-bottom:4px;"></div>
      <div style="font-size:9px;color:#888;letter-spacing:1px;text-transform:uppercase;">Competition Director</div>
    </div>
  </div>

</div>
</body>
</html>
"""

        resend.Emails.send({
            "from": "WSM Platform <onboarding@resend.dev>",
            "to": ath.email,
            "subject": f"🏆 Your Certificate — {comp.name}",
            "html": html,
        })

    return {"ok": True, "sent_to": ath.email}


# ─── RANKINGS PUBLIC PAGE ─────────────────────────────────────────────────────

@app.get("/rankings")
async def rankings_page(request: Request, division: str = "MEN", year: int = 2026):
    from models.athlete import Athlete
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.participant import Participant
    from models.overall_standing import OverallStanding
    from sqlalchemy import select
    from collections import defaultdict

    async with SessionLocal() as db:
        # Все дивизионы для фильтра
        divs_result = await db.execute(
            select(CompetitionDivision.division_key).distinct()
        )
        db_divisions = sorted(list(set([r[0] for r in divs_result.all() if r[0]])))
        # Standard WSM divisions always shown
        STANDARD_DIVISIONS = [
            'MEN_SENIOR_O110', 'MEN_SENIOR_U110', 'MEN_SENIOR_U95', 'MEN_SENIOR_U80', 'MEN_SENIOR_U70',
            'WOMEN_SENIOR_O85', 'WOMEN_SENIOR_U85', 'WOMEN_SENIOR_U75', 'WOMEN_SENIOR_U65', 'WOMEN_SENIOR_U55',
            'MEN_JUNIOR_O110', 'MEN_JUNIOR_U110', 'MEN_JUNIOR_U95', 'MEN_JUNIOR_U80', 'MEN_JUNIOR_U70',
            'WOMEN_JUNIOR_O85', 'WOMEN_JUNIOR_U85', 'WOMEN_JUNIOR_U75', 'WOMEN_JUNIOR_U65', 'WOMEN_JUNIOR_U55',
            'MEN_MASTERS40_O110', 'MEN_MASTERS40_U110', 'MEN_MASTERS40_U95', 'MEN_MASTERS40_U80', 'MEN_MASTERS40_U70',
            'WOMEN_MASTERS40_O85', 'WOMEN_MASTERS40_U85', 'WOMEN_MASTERS40_U75', 'WOMEN_MASTERS40_U65', 'WOMEN_MASTERS40_U55',
            'MEN_MASTERS50_O110', 'MEN_MASTERS50_U110', 'MEN_MASTERS50_U95', 'MEN_MASTERS50_U80', 'MEN_MASTERS50_U70',
            'WOMEN_MASTERS50_O85', 'WOMEN_MASTERS50_U85', 'WOMEN_MASTERS50_U75', 'WOMEN_MASTERS50_U65', 'WOMEN_MASTERS50_U55',
            'PARA_MEN_OPEN', 'PARA_MEN_U80', 'PARA_MEN_O80',
            'PARA_WOMEN_OPEN', 'PARA_WOMEN_U80', 'PARA_WOMEN_O80',
        ]
        all_divisions = sorted(list(set(db_divisions + STANDARD_DIVISIONS)))

        # Все годы
        years_result = await db.execute(
            select(Competition.date_start).where(Competition.date_start != None)
        )
        all_years = sorted(set(
            d[0].year for d in years_result.all() if d[0]
        ), reverse=True)
        if not all_years:
            all_years = [2026]

        # Соревнования за выбранный год
        comps_result = await db.execute(
            select(Competition).where(
                Competition.date_start != None,
            )
        )
        all_comps = {str(c.id): c for c in comps_result.scalars().all()
                     if c.date_start and c.date_start.year == year}

        # Дивизионы выбранного типа за этот год
        if not all_comps:
            return templates.TemplateResponse("rankings.html", {
                "request": request,
                "rankings": [],
                "all_divisions": all_divisions,
                "all_years": all_years,
                "selected_division": division if division in all_divisions else (all_divisions[0] if all_divisions else "MEN"),
                "selected_year": year,
            })

        comp_ids = list(all_comps.keys())

        import uuid as _uuid
        comp_uuids = [_uuid.UUID(c) for c in all_comps.keys()]
        divs_result2 = await db.execute(
            select(CompetitionDivision).where(
                CompetitionDivision.competition_id.in_(comp_uuids),
                CompetitionDivision.division_key == division,
            )
        )
        divisions = divs_result2.scalars().all()

        # Собираем очки по атлетам
        athlete_points = defaultdict(lambda: {"total": 0, "results": [], "athlete": None})

        for div in divisions:
            comp = all_comps.get(str(div.competition_id))
            if not comp:
                continue
            q = float(comp.coefficient_q or 1.0)

            parts_result = await db.execute(
                select(Participant).where(Participant.competition_division_id == div.id)
            )
            participants = {str(p.id): p for p in parts_result.scalars().all()}

            overall_result = await db.execute(
                select(OverallStanding).where(OverallStanding.competition_division_id == div.id)
            )
            for o in overall_result.scalars().all():
                p = participants.get(str(o.participant_id))
                if not p:
                    continue
                ath_id = str(p.athlete_id)
                pts = float(o.total_points or 0) * q
                athlete_points[ath_id]["total"] += pts
                athlete_points[ath_id]["results"].append({
                    "comp_name": comp.name,
                    "comp_id": str(comp.id),
                    "place": o.overall_place,
                    "points": float(o.total_points or 0),
                    "q": q,
                    "weighted": pts,
                })
                if not athlete_points[ath_id]["athlete"]:
                    ath = await db.get(Athlete, p.athlete_id)
                    athlete_points[ath_id]["athlete"] = ath

        # Сортируем по очкам
        rankings = sorted(
            [{"athlete_id": k, **v} for k, v in athlete_points.items()],
            key=lambda x: x["total"],
            reverse=True
        )
        for i, r in enumerate(rankings):
            r["rank"] = i + 1

    return templates.TemplateResponse("rankings.html", {
        "request": request,
        "rankings": rankings,
        "all_divisions": all_divisions,
        "all_years": all_years,
        "selected_division": division,
        "selected_year": year,
    })


# ─── RANKINGS MAP DATA ───────────────────────────────────────────────────────

@app.get("/rankings/map-data")
async def rankings_map_data(division: str = "MEN", year: int = 2026):
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.participant import Participant
    from models.athlete import Athlete
    from models.overall_standing import OverallStanding
    from sqlalchemy import select
    from collections import defaultdict
    import uuid

    async with SessionLocal() as db:
        comps_result = await db.execute(select(Competition).where(Competition.date_start != None))
        all_comps = {str(c.id): c for c in comps_result.scalars().all()
                     if c.date_start and c.date_start.year == year}

        if not all_comps:
            return []

        comp_uuids = [uuid.UUID(c) for c in all_comps.keys()]
        divs_result = await db.execute(
            select(CompetitionDivision).where(
                CompetitionDivision.competition_id.in_(comp_uuids),
                CompetitionDivision.division_key == division,
            )
        )
        divisions = divs_result.scalars().all()

        country_data = defaultdict(lambda: {"athletes": set(), "total_points": 0, "top_athlete": None, "top_pts": 0})

        for div in divisions:
            comp = all_comps.get(str(div.competition_id))
            if not comp:
                continue
            q = float(comp.coefficient_q or 1.0)

            parts_result = await db.execute(
                select(Participant).where(Participant.competition_division_id == div.id)
            )
            participants = {str(p.id): p for p in parts_result.scalars().all()}

            overall_result = await db.execute(
                select(OverallStanding).where(OverallStanding.competition_division_id == div.id)
            )
            for o in overall_result.scalars().all():
                p = participants.get(str(o.participant_id))
                if not p:
                    continue
                ath = await db.get(Athlete, p.athlete_id)
                if not ath or not ath.country:
                    continue
                pts = float(o.total_points or 0) * q
                country = ath.country.upper().strip()
                country_data[country]["athletes"].add(str(ath.id))
                country_data[country]["total_points"] += pts
                if pts > country_data[country]["top_pts"]:
                    country_data[country]["top_pts"] = pts
                    country_data[country]["top_athlete"] = f"{ath.first_name} {ath.last_name}"

        return [
            {
                "country": k,
                "athletes": len(v["athletes"]),
                "total_points": round(v["total_points"], 1),
                "top_athlete": v["top_athlete"],
                "top_pts": round(v["top_pts"], 1),
            }
            for k, v in country_data.items()
        ]

@app.post("/competitions/{competition_id}/send-certificates")
async def send_certificates(competition_id: str, request: Request):
    import os, resend
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.participant import Participant
    from models.athlete import Athlete
    from models.overall_standing import OverallStanding
    from sqlalchemy import select
    import uuid

    resend.api_key = os.environ.get("RESEND_API_KEY")
    base_url = str(request.base_url).rstrip("/")
    cert_url = f"https://ranking.worldstrongman.org/competitions/{competition_id}/certificates"
    sent = []
    errors = []

    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            return {"error": "Not found"}

        divs = await db.execute(select(CompetitionDivision).where(CompetitionDivision.competition_id == uuid.UUID(competition_id)))
        for div in divs.scalars().all():
            parts = await db.execute(select(Participant).where(Participant.competition_division_id == div.id))
            for p in parts.scalars().all():
                ath = await db.get(Athlete, p.athlete_id)
                if not ath or not ath.email:
                    continue
                overall = await db.execute(select(OverallStanding).where(
                    OverallStanding.competition_division_id == div.id,
                    OverallStanding.participant_id == p.id
                ))
                o = overall.scalar_one_or_none()
                place = o.overall_place if o else "—"
                try:
                    resend.Emails.send({
                        "from": "WSM Platform <noreply@ranking.worldstrongman.org>",
                        "to": ath.email,
                        "subject": f"Your Certificate — {comp.name}",
                        "html": f"""
                        <div style="font-family:Arial,sans-serif;background:#0a0a0a;color:#fff;padding:40px;max-width:600px;margin:0 auto;">
                            <img src="https://ranking.worldstrongman.org/static/logo.jpg" style="width:60px;height:60px;border-radius:50%;margin-bottom:20px;" />
                            <h1 style="color:#c9a84c;font-size:24px;margin-bottom:8px;">World Strongman</h1>
                            <p style="color:#888;font-size:13px;margin-bottom:32px;">International Union</p>
                            <h2 style="color:#fff;font-size:20px;margin-bottom:16px;">Dear {ath.first_name} {ath.last_name},</h2>
                            <p style="color:#ccc;font-size:15px;line-height:1.6;margin-bottom:24px;">
                                Congratulations on your participation in <strong style="color:#c9a84c;">{comp.name}</strong>.<br>
                                You finished <strong style="color:#c9a84c;">#{place}</strong> in the <strong>{div.division_key}</strong> division.
                            </p>
                            <a href="{cert_url}" style="display:inline-block;padding:14px 28px;background:#c9a84c;color:#000;text-decoration:none;font-weight:700;font-size:13px;letter-spacing:2px;border-radius:3px;">
                                VIEW & PRINT CERTIFICATE →
                            </a>
                            <p style="color:#333;font-size:11px;margin-top:32px;">© 2026 World Strongman International Union</p>
                        </div>
                        """
                    })
                    sent.append(ath.email)
                except Exception as e:
                    import traceback
                    errors.append({"email": ath.email, "error": str(e), "trace": traceback.format_exc()})

    return {"sent": sent, "errors": errors, "total": len(sent)}

# ── DRAW SHOW PAGE ─────────────────────────────────────────────
@app.get("/competitions/{competition_id}/draw")
async def draw_show(competition_id: str, request: Request):
    import uuid
    async with SessionLocal() as db:
        from models.competition import Competition
        from models.competition_division import CompetitionDivision
        from models.participant import Participant
        from models.athlete import Athlete

        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            return RedirectResponse("/competitions-list")

        divs_result = await db.execute(
            select(CompetitionDivision).where(CompetitionDivision.competition_id == uuid.UUID(competition_id))
        )
        divisions = divs_result.scalars().all()

        divisions_data = []
        for d in divisions:
            parts_result = await db.execute(
                select(Participant, Athlete)
                .join(Athlete, Participant.athlete_id == Athlete.id)
                .where(Participant.competition_division_id == d.id)
            )
            participants = [
                {
                    "participant_id": str(p.id),
                    "athlete_id": str(a.id),
                    "first_name": a.first_name,
                    "last_name": a.last_name,
                    "country": a.country,
                    "bib_no": p.bib_no,
                    "lot_number": p.lot_number,
                }
                for p, a in parts_result.all()
            ]
            divisions_data.append({"division": d, "participants": participants})

        public_url = f"https://ranking.worldstrongman.org/competitions/{competition_id}/page"
        return templates.TemplateResponse("draw_show.html", {
            "request": request,
            "competition": comp,
            "divisions_data": divisions_data,
            "public_url": public_url,
        })

# ── DRAW API ────────────────────────────────────────────────────
@app.post("/competitions/{competition_id}/divisions/{division_id}/draw/auto")
async def draw_auto(competition_id: str, division_id: str, discipline_order: int = 1):
    import uuid, random
    from models.participant import Participant
    from models.discipline_result import DisciplineResult
    from models.competition_discipline import CompetitionDiscipline
    async with SessionLocal() as db:
        parts_result = await db.execute(
            select(Participant).where(Participant.competition_division_id == uuid.UUID(division_id))
        )
        participants = parts_result.scalars().all()
        if discipline_order == 1:
            random.shuffle(participants)
            for i, p in enumerate(participants, 1):
                p.lot_number = i
        else:
            # получаем все дисциплины дивизиона
            discs_result = await db.execute(
                select(CompetitionDiscipline)
                .where(CompetitionDiscipline.competition_division_id == uuid.UUID(division_id))
                .order_by(CompetitionDiscipline.order_no)
            )
            discs = discs_result.scalars().all()
            is_last = discipline_order == len(discs)
            if is_last:
                # последняя дисциплина — реверс по общим очкам
                from models.overall_standing import OverallStanding
                standings_result = await db.execute(
                    select(OverallStanding)
                    .where(OverallStanding.competition_division_id == uuid.UUID(division_id))
                )
                standings = {str(s.participant_id): s.total_points for s in standings_result.scalars().all()}
                participants.sort(key=lambda p: standings.get(str(p.id), 0), reverse=True)
                for i, p in enumerate(participants, 1):
                    p.lot_number = i
            elif len(discs) >= discipline_order - 1:
                # дисциплина 2+ — реверс по результатам предыдущей дисциплины
                prev_disc = discs[discipline_order - 2]
                results_result = await db.execute(
                    select(DisciplineResult).where(DisciplineResult.competition_discipline_id == prev_disc.id)
                )
                results = {str(r.participant_id): r.standing_place for r in results_result.scalars().all()}
                participants.sort(key=lambda p: results.get(str(p.id), 999), reverse=True)
                for i, p in enumerate(participants, 1):
                    p.lot_number = i
        await db.commit()
        return {"ok": True, "order": [{"participant_id": str(p.id), "lot_number": p.lot_number} for p in participants]}

@app.patch("/competitions/{competition_id}/divisions/{division_id}/draw")
async def draw_save(competition_id: str, division_id: str, request: Request):
    import uuid
    from models.participant import Participant
    body = await request.json()
    order = body if isinstance(body, list) else body.get("order", [])
    async with SessionLocal() as db:
        for item in order:
            p = await db.get(Participant, uuid.UUID(item["participant_id"]))
            if p:
                p.lot_number = item["lot_number"]
        await db.commit()
        return {"ok": True}

@app.get("/competitions/{competition_id}/divisions/{division_id}/draw")
async def draw_get(competition_id: str, division_id: str):
    import uuid
    from models.participant import Participant
    from models.athlete import Athlete
    async with SessionLocal() as db:
        parts_result = await db.execute(
            select(Participant, Athlete)
            .join(Athlete, Participant.athlete_id == Athlete.id)
            .where(Participant.competition_division_id == uuid.UUID(division_id))
            .order_by(Participant.lot_number, Participant.bib_no)
        )
        return [
            {
                "participant_id": str(p.id),
                "first_name": a.first_name,
                "last_name": a.last_name,
                "country": a.country,
                "lot_number": p.lot_number,
                "bib_no": p.bib_no,
            }
            for p, a in parts_result.all()
        ]

# ── LIVE SCREEN ─────────────────────────────────────────────────
@app.get("/competitions/{competition_id}/live-screen")
async def live_screen(competition_id: str, request: Request):
    import uuid
    from db.database import SessionLocal
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            return RedirectResponse("/competitions-list")
        divs_result = await db.execute(
            select(CompetitionDivision).where(CompetitionDivision.competition_id == uuid.UUID(competition_id))
        )
        divisions_data = [{"division": d} for d in divs_result.scalars().all()]
        return templates.TemplateResponse("live_screen.html", {
            "request": request,
            "competition": comp,
            "divisions_data": divisions_data,
        })

# ── WARMUP SCREEN ───────────────────────────────────────────────
@app.get("/competitions/{competition_id}/warmup-screen")
async def warmup_screen(competition_id: str, request: Request):
    import uuid
    from db.database import SessionLocal
    from models.competition import Competition
    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            return RedirectResponse("/competitions-list")
        return templates.TemplateResponse("warmup_screen.html", {
            "request": request,
            "competition": comp,
        })

# ============ COMPETITION REGISTRATIONS ============

@app.get("/competitions/{competition_id}/registrations")
async def get_registrations(competition_id: str):
    import uuid
    from models.competition_registration import CompetitionRegistration
    from sqlalchemy import select
    async with SessionLocal() as db:
        res = await db.execute(
            select(CompetitionRegistration)
            .where(CompetitionRegistration.competition_id == uuid.UUID(competition_id))
            .order_by(CompetitionRegistration.created_at.desc())
        )
        regs = res.scalars().all()
        return [{
            "id": str(r.id),
            "athlete_id": str(r.athlete_id) if r.athlete_id else None,
            "division_key": r.division_key,
            "first_name": r.first_name,
            "last_name": r.last_name,
            "country": r.country,
            "email": r.email,
            "phone": r.phone,
            "notes": r.notes,
            "status": r.status,
            "reject_reason": r.reject_reason,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in regs]

@app.post("/competitions/{competition_id}/registrations/check-email")
async def check_athlete_email(competition_id: str, data: dict):
    from models.athlete import Athlete
    from sqlalchemy import select
    email = data.get("email", "").strip().lower()
    if not email:
        return {"found": False}
    async with SessionLocal() as db:
        res = await db.execute(select(Athlete).where(Athlete.email == email))
        athlete = res.scalar_one_or_none()
        if athlete:
            return {"found": True, "athlete": {"id": str(athlete.id), "first_name": athlete.first_name, "last_name": athlete.last_name, "country": athlete.country, "email": athlete.email}}
        return {"found": False}

@app.post("/competitions/{competition_id}/register")
async def submit_registration(competition_id: str, data: dict):
    import uuid
    from datetime import datetime
    from models.competition_registration import CompetitionRegistration
    from models.athlete import Athlete
    from sqlalchemy import select
    async with SessionLocal() as db:
        athlete_id = None
        if data.get("athlete_id"):
            athlete_id = uuid.UUID(data["athlete_id"])
        elif data.get("email"):
            res = await db.execute(select(Athlete).where(Athlete.email == data["email"].strip().lower()))
            existing = res.scalar_one_or_none()
            if existing:
                athlete_id = existing.id
            else:
                new_athlete = Athlete(
                    first_name=data.get("first_name", ""),
                    last_name=data.get("last_name", ""),
                    country=data.get("country"),
                    email=data["email"].strip().lower(),
                    phone=data.get("phone"),
                )
                db.add(new_athlete)
                await db.flush()
                athlete_id = new_athlete.id
        reg = CompetitionRegistration(
            competition_id=uuid.UUID(competition_id),
            athlete_id=athlete_id,
            division_key=data.get("division_key"),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            country=data.get("country"),
            email=data.get("email"),
            phone=data.get("phone"),
            notes=data.get("notes"),
            status="PENDING",
            created_at=datetime.utcnow(),
        )
        db.add(reg)
        await db.commit()
        return {"id": str(reg.id), "status": "PENDING"}

@app.patch("/competitions/{competition_id}/registrations/{reg_id}")
async def update_registration(competition_id: str, reg_id: str, data: dict):
    import uuid
    from models.competition_registration import CompetitionRegistration
    from models.participant import Participant
    from models.competition_division import CompetitionDivision
    from sqlalchemy import select
    async with SessionLocal() as db:
        res = await db.execute(select(CompetitionRegistration).where(CompetitionRegistration.id == uuid.UUID(reg_id)))
        reg = res.scalar_one_or_none()
        if not reg:
            raise HTTPException(404, "Not found")
        status = data.get("status")
        reg.status = status
        if data.get("reject_reason"):
            reg.reject_reason = data["reject_reason"]
        if status == "ACCEPTED" and reg.athlete_id:
            div_res = await db.execute(
                select(CompetitionDivision).where(
                    CompetitionDivision.competition_id == uuid.UUID(competition_id),
                    CompetitionDivision.division_key == reg.division_key
                )
            )
            div = div_res.scalar_one_or_none()
            if div:
                participant = Participant(
                    competition_division_id=div.id,
                    athlete_id=reg.athlete_id,
                )
                db.add(participant)
        db.add(reg)
        await db.commit()

        # Send email notification
        if reg.email:
            try:
                import resend
                comp_res = await db.execute(select(Competition).where(Competition.id == uuid.UUID(competition_id)))
                comp = comp_res.scalar_one_or_none()
                comp_name = comp.name if comp else "Competition"
                if status == "ACCEPTED":
                    subject = f"✅ Application Accepted — {comp_name}"
                    html = f"""<div style="font-family:sans-serif;max-width:500px;margin:0 auto;background:#0a0a0a;color:#fff;padding:32px;border-radius:8px;">
                        <div style="color:#c9a84c;font-size:12px;letter-spacing:3px;margin-bottom:16px;">WORLD STRONGMAN</div>
                        <h2 style="margin:0 0 16px;">Your application has been accepted!</h2>
                        <p style="color:#888;">You are officially registered for <strong style="color:#fff;">{comp_name}</strong>.</p>
                        <p style="color:#888;">Division: <strong style="color:#c9a84c;">{reg.division_key or '—'}</strong></p>
                        <p style="color:#555;font-size:12px;margin-top:24px;">World Strongman Platform</p>
                    </div>"""
                else:
                    subject = f"❌ Application Update — {comp_name}"
                    reason = reg.reject_reason or "No reason provided"
                    html = f"""<div style="font-family:sans-serif;max-width:500px;margin:0 auto;background:#0a0a0a;color:#fff;padding:32px;border-radius:8px;">
                        <div style="color:#c9a84c;font-size:12px;letter-spacing:3px;margin-bottom:16px;">WORLD STRONGMAN</div>
                        <h2 style="margin:0 0 16px;">Application Status Update</h2>
                        <p style="color:#888;">Your application for <strong style="color:#fff;">{comp_name}</strong> was not accepted.</p>
                        <p style="color:#888;">Reason: <strong style="color:#fff;">{reason}</strong></p>
                        <p style="color:#555;font-size:12px;margin-top:24px;">World Strongman Platform</p>
                    </div>"""
                resend.Emails.send({
                    "from": "WSM Platform <noreply@ranking.worldstrongman.org>",
                    "to": reg.email,
                    "subject": subject,
                    "html": html,
                })
            except Exception as e:
                print(f"Email error: {e}")

        return {"id": str(reg.id), "status": reg.status}


@app.get("/competitions/{competition_id}/mc-data")
async def get_mc_data(competition_id: str):
    from sqlalchemy import select, text
    from models.competition_sponsor import CompetitionSponsor as CS
    import uuid
    async with SessionLocal() as db:
        sp = await db.execute(select(CS).where(CS.competition_id == uuid.UUID(competition_id)))
        sponsors = sp.scalars().all()
        try:
            pr = await db.execute(text("SELECT id, order_no, time_slot, type, title, description, person_name, person_role FROM competition_program WHERE competition_id=:cid ORDER BY order_no, time_slot"), {"cid": competition_id})
            program = [{"id": str(r[0]), "order_no": r[1], "time_slot": r[2], "type": r[3], "title": r[4], "description": r[5], "person_name": r[6], "person_role": r[7]} for r in pr.fetchall()]
        except:
            program = []
        try:
            gr = await db.execute(text("SELECT id, order_no, name, title, country, photo_url, bio FROM competition_guests WHERE competition_id=:cid ORDER BY order_no"), {"cid": competition_id})
            guests = [{"id": str(r[0]), "order_no": r[1], "name": r[2], "title": r[3], "country": r[4], "photo_url": r[5], "bio": r[6]} for r in gr.fetchall()]
        except:
            guests = []
        return {
            "sponsors": [{"id": str(s.id), "name": s.name, "logo_url": s.logo_url, "tier": s.tier, "website_url": getattr(s, "website_url", ""), "mc_text": getattr(s, "mc_text", "")} for s in sponsors],
            "program": program,
            "guests": guests,
        }

@app.post("/competitions/{competition_id}/program")
async def add_program_item(competition_id: str, data: dict):
    from sqlalchemy import text
    import uuid
    async with SessionLocal() as db:
        id_ = str(uuid.uuid4())
        await db.execute(text("INSERT INTO competition_program (id, competition_id, order_no, time_slot, type, title, description, person_name, person_role) VALUES (:id, :cid, :order_no, :time_slot, :type, :title, :description, :person_name, :person_role)"), {
            "id": id_, "cid": competition_id,
            "order_no": data.get("order_no", 0),
            "time_slot": data.get("time_slot", ""),
            "type": data.get("type", "OTHER"),
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "person_name": data.get("person_name", ""),
            "person_role": data.get("person_role", ""),
        })
        await db.commit()
        return {"id": id_, **data}

@app.delete("/competitions/{competition_id}/program/{item_id}")
async def delete_program_item(competition_id: str, item_id: str):
    from sqlalchemy import text
    async with SessionLocal() as db:
        await db.execute(text("DELETE FROM competition_program WHERE id=:id AND competition_id=:cid"), {"id": item_id, "cid": competition_id})
        await db.commit()
        return {"ok": True}

@app.post("/competitions/{competition_id}/guests")
async def add_guest(competition_id: str, data: dict):
    from sqlalchemy import text
    import uuid
    async with SessionLocal() as db:
        id_ = str(uuid.uuid4())
        await db.execute(text("INSERT INTO competition_guests (id, competition_id, order_no, name, title, country, photo_url, bio) VALUES (:id, :cid, :order_no, :name, :title, :country, :photo_url, :bio)"), {
            "id": id_, "cid": competition_id,
            "order_no": data.get("order_no", 0),
            "name": data.get("name", ""),
            "title": data.get("title", ""),
            "country": data.get("country", ""),
            "photo_url": data.get("photo_url", ""),
            "bio": data.get("bio", ""),
        })
        await db.commit()
        return {"id": id_, **data}

@app.delete("/competitions/{competition_id}/guests/{guest_id}")
async def delete_guest(competition_id: str, guest_id: str):
    from sqlalchemy import text
    async with SessionLocal() as db:
        await db.execute(text("DELETE FROM competition_guests WHERE id=:id AND competition_id=:cid"), {"id": guest_id, "cid": competition_id})
        await db.commit()
        return {"ok": True}

@app.patch("/competitions/{competition_id}/sponsors/{sponsor_id}")
async def update_sponsor_mc(competition_id: str, sponsor_id: str, data: dict):
    from sqlalchemy import update
    from models.competition_sponsor import CompetitionSponsor as _CS
    import uuid
    async with SessionLocal() as db:
        if "mc_text" in data:
            await db.execute(update(_CS).where(_CS.id == uuid.UUID(sponsor_id)).values(mc_text=data["mc_text"]))
            await db.commit()
        return {"ok": True}

@app.get("/app")
async def app_install(request: Request):
    return templates.TemplateResponse("app_install.html", {"request": request})

@app.get("/organizer/help")
async def organizer_help(request: Request):
    return templates.TemplateResponse("organizer_help.html", {"request": request})

