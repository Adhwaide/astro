"""
core/yogas.py
──────────────
Rule-based Yoga & Interpretation generation based on planetary positions.
Detects major Yogas (Pancha Mahapurusha, Gajakesari, etc.) and generates
an automated written report.
"""

def get_lord_of_house(house_number, houses_list):
    # House number is 1-12
    # houses_list has [{"house": 1, "sign": ..., "sign_name": ...}]
    sign = houses_list[house_number - 1]['sign']
    ownership = {
        0: 'Ma', 1: 'Ve', 2: 'Me', 3: 'Mo', 
        4: 'Su', 5: 'Me', 6: 'Ve', 7: 'Ma', 
        8: 'Ju', 9: 'Sa', 10: 'Sa', 11: 'Ju'
    }
    return ownership.get(sign)

def detect_yogas(chart: dict):
    planets = chart['planets']
    houses = chart['houses']
    lagna = chart['lagna']
    
    yogas_found = []

    # Helper maps
    by_id = {p['id']: p for p in planets}
    
    # Exaltation & Own signs
    # Su: ex 0, own 4
    # Mo: ex 1, own 3
    # Ma: ex 9, own 0,7
    # Me: ex 5, own 2,5
    # Ju: ex 3, own 8,11
    # Ve: ex 11, own 1,6
    # Sa: ex 6, own 9,10
    
    # ── Pancha Mahapurusha Yogas ──
    # Mars: Ruchaka
    ma = by_id.get('Ma')
    if ma and ma['house'] in [1, 4, 7, 10]:
        if ma['sign'] in [0, 7, 9]:
            yogas_found.append({
                "name": "Ruchaka Yoga (Pancha Mahapurusha)",
                "description": "Mars is in a Kendra in its own or exalted sign.",
                "interpretation": "Bestows courage, strong physique, leadership qualities, and success in police, military, or sports."
            })
            
    # Mercury: Bhadra
    me = by_id.get('Me')
    if me and me['house'] in [1, 4, 7, 10]:
        if me['sign'] in [2, 5]:
            yogas_found.append({
                "name": "Bhadra Yoga (Pancha Mahapurusha)",
                "description": "Mercury is in a Kendra in its own or exalted sign.",
                "interpretation": "Confers high intelligence, excellent communication skills, and success in business, writing, or academia."
            })
            
    # Jupiter: Hamsa
    ju = by_id.get('Ju')
    if ju and ju['house'] in [1, 4, 7, 10]:
        if ju['sign'] in [3, 8, 11]:
            yogas_found.append({
                "name": "Hamsa Yoga (Pancha Mahapurusha)",
                "description": "Jupiter is in a Kendra in its own or exalted sign.",
                "interpretation": "Grants wisdom, purity of mind, profound knowledge, and respect in society."
            })
            
    # Venus: Malavya
    ve = by_id.get('Ve')
    if ve and ve['house'] in [1, 4, 7, 10]:
        if ve['sign'] in [1, 6, 11]:
            yogas_found.append({
                "name": "Malavya Yoga (Pancha Mahapurusha)",
                "description": "Venus is in a Kendra in its own or exalted sign.",
                "interpretation": "Brings luxury, charm, an eye for beauty, and success in arts, media, or comforts."
            })
            
    # Saturn: Shasha
    sa = by_id.get('Sa')
    if sa and sa['house'] in [1, 4, 7, 10]:
        if sa['sign'] in [6, 9, 10]:
            yogas_found.append({
                "name": "Shasha Yoga (Pancha Mahapurusha)",
                "description": "Saturn is in a Kendra in its own or exalted sign.",
                "interpretation": "Endows patience, authority, political power, and ability to rule or manage large organizations."
            })

    # ── Gajakesari Yoga ──
    mo = by_id.get('Mo')
    if ju and mo:
        # Distance calculation
        diff_houses = (ju['house'] - mo['house']) % 12
        if diff_houses in [0, 3, 6, 9]: # 1st, 4th, 7th, 10th from each other
            yogas_found.append({
                "name": "Gajakesari Yoga",
                "description": "Jupiter is in a Kendra (1st, 4th, 7th, 10th) from the Moon.",
                "interpretation": "One of the most auspicious yogas. Brings lasting fame, eloquence, brilliance, and victory over adversaries."
            })
            
    # ── Sun + Mercury: Budhaditya ──
    su = by_id.get('Su')
    if su and me:
        if su['house'] == me['house']:
            yogas_found.append({
                "name": "Budhaditya Yoga",
                "description": "Sun and Mercury are conjunct.",
                "interpretation": "Confers intellect, analytical abilities, and administrative success."
            })

    # ── Dhana Yogas (Wealth) ──
    # Simplification: Lord of 2 in 11, or 11 in 2.
    lord_2 = get_lord_of_house(2, houses)
    lord_11 = get_lord_of_house(11, houses)
    lord_2_planet = by_id.get(lord_2)
    lord_11_planet = by_id.get(lord_11)
    
    if lord_2_planet and lord_11_planet:
        if lord_2_planet['house'] == 11 or lord_11_planet['house'] == 2 or lord_2_planet['house'] == lord_11_planet['house']:
            yogas_found.append({
                "name": "Maha Dhana Yoga",
                "description": "Connection between the lords of the 2nd (wealth) and 11th (gains) houses.",
                "interpretation": "Indicates significant financial prosperity, multiple streams of income, and immense wealth generation."
            })
            
    # ── Raja Yogas (Power/Success) ──
    # Conjunction of Kendra Lord (1,4,7,10) and Trikona Lord (1,5,9)
    kendras = [1, 4, 7, 10]
    trikonas = [1, 5, 9]
    kendra_lords = {get_lord_of_house(h, houses) for h in kendras}
    trikona_lords = {get_lord_of_house(h, houses) for h in trikonas}
    
    raja_yoga_detected = set()
    for p in planets:
        house = p['house']
        house_planets = [pl['id'] for pl in planets if pl['house'] == house]
        if len(house_planets) > 1:
            # Check if any kendra lord and trikona lord are in this house
            kl_in_house = set(house_planets).intersection(kendra_lords)
            tl_in_house = set(house_planets).intersection(trikona_lords)
            for k in kl_in_house:
                for t in tl_in_house:
                    if k != t and (k, t) not in raja_yoga_detected and (t, k) not in raja_yoga_detected:
                        if (k in ['Ra', 'Ke']) or (t in ['Ra', 'Ke']):
                            continue
                        raja_yoga_detected.add((k, t))
    
    for (k, t) in raja_yoga_detected:
        yogas_found.append({
            "name": f"Kendra-Trikona Raja Yoga ({k}-{t})",
            "description": f"Conjunction of Kendra lord ({k}) and Trikona lord ({t}).",
            "interpretation": "Highly auspicious planetary combination bringing high status, power, authority, and phenomenal success."
        })

    return yogas_found


