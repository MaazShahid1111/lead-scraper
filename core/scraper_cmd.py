"""Scrape command handler"""
import asyncio
import json
import os
import re
from datetime import datetime
from playwright.async_api import async_playwright

# ── Country city/niche configs ────────────────────────────────
CITY_LISTS = {
    'usa': ['New York NY','Los Angeles CA','Chicago IL','Houston TX','Phoenix AZ','Philadelphia PA','San Antonio TX','San Diego CA','Dallas TX','San Jose CA','Austin TX','Jacksonville FL','Fort Worth TX','Columbus OH','Charlotte NC','Indianapolis IN','San Francisco CA','Seattle WA','Denver CO','Nashville TN','Oklahoma City OK','El Paso TX','Washington DC','Las Vegas NV','Boston MA','Memphis TN','Louisville KY','Portland OR','Baltimore MD','Milwaukee WI','Albuquerque NM','Tucson AZ','Fresno CA','Mesa AZ','Sacramento CA','Kansas City MO','Atlanta GA','Omaha NE','Colorado Springs CO','Raleigh NC','Minneapolis MN','Miami FL','Tampa FL','New Orleans LA','Cleveland OH'],
    'canada': ['Toronto ON','Vancouver BC','Montreal QC','Calgary AB','Edmonton AB','Ottawa ON','Winnipeg MB','Quebec City QC','Hamilton ON','Kitchener ON','London ON','Victoria BC','Halifax NS','Oshawa ON','Windsor ON','Saskatoon SK','Regina SK','Sherbrooke QC','St Johns NL','Barrie ON','Kelowna BC','Abbotsford BC','Kingston ON','Sudbury ON'],
    'uk': ['London','Birmingham','Manchester','Glasgow','Leeds','Liverpool','Sheffield','Edinburgh','Bristol','Leicester','Bradford','Cardiff','Coventry','Nottingham','Kingston upon Hull','Belfast','Stoke-on-Trent','Wolverhampton','Plymouth','Derby','Southampton','Reading','Luton','Preston','Aberdeen','Swansea','Sunderland','Dundee','Oxford','Cambridge'],
    'australia': ['Sydney NSW','Melbourne VIC','Brisbane QLD','Perth WA','Adelaide SA','Gold Coast QLD','Newcastle NSW','Canberra ACT','Sunshine Coast QLD','Wollongong NSW','Hobart TAS','Geelong VIC','Townsville QLD','Cairns QLD','Darwin NT','Toowoomba QLD','Ballarat VIC','Bendigo VIC'],
    'ireland': ['Dublin','Cork','Limerick','Galway','Waterford','Drogheda','Dundalk','Swords','Bray','Navan','Ennis','Kilkenny','Carlow','Tralee'],
    'new_zealand': ['Auckland','Wellington','Christchurch','Hamilton','Tauranga','Napier','Dunedin','Palmerston North','Nelson','Rotorua','New Plymouth','Whangarei'],
    'mexico': ['Mexico City','Guadalajara','Monterrey','Puebla','Tijuana','Leon','Juarez','Zapopan','Merida','San Luis Potosi','Aguascalientes','Hermosillo','Mexicali','Culiacan','Acapulco','Queretaro','Morelia','Cancun','Veracruz'],
    'brazil': ['Sao Paulo','Rio de Janeiro','Brasilia','Salvador','Fortaleza','Belo Horizonte','Manaus','Curitiba','Recife','Porto Alegre','Belem','Goiania','Guarulhos','Campinas','Sao Luis','Maceio','Natal'],
    'argentina': ['Buenos Aires','Cordoba','Rosario','Mendoza','La Plata','Tucuman','Mar del Plata','Salta','Santa Fe','San Juan'],
    'colombia': ['Bogota','Medellin','Cali','Barranquilla','Cartagena','Cucuta','Bucaramanga','Pereira','Santa Marta','Ibague','Manizales'],
    'chile': ['Santiago','Valparaiso','Concepcion','La Serena','Antofagasta','Temuco','Rancagua','Talca','Arica','Iquique'],
    'peru': ['Lima','Arequipa','Trujillo','Chiclayo','Piura','Iquitos','Cusco','Huancayo','Tacna'],
    'venezuela': ['Caracas','Maracaibo','Valencia','Barquisimeto','Maracay','Ciudad Guayana','Maturin','Barcelona'],
    'ecuador': ['Quito','Guayaquil','Cuenca','Santo Domingo','Machala','Manta','Ambato','Loja'],
    'bolivia': ['La Paz','Santa Cruz','Cochabamba','Sucre','Oruro','Potosi'],
    'paraguay': ['Asuncion','Ciudad del Este','San Lorenzo','Luque'],
    'uruguay': ['Montevideo','Salto','Paysandu','Las Piedras'],
    'panama': ['Panama City','San Miguelito','La Chorrera','David'],
    'costa_rica': ['San Jose','Alajuela','Desamparados','Liberia'],
    'guatemala': ['Guatemala City','Villa Nueva','Quetzaltenango','Escuintla','Mixco'],
    'honduras': ['Tegucigalpa','San Pedro Sula','Choloma','La Ceiba'],
    'el_salvador': ['San Salvador','Santa Ana','San Miguel','Mejicanos'],
    'nicaragua': ['Managua','Leon','Masaya','Matagalpa'],
    'cuba': ['Havana','Santiago de Cuba','Camaguey','Holguin'],
    'dominican_republic': ['Santo Domingo','Santiago','La Romana','La Vega'],
    'jamaica': ['Kingston','Spanish Town','Portmore','Montego Bay'],
    'trinidad_tobago': ['Port of Spain','San Fernando','Arima','Chaguanas'],
    'germany': ['Berlin','Hamburg','Munich','Cologne','Frankfurt','Stuttgart','Dusseldorf','Leipzig','Dortmund','Essen','Bremen','Dresden','Hanover','Nuremberg','Duisburg','Bochum','Wuppertal','Bielefeld','Bonn','Mannheim','Karlsruhe'],
    'france': ['Paris','Marseille','Lyon','Toulouse','Nice','Nantes','Strasbourg','Montpellier','Bordeaux','Lille','Rennes','Reims','Saint-Etienne','Toulon','Le Havre','Grenoble','Dijon','Angers','Nimes','Aix-en-Provence'],
    'italy': ['Rome','Milan','Naples','Turin','Palermo','Genoa','Bologna','Florence','Bari','Catania','Venice','Verona','Messina','Padua','Trieste','Brescia','Parma','Taranto','Prato','Modena'],
    'spain': ['Madrid','Barcelona','Valencia','Seville','Zaragoza','Malaga','Murcia','Palma','Las Palmas','Bilbao','Alicante','Cordoba','Valladolid','Vigo','Gijon','Granada','A Coruna','Oviedo'],
    'netherlands': ['Amsterdam','Rotterdam','The Hague','Utrecht','Eindhoven','Tilburg','Groningen','Almere','Breda','Nijmegen','Apeldoorn','Haarlem'],
    'belgium': ['Brussels','Antwerp','Ghent','Charleroi','Liege','Bruges','Namur','Leuven','Mons','Aalst'],
    'portugal': ['Lisbon','Porto','Amadora','Braga','Setubal','Coimbra','Funchal','Almada','Aveiro','Viseu'],
    'poland': ['Warsaw','Krakow','Lodz','Wroclaw','Poznan','Gdansk','Szczecin','Bydgoszcz','Lublin','Katowice','Bialystok','Gdynia'],
    'sweden': ['Stockholm','Gothenburg','Malmo','Uppsala','Vasteras','Orebro','Linkoping','Helsingborg','Jonkoping','Norrkoping'],
    'norway': ['Oslo','Bergen','Stavanger','Trondheim','Drammen','Fredrikstad','Kristiansand','Sandnes','Tromso'],
    'denmark': ['Copenhagen','Aarhus','Odense','Aalborg','Esbjerg','Vejle','Randers','Viborg','Kolding'],
    'finland': ['Helsinki','Espoo','Tampere','Vantaa','Oulu','Turku','Jyvaskyla','Lahti','Kuopio'],
    'switzerland': ['Zurich','Geneva','Basel','Bern','Lausanne','Winterthur','St Gallen','Lucerne','Biel','Thun'],
    'austria': ['Vienna','Graz','Linz','Salzburg','Innsbruck','Klagenfurt','Villach','Wels','St Polten'],
    'czech_republic': ['Prague','Brno','Ostrava','Plzen','Liberec','Olomouc','Usti nad Labem','Hradec Kralove','Pardubice'],
    'hungary': ['Budapest','Debrecen','Miskolc','Szeged','Pecs','Gyor','Nyiregyhaza','Kecskemet'],
    'romania': ['Bucharest','Cluj-Napoca','Timisoara','Iasi','Constanta','Craiova','Brasov','Galati','Ploiesti'],
    'greece': ['Athens','Thessaloniki','Patras','Heraklion','Larissa','Volos','Ioannina','Kavala','Rhodes'],
    'ukraine': ['Kyiv','Kharkiv','Odessa','Dnipro','Zaporizhzhia','Lviv','Kryvyi Rih','Mykolaiv'],
    'russia': ['Moscow','Saint Petersburg','Novosibirsk','Yekaterinburg','Nizhny Novgorod','Kazan','Chelyabinsk','Omsk','Samara','Rostov-on-Don','Ufa','Krasnoyarsk','Perm','Voronezh','Volgograd'],
    'turkey': ['Istanbul','Ankara','Izmir','Bursa','Adana','Gaziantep','Konya','Antalya','Kayseri','Diyarbakir','Mersin','Eskisehir'],
    'croatia': ['Zagreb','Split','Rijeka','Osijek','Zadar'],
    'serbia': ['Belgrade','Novi Sad','Nis','Kragujevac','Subotica'],
    'slovakia': ['Bratislava','Kosice','Presov','Zilina','Nitra'],
    'bulgaria': ['Sofia','Plovdiv','Varna','Burgas','Ruse','Stara Zagora'],
    'lithuania': ['Vilnius','Kaunas','Klaipeda','Siauliai','Panevezys'],
    'latvia': ['Riga','Daugavpils','Liepaja','Jelgava','Jurmala'],
    'estonia': ['Tallinn','Tartu','Narva','Parnu'],
    'slovenia': ['Ljubljana','Maribor','Celje','Kranj'],
    'luxembourg': ['Luxembourg City','Esch-sur-Alzette','Differdange'],
    'iceland': ['Reykjavik','Kopavogur','Hafnarfjordur','Akureyri'],
    'albania': ['Tirana','Durres','Vlore','Elbasan','Shkoder'],
    'north_macedonia': ['Skopje','Bitola','Kumanovo','Prilep','Tetovo'],
    'bosnia': ['Sarajevo','Banja Luka','Tuzla','Zenica','Mostar'],
    'moldova': ['Chisinau','Tiraspol','Balti','Bender'],
    'belarus': ['Minsk','Gomel','Mogilev','Vitebsk','Grodno'],
    'uae': ['Dubai','Abu Dhabi','Sharjah','Al Ain','Ajman','Ras al-Khaimah','Fujairah'],
    'saudi_arabia': ['Riyadh','Jeddah','Mecca','Medina','Dammam','Taif','Tabuk','Buraidah','Khamis Mushait'],
    'israel': ['Jerusalem','Tel Aviv','Haifa','Rishon LeZion','Petah Tikva','Ashdod','Netanya','Beer Sheva'],
    'jordan': ['Amman','Zarqa','Irbid','Russeifa','Aqaba'],
    'lebanon': ['Beirut','Tripoli','Sidon','Tyre'],
    'kuwait': ['Kuwait City','Salmiya','Hawalli','Al Farwaniyah'],
    'qatar': ['Doha','Al Rayyan','Umm Salal','Al Wakrah'],
    'bahrain': ['Manama','Riffa','Muharraq','Hamad Town'],
    'oman': ['Muscat','Seeb','Salalah','Bawshar','Sohar'],
    'iraq': ['Baghdad','Basra','Mosul','Erbil','Sulaymaniyah','Kirkuk'],
    'iran': ['Tehran','Mashhad','Isfahan','Karaj','Tabriz','Shiraz','Ahvaz'],
    'pakistan': ['Karachi','Lahore','Faisalabad','Rawalpindi','Islamabad','Gujranwala','Peshawar','Multan','Hyderabad','Quetta','Sialkot','Bahawalpur'],
    'india': ['Mumbai','Delhi','Bangalore','Hyderabad','Chennai','Kolkata','Pune','Ahmedabad','Surat','Jaipur','Lucknow','Kanpur','Nagpur','Indore','Thane','Bhopal','Visakhapatnam','Patna','Vadodara','Ludhiana','Agra','Nashik','Varanasi','Meerut','Rajkot','Aurangabad','Dhanbad','Amritsar','Ranchi','Allahabad','Coimbatore','Faridabad'],
    'bangladesh': ['Dhaka','Chittagong','Khulna','Rajshahi','Sylhet','Comilla','Mymensingh','Narayanganj','Gazipur'],
    'sri_lanka': ['Colombo','Dehiwala','Moratuwa','Kandy','Negombo','Jaffna'],
    'nepal': ['Kathmandu','Pokhara','Lalitpur','Biratnagar','Birgunj','Bharatpur'],
    'indonesia': ['Jakarta','Surabaya','Bandung','Medan','Bekasi','Tangerang','Depok','Semarang','Palembang','Makassar','Batam','Pekanbaru','Bogor','Malang','Yogyakarta','Denpasar'],
    'philippines': ['Manila','Quezon City','Davao','Caloocan','Zamboanga','Cebu City','Antipolo','Pasig','Taguig','Valenzuela','Cagayan de Oro'],
    'vietnam': ['Ho Chi Minh City','Hanoi','Da Nang','Hai Phong','Bien Hoa','Nha Trang','Can Tho','Hue','Da Lat'],
    'thailand': ['Bangkok','Nonthaburi','Pak Kret','Hat Yai','Chiang Mai','Pattaya','Khon Kaen','Udon Thani','Nakhon Ratchasima'],
    'malaysia': ['Kuala Lumpur','George Town','Ipoh','Shah Alam','Petaling Jaya','Johor Bahru','Subang Jaya','Miri','Kota Kinabalu','Kuching'],
    'singapore': ['Singapore','Jurong','Woodlands','Tampines','Sengkang'],
    'myanmar': ['Yangon','Mandalay','Naypyidaw','Mawlamyine'],
    'cambodia': ['Phnom Penh','Siem Reap','Battambang','Kampong Cham'],
    'laos': ['Vientiane','Savannakhet','Pakse','Luang Prabang'],
    'china': ['Shanghai','Beijing','Guangzhou','Shenzhen','Tianjin','Chongqing','Chengdu','Nanjing','Wuhan','Xian','Hangzhou','Shenyang','Harbin','Qingdao','Jinan','Zhengzhou','Dalian','Dongguan','Changsha','Kunming','Changchun','Wenzhou','Xiamen','Fuzhou'],
    'japan': ['Tokyo','Yokohama','Osaka','Nagoya','Sapporo','Kobe','Kyoto','Fukuoka','Kawasaki','Saitama','Hiroshima','Sendai','Chiba','Kitakyushu','Niigata','Hamamatsu','Kumamoto','Okayama'],
    'south_korea': ['Seoul','Busan','Incheon','Daegu','Daejeon','Gwangju','Suwon','Ulsan','Seongnam','Goyang','Bucheon'],
    'taiwan': ['Taipei','Kaohsiung','Taichung','Tainan','Banqiao','Zhongli','Hsinchu','Keelung'],
    'hong_kong': ['Hong Kong','Kowloon','Tsuen Wan','Sha Tin','Tuen Mun'],
    'mongolia': ['Ulaanbaatar','Erdenet','Darkhan'],
    'kazakhstan': ['Almaty','Nur-Sultan','Shymkent','Karaganda','Aktobe'],
    'uzbekistan': ['Tashkent','Samarkand','Namangan','Andijan'],
    'nigeria': ['Lagos','Kano','Ibadan','Abuja','Port Harcourt','Benin City','Maiduguri','Zaria','Aba','Jos','Ilorin','Enugu'],
    'south_africa': ['Johannesburg','Cape Town','Durban','Pretoria','Port Elizabeth','Pietermaritzburg','Benoni','Tembisa','East London'],
    'kenya': ['Nairobi','Mombasa','Nakuru','Ruiru','Eldoret','Kisumu'],
    'ethiopia': ['Addis Ababa','Dire Dawa','Nazret','Bahir Dar','Mekelle','Gondar'],
    'ghana': ['Accra','Kumasi','Tamale','Sekondi-Takoradi'],
    'tanzania': ['Dar es Salaam','Mwanza','Arusha','Dodoma'],
    'egypt': ['Cairo','Alexandria','Giza','Shubra El Kheima','Port Said','Suez','Luxor','Aswan','Mansoura','Tanta'],
    'morocco': ['Casablanca','Fez','Tangier','Marrakech','Sale','Meknes','Rabat','Oujda','Kenitra','Agadir'],
    'algeria': ['Algiers','Oran','Constantine','Batna','Djelfa','Setif','Annaba'],
    'tunisia': ['Tunis','Sfax','Sousse','Kairouan','Gabes'],
    'senegal': ['Dakar','Thies','Touba','Kaolack'],
    'ivory_coast': ['Abidjan','Abobo','Bouake','Korhogo','Daloa'],
    'cameroon': ['Douala','Yaounde','Garoua','Bamenda','Bafoussam'],
    'angola': ['Luanda','Lubango','Huambo','Lobito','Benguela'],
    'mozambique': ['Maputo','Matola','Beira','Nampula','Chimoio'],
    'zambia': ['Lusaka','Kitwe','Ndola','Livingstone'],
    'zimbabwe': ['Harare','Bulawayo','Chitungwiza','Mutare'],
    'madagascar': ['Antananarivo','Toamasina','Antsirabe','Fianarantsoa'],
    'uganga': ['Kampala','Gulu','Lira','Mbarara','Jinja'],
    'rwanda': ['Kigali','Butare','Gitarama','Musanze'],
    'haiti': ['Port-au-Prince','Carrefour','Delmas','Cap-Haitien'],
    'puerto_rico': ['San Juan','Bayamon','Carolina','Ponce','Caguas'],
    'papua_new_guinea': ['Port Moresby','Lae','Mount Hagen','Madang'],
    'fiji': ['Suva','Lautoka','Nadi'],
}

