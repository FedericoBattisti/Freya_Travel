import './bootstrap';
import 'bootstrap/dist/js/bootstrap.min.js';

const dropzoneAreas = document.querySelectorAll('.dropzone-area');


if( dropzoneAreas.length > 0 ){
    dropzoneAreas.forEach( dropzoneArea => {

        dropzoneArea.addEventListener('change', (e) => {


            let file = e.target.files[0];
            let fileNameWrapper = dropzoneArea.querySelector('.file-name');

            if( file ){
                let fileName = file.name
                let fileSize = humanReadableBytes(file.size)

                fileNameWrapper.innerHTML = `${fileName} (${fileSize})`;
            } else {
                fileNameWrapper.innerHTML = '<i class="bi bi-upload"></i> Upload a file';
            }




        });
    });
}

function humanReadableBytes(bytes) {
    let i = Math.floor( Math.log(bytes) / Math.log(1024) );
    return ( bytes / Math.pow(1024, i) ).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i];
}

document.addEventListener('DOMContentLoaded', function() {
    // Inizializza la sidebar
    initializeSidebar();
    initializeChatbot();
});

function initializeSidebar() {
    // Gestione navigation links
    handleNavigationLinks();
    
    // Gestione dropdown
    handleDropdown();
    
    // Gestione mobile menu
    handleMobileMenu();
    
    // Auto-close su mobile dopo click
    handleAutoClose();
}

function handleNavigationLinks() {
    const navLinks = document.querySelectorAll('.minimal-nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Rimuovi active da tutti i link
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Aggiungi active al link cliccato
            this.classList.add('active');
            
            // Salva stato nel localStorage
            const page = this.getAttribute('data-page');
            if (page) {
                localStorage.setItem('activePage', page);
            }
            
            // Effetto click
            addClickEffect(this);
        });
    });
    
    // Ripristina stato attivo dal localStorage
    restoreActiveState();
}

function handleDropdown() {
    const dropdownToggle = document.querySelector('.user-profile.dropdown-toggle');
    const dropdown = document.querySelector('.minimal-dropdown');
    
    if (dropdownToggle) {
        dropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Bootstrap gestisce già il dropdown, aggiungiamo solo effetti custom
            setTimeout(() => {
                const isExpanded = this.getAttribute('aria-expanded') === 'true';
                this.classList.toggle('dropdown-active', isExpanded);
            }, 10);
        });
    }
}

function handleMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            // Effetto ripple al click
            addRippleEffect(this);
        });
    }
}

function handleAutoClose() {
    const navLinks = document.querySelectorAll('.minimal-nav-link');
    const offcanvas = document.getElementById('offcanvasResponsive');
    
    if (window.innerWidth <= 768) {
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                // Chiudi il menu mobile dopo il click
                setTimeout(() => {
                    const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvas);
                    if (bsOffcanvas) {
                        bsOffcanvas.hide();
                    }
                }, 150);
            });
        });
    }
}

function addClickEffect(element) {
    // Aggiungi classe per effetto visivo
    element.classList.add('clicked');
    
    // Rimuovi la classe dopo l'animazione
    setTimeout(() => {
        element.classList.remove('clicked');
    }, 200);
}

function addRippleEffect(element) {
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = (rect.width / 2 - size / 2) + 'px';
    ripple.style.top = (rect.height / 2 - size / 2) + 'px';
    
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

function restoreActiveState() {
    const activePage = localStorage.getItem('activePage');
    if (activePage) {
        const activeLink = document.querySelector(`[data-page="${activePage}"]`);
        if (activeLink) {
            // Rimuovi active da tutti
            document.querySelectorAll('.minimal-nav-link').forEach(l => l.classList.remove('active'));
            // Aggiungi active al link salvato
            activeLink.classList.add('active');
        }
    }
}

// Utility per responsive behavior
function handleResize() {
    const sidebar = document.querySelector('.minimal-sidebar');
    
    if (window.innerWidth > 768) {
        // Desktop: assicurati che la sidebar sia visibile
        sidebar.classList.remove('show');
    }
}

// Event listener per resize
window.addEventListener('resize', handleResize);

// CSS aggiuntivo per effetti JavaScript
const additionalStyles = `
<style>
.minimal-nav-link.clicked {
    transform: scale(0.98);
    transition: transform 0.1s ease;
}

.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: scale(0);
    animation: ripple-effect 0.6s linear;
    pointer-events: none;
}

@keyframes ripple-effect {
    to {
        transform: scale(4);
        opacity: 0;
    }
}

.dropdown-active .dropdown-icon {
    color: var(--sidebar-active);
}
</style>
`;

// Aggiungi gli stili al head
document.head.insertAdjacentHTML('beforeend', additionalStyles);

function initializeChatbot() {
    // Elementi principali
    const chatBox = document.getElementById('chatBox');
    const messageInput = document.querySelector('.message-input');
    const chatForm = document.getElementById('chatForm');
    const typingIndicator = document.getElementById('typingIndicator');
    
    // Inizializza funzionalità
    handleAutoScroll();
    handleSuggestions();
    handleInputEvents();
    handleMessageActions();
    handleTypingIndicator();
    handleKeyboardShortcuts();
}

function handleAutoScroll() {
    const chatBox = document.getElementById('chatBox');
    
    // Scroll automatico quando arrivano nuovi messaggi
    if (window.Livewire) {
        Livewire.on('scrollChatToBottom', () => {
            setTimeout(() => {
                scrollToBottom(chatBox);
            }, 100);
        });
    }
    
    // Scroll automatico con animazione smooth
    function scrollToBottom(element) {
        element.scrollTo({
            top: element.scrollHeight,
            behavior: 'smooth'
        });
    }
}

function handleSuggestions() {
    const suggestionButtons = document.querySelectorAll('.suggestion-btn');
    const messageInput = document.querySelector('.message-input');
    
    suggestionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const message = this.getAttribute('data-message');
            if (message && messageInput) {
                messageInput.value = message;
                messageInput.focus();
                
                // Trigger Livewire update
                messageInput.dispatchEvent(new Event('input'));
                
                // Aggiungi effetto click
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            }
        });
    });
}

