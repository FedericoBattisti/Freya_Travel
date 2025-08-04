from langchain_core.tools import tool
from serpapi import GoogleSearch
import os
from typing import Dict, Optional

@tool
def images_finder_tool(destination: str, image_type: str = "tourist attractions") -> str:
    """
    Cerca immagini di destinazioni turistiche usando SerpAPI Google Images.
    
    Args:
        destination: Nome della destinazione (es. "Roma", "Torre Eiffel")
        image_type: Tipo di immagini (tourist attractions, hotels, restaurants, beaches, etc.)
    
    Returns:
        Stringa formattata con le immagini trovate
    """
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "❌ SERPAPI_API_KEY non configurata per la ricerca immagini"
        
        print(f"🔍 Cercando immagini per: {destination} - Tipo: {image_type}")
        
        # Costruisci query di ricerca ottimizzata
        search_query = f"{destination} {image_type}"
        
        # Parametri per Google Images via SerpAPI
        params = {
            "engine": "google_images",
            "q": search_query,
            "api_key": api_key,
            "num": 8,  # Più immagini per avere scelta migliore
            "safe": "active",
            "tbs": "ic:color,itp:photo,isz:l"  # Solo foto a colori, grandi dimensioni
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            return f"❌ Errore nella ricerca immagini: {results['error']}"
        
        # Processa i risultati delle immagini
        image_results = results.get("images_results", [])
        
        if not image_results:
            return f"❌ Nessuna immagine trovata per {destination}"
        
        # Formatta la risposta con le immagini
        response = f"🖼️ **Immagini di {destination}**\n\n"
        response += f"Ho trovato {len(image_results[:6])} bellissime immagini per te:\n\n"
        
        for i, img in enumerate(image_results[:6], 1):
            # Estrai il nome dell'attrazione dal titolo
            attraction_name = extract_attraction_name(img.get("title", ""), destination)
            
            response += f"## {i}. {attraction_name}\n"
            
            # Link diretto all'immagine - SEMPRE PRESENTE
            image_url = img.get("original") or img.get("link") or ""
            if image_url:
                response += f"![{attraction_name}]({image_url})\n"
                response += f"🔗 **[Visualizza immagine a schermo intero]({image_url})**\n"
            
            # Informazioni aggiuntive
            if img.get("original_width") and img.get("original_height"):
                response += f"📐 **Dimensioni:** {img['original_width']} × {img['original_height']} px\n"
            
            if img.get("source"):
                response += f"📍 **Fonte:** {img['source']}\n"
            
            response += "\n---\n\n"
        
        response += f"💡 **Suggerimento:** Clicca sui link per vedere le immagini in alta risoluzione!\n"
        response += f"🔍 **Ricerca effettuata:** {search_query}\n"
        response += f"🌟 **Destinazione:** {destination}"
        
        return response
        
    except Exception as e:
        return f"❌ Errore nella ricerca immagini: {str(e)}"

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