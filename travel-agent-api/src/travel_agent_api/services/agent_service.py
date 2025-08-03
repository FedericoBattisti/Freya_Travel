from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from dotenv import load_dotenv

# Importa i tool con path assoluto
try:
    from travel_agent_api.tools.flights_finder import flights_finder_tool
    from travel_agent_api.tools.hotels_finder import hotels_finder_tool  
    from travel_agent_api.tools.chain_historical_expert import chain_historical_expert_tool
    from travel_agent_api.tools.chain_travel_plan import chain_travel_plan_tool
    print("✅ Tool importati con successo")
except ImportError as e:
    print(f"⚠️ Errore nell'importazione dei tool: {e}")
    flights_finder_tool = None
    hotels_finder_tool = None
    chain_historical_expert_tool = None
    chain_travel_plan_tool = None

load_dotenv()

class Agent:
    def __init__(self):
        self.current_datetime = datetime.now()
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini", 
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Crea la lista dei tool disponibili (solo se importati correttamente)
        self.tools = []
        available_tools = [
            ("flights_finder", flights_finder_tool),
            ("hotels_finder", hotels_finder_tool),
            ("historical_expert", chain_historical_expert_tool),
            ("travel_plan", chain_travel_plan_tool)
        ]
        
        for name, tool in available_tools:
            if tool is not None:
                self.tools.append(tool)
                print(f"✅ Tool '{name}' aggiunto")
            else:
                print(f"❌ Tool '{name}' non disponibile")
        
        # Se abbiamo dei tool, crea un agente con tool, altrimenti usa chat semplice
        if self.tools:
            self._setup_agent_with_tools()
        else:
            print("🔧 Usando modalità chat semplice (nessun tool disponibile)")
            self.agent_executor = None
        
    def _setup_agent_with_tools(self):
        """Configura l'agente con i tool disponibili"""
        try:
            # Crea il prompt per l'agente con tool
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""
🌟 Sei TravelAgent, un esperto agente di viaggio AI professionale e amichevole!

Data di oggi: {self.current_datetime.strftime('%d/%m/%Y')}

Hai accesso a questi strumenti potenti e DEVI utilizzarli quando appropriato:
- flights_finder: per cercare voli reali usando SerpAPI
- hotels_finder: per trovare hotel disponibili usando SerpAPI
- chain_historical_expert: per informazioni storiche sui luoghi
- chain_travel_plan: per creare piani di viaggio dettagliati

REGOLE OBBLIGATORIE:
1. LEGGI ATTENTAMENTE la richiesta dell'utente
2. SE l'utente menziona VOLI/AEREO/VIAGGIO AEREO → USA SEMPRE flights_finder
3. SE l'utente menziona HOTEL/ALLOGGIO/DORMIRE → USA SEMPRE hotels_finder  
4. SE l'utente chiede STORIA/CULTURA/MONUMENTI → USA SEMPRE chain_historical_expert
5. SE l'utente chiede ITINERARIO/PIANO/PROGRAMMA → USA SEMPRE chain_travel_plan

ANALIZZA il contenuto del messaggio dell'utente e identifica le parole chiave che indicano quale tool usare.

NON dare mai risposte generiche come "Come posso aiutarti?" - USA SEMPRE i tool appropriati!

Esempi di analisi:
- "Voglio un volo da Milano a Roma" → CONTIENE "volo" → USA flights_finder
- "Dimmi qualcosa su Roma" → CONTIENE richiesta di informazioni → USA chain_historical_expert
- "Hotel a Roma" → CONTIENE "hotel" → USA hotels_finder
- "Pianifica 3 giorni a Roma" → CONTIENE "pianifica" → USA chain_travel_plan

Mantieni sempre il context della conversazione precedente per fornire risposte coerenti.

