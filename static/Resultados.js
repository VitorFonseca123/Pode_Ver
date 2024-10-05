document.addEventListener("DOMContentLoaded", function() {
        const cortinaLeft = document.querySelector('.cortina-left');
        const cortinaRight = document.querySelector('.cortina-right');
        
        // Adiciona a classe de animação
        setTimeout(() => {
            cortinaLeft.classList.add('animate');
            cortinaRight.classList.add('animate');
        }, 1000); // Ajuste o tempo de acordo com a necessidade
    
        // Detecta o final da animação de transição
        cortinaLeft.addEventListener('transitionend', function() {
            cortinaLeft.parentElement.classList.add('hidden');
        });
        
        cortinaRight.addEventListener('transitionend', function() {
            cortinaRight.parentElement.classList.add('hidden');
        });
    });