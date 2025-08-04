from datetime import datetime
from typing import Dict
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
    from travel_agent_api.tools.images_finder import images_finder_tool  # NUOVO!
    print("✅ Tool importati con successo")
except ImportError as e:
    print(f"⚠️ Errore nell'importazione dei tool: {e}")
    flights_finder_tool = None
    hotels_finder_tool = None
    chain_historical_expert_tool = None
    chain_travel_plan_tool = None
    images_finder_tool = None  # NUOVO!

load_dotenv()

class Agent:
    def __init__(self):
        self.current_datetime = datetime.now()
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini", 
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Crea la lista dei tool disponibili (incluse le immagini!)
        self.tools = []
        available_tools = [
            ("flights_finder", flights_finder_tool),
            ("hotels_finder", hotels_finder_tool),
            ("historical_expert", chain_historical_expert_tool),
            ("travel_plan", chain_travel_plan_tool),
            ("images_finder", images_finder_tool)  # AGGIUNTO!
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
            # Crea il prompt per l'agente con tool (AGGIORNATO!)
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""
🌟 Sei TravelAgent, un esperto agente di viaggio AI professionale e amichevole!

Data di oggi: {self.current_datetime.strftime('%d/%m/%Y')}

Hai accesso a questi strumenti potenti e DEVI utilizzarli quando appropriato:
- flights_finder: per cercare voli reali usando SerpAPI
- hotels_finder: per trovare hotel disponibili usando SerpAPI
- chain_historical_expert: per informazioni storiche sui luoghi
- chain_travel_plan: per creare piani di viaggio dettagliati
- images_finder: per cercare e mostrare immagini di destinazioni, hotel, attrazioni

REGOLE OBBLIGATORIE:
1. LEGGI ATTENTAMENTE la richiesta dell'utente
2. SE l'utente menziona VOLI/AEREO/VIAGGIO AEREO → USA SEMPRE flights_finder
3. SE l'utente menziona HOTEL/ALLOGGIO/DORMIRE → USA SEMPRE hotels_finder  
4. SE l'utente chiede STORIA/CULTURA/MONUMENTI → USA SEMPRE chain_historical_expert
5. SE l'utente chiede ITINERARIO/PIANO/PROGRAMMA → USA SEMPRE chain_travel_plan
6. SE l'utente chiede IMMAGINI/FOTO/MOSTRA/VEDERE → USA SEMPRE images_finder

QUANDO DESCRIVI UNA DESTINAZIONE, USA SEMPRE images_finder per mostrare foto!

ANALIZZA il contenuto del messaggio dell'utente e identifica le parole chiave che indicano quale tool usare.

Esempi di analisi:
- "Voglio un volo da Milano a Roma" → CONTIENE "volo" → USA flights_finder
- "Dimmi qualcosa su Roma" → CONTIENE richiesta di informazioni → USA chain_historical_expert + images_finder
- "Hotel a Roma" → CONTIENE "hotel" → USA hotels_finder + images_finder
- "Pianifica 3 giorni a Roma" → CONTIENE "pianifica" → USA chain_travel_plan + images_finder
- "Mostra Roma" → CONTIENE "mostra" → USA images_finder
- "Come è Venezia?" → Descrizione richiesta → USA images_finder + chain_historical_expert
- "Itinerario turistico di Amsterdam" → CONTIENE "itinerario" → USA chain_travel_plan + images_finder, le immagini devono essere pertinenti all'attrazione richiesta e devono essere messe nel contesto giusto.

IMPORTANTE: Quando parli di una destinazione, INCLUDI SEMPRE le immagini per rendere la risposta più ricca!

Rispondi sempre in italiano con emoji e usa i tool per dare risposte specifiche e complete!
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
            
            print(f"🚀 Agente configurato con {len(self.tools)} tool (incluse immagini!)")
            
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
        8. Quando mostri immagini, usa sempre il tool images_finder per cercare foto pertinenti alla destinazione o all'attrazione richiesta inserendo sotto il link per l'immagine in modale in alta risoluzione oppure rendi l'immagine stessa il link cliccabile.
        
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
    
    def _should_search_images(self, message: str) -> bool:
        """Rileva se l'utente vuole vedere immagini"""
        image_keywords = [
            'mostra', 'immagini', 'foto', 'vedere', 'come', 'aspetto',
            'panorama', 'vista', 'paesaggio', 'hotel', 'ristorante',
            'show me', 'pictures', 'photos', 'looks like', 'visual'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in image_keywords)
    
    def _handle_image_search(self, user_message: str) -> str:
        """Gestisce le richieste di ricerca immagini"""
        try:
            # Estrai destinazione e tipo dal messaggio
            destination = self._extract_destination(user_message)
            image_type = self._extract_image_type(user_message)
            
            if not destination:
                return "🖼️ Per cercare immagini, specifica una destinazione. Es: 'Mostra immagini di Roma'"
            
            # Cerca immagini
            result = self.images_finder.search_destination_images(
                destination=destination,
                image_type=image_type,
                num_results=6
            )
            
            if result["success"]:
                return self._format_image_results(result)
            else:
                return f"❌ Non sono riuscito a trovare immagini per {destination}. {result.get('error', '')}"
                
        except Exception as e:
            return f"❌ Errore nella ricerca immagini: {str(e)}"
    
    def _extract_image_type(self, message: str) -> str:
        """Estrae il tipo di immagini richieste"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hotel', 'albergo', 'resort']):
            return "hotels luxury accommodations"
        elif any(word in message_lower for word in ['ristorante', 'cibo', 'cucina', 'food']):
            return "restaurants local cuisine food"
        elif any(word in message_lower for word in ['spiaggia', 'mare', 'beach']):
            return "beaches coast seaside"
        elif any(word in message_lower for word in ['panorama', 'vista', 'skyline']):
            return "skyline panorama cityscape"
        else:
            return "tourist attractions landmarks monuments"
    
    def _format_image_results(self, result: Dict) -> str:
        """Formatta i risultati delle immagini per la risposta"""
        destination = result["destination"]
        images = result["images"]
        total = result["total_results"]
        
        response = f"🖼️ **Immagini di {destination}**\n\n"
        response += f"Ho trovato {total} immagini per te:\n\n"
        
        for i, img in enumerate(images[:6], 1):
            title = img["title"][:50] + "..." if len(img["title"]) > 50 else img["title"]
            response += f"**{i}. {title}**\n"
            response += f"🔗 [Visualizza immagine]({img['original']})\n"
            response += f"📐 Dimensioni: {img['width']}x{img['height']}px\n"
            if img["source"]:
                response += f"📍 Fonte: {img['source']}\n"
            response += "\n"
        
        response += "💡 **Suggerimento:** Clicca sui link per vedere le immagini ad alta risoluzione!"
        
        return response
