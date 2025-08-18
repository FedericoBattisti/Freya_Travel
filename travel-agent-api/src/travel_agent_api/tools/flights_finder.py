import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional

try:
    from serpapi import GoogleSearch
except ImportError:
    try:
        from googlesearch import GoogleSearch
    except ImportError:
        try:
            from serpapi.google_search import GoogleSearch
        except ImportError:
            print("❌ SerpAPI non disponibile")
            GoogleSearch = None

load_dotenv()


class FlightsInput(BaseModel):
    departure_airport: str = Field(description="The departure airport code (IATA).")
    arrival_airport: str = Field(description="The arrival airport code (IATA).")
    outbound_date: str = Field(
        description="The outbound date (YYYY-MM-DD) e.g. 2024-12-13."
    )
    return_date: str = Field(
        description="The return date (YYYY-MM-DD) e.g. 2024-12-19."
    )
    adults: Optional[int] = Field(1, description="The number of adults. Defaults to 1.")
    children: Optional[int] = Field(
        0, description="The number of children. Defaults to 0."
    )


class FlightsInputSchema(BaseModel):
    params: FlightsInput


@tool(args_schema=FlightsInputSchema)
def flights_finder(params: FlightsInput):
    """
    🛫 Cerca voli usando SerpAPI Google Flights.
    
    Questo tool utilizza l'API SerpAPI Google Flights per cercare voli disponibili.
    
    Parametri:
        departure_airport (str): Il codice aeroporto di partenza (IATA).
        arrival_airport (str): Il codice aeroporto di arrivo (IATA).
        outbound_date (str): La data di partenza (YYYY-MM-DD) es. 2024-12-13.
        return_date (str): La data di ritorno (YYYY-MM-DD) es. 2024-12-19.
        adults (int): Il numero di adulti. Default 1.
        children (int): Il numero di bambini. Default 0.
        
    Returns:
        dict: Un dizionario con le informazioni sui voli trovati.
    """
    if GoogleSearch is None:
        return {
            "error": "SERPAPI_API_KEY non configurata",
            "message": "Per cercare voli reali è necessario configurare SERPAPI_API_KEY nel file .env",
            "suggestion": "Aggiungi SERPAPI_API_KEY=tua_chiave_api nel file .env"
        }
    
    try:
        # Verifica che la chiave API sia configurata
        if not os.getenv("SERPAPI_API_KEY"):
            return {
                "error": "SERPAPI_API_KEY non configurata",
                "message": "Per cercare voli reali è necessario configurare SERPAPI_API_KEY nel file .env",
                "suggestion": "Aggiungi SERPAPI_API_KEY=tua_chiave_api nel file .env"
            }
        
        search_params = {
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "engine": "google_flights",
            "hl": "it",
            "gl": "it",
            "currency": "EUR",
            "stops": "1",
            "departure_id": params.departure_airport,
            "arrival_id": params.arrival_airport,
            "outbound_date": params.outbound_date,
            "return_date": params.return_date,
            "adults": params.adults,
            "children": params.children,
        }
        
        print(f"🔍 Cercando voli: {params.departure_airport} → {params.arrival_airport}")
        search = GoogleSearch(search_params)
        result = search.get_dict()
        
        # Controlla se ci sono errori nell'API
        if "error" in result:
            return {
                "error": result["error"],
                "message": "Errore nella ricerca voli tramite SerpAPI"
            }
        
        # Formatta la risposta
        return {
            "success": True,
            "search_info": {
                "from": params.departure_airport,
                "to": params.arrival_airport,
                "departure": params.outbound_date,
                "return": params.return_date,
                "passengers": f"{params.adults} adulti, {params.children} bambini"
            },
            "flights_data": result
        }
        
    except Exception as e:
        print(f"❌ Errore nella ricerca voli: {e}")
        return {
            "error": str(e),
            "message": "Errore durante la ricerca dei voli"
        }

# Crea un alias per mantenere compatibilità
flights_finder_tool = flights_finder
