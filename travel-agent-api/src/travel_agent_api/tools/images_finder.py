from langchain_core.tools import tool
from serpapi import GoogleSearch
import os
from typing import Dict, Optional

@tool
def images_finder_tool(destination: str, image_type: str = "tourist attractions") -> str:
    """
    Cerca immagini specifiche di destinazioni turistiche usando SerpAPI Google Images.
    
    Args:
        destination: Nome SPECIFICO della destinazione (es. "Colosseo Roma", "Sagrada Familia Barcellona")
        image_type: Tipo di immagini (tourist attractions, hotels, restaurants, monuments, etc.)
    
    Returns:
        Stringa formattata con le immagini trovate
    """
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "❌ SERPAPI_API_KEY non configurata per la ricerca immagini"
        
        print(f"🎯 Cercando immagini SPECIFICHE per: {destination} - Tipo: {image_type}")
        
        # Query più specifica e mirata
        if "monuments" in image_type or "attractions" in image_type:
            search_query = f'"{destination}" {image_type} landmark monument'
        elif "hotels" in image_type:
            search_query = f'"{destination}" luxury hotel exterior interior'
        elif "restaurants" in image_type or "food" in image_type:
            search_query = f'"{destination}" traditional food cuisine restaurant'
        else:
            search_query = f'"{destination}" {image_type}'
        
        # Parametri ottimizzati per risultati specifici
        params = {
            "engine": "google_images",
            "q": search_query,
            "api_key": api_key,
            "num": 8,
            "safe": "active",
            "tbs": "ic:color,itp:photo,isz:l",  # Foto grandi a colori
            "ijn": 0
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            return f"❌ Errore nella ricerca immagini: {results['error']}"
        
        image_results = results.get("images_results", [])
        
        if not image_results:
            return f"❌ Nessuna immagine trovata per {destination}"
        
        # Filtra risultati per pertinenza
        filtered_results = filter_relevant_images(image_results, destination)
        
        # Formatta la risposta con le immagini specifiche
        response = f"🖼️ **Immagini di {destination}**\n\n"
        
        for i, img in enumerate(filtered_results[:6], 1):
            attraction_name = extract_attraction_name(img.get("title", ""), destination)
            
            response += f"### {i}. {attraction_name}\n"
            
            image_url = img.get("original") or img.get("link") or ""
            if image_url:
                response += f"![{attraction_name}]({image_url})\n"
                response += f"🔗 **[Visualizza a schermo intero]({image_url})**\n"
            
            if img.get("original_width") and img.get("original_height"):
                response += f"📐 {img['original_width']} × {img['original_height']} px\n"
            
            if img.get("source"):
                response += f"📍 Fonte: {img['source']}\n"
            
            response += "\n"
        
        response += f"🔍 **Query usata:** {search_query}\n"
        response += f"🎯 **Risultati filtrati:** {len(filtered_results)} di {len(image_results)}\n"
        
        return response
        
    except Exception as e:
        return f"❌ Errore nella ricerca immagini: {str(e)}"

def filter_relevant_images(image_results: list, target_destination: str) -> list:
    """
    Filtra le immagini per rilevanza rispetto alla destinazione specifica
    """
    target_lower = target_destination.lower()
    relevant_images = []
    
    for img in image_results:
        title = img.get("title", "").lower()
        source = img.get("source", "").lower()
        
        # Punteggio di rilevanza
        relevance_score = 0
        
        # Controlla se il titolo contiene parole chiave della destinazione
        target_words = target_lower.split()
        for word in target_words:
            if len(word) > 2:  # Ignora preposizioni
                if word in title:
                    relevance_score += 2
                if word in source:
                    relevance_score += 1
        
        # Bonus per fonti affidabili
        reliable_sources = ["wikipedia", "tripadvisor", "booking", "expedia", "lonely planet"]
        if any(source_name in source for source_name in reliable_sources):
            relevance_score += 1
        
        # Aggiungi solo se ha un punteggio minimo
        if relevance_score >= 2:
            img["relevance_score"] = relevance_score
            relevant_images.append(img)
    
    # Ordina per rilevanza
    relevant_images.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    return relevant_images

def extract_attraction_name(title: str, destination: str) -> str:
    """
    Estrae il nome dell'attrazione dal titolo dell'immagine
    """
    if not title:
        return f"Attrazione a {destination}"
    
    # Pulisci il titolo rimuovendo parti non necessarie
    title_clean = title.strip()
    
    # Rimuovi parti comuni come "Foto di", "Image of", etc.
    remove_prefixes = [
        "Foto di ", "Image of ", "Picture of ", "View of ", "Vista di ",
        "Photo of ", "Immagine di ", "Veduta di ", "Panorama di "
    ]
    
    for prefix in remove_prefixes:
        if title_clean.startswith(prefix):
            title_clean = title_clean[len(prefix):]
    
    # Rimuovi suffissi comuni
    remove_suffixes = [
        " - Wikipedia", " | TripAdvisor", " - Booking.com", 
        " - Google Images", " - Pinterest", " foto", " image"
    ]
    
    for suffix in remove_suffixes:
        if title_clean.endswith(suffix):
            title_clean = title_clean[:-len(suffix)]
    
    # Limita la lunghezza e aggiungi ellipsis se necessario
    if len(title_clean) > 60:
        title_clean = title_clean[:57] + "..."
    
    # Se il titolo è troppo corto o generico, usa il nome della destinazione
    if len(title_clean) < 3 or title_clean.lower() in ['image', 'foto', 'picture', 'view']:
        return f"Vista di {destination}"
    
    return title_clean

@tool 
def images_finder_attractions_tool(destination: str) -> str:
    """
    Cerca specificamente immagini di attrazioni turistiche famose di una destinazione.
    Restituisce sempre nome attrazione + link immagine.
    """
    return images_finder_tool(destination, "famous tourist attractions monuments landmarks")

@tool
def images_finder_hotels_tool(destination: str) -> str:
    """
    Cerca immagini di hotel e alloggi di una destinazione.
    Restituisce sempre nome hotel + link immagine.
    """
    return images_finder_tool(destination, "luxury hotels resorts accommodations")

@tool  
def images_finder_food_tool(destination: str) -> str:
    """
    Cerca immagini di cucina e ristoranti locali di una destinazione.
    Restituisce sempre nome piatto/ristorante + link immagine.
    """
    return images_finder_tool(destination, "traditional local cuisine food restaurants")

@tool
def images_finder_panorama_tool(destination: str) -> str:
    """
    Cerca immagini panoramiche e vedute di una destinazione.
    Restituisce sempre nome del panorama + link immagine.
    """
    return images_finder_tool(destination, "panoramic view skyline cityscape aerial")

# Test function aggiornata
def test_images_finder():
    """Test delle funzionalità del tool"""
    try:
        print("🧪 Test ricerca immagini Roma...")
        result = images_finder_tool("Roma", "tourist attractions")
        print("✅ Risultato:")
        print(result[:300] + "..." if len(result) > 300 else result)
        
        print("\n🧪 Test estrazione nome attrazione...")
        test_titles = [
            "Colosseo - Wikipedia",
            "Foto di Fontana di Trevi | TripAdvisor", 
            "Image of Vatican City St Peter's Basilica",
            "Pantheon Roma vista notturna"
        ]
        
        for title in test_titles:
            extracted = extract_attraction_name(title, "Roma")
            print(f"'{title}' → '{extracted}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Test fallito: {e}")
        return False

if __name__ == "__main__":
    test_images_finder()