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
    from travel_agent_api.tools.chain_historical_expert import (
        chain_historical_expert_tool,
    )
    from travel_agent_api.tools.chain_travel_plan import chain_travel_plan_tool
    from travel_agent_api.tools.images_finder import images_finder_tool  # NUOVO!
    from travel_agent_api.tools.destination_guide import create_destination_guide_tool
    from travel_agent_api.tools.itinerary_with_images import create_itinerary_with_images_tool

    print("✅ Tool importati con successo")
except ImportError as e:
    print(f"⚠️ Errore nell'importazione dei tool: {e}")
    flights_finder_tool = None
    hotels_finder_tool = None
    chain_historical_expert_tool = None
    chain_travel_plan_tool = None
    images_finder_tool = None  # NUOVO!
    create_destination_guide_tool = None
    create_itinerary_with_images_tool = None

load_dotenv()


class Agent:
    def __init__(self):
        self.current_datetime = datetime.now()
        self.model = ChatOpenAI(
            model_name="gpt-4.1",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        # Crea la lista dei tool disponibili (incluse le immagini!)
        self.tools = []
        base_tools = [
            ("flights_finder", flights_finder_tool),
            ("hotels_finder", hotels_finder_tool),
            ("historical_expert", chain_historical_expert_tool),
            ("travel_plan", chain_travel_plan_tool),
            ("images_finder", images_finder_tool),
        ]

        # Tool combinati per workflow coordinati
        combined_tools = [
            ("destination_guide", create_destination_guide_tool),
            ("itinerary_with_images", create_itinerary_with_images_tool),
        ]

        all_tools = base_tools + combined_tools

        for name, tool in all_tools:
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
            # Crea il prompt per l'agente con tool coordinati
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        f"""
🌟 Sei TravelAgent, un esperto agente di viaggio AI professionale e amichevole!

Data di oggi: {self.current_datetime.strftime('%d/%m/%Y')}

Hai accesso a questi strumenti e DEVI COORDINARLI tra loro:
- flights_finder: per cercare voli reali usando SerpAPI
- hotels_finder: per trovare hotel disponibili usando SerpAPI
- chain_historical_expert: per informazioni storiche sui luoghi
- chain_travel_plan: per creare piani di viaggio dettagliati
- images_finder: per cercare e mostrare immagini COERENTI con il contesto
- destination_guide: per guide dettagliate sulle destinazioni
- itinerary_with_images: per creare itinerari con immagini integrate

🎯 REGOLE DI COORDINAMENTO TOOL:

1. **FLUSSO PIANIFICAZIONE VIAGGIO:**
   - Prima: usa chain_travel_plan per l'itinerario completo
   - Poi: usa images_finder per OGNI destinazione/attrazione menzionata nell'itinerario
   - Quindi: usa hotels_finder per alloggi nelle città dell'itinerario
   - Infine: usa flights_finder se servono voli

2. **FLUSSO RICERCA DESTINAZIONE:**
   - Prima: usa chain_historical_expert per contesto storico/culturale
   - Poi: usa images_finder con i NOMI SPECIFICI dei monumenti/attrazioni menzionati
   - Aggiungi: hotels_finder per alloggi nella zona

3. **COORDINAMENTO IMMAGINI:**
   - Le immagini DEVONO essere specifiche per quello che hai appena descritto
   - Se parli del "Colosseo", cerca immagini del "Colosseo", non di "Roma generica"
   - Se menzioni "Sagrada Familia", cerca "Sagrada Familia Barcelona"
   - Se descrivi un itinerario con tappe, cerca immagini per OGNI tappa specifica

4. **ESEMPI DI COORDINAMENTO:**

   Richiesta: "Itinerario 3 giorni a Roma"
   1. chain_travel_plan("3 giorni Roma itinerario dettagliato")
   2. Per ogni attrazione nell'itinerario: images_finder("nome_attrazione_specifica")
   3. hotels_finder("Roma centro storico")

   Richiesta: "Dimmi del Colosseo"
   1. chain_historical_expert("Colosseo Roma storia")
   2. images_finder("Colosseo Roma anfiteatro")

   Richiesta: "Viaggio Barcellona"
   1. chain_travel_plan("Barcellona itinerario completo")
   2. images_finder("Sagrada Familia Barcellona") per ogni attrazione specifica
   3. images_finder("Park Güell Barcellona")
   4. hotels_finder("Barcellona centro")

5. **PAROLE CHIAVE PER ATTIVAZIONE:**
   - "volo/aereo" → flights_finder + destinazione images_finder
   - "hotel/alloggio" → hotels_finder + zona images_finder  
   - "storia/monumenti" → chain_historical_expert + monumenti specifici images_finder
   - "itinerario/programma" → chain_travel_plan + ogni tappa images_finder
   - "viaggio a [città]" → chain_travel_plan + chain_historical_expert + images_finder specifiche

6. **FORMATO RISPOSTA COORDINATA:**
   - Descrivi il contenuto
   - Mostra immagini SPECIFICHE di quello che hai descritto
   - Aggiungi informazioni pratiche (hotel/voli se rilevanti)

IMPORTANTE: 
- OGNI immagine deve essere PERTINENTE al contenuto specifico
- USA i nomi esatti delle attrazioni nelle ricerche immagini
- COORDINA i tool in sequenza logica
- NON usare immagini generiche se puoi essere specifico

Rispondi sempre in italiano con emoji e usa i tool in modo coordinato!
                """,
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("user", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )

            # Crea l'agente
            agent = create_openai_functions_agent(
                llm=self.model, tools=self.tools, prompt=prompt
            )

            # Crea l'executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                return_intermediate_steps=True,
                handle_parsing_errors=True,
                max_execution_time=300,
                max_iterations=100,
            )

            print(
                f"🚀 Agente configurato con {len(self.tools)} tool (incluse immagini!)"
            )

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
                                chat_history.append(
                                    HumanMessage(content=msg["content"])
                                )
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

                result = self.agent_executor.invoke(
                    {"input": user_message, "chat_history": chat_history}
                )

                response_content = result.get("output", "Nessuna risposta generata")
                print(f"🤖 Risposta agente: {response_content}")

                return {
                    "output": response_content,
                    "status": "success",
                    "tools_used": len(self.tools),
                    "context_messages": len(chat_history),
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
                "error_details": str(e),
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
            "context_messages": len(chat_history),
        }

    def _should_search_images(self, message: str) -> bool:
        """Rileva se l'utente vuole vedere immagini"""
        image_keywords = [
            "mostra",
            "immagini",
            "foto",
            "vedere",
            "come",
            "aspetto",
            "panorama",
            "vista",
            "paesaggio",
            "hotel",
            "ristorante",
            "show me",
            "pictures",
            "photos",
            "looks like",
            "visual",
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
                destination=destination, image_type=image_type, num_results=6
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

        if any(word in message_lower for word in ["hotel", "albergo", "resort"]):
            return "hotels luxury accommodations"
        elif any(
            word in message_lower for word in ["ristorante", "cibo", "cucina", "food"]
        ):
            return "restaurants local cuisine food"
        elif any(word in message_lower for word in ["spiaggia", "mare", "beach"]):
            return "beaches coast seaside"
        elif any(word in message_lower for word in ["panorama", "vista", "skyline"]):
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
            title = (
                img["title"][:50] + "..." if len(img["title"]) > 50 else img["title"]
            )
            response += f"**{i}. {title}**\n"
            response += f"🔗 [Visualizza immagine]({img['original']})\n"
            response += f"📐 Dimensioni: {img['width']}x{img['height']}px\n"
            if img["source"]:
                response += f"📍 Fonte: {img['source']}\n"
            response += "\n"

        response += "💡 **Suggerimento:** Clicca sui link per vedere le immagini ad alta risoluzione!"

        return response