function handleInputEvents() {
    const messageInput = document.querySelector('.message-input');
    const chatForm = document.getElementById('chatForm');
    
    if (messageInput) {
        // Auto-resize textarea (se necessario in futuro)
        messageInput.addEventListener('input', function() {
            // Possibile espansione futura per textarea auto-resize
        });
        
        // Gestione invio con Enter
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (this.value.trim()) {
                    chatForm.dispatchEvent(new Event('submit'));
                }
            }
        });
        
        // Focus automatico
        messageInput.focus();
    }
}

function handleMessageActions() {
    // Event delegation per i pulsanti delle azioni sui messaggi
    document.addEventListener('click', function(e) {
        if (e.target.closest('.action-btn')) {
            const button = e.target.closest('.action-btn');
            const action = getActionType(button);
            const messageContent = button.closest('.message-bubble').querySelector('.message-content');
            
            switch(action) {
                case 'copy':
                    copyToClipboard(messageContent.textContent);
                    showTooltip(button, 'Copiato!');
                    break;
                case 'like':
                    toggleLike(button);
                    break;
                case 'dislike':
                    toggleDislike(button);
                    break;
            }
        }
    });
}

function getActionType(button) {
    if (button.querySelector('.bi-clipboard')) return 'copy';
    if (button.querySelector('.bi-hand-thumbs-up')) return 'like';
    if (button.querySelector('.bi-hand-thumbs-down')) return 'dislike';
    return null;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log('Testo copiato negli appunti');
    }).catch(err => {
        console.error('Errore nella copia:', err);
    });
}

function toggleLike(button) {
    button.classList.toggle('liked');
    const icon = button.querySelector('i');
    if (button.classList.contains('liked')) {
        icon.className = 'bi bi-hand-thumbs-up-fill';
        button.style.color = 'var(--success-color)';
    } else {
        icon.className = 'bi bi-hand-thumbs-up';
        button.style.color = '';
    }
}

function toggleDislike(button) {
    button.classList.toggle('disliked');
    const icon = button.querySelector('i');
    if (button.classList.contains('disliked')) {
        icon.className = 'bi bi-hand-thumbs-down-fill';
        button.style.color = 'var(--error-color)';
    } else {
        icon.className = 'bi bi-hand-thumbs-down';
        button.style.color = '';
    }
}

function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = text;
    
    element.appendChild(tooltip);
    
    setTimeout(() => {
        tooltip.remove();
    }, 2000);
}

function handleTypingIndicator() {
    let typingTimeout;
    
    // Simula indicatore di scrittura quando l'AI sta "pensando"
    function showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.style.display = 'flex';
            scrollToBottom(document.getElementById('chatBox'));
        }
    }
    
    function hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    // Integrazione con Livewire per mostrare/nascondere l'indicatore
    if (window.Livewire) {
        Livewire.on('showTyping', () => {
            showTypingIndicator();
        });
        
        Livewire.on('hideTyping', () => {
            hideTypingIndicator();
        });
    }
}

function handleKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K per focus sull'input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const messageInput = document.querySelector('.message-input');
            if (messageInput) {
                messageInput.focus();
            }
        }
        
        // Escape per pulire l'input
        if (e.key === 'Escape') {
            const messageInput = document.querySelector('.message-input');
            if (messageInput && document.activeElement === messageInput) {
                messageInput.value = '';
                messageInput.blur();
            }
        }
    });
}

function scrollToBottom(element) {
    if (element) {
        element.scrollTo({
            top: element.scrollHeight,
            behavior: 'smooth'
        });
    }
}

// Utility per responsive behavior
function handleResize() {
    const chatContainer = document.querySelector('.chat-container');
    
    if (window.innerWidth <= 768) {
        // Mobile adjustments
        chatContainer.classList.add('mobile-view');
    } else {
        // Desktop adjustments  
        chatContainer.classList.remove('mobile-view');
    }
}

window.addEventListener('resize', handleResize);

// CSS aggiuntivo per tooltip e effetti
const additionalStylesChatbot = `
<style>
.custom-tooltip {
    position: absolute;
    top: -30px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--chat-surface);
    color: var(--chat-text);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    white-space: nowrap;
    z-index: 1000;
    border: 1px solid var(--chat-border);
    animation: tooltipFadeIn 0.2s ease;
}

@keyframes tooltipFadeIn {
    from { opacity: 0; transform: translateX(-50%) translateY(-5px); }
    to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

.mobile-view .message-wrapper {
    max-width: 95%;
}

.mobile-view .chat-header {
    padding: 0.75rem 1rem;
}

.mobile-view .chat-input-container {
    padding: 0.75rem 1rem;
}

.liked {
    animation: likeAnimation 0.3s ease;
}

.disliked {
    animation: dislikeAnimation 0.3s ease;
}

@keyframes likeAnimation {
    0% { transform: scale(1); }
    50% { transform: scale(1.2); }
    100% { transform: scale(1); }
}

@keyframes dislikeAnimation {
    0% { transform: scale(1); }
    50% { transform: scale(1.2); }
    100% { transform: scale(1); }
}
</style>
`;

// Aggiungi gli stili al head
document.head.insertAdjacentHTML('beforeend', additionalStylesChatbot);

// Inizializza al caricamento della pagina
handleResize();