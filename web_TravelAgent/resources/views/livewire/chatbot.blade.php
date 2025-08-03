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
                        {!! $chatMessage['content'] !!}
                    </div>
                    <div class="message-actions">
                        <button class="action-btn" title="Copia">
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
                <div class="input-actions-left">
                    <button type="button" class="input-btn" title="Allega file">
                        <i class="bi bi-paperclip"></i>
                    </button>
                </div>
                
                <input 
                    class="message-input" 
                    placeholder="Scrivi un messaggio..." 
                    wire:model.live="currentMessage" 
                    type="text"
                    autocomplete="off">
                
                <div class="input-actions-right">
                    <button type="button" class="input-btn" title="Emoji">
                        <i class="bi bi-emoji-smile"></i>
                    </button>
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
</script>
@endscript