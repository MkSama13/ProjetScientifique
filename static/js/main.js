function deleteReponse(event, reponseId) {
    event.preventDefault();
    const form = event.target;
    const url = form.action;
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const replyElement = document.getElementById(`reponse-${data.reponse_id}`);
            if (replyElement) {
                replyElement.style.transition = 'opacity 0.5s ease-out';
                replyElement.style.opacity = '0';
                setTimeout(() => {
                    replyElement.remove();
                }, 500);
            }
        } else {
            console.error('Failed to delete reply:', data.error);
        }
    })
    .catch(error => console.error('Error deleting reply:', error));
}