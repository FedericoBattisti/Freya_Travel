"""
Itinerary with Images Tool - Crea itinerari con immagini integrate
"""

from langchain_core.tools import tool
from .chain_travel_plan import chain_travel_plan_tool
from .images_finder import images_finder_tool
from .hotels_finder import hotels_finder_tool
import re

@tool
def create_itinerary_with_images_tool(requirements: str) -> str:
    """
    Crea un itinerario dettagliato con immagini specifiche per ogni tappa.
    
    Args:
        requirements: Requisiti del viaggio (es. "3 giorni a Roma", "Weekend romantico Parigi")
    
    Returns:
        Itinerario completo con immagini integrate per ogni destinazione
    """
    try:
        print(f"🗺️ Creando itinerario con immagini per: {requirements}")
        
        # 1. Crea l'itinerario base
        print("📋 Generando itinerario base...")
        itinerary = chain_travel_plan_tool(requirements + " - crea un itinerario dettagliato con attrazioni specifiche")
        
        # 2. Estrai destinazioni e attrazioni dall'itinerario
        destinations = extract_destinations_from_itinerary(itinerary)
        main_city = extract_main_city_from_requirements(requirements)
        
        print(f"🎯 Destinazione principale: {main_city}")
        print(f"📍 Attrazioni identificate: {destinations}")
        
        # 3. Aggiungi immagini specifiche per ogni destinazione/attrazione
        enhanced_sections = []
        
        # Dividi l'itinerario in sezioni (giorni)
        itinerary_sections = split_itinerary_by_days(itinerary)
        
        for section in itinerary_sections:
            # Identifica attrazioni in questa sezione
            section_attractions = extract_attractions_from_section(section, main_city)
            
            enhanced_section = section
            
            # Aggiungi immagini per ogni attrazione in questa sezione
            for attraction in section_attractions[:2]:  # Max 2 per sezione per non appesantire
                print(f"🖼️ Aggiungendo immagini per: {attraction}")
                images = images_finder_tool(f"{attraction} {main_city}", "tourist attractions monuments")
                
                # Inserisci le immagini dopo la menzione dell'attrazione
                enhanced_section = insert_images_after_attraction(enhanced_section, attraction, images)
            
            enhanced_sections.append(enhanced_section)
        
        # 4. Aggiungi informazioni pratiche
        print(f"🏨 Aggiungendo informazioni alloggi per {main_city}")
        hotels_info = hotels_finder_tool(main_city, "", "")
        
        # 5. Ricomponi l'itinerario enhanced
        enhanced_itinerary = "\n\n".join(enhanced_sections)
        
        # 6. Aggiungi sezione finale con informazioni pratiche
        enhanced_itinerary += f"""

## 🏨 Dove Alloggiare
{hotels_info}

---
💡 **Suggerimenti per il viaggio:**
- Prenota in anticipo le attrazioni principali
- Porta scarpe comode per camminare
- Controlla gli orari di apertura dei musei
- Prova la cucina locale nei ristoranti consigliati

🎯 **Personalizza il tuo itinerario:** Chiedi modifiche specifiche o informazioni aggiuntive su qualsiasi tappa!
        """
        
        print(f"✅ Itinerario con immagini completato per {requirements}")
        return enhanced_itinerary
        
    except Exception as e:
        print(f"❌ Errore nella creazione itinerario: {str(e)}")
        return f"❌ Errore nella creazione dell'itinerario: {str(e)}"

def extract_main_city_from_requirements(requirements: str) -> str:
    """Estrae la città principale dai requisiti"""
    # Pattern per identificare città
    import re
    
    # Lista di città comuni
    major_cities = [
        "Roma", "Milano", "Napoli", "Firenze", "Venezia", "Torino", "Bologna", "Palermo",
        "Parigi", "Londra", "Berlino", "Madrid", "Barcellona", "Amsterdam", "Vienna",
        "Praga", "Budapest", "Varsavia", "Stoccolma", "Copenaghen", "Oslo",
        "New York", "Los Angeles", "Chicago", "San Francisco", "Boston", "Miami",
        "Tokyo", "Kyoto", "Osaka", "Seoul", "Shanghai", "Beijing", "Hong Kong",
        "Sydney", "Melbourne", "Auckland", "Mumbai", "Delhi", "Bangkok", "Singapore"
    ]
    
    requirements_lower = requirements.lower()
    
    for city in major_cities:
        if city.lower() in requirements_lower:
            return city
    
    # Pattern generico per estrarre nomi di luoghi
    place_patterns = [
        r"(?:a|in|per)\s+([A-Z][a-zA-ZÀ-ÿ\s]{2,20})",
        r"([A-Z][a-zA-ZÀ-ÿ\s]{2,20})\s+(?:viaggio|tour|vacanza)"
    ]
    
    for pattern in place_patterns:
        matches = re.findall(pattern, requirements)
        if matches:
            return matches[0].strip()
    
    return "destinazione"