Rispondi sempre in italiano con emoji e usa i tool per dare risposte specifiche!
                """),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # Crea l'agente
            agent = create_openai_functions_agent(
                llm=self.model,
                tools=self.tools,
                prompt=prompt
            )
            
            # Crea l'executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                return_intermediate_steps=True,
                handle_parsing_errors=True,
                max_iterations=5
            )
            
            print(f"🚀 Agente configurato con {len(self.tools)} tool")
            
        except Exception as e:
            print(f"❌ Errore nella configurazione dell'agente: {e}")
            self.agent_executor = None
        
    def run(self, messages: list):
        try:
            # Estrai l'ultimo messaggio dell'utente e costruisci la chat history
            user_message = ""
            chat_history = []
            
            if isinstance(messages, list) and messages:
                # Processa tutti i messaggi per costruire la chat history
                for i, msg in enumerate(messages):
                    if isinstance(msg, dict) and "content" in msg:
                        if msg.get("role") == "user":
                            if i == len(messages) - 1:  # Ultimo messaggio
                                user_message = msg["content"]
                            else:
                                chat_history.append(HumanMessage(content=msg["content"]))
                        elif msg.get("role") == "assistant":
                            chat_history.append(SystemMessage(content=msg["content"]))
                
                # Se non abbiamo trovato un messaggio utente, usa l'ultimo
                if not user_message and messages:
                    last_msg = messages[-1]
                    if isinstance(last_msg, dict) and "content" in last_msg:
                        user_message = last_msg["content"]
                    elif isinstance(last_msg, str):
                        user_message = last_msg
            elif isinstance(messages, str):
                user_message = messages
            
            print(f"💬 Messaggio ricevuto: {user_message}")
            print(f"📝 Chat history: {len(chat_history)} messaggi precedenti")
            
            # Se abbiamo l'agente con tool, usalo
            if self.agent_executor:
                print("🔧 Usando agente con tool...")
                
                result = self.agent_executor.invoke({
                    "input": user_message,
                    "chat_history": chat_history
                })
                
                response_content = result.get("output", "Nessuna risposta generata")
                print(f"🤖 Risposta agente: {response_content}")
                
                return {
                    "output": response_content,
                    "status": "success",
                    "tools_used": len(self.tools),
                    "context_messages": len(chat_history)
                }
                
            else:
                # Fallback a chat semplice
                print("💭 Usando chat semplice...")
                return self._simple_chat_response(user_message, chat_history)
                
        except Exception as e:
            print(f"🚨 Errore nell'agent: {e}")
            import traceback
            traceback.print_exc()
            return {
                "output": f"🚨 Mi dispiace, ho riscontrato un problema: {str(e)}. Potresti riprovare?",
                "status": "error",
                "error_details": str(e)
            }
    
    def _simple_chat_response(self, user_message: str, chat_history: list = None):
        """Risposta chat semplice senza tool"""
        if chat_history is None:
            chat_history = []
            
        SYSTEM_PROMPT = f"""
        🌟 Sei TravelAgent, un travel planner professionale e amichevole! 
        
        Il tuo compito è organizzare viaggi per gli utenti con entusiasmo e competenza.
        La data di oggi è {self.current_datetime.strftime('%d/%m/%Y')}
        
        Rispondi sempre in italiano con emoji appropriate per rendere la conversazione più coinvolgente.
        
        Quando ti chiedono di un viaggio:
        1. 🎯 Raccogli informazioni: destinazione, date, budget, preferenze
        2. ✈️ Suggerisci voli (consigli generali)
        3. 🏨 Consiglia hotel e alloggi
        4. 🗓️ Proponi un itinerario giornaliero
        5. 🍝 Suggerisci ristoranti e piatti locali
        6. 🎨 Includi attrazioni e attività culturali
        7. Inserisci sempre i loghi delle compagnie aeree e degli hotel quando possibile
        
        Sii sempre positivo, utile e professionale!
        """

        # Costruisci i messaggi includendo la chat history
        langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        langchain_messages.extend(chat_history)
        langchain_messages.append(HumanMessage(content=user_message))
        
        response = self.model.invoke(langchain_messages)
        
        return {
            "output": response.content,
            "status": "success",
            "mode": "simple_chat",
            "context_messages": len(chat_history)
        }