COUNTRY_ALIASES = {
    'us': 'usa', 'united_states': 'usa', 'america': 'usa',
    'united_kingdom': 'uk', 'england': 'uk', 'britain': 'uk',
    'emirates': 'uae', 'united_arab_emirates': 'uae',
    'korea': 'south_korea', 'south korea': 'south_korea',
    'nz': 'new_zealand', 'new zealand': 'new_zealand',
    'sa': 'south_africa', 'south africa': 'south_africa',
    'czech': 'czech_republic', 'czechia': 'czech_republic',
    'dr': 'dominican_republic',
    'trinidad': 'trinidad_tobago', 'tt': 'trinidad_tobago',
    'png': 'papua_new_guinea',
    'ivory_coast': 'ivory_coast', 'cote_divoire': 'ivory_coast',
}

def resolve_country(name):
    key = name.lower().strip().replace('-', '_').replace(' ', '_')
    return COUNTRY_ALIASES.get(key, key)


DEFAULT_NICHES = [
    "Coffee Shop", "Cafe", "Bakery", "Restaurant", "Food Truck",
    "Gym", "Fitness Studio", "Yoga Studio",
    "Hair Salon", "Barber Shop", "Nail Salon", "Spa",
    "Roofing Contractor", "Landscaping Service", "Cleaning Service",
    "Plumber", "Electrician", "Handyman", "Painter", "HVAC",
    "Auto Repair", "Car Wash", "Pet Grooming", "Florist",
    "Tattoo Shop", "Photography Studio",
]


