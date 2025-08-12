"""
Destination Guide Tool - Crea guide complete coordinando più tool
"""

from langchain_core.tools import tool
from .chain_historical_expert import chain_historical_expert_tool
from .images_finder import images_finder_tool
from .hotels_finder import hotels_finder_tool
import re

@tool
def create_destination_guide_tool(destination: str) -> str:
    """
    Crea una guida completa di una destinazione coordinando più tool.
    
    Args:
        destination: Nome della destinazione (es. "Roma", "Parigi", "Tokyo")
    
    Returns:
        Guida completa con storia, immagini e informazioni pratiche
    """
    try:
        print(f"🌟 Creando guida completa per {destination}")
        
        # 1. Informazioni storiche e culturali
        print(f"📚 Recuperando informazioni storiche per {destination}")
        historical_info = chain_historical_expert_tool(f"{destination} storia cultura monumenti principali attrazioni")
        
        # 2. Estrai attrazioni specifiche dalle informazioni storiche
        attractions = extract_attractions_from_text(historical_info, destination)
        print(f"🏛️ Attrazioni identificate: {attractions}")
        
        # 3. Cerca immagini per ogni attrazione specifica
        images_content = ""
        for i, attraction in enumerate(attractions[:4], 1):  # Limita a 4 attrazioni principali
            print(f"🖼️ Cercando immagini per: {attraction}")
            attraction_images = images_finder_tool(f"{attraction} {destination}", "monument tourist attraction landmark")
            images_content += f"\n### 📸 {attraction}\n{attraction_images}\n"
        
        # 4. Informazioni pratiche sugli alloggi
        print(f"🏨 Recuperando informazioni alloggi per {destination}")
        hotels_info = hotels_finder_tool(destination, "", "")
        
        # 5. Combina tutto in una guida completa
        complete_guide = f"""# 🌟 Guida Completa: {destination}

## 📖 Storia e Cultura
{historical_info}

## 🏛️ Attrazioni Principali con Immagini
{images_content}

## 🏨 Dove Alloggiare
{hotels_info}

---
💡 **Prossimi passi:** 
- Usa "Pianifica itinerario {destination}" per un programma dettagliato
- Chiedi "Voli per {destination}" per informazioni sui collegamenti aerei
- Scopri "Cucina locale {destination}" per i piatti tipici da provare
        """
        
        print(f"✅ Guida completa creata per {destination}")
        return complete_guide
        
    except Exception as e:
        print(f"❌ Errore nella creazione guida per {destination}: {str(e)}")
        return f"❌ Errore nella creazione della guida per {destination}: {str(e)}"

def extract_attractions_from_text(text: str, destination: str) -> list:
    """Estrae nomi di attrazioni da un testo storico"""
    
    # Keywords che indicano attrazioni
    attraction_keywords = [
        # Edifici religiosi
        "basilica", "cattedrale", "chiesa", "duomo", "santuario", "abbazia", "monastero",
        # Edifici storici
        "palazzo", "castello", "fortezza", "villa", "residenza", "reggia",
        # Musei e cultura
        "museo", "galleria", "pinacoteca", "biblioteca", "teatro", "opera",
        # Monumenti
        "torre", "ponte", "arco", "colonna", "obelisco", "statua",
        # Spazi urbani
        "piazza", "fontana", "giardino", "parco", "mercato", "quartiere",
        # Attrazioni specifiche famose
        "colosseo", "pantheon", "vaticano", "sagrada familia", "eiffel", "big ben",
        "statue liberty", "christ redeemer", "machu picchu", "taj mahal", "petra",
        "stonehenge", "acropolis", "alhambra", "versailles"
    ]
    
    attractions = []
    lines = text.split('\n')
    
    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()
        
        # Salta linee troppo corte o che sono solo punteggiatura
        if len(line_clean) < 5 or line_clean in ['', '-', '*', '•']:
            continue
            
        for keyword in attraction_keywords:
            if keyword in line_lower:
                # Estrai il nome dell'attrazione dalla linea
                attraction = extract_attraction_name_from_line(line_clean, keyword, destination)
                if attraction and len(attraction) > 3 and attraction not in attractions:
                    attractions.append(attraction)
                break  # Una keyword per linea
    
    # Aggiungi attrazioni da pattern specifici
    pattern_attractions = extract_attractions_by_patterns(text, destination)
    attractions.extend(pattern_attractions)
    
    # Rimuovi duplicati e filtra
    unique_attractions = []
    for attraction in attractions:
        if attraction not in unique_attractions and len(attraction) > 3:
            unique_attractions.append(attraction)
    
    return unique_attractions[:6]  # Massimo 6 attrazioni

