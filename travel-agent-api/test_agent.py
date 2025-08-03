"""
Test semplice per verificare il funzionamento dell'agent
"""
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

def test_simple_agent():
    try:
        # Test base del modello OpenAI
        model = ChatOpenAI(model_name="gpt-4")
        
        messages = [
            SystemMessage(content="Sei un assistente di viaggio amichevole. Rispondi brevemente."),
            HumanMessage(content="Ciao, dimmi qualcosa su Roma")
        ]
        
        response = model.invoke(messages)
        print(f"✅ Risposta: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

if __name__ == "__main__":
    test_simple_agent()
