document.addEventListener('DOMContentLoaded', function() {
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatWindow = document.getElementById('chat-window');

    chatToggleBtn.addEventListener('click', function() {
        if (chatWindow.style.display === 'none') {
            chatWindow.style.display = 'block';
        } else {
            chatWindow.style.display = 'none';
        }
    });
});