def is_valid_email(email):
    if not email:
        return False
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


def extract_email(text):
    if not text:
        return None
    m = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return m.group(0) if m else None


def clean_name(name):
    if not name:
        return 'Unknown'
    for s in ['Ltd','Limited','LTD','LLC','Inc','Corp','Pty','L.L.C.']:
        name = re.sub(rf'\b{s}\.?\b', '', name, flags=re.IGNORECASE)
    return ' '.join(name.split()).strip()


def load_existing(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []


def save(leads, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(leads)} leads → {filepath}")



async def _extract_email_from_website(page, url):
    """Visit a business website and hunt for email addresses."""
    try:
        await page.goto(url, timeout=15000, wait_until='domcontentloaded')
        await page.wait_for_timeout(1500)
        text = await page.content()
        m = re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
        if m:
            email = m.group(0).lower()
            if is_valid_email(email) and not any(x in email for x in ['example','placeholder','sentry','wix','schema','wordpress']):
                return email
        for contact_path in ['/contact', '/contact-us', '/about']:
            try:
                await page.goto(url.rstrip('/') + contact_path, timeout=10000, wait_until='domcontentloaded')
                await page.wait_for_timeout(800)
                text2 = await page.content()
                m2 = re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text2)
                if m2:
                    email = m2.group(0).lower()
                    if is_valid_email(email) and not any(x in email for x in ['example','placeholder','sentry','wix','schema','wordpress']):
                        return email
            except Exception:
                continue
    except Exception:
        pass
    return None