def extract_attraction_name_from_line(line: str, keyword: str, destination: str) -> str:
    """Estrae il nome di un'attrazione da una linea di testo"""
    
    # Pulisci la linea
    line = line.strip('.,!?:;-*•')
    
    # Pattern comuni per estrarre nomi
    patterns = [
        # "La Basilica di San Pietro"
        rf"((?:la|il|lo|l'|le|gli|i)?\s*{keyword}[^.,!?;]*)",
        # "San Pietro (basilica)"
        rf"([^.,!?;]*{keyword}[^.,!?;]*)",
        # Pattern per nomi propri prima del keyword
        rf"([A-Z][a-zA-ZÀ-ÿ\s]*{keyword}[^.,!?;]*)"
    ]
    
    for pattern in patterns:
        import re
        matches = re.findall(pattern, line, re.IGNORECASE)
        for match in matches:
            attraction = match.strip()
            # Filtra risultati troppo generici
            if len(attraction) > len(keyword) + 2 and not is_generic_phrase(attraction):
                return clean_attraction_name(attraction)
    
    return ""

def extract_attractions_by_patterns(text: str, destination: str) -> list:
    """Estrae attrazioni usando pattern specifici"""
    import re
    
    attractions = []
    
    # Pattern per nomi propri seguiti da descrizioni
    patterns = [
        r"([A-Z][a-zA-ZÀ-ÿ\s]{2,30})\s+(?:è|sono|rappresenta|costituisce)",
        r"(?:visitare|vedere|ammirare)\s+([A-Z][a-zA-ZÀ-ÿ\s]{2,30})",
        r"([A-Z][a-zA-ZÀ-ÿ\s]{2,30})\s+(?:costruit|erett|fondat)",
        r"(?:famoso|celebre|noto|importante)\s+([A-Z][a-zA-ZÀ-ÿ\s]{2,30})"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            attraction = match.strip()
            if len(attraction) > 3 and not is_generic_phrase(attraction):
                attractions.append(clean_attraction_name(attraction))
    
    return attractions

def is_generic_phrase(text: str) -> bool:
    """Controlla se una frase è troppo generica"""
    generic_words = [
        "questa città", "il centro", "la zona", "l'area", "il territorio",
        "la regione", "il paese", "la nazione", "il luogo", "la località",
        "molti", "alcuni", "diversi", "vari", "tutti", "ogni",
        "storia", "cultura", "tradizione", "popolazione", "abitanti"
    ]
    
    text_lower = text.lower()
    return any(generic in text_lower for generic in generic_words)

def clean_attraction_name(name: str) -> str:
    """Pulisce il nome di un'attrazione"""
    # Rimuovi articoli all'inizio
    articles = ["la ", "il ", "lo ", "l'", "le ", "gli ", "i ", "un ", "una ", "uno "]
    name_clean = name
    
    for article in articles:
        if name_clean.lower().startswith(article):
            name_clean = name_clean[len(article):]
            break
    
    # Capitalizza correttamente
    name_clean = name_clean.strip()
    if name_clean:
        name_clean = name_clean[0].upper() + name_clean[1:]
    
    return name_clean