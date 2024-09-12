document.addEventListener('DOMContentLoaded', (event) => {
    loadCartFromLocalStorage();
    document.querySelectorAll('.add-button').forEach(button => {
        button.addEventListener('click', () => {
            const movieTitle = button.getAttribute('data-title');
            const moviePosterUrl = button.getAttribute('data-poster');
            addToCart(movieTitle, moviePosterUrl);
        });
    });
});

function addToCart(movieTitle, moviePosterUrl) {
    const sidebar = document.getElementById('sidebar');
    const cartList = document.getElementById('cart-list');
    const listItem = document.createElement('li');
    const img = document.createElement('img');
    const deleteButton = document.createElement('button');
    
    img.src = moviePosterUrl;
    deleteButton.textContent = 'Excluir';
    deleteButton.className = 'delete-button';
    deleteButton.onclick = function() {
        cartList.removeChild(listItem);
        saveCartToLocalStorage();
        if (cartList.children.length === 0) {
            closeSidebar();
        }
    };

    listItem.appendChild(img);
    listItem.appendChild(document.createTextNode(movieTitle));
    listItem.appendChild(deleteButton);
    cartList.appendChild(listItem);

    saveCartToLocalStorage();
    openSidebar(); // Abrir a barra lateral após adicionar o filme
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.remove('visible');
}

function openSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.add('visible');
}

function saveCartToLocalStorage() {
    const cartList = document.getElementById('cart-list');
    const movies = [];
    for (let i = 0; i < cartList.children.length; i++) {
        const listItem = cartList.children[i];
        const movieTitle = listItem.childNodes[1].nodeValue;
        const moviePosterUrl = listItem.childNodes[0].src;
        movies.push({ title: movieTitle, posterUrl: moviePosterUrl });
    }
    localStorage.setItem('cart', JSON.stringify(movies));
}

function loadCartFromLocalStorage() {
    const cartList = document.getElementById('cart-list');
    const movies = JSON.parse(localStorage.getItem('cart')) || [];
    movies.forEach(movie => {
        const listItem = document.createElement('li');
        const img = document.createElement('img');
        const deleteButton = document.createElement('button');
        
        img.src = movie.posterUrl;
        deleteButton.textContent = 'Excluir';
        deleteButton.className = 'delete-button';
        deleteButton.onclick = function() {
            cartList.removeChild(listItem);
            saveCartToLocalStorage();
            if (cartList.children.length === 0) {
                closeSidebar();
            }
        };

        listItem.appendChild(img);
        listItem.appendChild(document.createTextNode(movie.title));
        listItem.appendChild(deleteButton);
        cartList.appendChild(listItem);
    });
}