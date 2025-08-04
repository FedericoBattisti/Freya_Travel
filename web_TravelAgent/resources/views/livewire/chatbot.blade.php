<div class="chat-container">
    <!-- Chat Header -->
    <div class="chat-header">
        <div class="chat-status">
            <div class="status-indicator online"></div>
            <div class="status-text">
                <h3 class="chat-title">Freya AI Assistant</h3>
                <span class="chat-subtitle">Sempre pronta ad aiutarti</span>
            </div>
        </div>
        <div class="chat-actions">
            <button class="btn-icon" title="Nuova conversazione">
                <i class="bi bi-plus-lg"></i>
            </button>
            <button class="btn-icon" title="Impostazioni">
                <i class="bi bi-gear"></i>
            </button>
        </div>
    </div>

    <!-- Chat Messages -->
    <div class="chat-box" id="chatBox">
        @forelse ($chatMessages as $key => $chatMessage)
            @if($chatMessage['type'] == 'human')
            <div wire:key="{{ $key }}" class="message-wrapper user-message">
                <div class="message-bubble user-bubble">
                    <div class="message-content">
                        {{ $chatMessage['content'] }}
                    </div>
                    <div class="message-time">
                        {{ now()->format('H:i') }}
                    </div>
                </div>
                <div class="message-avatar">
                    <img src="/user.png" alt="User" class="avatar-img">
                </div>
            </div>
            @endif

            @if($chatMessage['type'] == 'ai' && $chatMessage['content'])
            <div wire:key="{{ $key }}" class="message-wrapper ai-message">
                <div class="message-avatar">
                    <div class="ai-avatar">
                        <i class="bi bi-airplane-engines"></i>
                    </div>
                </div>
                <div class="message-bubble ai-bubble">
                    <div class="message-content">
                        <!-- Processa il contenuto per renderizzare le immagini -->
                        <div class="ai-response-content">
                            {!! $this->processAIContent($chatMessage['content']) !!}
                        </div>
                    </div>
                    <div class="message-actions">
                        <button class="action-btn" title="Copia" onclick="copyToClipboard('{{ $key }}')">
                            <i class="bi bi-clipboard"></i>
                        </button>
                        <button class="action-btn" title="Like">
                            <i class="bi bi-hand-thumbs-up"></i>
                        </button>
                        <button class="action-btn" title="Dislike">
                            <i class="bi bi-hand-thumbs-down"></i>
                        </button>
                        <span class="message-time">{{ now()->format('H:i') }}</span>
                    </div>
                </div>
            </div>
            @endif
        @empty
            <div class="welcome-message">
                <div class="welcome-avatar">
                    <i class="bi bi-airplane-engines"></i>
                </div>
                <div class="welcome-content">
                    <h4>Ciao! Sono Freya 👋</h4>
                    <p>Il tuo assistente di viaggio personale. Come posso aiutarti oggi?</p>
                    <div class="quick-suggestions">
                        <button class="suggestion-btn" data-message="Trova voli per Roma">
                            ✈️ Cerca voli
                        </button>
                        <button class="suggestion-btn" data-message="Hotel a Parigi">
                            🏨 Trova hotel
                        </button>
                        <button class="suggestion-btn" data-message="Mostra immagini di Venezia">
                            🖼️ Mostra immagini
                        </button>
                        <button class="suggestion-btn" data-message="Itinerario per il Giappone">
                            🗺️ Crea itinerario
                        </button>
                    </div>
                </div>
            </div>
        @endforelse 
    </div>

    <!-- Chat Input -->
    <div class="chat-input-container">
        <form id="chatForm" wire:submit.prevent="ask" class="chat-input-form">
            <div class="input-wrapper">
                <input 
                    class="message-input" 
                    placeholder="Scrivi un messaggio..." 
                    wire:model.live="currentMessage" 
                    type="text"
                    autocomplete="off">
                
                <div class="input-actions-right">
                    <button type="submit" class="send-btn" title="Invia">
                        <i class="bi bi-send-fill"></i>
                    </button>
                </div>
            </div>
            
            @error('currentMessage') 
                <div class="error-message">{{ $message }}</div> 
            @enderror
        </form>
        
        <!-- Typing Indicator -->
        <div class="typing-indicator" id="typingIndicator" style="display: none;">
            <div class="typing-avatar">
                <i class="bi bi-airplane-engines"></i>
            </div>
            <div class="typing-bubble">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    </div>
</div>

@script
<script>
const chatBox = document.querySelector('.chat-box');

$wire.on('scrollChatToBottom', () => {
    setTimeout(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 500);
});

// Gestione dei suggerimenti
document.addEventListener('DOMContentLoaded', function() {
    // Click sui suggestion buttons
    document.querySelectorAll('.suggestion-btn').forEach(button => {
        button.addEventListener('click', function() {
            const message = this.getAttribute('data-message');
            $wire.set('currentMessage', message);
            $wire.call('ask');
        });
    });
});

// Funzione per suggerire ricerca immagini
function suggestImageSearch() {
    const input = document.querySelector('.message-input');
    input.value = 'Mostra immagini di ';
    input.focus();
    input.setSelectionRange(input.value.length, input.value.length);
}

// Funzione per copiare testo
function copyToClipboard(messageKey) {
    const messageContent = document.querySelector(`[wire\\:key="${messageKey}"] .message-content`);
    if (messageContent) {
        const text = messageContent.innerText;
        navigator.clipboard.writeText(text).then(() => {
            // Mostra feedback visivo
            const button = event.target.closest('.action-btn');
            const originalIcon = button.innerHTML;
            button.innerHTML = '<i class="bi bi-check"></i>';
            setTimeout(() => {
                button.innerHTML = originalIcon;
            }, 1000);
        });
    }
}

// Gestione click sulle immagini per zoom
function openImageModal(src, alt) {
    // Crea modal per visualizzare immagine grande
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.innerHTML = `
        <div class="image-modal-backdrop" onclick="closeImageModal()">
            <div class="image-modal-content" onclick="event.stopPropagation()">
                <button class="image-modal-close" onclick="closeImageModal()">
                    <i class="bi bi-x-lg"></i>
                </button>
                <img src="${src}" alt="${alt}" class="image-modal-img">
                <div class="image-modal-caption">${alt}</div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    document.body.classList.add('modal-open');
}

function closeImageModal() {
    const modal = document.querySelector('.image-modal');
    if (modal) {
        modal.remove();
        document.body.classList.remove('modal-open');
    }
}

// Gestione lazy loading delle immagini
function setupLazyLoading() {
    const images = document.querySelectorAll('.ai-image[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// Inizializza lazy loading quando nuovi messaggi vengono aggiunti
$wire.on('messageAdded', () => {
    setTimeout(() => {
        setupLazyLoading();
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 100);
});
</script>
@endscript