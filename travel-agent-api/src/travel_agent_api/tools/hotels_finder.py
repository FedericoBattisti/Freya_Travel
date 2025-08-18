import os
from langchain_core.tools import tool
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from enum import IntEnum

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


class HotelClassEnum(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class HotelsInput(BaseModel):
    q: str = Field(description="Location of the hotel.")
    check_in_date: str = Field(
        description="The outbound date (YYYY-MM-DD) e.g. 2024-12-13."
    )
    check_out_date: str = Field(
        description="The return date (YYYY-MM-DD) e.g. 2024-12-19."
    )
    adults: Optional[int] = Field(1, description="The number of adults. Defaults to 1.")
    children: Optional[int] = Field(
        0, description="The number of children. Defaults to 0."
    )
    hotel_class: Optional[int] = Field(
        2, description="The hotel class avaible from 2 to 5 . Defaults to 2."
    )


class HotelsInputSchema(BaseModel):
    params: HotelsInput


@tool(args_schema=HotelsInputSchema)
def hotels_finder(params: HotelsInput):
    """
    🏨 Cerca hotel usando SerpAPI Google Hotels.

    Questo tool utilizza l'API SerpAPI Google Hotels per cercare hotel disponibili.

    Parametri:
    q (str): Località dove cercare l'hotel.
    check_in_date (str): Data di check-in (YYYY-MM-DD) es. 2024-12-13.
    check_out_date (str): Data di check-out (YYYY-MM-DD) es. 2024-12-19.
    adults (int): Numero di adulti. Default 1.
    children (int): Numero di bambini. Default 0.
    hotel_class (int): Classe hotel da 2 a 5 stelle. Default 2.

    Returns:
    dict: Un dizionario con le informazioni sugli hotel trovati.
    """
    if GoogleSearch is None:
        return {
            "error": "SERPAPI_API_KEY non configurata",
            "message": "Per cercare hotel reali è necessario configurare SERPAPI_API_KEY nel file .env",
            "suggestion": "Aggiungi SERPAPI_API_KEY=tua_chiave_api nel file .env",
        }

    try:
        # Verifica che la chiave API sia configurata
        if not os.getenv("SERPAPI_API_KEY"):
            return {
                "error": "SERPAPI_API_KEY non configurata",
                "message": "Per cercare hotel reali è necessario configurare SERPAPI_API_KEY nel file .env",
                "suggestion": "Aggiungi SERPAPI_API_KEY=tua_chiave_api nel file .env",
            }

        search_params = {
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "engine": "google_hotels",
            "hl": "it",
            "gl": "it",
            "currency": "EUR",
            "q": params.q,
            "check_in_date": params.check_in_date,
            "check_out_date": params.check_out_date,
            "adults": params.adults,
            "children": params.children,
            "hotel_class": params.hotel_class,
            "num": 5,
        }

        print(f"🔍 Cercando hotel a: {params.q}")
        search = GoogleSearch(search_params)
        result = search.get_dict()

        # Controlla se ci sono errori
        if "error" in result:
            return {
                "error": result["error"],
                "message": "Errore nella ricerca hotel tramite SerpAPI",
            }

        hotels = result.get("properties", [])

        return {
            "success": True,
            "search_info": {
                "location": params.q,
                "check_in": params.check_in_date,
                "check_out": params.check_out_date,
                "guests": f"{params.adults} adulti, {params.children} bambini",
                "hotel_class": f"{params.hotel_class} stelle",
            },
            "hotels_found": len(hotels),
            "hotels_data": hotels,
        }

    except Exception as e:
        print(f"❌ Errore nella ricerca hotel: {e}")
        return {"error": str(e), "message": "Errore durante la ricerca degli hotel"}


# Crea un alias per mantenere compatibilità
hotels_finder_tool = hotels_finder
