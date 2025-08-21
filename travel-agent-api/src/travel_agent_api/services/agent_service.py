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
    from travel_agent_api.tools.images_finder import images_finder_tool
    from travel_agent_api.tools.destination_guide import create_destination_guide_tool
    from travel_agent_api.tools.itinerary_with_images import create_itinerary_with_images_tool

    print("✅ Tool importati con successo")
except ImportError as e:
    print(f"⚠️ Errore nell'importazione dei tool: {e}")
    flights_finder_tool = None
    hotels_finder_tool = None
    chain_historical_expert_tool = None
    chain_travel_plan_tool = None
    images_finder_tool = None
    create_destination_guide_tool = None
    create_itinerary_with_images_tool = None

load_dotenv()


class Agent:
    def __init__(self):
        self.current_datetime = datetime.now()
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            request_timeout=60,
            max_retries=2
        )

        # Crea la lista dei tool disponibili
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
            # Crea il prompt per l'agente con tool coordinati E personalità Freya
            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    f"""
🌟 Il tuo nome è FREYA e sei un'esperta agente di viaggio AI femminile, professionale e amichevole!

PERSONALITÀ E IDENTITÀ:
- Nome: Freya
- Ruolo: Assistente di viaggio esperta e appassionata
- Personalità: Entusiasta, professionale, amichevole, esperta di culture mondiali
- Stile: Conversazionale ma informativo, usa emoji appropriati
- Obiettivo: Aiutare gli utenti a pianificare viaggi incredibili e memorabili

PRESENTAZIONE:
- Presentati sempre come "Freya" quando richiesto
- Usa un tono caloroso e professionale
- Mostra passione per i viaggi e le culture
- Sii precisa e dettagliata nelle informazioni

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

🎯 REGOLE DI COMUNICAZIONE FREYA:

1. **SALUTO INIZIALE:**
   - Presentati come Freya se è il primo messaggio o se richiesto
   - Usa un tono caloroso: "Ciao! Sono Freya, la tua assistente di viaggio personale!"
   - Mostra entusiasmo per aiutare nei viaggi

2. **STILE DI RISPOSTA:**
   - Inizia sempre con un'emoji appropriata (✈️🌍🏖️🏛️)
   - Usa un linguaggio amichevole ma professionale
   - Mostra passione genuina per i viaggi e le culture
   - Usa espressioni come "Che fantastica destinazione!", "Adoro questa città!"
   - Concludi con suggerimenti o domande per continuare la conversazione

3. **PERSONALITÀ NELLE RISPOSTE:**
   - Mostra passione per i viaggi e le culture
   - Condividi curiosità e aneddoti interessanti sui luoghi
   - Sii sempre positiva e incoraggiante

4. **GESTIONE ERRORI:**
   - Se qualcosa non funziona, mantieni il tono professionale ma empatico
   - "Mi dispiace, sto avendo qualche difficoltà tecnica..."
   - Offri sempre alternative o suggerisci di riprovare

IMPORTANTE: 
- Ricorda sempre che sei FREYA, l'assistente di viaggio esperta
- OGNI immagine deve essere PERTINENTE al contenuto specifico
- USA i nomi esatti delle attrazioni nelle ricerche immagini
- COORDINA i tool in sequenza logica
- NON usare immagini generiche se puoi essere specifico
- Mantieni sempre la tua personalità calorosa e professionale
- Se NON ci sono immagini specifiche disponibili, usa immagini generiche solo come ultima risorsa

Rispondi sempre in italiano con emoji e usa i tool in modo coordinato!
                    """
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            # Crea l'agente
            agent = create_openai_functions_agent(
                llm=self.model, 
                tools=self.tools, 
                prompt=prompt
            )

            # Crea l'executor con timeout esteso
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                return_intermediate_steps=True,
                handle_parsing_errors=True,
                max_execution_time=1200,  # 20 minuti
                max_iterations=8,
                early_stopping_method="generate"
            )

            print(f"🚀 Freya configurata con {len(self.tools)} tool e timeout di 1200 secondi")

        except Exception as e:
            print(f"❌ Errore nella configurazione di Freya: {e}")
            self.agent_executor = None

    def run(self, messages: list):
        try:
            # Reset timeout per richieste lunghe
            import threading
            import time
            
            def timeout_handler():
                time.sleep(1080)  # 18 minuti
                raise TimeoutError("Timeout globale raggiunto")
            
            # Timeout globale di 18 minuti usando threading
            timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
            timeout_thread.start()
            
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

                print(f"💬 Messaggio ricevuto da Freya: {user_message}")
                print(f"📝 Chat history: {len(chat_history)} messaggi precedenti")

                # Se abbiamo l'agente con tool, usalo
                if self.agent_executor:
                    print("🔧 Freya sta usando i suoi strumenti...")

                    result = self.agent_executor.invoke(
                        {"input": user_message, "chat_history": chat_history}
                    )

                    response_content = result.get("output", "Nessuna risposta generata")
                    print(f"🤖 Risposta di Freya: {response_content}")

                    return {
                        "output": response_content,
                        "status": "success",
                        "tools_used": len(self.tools),
                        "context_messages": len(chat_history),
                        "agent": "Freya"
                    }

                else:
                    # Fallback a chat semplice
                    print("💭 Freya sta usando la modalità chat semplice...")
                    
                    # Usa chat semplice come fallback
                    return self._simple_chat_response(user_message, chat_history)
            finally:
                pass  # Il thread daemon si chiuderà automaticamente

        except TimeoutError:
            return {
                "output": "⏰ Mi dispiace, la richiesta sta richiedendo più tempo del previsto. Freya sta lavorando su richieste complesse. Riprova tra qualche momento!",
                "status": "timeout",
                "agent": "Freya"
            }
        except Exception as e:
            print(f"🚨 Errore di Freya: {e}")
            import traceback
            traceback.print_exc()
            return {
                "output": f"🚨 Mi dispiace, Freya ha riscontrato un problema tecnico: {str(e)}. Potresti riprovare?",
                "status": "error",
                "error_details": str(e),
                "agent": "Freya"
            }

    def _simple_chat_response(self, user_message: str, chat_history: list = None):
        """Risposta chat semplice senza tool ma con personalità Freya"""
        if chat_history is None:
            chat_history = []

        FREYA_SYSTEM_PROMPT = f"""
🌟 Sei FREYA, un'assistente di viaggio AI femminile, esperta e appassionata! 

PERSONALITÀ:
- Nome: Freya
- Personalità: Entusiasta, professionale, amichevole, esperta di culture mondiali
- Stile: Conversazionale ma informativo, usa emoji appropriati
- Obiettivo: Aiutare gli utenti a pianificare viaggi incredibili

Il tuo compito è organizzare viaggi per gli utenti con entusiasmo e competenza.
La data di oggi è {self.current_datetime.strftime('%d/%m/%Y')}

PRESENTAZIONE:
- Presentati come "Freya" se è il primo messaggio
- Usa un tono caloroso: "Ciao! Sono Freya, la tua assistente di viaggio personale!"
- Mostra entusiasmo per aiutare nei viaggi

STILE DI RISPOSTA:
- Inizia sempre con un'emoji appropriata (✈️🌍🏖️🏛️)
- Usa un linguaggio amichevole ma professionale
- Mostra passione genuina per i viaggi e le culture
- Usa espressioni come "Che fantastica destinazione!", "Adoro questa città!"
- Concludi con suggerimenti o domande per continuare la conversazione

Quando ti chiedono di un viaggio:
1. 🎯 Raccogli informazioni: destinazione, date, budget, preferenze
2. ✈️ Suggerisci voli (consigli generali)
3. 🏨 Consiglia hotel e alloggi
4. 🗓️ Proponi un itinerario giornaliero
5. 🍝 Suggerisci ristoranti e piatti locali
6. 🎨 Includi attrazioni e attività culturali

Sii sempre positiva, utile e professionale! Ricorda che sei Freya!
        """

        # Costruisci i messaggi includendo la chat history
        langchain_messages = [SystemMessage(content=FREYA_SYSTEM_PROMPT)]
        langchain_messages.extend(chat_history)
        langchain_messages.append(HumanMessage(content=user_message))

        response = self.model.invoke(langchain_messages)

        return {
            "output": response.content,
            "status": "success",
            "mode": "freya_simple_chat",
            "context_messages": len(chat_history),
            "agent": "Freya"
        }

    def _should_search_images(self, message: str) -> bool:
        """Rileva se l'utente vuole vedere immagini"""
        image_keywords = [
            "mostra", "immagini", "foto", "vedere", "come", "aspetto", 
            "panorama", "vista", "paesaggio", "hotel", "ristorante",
            "show me", "pictures", "photos", "looks like", "visual",
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in image_keywords)

    def _extract_destination(self, message: str) -> str:
        """Estrae la destinazione dal messaggio dell'utente"""
        # Lista di città comuni
        major_cities = [
            "Roma", "Milano", "Napoli", "Firenze", "Venezia", "Torino", "Bologna",
            "Parigi", "Londra", "Berlino", "Madrid", "Barcellona", "Amsterdam",
            "New York", "Tokyo", "Sydney", "Dubai", "Istanbul", "Cairo"
        ]
        
        message_lower = message.lower()
        
        for city in major_cities:
            if city.lower() in message_lower:
                return city
        
        # Pattern generico per estrarre nomi di luoghi
        import re
        patterns = [
            r"(?:a|in|per|di)\s+([A-Z][a-zA-ZÀ-ÿ\s]{2,20})",
            r"([A-Z][a-zA-ZÀ-ÿ\s]{2,20})\s+(?:viaggio|tour|vacanza)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message)
            if matches:
                return matches[0].strip()
        
        return ""

    def _extract_image_type(self, message: str) -> str:
        """Estrae il tipo di immagini richieste"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["hotel", "albergo", "resort"]):
            return "hotels luxury accommodations"
        elif any(word in message_lower for word in ["ristorante", "cibo", "cucina", "food"]):
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
            title = img["title"][:50] + "..." if len(img["title"]) > 50 else img["title"]
            response += f"**{i}. {title}**\n"
            response += f"🔗 [Visualizza immagine]({img['original']})\n"
            response += f"📐 Dimensioni: {img['width']}x{img['height']}px\n"
            if img["source"]:
                response += f"📍 Fonte: {img['source']}\n"
            response += "\n"

        response += "💡 **Suggerimento:** Clicca sui link per vedere le immagini ad alta risoluzione!"
        return response
