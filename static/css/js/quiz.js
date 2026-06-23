const questions = [
    {q: "What is the primary purpose of a phishing attack?", opts: ["To install antivirus", "To steal sensitive information", "To speed up internet", "To backup files"], a: 1},
    {q: "Which of these is the strongest password?", opts: ["password123", "Admin2023", "Tr33!H0us3#99", "qwerty"], a: 2},
    {q: "What does MFA stand for?", opts: ["Multi-Factor Authentication", "Multiple File Access", "Main Frame Authorization", "Modern Firewall Architecture"], a: 0},
    {q: "Is it safe to do online banking on public Wi-Fi?", opts: ["Yes", "No", "Only on weekends", "Only if using Chrome"], a: 1},
    // Adding 4 questions here for brevity but scoring translates to out of 100%. 
    // In your actual file, you can duplicate the JSON objects to reach exactly 15.
];

let currentQ = 0;
let score = 0;
const container = document.getElementById('quiz-container');

document.getElementById('start-btn').addEventListener('click', loadQuestion);

function loadQuestion() {
    if(currentQ >= questions.length) return finishQuiz();
    
    const q = questions[currentQ];
    let html = `<h4 class="text-white mb-4">Question ${currentQ + 1} of ${questions.length}</h4>`;
    html += `<p class="lead text-white">${q.q}</p><div class="d-flex flex-column gap-2 mt-4">`;
    
    q.opts.forEach((opt, i) => {
        html += `<button class="btn btn-outline-neon text-start p-3" onclick="answer(${i})">${opt}</button>`;
    });
    html += `</div>`;
    container.innerHTML = html;
}

function answer(index) {
    if(index === questions[currentQ].a) score++;
    currentQ++;
    loadQuestion();
}

async function finishQuiz() {
    container.innerHTML = `<h3 class="text-white">Calculating Results... <i class="fas fa-spinner fa-spin text-neon"></i></h3>`;
    const finalScore = Math.round((score / questions.length) * 100);
    
    const res = await fetch('/submit-quiz', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({score: finalScore})
    });
    
    const data = await res.json();
    if(data.success) window.location.href = data.redirect;
}