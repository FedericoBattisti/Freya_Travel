from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.agent_service import Agent

router = APIRouter()


class ChatCompletionRequest(BaseModel):
    messages: list

    model_config = {
        "json_schema_extra": {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Vorrei organizzare un viaggio a Roma",
                    }
                ]
            }
        }
    }


@router.post("/travel-agent")
def chat_completion(request: ChatCompletionRequest):
    """
    Endpoint per la gestione delle richieste di chat.
    Processa i messaggi ricevuti e restituisce una risposta dall'agente di viaggio.
    Args:
        request (ChatCompletionRequest): La richiesta contenente i messaggi della conversazione
    Returns:
        dict: La risposta elaborata dall'agente di viaggio
    Raises:
        HTTPException: In caso di errori durante l'elaborazione della richiesta
    """
    try:
        agent = Agent()
        response = agent.run(messages=request.messages)
        
        if not response or "output" not in response:
            raise HTTPException(
                status_code=500,
                detail="Nessuna risposta generata dall'agente"
            )
            
        return {
            "response": response.get("output"),
            "status": "success"
        }
    except Exception as e:
        print(f"Errore in chat_completion: {str(e)}")  # Debug
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante l'elaborazione: {str(e)}"
        )
