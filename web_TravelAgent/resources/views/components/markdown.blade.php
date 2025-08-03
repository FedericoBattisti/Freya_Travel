@php
use Illuminate\Support\Str;

// Funzione per processare markdown e link
function processMarkdownWithLinks($content) {
    // Prima gestisco i link in formato markdown [testo](url)
    $content = preg_replace('/\[([^\]]+)\]\(([^)]+)\)/', '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-primary text-decoration-underline">$1</a>', $content);
    
    // Poi gestisco gli URL diretti che non sono già dentro tag <a>
    $content = preg_replace('/(?<!href="|href=\')(?<!src="|src=\')\b(https?:\/\/[^\s<>"]+)/', '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-primary text-decoration-underline">$1</a>', $content);
    
    // Gestisco i line breaks
    $content = str_replace("\n", "<br>", $content);
    
    // Gestisco il testo in grassetto **testo**
    $content = preg_replace('/\*\*([^*]+)\*\*/', '<strong>$1</strong>', $content);
    
    // Gestisco il testo in corsivo *testo*
    $content = preg_replace('/\*([^*]+)\*/', '<em>$1</em>', $content);
    
    // Gestisco le liste con -
    $content = preg_replace('/^- (.+)$/m', '<li>$1</li>', $content);
    $content = preg_replace('/(<li>.*<\/li>)/s', '<ul>$1</ul>', $content);
    
    return $content;
}

$processedContent = processMarkdownWithLinks($slot);
@endphp

<div class="markdown-content">
    {!! $processedContent !!}
</div>

<style>
.markdown-content a {
    color: #0d6efd;
    text-decoration: underline;
    transition: color 0.2s ease;
}

.markdown-content a:hover {
    color: #0a58ca;
    text-decoration: underline;
}

.markdown-content ul {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
}

.markdown-content li {
    margin: 0.25rem 0;
}

.markdown-content br {
    line-height: 1.5;
}
</style>
