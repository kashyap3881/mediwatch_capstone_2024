// Initialize all collapse buttons
document.querySelectorAll('.collapse-btn').forEach(button => {
    // Set initial state to open
    button.classList.add('active');
    const content = button.nextElementSibling;
    content.style.maxHeight = content.scrollHeight + "px";

    // Add click handler
    button.addEventListener('click', () => {
        button.classList.toggle('active');
        const content = button.nextElementSibling;
        
        if (button.classList.contains('active')) {
            content.style.maxHeight = content.scrollHeight + "px";
        } else {
            content.style.maxHeight = null;
        }
    });
});