def split_itinerary_by_days(itinerary: str) -> list:
    """Divide l'itinerario in sezioni per giorno"""
    import re
    
    # Pattern per identificare i giorni
    day_patterns = [
        r"(Giorno \d+:.*?)(?=Giorno \d+:|$)",
        r"(Day \d+:.*?)(?=Day \d+:|$)",
        r"(\d+° giorno:.*?)(?=\d+° giorno:|$)",
        r"(GIORNO \d+.*?)(?=GIORNO \d+|$)"
    ]
    
    sections = []
    
    for pattern in day_patterns:
        matches = re.findall(pattern, itinerary, re.DOTALL | re.IGNORECASE)
        if matches:
            sections.extend(matches)
            break
    
    # Se non trova pattern di giorni, divide per paragrafi
    if not sections:
        sections = [section.strip() for section in itinerary.split('\n\n') if section.strip()]
    
    return sections

def extract_destinations_from_itinerary(itinerary: str) -> list:
    """Estrae destinazioni specifiche da un itinerario"""
    import re
    
    destinations = []
    
    # Pattern per riconoscere attrazioni
    patterns = [
        r"(?:Visita|Visitare|Vedere|Ammirare|Scoprire)\s+(?:al|alla|il|la|lo|l')?\s*([A-Z][a-zA-ZÀ-ÿ\s]{3,30})",
        r"([A-Z][a-zA-ZÀ-ÿ\s]{3,30})\s+(?:è|sono|rappresenta|costituisce)",
        r"(?:fermata|tappa|destinazione|attrazione)(?:\s+a)?\s+([A-Z][a-zA-ZÀ-ÿ\s]{3,30})",
        r"(\w+(?:\s+\w+){0,3})\s+(?:Basilica|Cattedrale|Chiesa|Palazzo|Castello|Museo|Galleria|Torre|Ponte|Piazza|Fontana)"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, itinerary)
        for match in matches:
            dest = match.strip().strip('.,!?:')
            if len(dest) > 3 and dest not in destinations:
                destinations.append(dest)
    
    return destinations[:8]  # Limita a 8 destinazioni

def extract_attractions_from_section(section: str, main_city: str) -> list:
    """Estrae attrazioni da una sezione specifica dell'itinerario"""
    import re
    
    attractions = []
    
    # Pattern specifici per questa sezione
    patterns = [
        r"([A-Z][a-zA-ZÀ-ÿ\s]{3,25})(?:\s+(?:Basilica|Cattedrale|Chiesa|Palazzo|Castello|Museo|Galleria|Torre|Ponte|Piazza|Fontana))",
        r"(?:Basilica|Cattedrale|Chiesa|Palazzo|Castello|Museo|Galleria|Torre|Ponte|Piazza|Fontana)\s+([A-Z][a-zA-ZÀ-ÿ\s]{3,25})"
    ]
    
    section_lower = section.lower()
    
    # Cerca nomi di attrazioni famose
    famous_attractions = [
        "Colosseo", "Pantheon", "Fontana di Trevi", "Vaticano", "Cappella Sistina",
        "Torre Eiffel", "Louvre", "Notre Dame", "Arc de Triomphe", "Sacré-Cœur",
        "Big Ben", "Tower Bridge", "British Museum", "Westminster Abbey",
        "Sagrada Familia", "Park Güell", "Casa Batlló", "Casa Milà"
    ]
    
    for attraction in famous_attractions:
        if attraction.lower() in section_lower:
            attractions.append(attraction)
    
    # Usa pattern per trovare altre attrazioni
    for pattern in patterns:
        matches = re.findall(pattern, section)
        for match in matches:
            attr = match.strip()
            if len(attr) > 3 and attr not in attractions:
                attractions.append(attr)
    
    return attractions[:3]  # Max 3 per sezione

def insert_images_after_attraction(section: str, attraction: str, images: str) -> str:
    """Inserisce immagini dopo la menzione di un'attrazione"""
    
    # Trova la posizione dell'attrazione nel testo
    import re
    
    # Pattern per trovare l'attrazione nel testo
    pattern = rf"({re.escape(attraction)}[^.\n]*[.\n])"
    match = re.search(pattern, section, re.IGNORECASE)
    
    if match:
        # Inserisci le immagini dopo la frase che contiene l'attrazione
        insertion_point = match.end()
        enhanced_section = (
            section[:insertion_point] + 
            f"\n\n{images}\n\n" + 
            section[insertion_point:]
        )
        return enhanced_section
    else:
        # Se non trova l'attrazione, aggiungi le immagini alla fine della sezione
        return section + f"\n\n{images}\n"