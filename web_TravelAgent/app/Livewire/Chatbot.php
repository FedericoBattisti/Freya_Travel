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


    public function generateResponse()
    {

        // Prepara i messaggi nel formato corretto per FastAPI
        $messages = [];
        foreach ($this->chatMessages as $message) {
            if (isset($message['role']) && isset($message['content'])) {
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

    /**
     * Processa il contenuto AI per renderizzare correttamente le immagini
     */
    public function processAIContent($content)
    {
        // Converti i link delle immagini in tag HTML img
        $content = $this->convertImageLinksToHtml($content);

        // Converti Markdown in HTML
        $content = $this->convertMarkdownToHtml($content);

        // Aggiungi classi CSS per lo styling
        $content = $this->addStylingClasses($content);

        return $content;
    }

    /**
     * Converte i link delle immagini in tag HTML img
     */
    private function convertImageLinksToHtml($content)
    {
        // Pattern per i link delle immagini ![alt](url)
        $pattern = '/!\[([^\]]*)\]\(([^)]+)\)/';
        $content = preg_replace($pattern, '<img src="$2" alt="$1" class="ai-image lazy" data-src="$2" onclick="openImageModal(\'$2\', \'$1\')" loading="lazy">', $content);

        // Pattern per i link normali alle immagini [text](url) quando url è un'immagine
        $pattern = '/\[([^\]]*)\]\((https?:\/\/[^)]*\.(jpg|jpeg|png|gif|webp)[^)]*)\)/i';
        $content = preg_replace($pattern, '<div class="image-link-container"><img src="$2" alt="$1" class="ai-image lazy" data-src="$2" onclick="openImageModal(\'$2\', \'$1\')" loading="lazy"><span class="image-caption">$1</span></div>', $content);

        return $content;
    }

    /**
     * Converte Markdown base in HTML
     */
    private function convertMarkdownToHtml($content)
    {
        // Titoli
        $content = preg_replace('/^### (.*$)/m', '<h3>$1</h3>', $content);
        $content = preg_replace('/^## (.*$)/m', '<h2>$1</h2>', $content);
        $content = preg_replace('/^\*\*(.*?)\*\*$/m', '<h4>$1</h4>', $content);

        // Grassetto
        $content = preg_replace('/\*\*(.*?)\*\*/', '<strong>$1</strong>', $content);

        // Corsivo
        $content = preg_replace('/\*(.*?)\*/', '<em>$1</em>', $content);

        // Liste puntate
        $content = preg_replace('/^• (.*)$/m', '<li>$1</li>', $content);
        $content = preg_replace('/(<li>.*<\/li>)/s', '<ul>$1</ul>', $content);

        // Link normali
        $content = preg_replace('/\[([^\]]*)\]\(([^)]+)\)/', '<a href="$2" target="_blank" rel="noopener">$1</a>', $content);

        // Emoji e icone
        $content = str_replace(
            ['🖼️', '📍', '🔗', '📐', '💡'],
            ['<span class="emoji">🖼️</span>', '<span class="emoji">📍</span>', '<span class="emoji">🔗</span>', '<span class="emoji">📐</span>', '<span class="emoji">💡</span>'],
            $content
        );

        // Converti newlines in <br>
        $content = nl2br($content);

        return $content;
    }

    /**
     * Aggiunge classi CSS per lo styling
     */
    private function addStylingClasses($content)
    {
        // Aggiungi classe ai link
        $content = str_replace('<a href=', '<a class="ai-link" href=', $content);

        // Aggiungi classe ai titoli
        $content = str_replace(
            ['<h2>', '<h3>', '<h4>'],
            ['<h2 class="ai-heading">', '<h3 class="ai-heading">', '<h4 class="ai-heading">'],
            $content
        );

        // Aggiungi classe alle liste
        $content = str_replace('<ul>', '<ul class="ai-list">', $content);

        return $content;
    }

    public function render()
    {
        $this->dispatch('scrollChatToBottom');
        return view('livewire.chatbot');
    }
}
