const API_URL = "http://localhost:8000";

document.addEventListener('DOMContentLoaded', () => {
    const starContainer = document.getElementById('starContainer');
    const stars = starContainer.querySelectorAll('.star');
    const ratingInput = document.getElementById('ratingValue');
    const form = document.getElementById('feedbackForm');
    const submitBtn = document.getElementById('submitBtn');
    const responseContainer = document.getElementById('responseContainer');
    const responseText = document.getElementById('responseText');

    // Star Rating Logic
    stars.forEach(star => {
        star.addEventListener('click', () => {
            const value = parseInt(star.getAttribute('data-value'));
            ratingInput.value = value;
            updateStars(value);
        });
    });

    function updateStars(value) {
        stars.forEach(star => {
            const starValue = parseInt(star.getAttribute('data-value'));
            if (starValue <= value) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    // Form Submission
    submitBtn.addEventListener('click', async (e) => {
        // Prevent default behavior just in case
        e.preventDefault();

        const rating = ratingInput.value;
        const review = document.getElementById('review').value;

        if (!rating) {
            alert("Please select a star rating.");
            return;
        }

        // UI State: Loading
        submitBtn.disabled = true;
        submitBtn.textContent = "Submitting...";
        responseContainer.classList.add('hidden');

        try {
            const response = await fetch(`${API_URL}/reviews`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rating: parseInt(rating),
                    review: review
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Success State
                responseContainer.classList.remove('hidden');
                responseText.textContent = data.ai_response;

                // Show success state on button
                submitBtn.textContent = "Feedback Sent!";
                submitBtn.style.backgroundColor = "#059669"; // Green
            } else {
                alert("Error: " + (data.detail || "Unknown error"));
                submitBtn.disabled = false;
                submitBtn.textContent = "Submit Feedback";
            }
        } catch (error) {
            console.error('Error:', error);
            alert("Failed to connect to the server.");
            submitBtn.disabled = false;
            submitBtn.textContent = "Submit Feedback";
        }
    });
});
