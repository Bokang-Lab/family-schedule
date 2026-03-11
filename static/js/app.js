// ─── 모달 ───
function openModal(title, bodyHtml) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = bodyHtml;
    document.getElementById('modal').classList.remove('hidden');
    document.getElementById('modal-overlay').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('modal').classList.add('hidden');
    document.getElementById('modal-overlay').classList.add('hidden');
    document.body.style.overflow = '';
}

// ─── 토스트 ───
function showToast(msg, isError) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = 'toast' + (isError ? ' error' : '');
    setTimeout(() => toast.classList.add('hidden'), 2500);
}

// ─── ESC로 모달 닫기 ───
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
});
