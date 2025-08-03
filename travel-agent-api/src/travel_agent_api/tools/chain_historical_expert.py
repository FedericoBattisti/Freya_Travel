from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()


@tool
def chain_historical_expert(input_text: str) -> str:
      """
      📚 Esperto storico AI per informazioni approfondite sui luoghi.
      
      Questo tool utilizza un modello AI specializzato per fornire informazioni storiche
      dettagliate su destinazioni di viaggio, monumenti, culture e tradizioni locali.
      
      Args:
      input_text (str): Il luogo o argomento storico per cui si vogliono informazioni.
      
      Returns:
      str: Informazioni storiche dettagliate e coinvolgenti.
      """
      try:
            if not os.getenv("OPENAI_API_KEY"):
                  return "❌ OPENAI_API_KEY non configurata. Aggiungi la chiave API nel file .env"
            
            model = ChatOpenAI(
                  model_name="gpt-4o-mini",
                  temperature=0.7,
                  openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            
            system_prompt = """
            🏛️ Sei un esperto storico specializzato in storia del turismo e delle destinazioni di viaggio.
            
            La tua missione è fornire informazioni storiche affascinanti e dettagliate su:
            - Luoghi e destinazioni turistiche
            - Monumenti e siti storici  
            - Culture e tradizioni locali
            - Eventi storici significativi
            - Curiosità e aneddoti interessanti
            
            Rispondi sempre in italiano con emoji appropriate per rendere le informazioni più coinvolgenti.
            Fornisci dettagli accurati, storie affascinanti e consigli pratici per i viaggiatori.
            Sii professionale ma accessibile, rendendo la storia viva e interessante.
            """
            
            prompt = ChatPromptTemplate([
                  ("system", system_prompt), 
                  ("user", "Fornisci informazioni storiche dettagliate su: {input}")
            ])
            
            chain = prompt | model
            print(f"🔍 Cercando informazioni storiche su: {input_text}")
            
            result = chain.invoke({"input": input_text})
            
            # Restituisce solo il contenuto del messaggio
            return result.content if hasattr(result, 'content') else str(result)
            
      except Exception as e:
            print(f"❌ Errore nell'esperto storico: {e}")
            return f"🚨 Errore durante la ricerca di informazioni storiche: {str(e)}"

# Crea un alias per mantenere compatibilità
chain_historical_expert_tool = chain_historical_expert
