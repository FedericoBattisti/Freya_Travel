from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel , Field
from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

class TravelPlanInput(BaseModel):
      start_date: str = Field(description="The start date of the trip (YYYY-MM-DD) e.g. 2024-12-13.")
      end_date: str = Field(description="The end date of the trip (YYYY-MM-DD) e.g. 2024-12-19.")
      destination: str = Field(description="The destination of the trip.")
      adults: Optional[int] = Field(1, description="The number of adults. Defaults to 1.")
      children: Optional[int] = Field(0, description="The number of children. Defaults to 0.")
      travel_style: str = Field(description="The style of travel. e.g. adventure, relax,culture, backpacking, luxury, family-friendly")
      budget: Optional[int] = Field(description="The total budget for the trip.")
      activities: str = Field(description="The preferred activities. e.g. culture, nature,food, shopping.")
      food_restriction: str = Field(description="Any food restrictions. e.g. vegetarian,gluten-free.")

class TravelPlanInputSchema(BaseModel):
      params : TravelPlanInput

class TravelDayOutput(BaseModel):
      morning: str = Field(description="The activities for the morning.")
      afternoon: str = Field(description="The activities for the afternoon.")
      evening: str = Field(description="The activities for the evening.")

class TravelPlanOutput(BaseModel):
      travel_plan: list[TravelDayOutput]

@tool(args_schema=TravelPlanInputSchema)
def chain_travel_plan(params: TravelPlanInput) -> str:
      """
      🗓️ Genera un piano di viaggio completo e personalizzato.
      
      Questo tool crea itinerari dettagliati giorno per giorno basati sulle preferenze dell'utente.
      
      Parametri:
      params (TravelPlanInput): I parametri del viaggio inclusi date, destinazione, 
      numero di viaggiatori, stile di viaggio, budget, attività preferite e restrizioni alimentari.
      
      Returns:
      str: Un piano di viaggio dettagliato e personalizzato.
      """
      try:
            if not os.getenv("OPENAI_API_KEY"):
                  return "❌ OPENAI_API_KEY non configurata. Aggiungi la chiave API nel file .env"
            
            model = ChatOpenAI(
                  model_name="gpt-4o-mini",
                  temperature=0.7,
                  openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            
            system_prompt = f"""
            🗺️ Sei un esperto travel planner specializzato nella creazione di itinerari personalizzati.
            
            Crea un piano di viaggio dettagliato con queste specifiche:
            📅 Date: dal {params.start_date} al {params.end_date}
            🏛️ Destinazione: {params.destination}
            👥 Viaggiatori: {params.adults} adulti, {params.children} bambini
            🎯 Stile di viaggio: {params.travel_style}
            💰 Budget: {params.budget if params.budget else 'Non specificato'}
            🎨 Attività preferite: {params.activities}
            🥗 Restrizioni alimentari: {params.food_restriction if params.food_restriction else 'Nessuna'}
            
            Crea un itinerario giornaliero dettagliato che includa:
            - 🌅 Attività mattutine
            - ☀️ Attività pomeridiane  
            - 🌙 Attività serali
            - 🍽️ Suggerimenti per ristoranti (considerando le restrizioni alimentari)
            - 🚌 Mezzi di trasporto consigliati
            - 💡 Consigli pratici e tips locali
            - 💵 Stime dei costi quando possibile
            
            Usa emoji per rendere l'itinerario più coinvolgente e struttura tutto in modo chiaro e leggibile.
            Rispondi sempre in italiano.
            """
            
            prompt = ChatPromptTemplate([("human", "{input}")])
            chain = prompt | model
            
            print(f"🔍 Creando piano di viaggio per: {params.destination}")
            result = chain.invoke({"input": system_prompt})
            
            return result.content if hasattr(result, 'content') else str(result)
            
      except Exception as e:
            print(f"❌ Errore nella creazione del piano di viaggio: {e}")
            return f"🚨 Errore durante la creazione del piano di viaggio: {str(e)}"

# Crea un alias per mantenere compatibilità
chain_travel_plan_tool = chain_travel_plan
