from langchain_core.tools import tool
import os
from typing import Dict, Optional

# Import corretto per SerpAPI
try:
    from serpapi import GoogleSearch
except ImportError:
    try:
        from googlesearch import GoogleSearch
    except ImportError:
        try:
            # Alternativa con google-search-results
            from serpapi.google_search import GoogleSearch
        except ImportError:
            print("❌ SerpAPI non disponibile. Installare con: poetry add google-search-results")
            GoogleSearch = None

@tool
def images_finder_tool(destination: str, image_type: str = "tourist attractions") -> str:
    """
    Cerca immagini di destinazioni turistiche usando SerpAPI Google Images.
    """
    if GoogleSearch is None:
        return "❌ SerpAPI non configurato. Contatta l'amministratore del sistema."
    
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
            "num": 8,
            "safe": "active",
            "tbs": "ic:color,itp:photo,isz:l"
        }
        
        # Crea e esegui la ricerca
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
            
            response += f"### {i}. {attraction_name}\n"
            
            # Link diretto all'immagine
            image_url = img.get("original") or img.get("link") or ""
            if image_url:
                response += f"![{attraction_name}]({image_url})\n"
                response += f"🔗 **[Visualizza a schermo intero]({image_url})**\n"
            
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
    """Estrae il nome dell'attrazione dal titolo dell'immagine"""
    if not title:
        return f"Attrazione a {destination}"
    
    # Pulisci il titolo rimuovendo parti non necessarie
    title_clean = title.strip()
    
    # Rimuovi parti comuni
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
    
    # Limita la lunghezza
    if len(title_clean) > 60:
        title_clean = title_clean[:57] + "..."
    
    # Se il titolo è troppo corto, usa il nome della destinazione
    if len(title_clean) < 3:
        return f"Vista di {destination}"
    
    return title_clean