document.getElementById('analyze-btn').addEventListener('click', async () => {
    const msg = document.getElementById('scam-input').value;
    if(!msg) return alert('Please enter a message.');
    
    const res = await fetch('/analyze-message', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg})
    });
    
    const data = await res.json();
    document.getElementById('result-box').classList.remove('d-none');
    
    const levelEl = document.getElementById('risk-level');
    levelEl.innerText = data.level;
    levelEl.className = data.level === 'High' ? 'text-danger' : (data.level === 'Medium' ? 'text-warning' : 'text-success');
    
    document.getElementById('risk-score').innerText = data.score;
    
    const threatList = data.threats.map(t => `<li><i class="fas fa-exclamation-triangle"></i> ${t}</li>`).join('');
    document.getElementById('threat-list').innerHTML = `<ul>${threatList}</ul>`;
    
    document.getElementById('recommendation').innerText = data.recommendation;
});