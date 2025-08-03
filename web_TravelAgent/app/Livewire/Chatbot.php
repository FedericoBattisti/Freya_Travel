<?php

namespace App\Livewire;

use Livewire\Component;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Http;

class Chatbot extends Component
{

    public $currentMessage = '';
    public $userPrompt = '';
    public $chatMessages = [];

    protected $rules = [
        'currentMessage' => 'required'
    ];

    protected $messages = [
        'currentMessage.required' => 'Please enter a message'
    ];

    public function ask()
    {
        $this->validate();

        // Aggiungi il messaggio dell'utente con il formato corretto per FastAPI
        $this->chatMessages[] = [
            'role' => 'user',
            'content' => $this->currentMessage,
            'type' => 'human' // Per la visualizzazione nel frontend
        ];

        $this->userPrompt = $this->currentMessage;

        $this->currentMessage = '';

        $this->js('$wire.generateResponse');
    }


    public function generateResponse(){

        // Prepara i messaggi nel formato corretto per FastAPI
        $messages = [];
        foreach($this->chatMessages as $message) {
            if(isset($message['role']) && isset($message['content'])) {
                // Invia SOLO role e content, senza il campo 'type' che è solo per il frontend
                $messages[] = [
                    'role' => $message['role'],
                    'content' => $message['content']
                ];
            }
        }

        try {
            $response = Http::timeout(120)->post("http://127.0.0.1:8080/chat/travel-agent", [
                'messages' => $messages
            ]);

            if ($response->successful()) {
                $content = $response->json();
                
                // Aggiungi la risposta del bot ai messaggi
                if (isset($content['response'])) {
                    // Processa i link per aprirli in nuove schede
                    $processedContent = $this->processLinksForNewTab($content['response']);
                    
                    $this->chatMessages[] = [
                        'role' => 'assistant',
                        'content' => $processedContent,
                        'type' => 'ai' // Per la visualizzazione nel frontend
                    ];
                } else {
                    // Fallback se la struttura è diversa
                    $this->chatMessages[] = [
                        'role' => 'assistant', 
                        'content' => 'Scusa, ho riscontrato un problema. Puoi riprovare?',
                        'type' => 'ai'
                    ];
                }
            } else {
                // Gestione errore HTTP
                $this->chatMessages[] = [
                    'role' => 'assistant',
                    'content' => 'Mi dispiace, il servizio non è al momento disponibile. Riprova più tardi.',
                    'type' => 'ai'
                ];
            }
            
        } catch (\Exception $e) {
            // Gestione eccezioni
            $this->chatMessages[] = [
                'role' => 'assistant',
                'content' => 'Si è verificato un errore di connessione. Controlla che il server FastAPI sia attivo.',
                'type' => 'ai'
            ];
            
            // Log dell'errore per debug
            Log::error('Chatbot API Error: ' . $e->getMessage());
        }
    }

    /**
     * Processa i link nella risposta per aprirli in nuove schede
     */
    private function processLinksForNewTab($content)
    {
        // Gestisce le immagini markdown ![alt](url)
        $content = preg_replace(
            '/!\[([^\]]*)\]\(([^)]+)\)/',
            '<img src="$2" alt="$1" style="max-width: 50px; height: auto; display: inline-block; vertical-align: middle; margin: 0 5px;">',
            $content
        );
        
        // Gestisce i testi di immagini non formattati come "!Nome Logo"
        $content = preg_replace('/!([A-Za-z\s]+)\s+Logo/i', '<span style="color: #666; font-size: 0.9em; font-style: italic;">($1)</span>', $content);
        
        // Gestisce i titoli ### 
        $content = preg_replace('/^### (.+)$/m', '<h3>$1</h3>', $content);
        
        // Gestisce il testo in grassetto **testo**
        $content = preg_replace('/\*\*([^*]+)\*\*/', '<strong>$1</strong>', $content);
        
        // Gestisce il testo in corsivo *testo* (ma non gli asterischi dei grassetti)
        $content = preg_replace('/(?<!\*)\*([^*]+)\*(?!\*)/', '<em>$1</em>', $content);
        
        // Converte i link markdown [testo](url) in HTML con target="_blank" 
        $content = preg_replace(
            '/\[([^\]]+)\]\(([^)]+)\)/',
            '<a href="$2" target="_blank" rel="noopener noreferrer" style="color: #0066cc; text-decoration: underline;">$1</a>',
            $content
        );
        
        // Converte gli URL diretti (che iniziano con http) in link cliccabili
        $content = preg_replace(
            '/(?<!href="|href=\')(?<!src="|src=\')(?<!>)(https?:\/\/[^\s<>"]+)(?!<)/',
            '<a href="$1" target="_blank" rel="noopener noreferrer" style="color: #0066cc; text-decoration: underline;">$1</a>',
            $content
        );
        
        // Gestisce le liste con punti elenco
        $content = preg_replace('/^- (.+)$/m', '<div style="margin: 5px 0; padding-left: 15px;">• $1</div>', $content);
        
        // Preserva i line breaks convertendoli in <br> MA evita doppi <br> dopo i div
        $content = nl2br($content);
        $content = preg_replace('/<\/div><br\s*\/?>/i', '</div>', $content);
        $content = preg_replace('/<\/h3><br\s*\/?>/i', '</h3>', $content);
        
        return $content;
    }

    public function render()
    {
        $this->dispatch('scrollChatToBottom');
        return view('livewire.chatbot');
    }
}
