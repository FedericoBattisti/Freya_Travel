from fastapi import FastAPI
from .routes.chat_route import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Travel Agent API",
    description="API per l'assistente di viaggio con AI",
    version="2.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Travel Agent API is running!", "status": "active"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "services": {
            "agent_service": "active",
            "tools": ["flights_finder", "hotels_finder", "images_finder", "chain_historical_expert", "chain_travel_plan"]
        }
    }

@app.get("/services")
def list_services():
    return {
        "services": [
            {
                "name": "agent_service",
                "description": "Servizio principale dell'agente di viaggio AI",
                "status": "active",
                "endpoints": ["/chat/travel-agent"],
                "capabilities": [
                    "Pianificazione viaggi personalizzata",
                    "Suggerimenti per destinazioni", 
                    "Consigli su alloggi e ristoranti",
                    "Creazione di itinerari dettagliati",
                    "Ricerca immagini di destinazioni"
                ]
            }
        ],
        "total_services": 1
    }

@app.get("/tools")
def list_tools():
    return {
        "available_tools": [
            {
                "name": "flights_finder",
                "description": "Trova voli usando SerpAPI Google Flights",
                "endpoint": "/chat/travel-agent",
                "status": "available",
                "requirements": ["SERPAPI_API_KEY"]
            },
            {
                "name": "hotels_finder", 
                "description": "Trova hotel using SerpAPI Google Hotels",
                "endpoint": "/chat/travel-agent",
                "status": "available", 
                "requirements": ["SERPAPI_API_KEY"]
            },
            {
                "name": "images_finder",
                "description": "Cerca immagini di destinazioni usando SerpAPI Google Images",
                "endpoint": "/chat/travel-agent",
                "status": "available",
                "requirements": ["SERPAPI_API_KEY"],
                "features": [
                    "Immagini di attrazioni turistiche",
                    "Foto di hotel e ristoranti", 
                    "Panorami e paesaggi",
                    "Street view e mappe visive"
                ]
            },
            {
                "name": "chain_historical_expert",
                "description": "Esperto storico per informazioni sui luoghi",
                "endpoint": "/chat/travel-agent",
                "status": "available",
                "requirements": ["OPENAI_API_KEY"]
            },
            {
                "name": "chain_travel_plan",
                "description": "Genera piani di viaggio dettagliati",
                "endpoint": "/chat/travel-agent", 
                "status": "available",
                "requirements": ["OPENAI_API_KEY"]
            }
        ],
        "total_tools": 5
    }

origins = ["http://127.0.0.1:8000", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    chat_router,  
    tags=["Chat"],
    prefix="/chat",
)
