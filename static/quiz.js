const questions = [
    {
        question:"Como você está s sentindo hoje?",
        options:["Feliz","Triste","Ansioso","Estressado","Cansado"],
        type:"single"
    },
    {
        question: "Qual é o seu gênero de filme favorito?",
        options: ["Ação", "Comédia", "Drama", "Terror", "Aventura", "Thriller","Crime", "Romance", 
            "Ficção Científica", "Fantasia", "Animação", "Documentário", "Familia", "Mistério", "História",
             "Biografia", "Musical", "Esportes", "Desastre", "Velho-Oeste", "Guerra", "Super-Herói", "Suspense"],
        type: "multiple"
    },
    {
        Question: "Como deseja assistir o filme?",
        options:["Sozinho","Família","Amigos","Namorado(a)"],
        type:"single"
    },
   {
    question: "Classificação indicativa do filme é importante para você?",
    options: ["Livre", "10 anos", "12 anos", "14 anos", "16 anos", "18 anos"],
    type: "single"
   },

    
];
let currentQuestionIndex = 0;
const answers = [];

function showNextQuestion() {
    const contentDiv = document.getElementById('content');
    if (currentQuestionIndex < questions.length) {
        const questionObj = questions[currentQuestionIndex];
        const inputType = questionObj.type === "multiple" ? "checkbox" : "radio";
        const optionsHtml = questionObj.options.map(option => `
            <label>
                <input type="${inputType}" name="options" value="${option}"> ${option}
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
    const selectedOptions = Array.from(document.querySelectorAll('input[name="options"]:checked, input[name="options"]:checked'))
        .map(input => input.value);
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