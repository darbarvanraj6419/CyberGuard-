document.getElementById('password-input').addEventListener('input', function(e) {
    const pw = e.target.value;
    let score = 0;
    
    // Checks
    const len = pw.length >= 8;
    const up = /[A-Z]/.test(pw);
    const low = /[a-z]/.test(pw);
    const num = /[0-9]/.test(pw);
    const sym = /[^A-Za-z0-9]/.test(pw);
    
    // Update UI Checklist
    const updateCheck = (id, condition) => {
        const el = document.getElementById(id);
        if(condition) {
            el.innerHTML = '<i class="fas fa-check text-success"></i> ' + el.innerText.trim();
            score += 20;
        } else {
            el.innerHTML = '<i class="fas fa-times text-danger"></i> ' + el.innerText.trim();
        }
    };

    updateCheck('req-len', len);
    updateCheck('req-up', up);
    updateCheck('req-low', low);
    updateCheck('req-num', num);
    updateCheck('req-sym', sym);

    // Update Bar
    const bar = document.getElementById('strength-bar');
    const text = document.getElementById('strength-text');
    bar.style.width = score + '%';
    
    if(score === 0) { bar.className = 'progress-bar'; text.innerText = 'Strength: None'; text.style.color = 'white';}
    else if(score <= 40) { bar.className = 'progress-bar bg-danger'; text.innerText = 'Strength: Weak'; text.style.color = '#dc3545'; }
    else if(score <= 80) { bar.className = 'progress-bar bg-warning'; text.innerText = 'Strength: Medium'; text.style.color = '#ffc107'; }
    else { bar.className = 'progress-bar bg-success'; text.innerText = 'Strength: Strong'; text.style.color = '#198754'; }
});