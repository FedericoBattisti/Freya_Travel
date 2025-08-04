# Freya Travel Assistant 🌍

## Panoramica
Assistente di viaggio AI sviluppato con architettura **FastAPI** + **Laravel**, integrando **agenti LangChain**, **strumenti SerpAPI** e **OpenAI GPT-4** per pianificazione intelligente di viaggi e visualizzazione di destinazioni.

## Architettura

### Backend (Python/FastAPI)
- **FastAPI** REST API con middleware CORS
- **LangChain** agent executor con function calling
- **OpenAI GPT-4o-mini** per AI conversazionale
- Integrazione **SerpAPI** per recupero dati in tempo reale

### Frontend (Laravel/Livewire)
- **Laravel 11** con componenti **Livewire** real-time
- **Template Blade** con styling CSS personalizzato
- Comunicazione **AJAX** con API Python
- **Design responsive** con sistema modal per immagini

## Strumenti Principali

### 1. **flights_finder_tool**
```python
@tool
def flights_finder_tool(origin: str, destination: str, date: str) -> str:
```
- Ricerca Google Flights tramite SerpAPI
- Prezzi e disponibilità in tempo reale
- Confronto multiple compagnie aeree

### 2. **hotels_finder_tool**
```python
@tool  
def hotels_finder_tool(destination: str, checkin: str, checkout: str) -> str:
```
- Integrazione Google Hotels
- Filtri prezzo e disponibilità
- Dati rating e servizi

### 3. **images_finder_tool**
```python
@tool
def images_finder_tool(destination: str, image_type: str) -> str:
```
- Ricerca Google Images con SerpAPI
- Estrazione immagini ad alta risoluzione
- Parsing e pulizia nomi attrazioni
- Formattazione Markdown per immagini

### 4. **chain_historical_expert_tool**
```python
@tool
def chain_historical_expert_tool(location: str) -> str:
```
- Generazione contesto storico
- Recupero informazioni culturali
- Dettagli monumenti e landmark

### 5. **chain_travel_plan_tool**
```python
@tool
def chain_travel_plan_tool(requirements: str) -> str:
```
- Generazione itinerari
- Programmazione giorno per giorno
- Suggerimenti attività e ristoranti

## Configurazione Agent

```python
class Agent:
    def __init__(self):
        self.model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)
        self.tools = [flights_finder_tool, hotels_finder_tool, images_finder_tool, 
                     chain_historical_expert_tool, chain_travel_plan_tool]
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
```

## Endpoint API

- `POST /chat/travel-agent` - Interfaccia chat principale
- `GET /health` - Controllo stato servizi
- `GET /tools` - Lista strumenti disponibili
- `GET /services` - Capacità servizi

## Funzionalità Frontend

- **Chat real-time** con indicatori di digitazione
- **Rendering immagini** con lazy loading e zoom modal
- **Elaborazione Markdown** per risposte AI
- **Layout grid responsive** per immagini multiple
- **Pulsanti suggerimenti rapidi** per query comuni

## Variabili d'Ambiente

```env
OPENAI_API_KEY=sk-your-key
SERPAPI_API_KEY=your-serpapi-key
DATABASE_URL=postgresql://user:pass@host/db
```

## Deploy

```bash
# Backend
cd travel-agent-api
uvicorn src.travel_agent_api.main:app --host 127.0.0.1 --port 8080

# Frontend  
cd web_TravelAgent
php artisan serve
```

## Tecnologie Chiave
- **LangChain** 0.1.x con function calling
- **SerpAPI** per integrazione servizi Google
- **FastAPI** con supporto async/await
- **Livewire** per componenti frontend reattivi
- **CSS Grid/Flexbox** per layout responsive

## Ottimizzazioni Performance
- **Lazy loading** per immagini
- **Cache delle risposte** per query ripetute
- **Elaborazione asincrona** per chiamate API
- **Intersection Observer**