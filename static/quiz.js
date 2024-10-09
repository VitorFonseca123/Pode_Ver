const questions = [
    {
        question: "Qual é o seu gênero de filme favorito?",
        options: ["Ação", "Comédia", "Drama", "Terror", "Aventura", "Thriller","Crime", "Romance", 
            "Ficção Científica", "Fantasia", "Animação", "Documentário", "Familia", "Mistério", "História",
             "Biografia", "Musical", "Esportes", "Desastre", "Velho-Oeste", "Guerra", "Super-Herói", "Suspense"]
    },
    {
        question: "Qual é o seu diretor de filme favorito?",
        options: ["Steven Spielberg", "Christopher Nolan", "Quentin Tarantino", "Martin Scorsese"]
    },
    {
        question: "Qual é o seu ator ou atriz favorito?",
        options: ["Leonardo DiCaprio", "Meryl Streep", "Robert De Niro", "Scarlett Johansson"]
    },
    {
        question: "Qual é o seu filme favorito de todos os tempos?",
        options: ["O Poderoso Chefão", "Pulp Fiction", "Forrest Gump", "Titanic"]
    }
];
let currentQuestionIndex = 0;
const answers = [];

function showNextQuestion() {
    const contentDiv = document.getElementById('content');
    if (currentQuestionIndex < questions.length) {
        const questionObj = questions[currentQuestionIndex];
        const optionsHtml = questionObj.options.map(option => `
            <label>
                <input type="checkbox" name="options" value="${option}"> ${option}
            </label><br>
        `).join('');
        contentDiv.innerHTML = `
            <h1>${questionObj.question}</h1>
            ${optionsHtml}
            ${currentQuestionIndex > 0 ? '<button class="back-button" onclick="goBack()">Voltar</button>' : ''}
            <button class="next-button" onclick="submitAnswer()">Enviar</button>
        `;
    } else {
        contentDiv.innerHTML = `
            <h1>Obrigado por responder!</h1>
            <p>Baseado nas suas respostas, recomendamos assistir a...</p>
        `;
    }
}

function submitAnswer() {
    const selectedOptions = Array.from(document.querySelectorAll('input[name="options"]:checked'))
        .map(checkbox => checkbox.value);
    answers[currentQuestionIndex] = selectedOptions;
    currentQuestionIndex++;
    showNextQuestion();
}

function goBack() {
    currentQuestionIndex--;
    showNextQuestion();
}

// Initialize the first question
showNextQuestion();