async def _scrape(cities, niches, target, output_file, headless=True, no_website_only=False):
    leads    = load_existing(output_file)
    initial  = len(leads)
    existing = {l.get('email','') for l in leads if l.get('email')}

    print(f"🎯 Target: {target} leads  |  Currently: {initial}")
    print(f"🌍 Cities: {len(cities)}  |  Niches: {len(niches)}\n")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled','--no-sandbox']
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1366, 'height': 768}
        )
        maps_page    = await ctx.new_page()
        website_page = await ctx.new_page()

        try:
            for city in cities:
                if len(leads) >= target:
                    break
                print(f"\n{'='*55}")
                print(f"🏙  {city}")
                print(f"{'='*55}")

                for niche in niches:
                    if len(leads) >= target:
                        break

                    query = f"{niche} in {city}"
                    print(f"  🔍 Searching: {query}")
                    found_this_niche = 0

                    try:
                        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
                        await maps_page.goto(url, timeout=60000, wait_until='domcontentloaded')
                        await maps_page.wait_for_timeout(3500)

                        for _ in range(5):
                            await maps_page.keyboard.press('End')
                            await maps_page.wait_for_timeout(800)
                            try:
                                feed = await maps_page.query_selector('div[role="feed"]')
                                if feed:
                                    await feed.evaluate('el => el.scrollTop += 2000')
                            except Exception:
                                pass

                        try:
                            await maps_page.wait_for_selector('div[role="article"]', timeout=15000)
                        except Exception:
                            print(f"     ⚠️  No listings loaded — skipping")
                            continue
                        listings = await maps_page.query_selector_all('div[role="article"]')
                        print(f"     Found {len(listings)} listings on map")

                        for listing in listings:
                            if len(leads) >= target:
                                break
                            try:
                                await listing.click()
                                # Wait for the detail panel to load with the actual business name
                                try:
                                    await maps_page.wait_for_selector('h1', timeout=5000)
                                except Exception:
                                    pass
                                await maps_page.wait_for_timeout(1500)

                                # Business name — must be from detail panel, not search results header
                                name = None
                                for sel in ['h1.DUwDid', 'h1.DUO9ee', 'h1.lMbq3e', 'h1']:
                                    el = await maps_page.query_selector(sel)
                                    if el:
                                        t = (await el.inner_text()).strip()
                                        if t and len(t) > 2:
                                            name = clean_name(t)
                                            break
                                if not name:
                                    continue
                                # Filter out Google Maps UI text mistaken as business names
                                junk_names = {'results', 'more results', 'next page', 'all results',
                                              'showing results', 'sponsored', 'advertisement', 'open now',
                                              'closed', 'closes soon', 'opens soon'}
                                if name.lower().strip() in junk_names or len(name.strip()) < 3:
                                    continue

                                # Phone number
                                phone = None
                                for sel in ['button[data-item-id^="phone:tel:"]', 'button[aria-label*="phone" i]']:
                                    el = await maps_page.query_selector(sel)
                                    if el:
                                        v = await el.get_attribute('data-item-id') or await el.get_attribute('aria-label') or ''
                                        phone = v.replace('phone:tel:', '').replace('Phone:', '').strip()
                                        if phone:
                                            break

                                # Website
                                website = None
                                for sel in ['a[data-item-id="authority"]', 'a[aria-label*="website" i]']:
                                    el = await maps_page.query_selector(sel)
                                    if el:
                                        website = await el.get_attribute('href')
                                        if website:
                                            break

                                # WhatsApp link on Maps panel
                                whatsapp = None
                                for sel in ['a[href*="whatsapp"]', 'a[aria-label*="whatsapp" i]', 'button[aria-label*="whatsapp" i]']:
                                    el = await maps_page.query_selector(sel)
                                    if el:
                                        href = await el.get_attribute('href') or ''
                                        if 'whatsapp' in href.lower() or 'wa.me' in href.lower():
                                            whatsapp = href
                                            break
                                # Derive WhatsApp from phone if no direct link
                                if not whatsapp and phone:
                                    digits = re.sub(r'[^0-9]', '', phone)
                                    if len(digits) >= 7:
                                        whatsapp = f"https://wa.me/{digits}"

                                # Email — check Maps panel first
                                email = None
                                for sel in ['a[href^="mailto:"]', 'button[data-item-id^="email"]']:
                                    el = await maps_page.query_selector(sel)
                                    if el:
                                        v = await el.get_attribute('href') or await el.get_attribute('data-item-id') or ''
                                        candidate = v.replace('mailto:', '').replace('email:', '').split('?')[0].strip()
                                        if is_valid_email(candidate):
                                            email = candidate.lower()
                                            break

                                # If has website, visit it for email
                                if not email and website:
                                    print(f"     🌐 Checking: {website[:55]}...")
                                    email = await _extract_email_from_website(website_page, website)

                                # Filter: skip businesses WITH a website if --no-website-only
                                if no_website_only and website:
                                    print(f"     ⏭  {name} — has website, skipping")
                                    continue

                                # Must have email OR whatsapp/phone — skip if neither
                                has_contact = email or whatsapp or phone
                                if not has_contact:
                                    print(f"     ⏭  {name} — no contact info")
                                    continue

                                # Skip duplicate emails
                                if email and email in existing:
                                    continue
                                if email:
                                    existing.add(email)

                                lead = {
                                    'business_name': name,
                                    'email':         email or '',
                                    'phone':         phone or '',
                                    'whatsapp':      whatsapp or '',
                                    'has_website':   bool(website),
                                    'website':       website or '',
                                    'city':          city,
                                    'niche':         niche,
                                    'status':        'pending',
                                    'contacted':     False,
                                    'scraped_at':    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                }
                                leads.append(lead)
                                found_this_niche += 1

                                contact_str = f"{email or ''} | WA:{whatsapp[:30] if whatsapp else 'no'} | {phone or 'no phone'}"
                                site_str    = '🌐 has site' if website else '🚫 no site'
                                print(f"     ✅ #{len(leads)} {name} | {site_str} | {contact_str}")

                                if len(leads) % 5 == 0:
                                    save(leads, output_file)

                            except Exception:
                                continue

                        print(f"  ✔  {niche}: {found_this_niche} leads\n")

                    except Exception as e:
                        print(f"  ⚠️  {str(e)[:80]}")

        finally:
            save(leads, output_file)
            await browser.close()


def run_scrape(args):
    country = resolve_country(args.country)
    cities  = args.cities  if args.cities  else CITY_LISTS.get(country, [])
    niches  = args.niches  if args.niches  else DEFAULT_NICHES
    output  = args.output  if args.output  else f"{country}_leads.json"
    target  = args.target
    headless = getattr(args, 'headless', True)
    no_website_only = getattr(args, 'no_website_only', False)

    if not cities:
        print(f"❌ No cities found for country: {country}")
        return

    print(f"🌍 Country: {country.upper()}")
    asyncio.run(_scrape(cities, niches, target, output, headless, no_website_only))