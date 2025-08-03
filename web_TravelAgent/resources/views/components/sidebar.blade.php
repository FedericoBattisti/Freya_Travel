{{-- filepath: c:\Users\User\wa\Progetto Finale\web_TravelAgent\resources\views\components\sidebar.blade.php --}}
<div class="d-flex align-items-center">
    <button class="btn d-md-none ms-3 mobile-menu-btn" type="button" data-bs-toggle="offcanvas" 
        data-bs-target="#offcanvasResponsive" aria-controls="offcanvasResponsive">
        <i class="bi bi-list fs-1"></i>
    </button>
</div>

<div class="offcanvas-md offcanvas-start minimal-sidebar" tabindex="-1" id="offcanvasResponsive"
    aria-labelledby="offcanvasResponsiveLabel">
    <div class="offcanvas-body">
        <div class="d-flex flex-column flex-shrink-0 p-md-4 sidebar">
            <!-- Brand per desktop -->
            <a href="{{ route('chat.index') }}" class="d-none d-md-flex brand-link-desktop">
                <div >
                    <img src="/RagsAI-LOGO.png" class="brand-logo" alt="Freya Travel Logo">
                </div>
                <h1 class="brand-title">Freya Travel</h1>
            </a>
            
            <div class="divider"></div>
            
            <!-- Navigation -->
            <ul class="nav nav-pills flex-column mb-auto minimal-nav">
                <li class="nav-item">
                    <a href="{{ route('chat.index') }}" class="nav-link minimal-nav-link active" data-page="chat">
                        <i class="bi bi-chat-dots nav-icon"></i>
                        <span class="nav-text">Chat</span>
                    </a>
                </li>
                <li class="nav-item">
                    <a href="#" class="nav-link minimal-nav-link" data-page="trips">
                        <i class="bi bi-airplane nav-icon"></i>
                        <span class="nav-text">Viaggi</span>
                    </a>
                </li>
                <li class="nav-item">
                    <a href="#" class="nav-link minimal-nav-link" data-page="favorites">
                        <i class="bi bi-heart nav-icon"></i>
                        <span class="nav-text">Preferiti</span>
                    </a>
                </li>
                <li class="nav-item">
                    <a href="#" class="nav-link minimal-nav-link" data-page="history">
                        <i class="bi bi-clock-history nav-icon"></i>
                        <span class="nav-text">Cronologia</span>
                    </a>
                </li>
            </ul>
            
            <div class="divider"></div>
        </div>
    </div>
</div>