def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        return str(n) + 'th'
    return str(n) + ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]

def generate_written_report(chart: dict, yogas: list) -> str:
    """
    Generates a rule-based written interpretation in Markdown.
    """
    lagna = chart['lagna']
    moon = next((p for p in chart['planets'] if p['id'] == 'Mo'), None)
    sun = next((p for p in chart['planets'] if p['id'] == 'Su'), None)
    
    report = f"## Astrological Birth Report\n\n"
    report += f"### Core Personality (Lagna)\n"
    report += f"Your Ascendant (Lagna) is **{lagna['sign_name']}**. "
    if lagna['sign'] in [0, 4, 8]:
        report += "This gives you a fiery, energetic, and action-oriented nature. "
    elif lagna['sign'] in [1, 5, 9]:
        report += "This gives you a practical, grounded, and stable approach to life. "
    elif lagna['sign'] in [2, 6, 10]:
        report += "This bestows a cerebral, communicative, and intellectual disposition. "
    elif lagna['sign'] in [3, 7, 11]:
        report += "This implies a deeply emotional, intuitive, and sensitive core personality. "

    if moon:
        report += f"\n\n### Mind & Emotions (Moon)\n"
        report += f"Your Moon is in **{moon['sign_name']}** in the **{ordinal(moon['house'])} house**. "
        report += f"The Nakshatra of the Moon is **{moon['nakshatra']}**. "
        report += "This placement heavily focuses your mental energy, showing where you seek emotional security and satisfaction."

    if sun:
        report += f"\n\n### Soul & Vitality (Sun)\n"
        report += f"Your Sun is in **{sun['sign_name']}** in the **{ordinal(sun['house'])} house**. "
        report += "This illuminates the core area of your life where your soul seeks expression, power, and identity."
        
    report += f"\n\n### Formative Yogas Discovered\n"
    if not yogas:
        report += "*No major classic yogas identified in this basic scan.*\n"
    else:
        for y in yogas:
            report += f"- **{y['name']}**: {y['interpretation']}\n"
            
    report += "\n***Disclaimer:** This automated report is generated using classical Vedic rules and should be contextualized by a human astrologer for detailed life advice.*"
    return report

