const API_URL = ""; // Relative URL (Same Domain)

document.addEventListener('DOMContentLoaded', () => {
    const listContainer = document.getElementById('reviewsList');
    const refreshBtn = document.getElementById('refreshBtn');
    const countSpan = document.getElementById('reviewCount');

    async function fetchReviews() {
        listContainer.innerHTML = '<p style="text-align: center; color: #6b7280;">Refreshing...</p>';
        try {
            const response = await fetch(`${API_URL}/admin/reviews`);
            const json = await response.json();

            // Expected { count: number, data: array }
            const reviews = json.data;
            countSpan.textContent = json.count;

            renderReviews(reviews);
        } catch (error) {
            console.error('Error fetching reviews:', error);
            listContainer.innerHTML = '<p style="text-align: center; color: red;">Failed to load reviews. Is backend running?</p>';
        }
    }

    function renderReviews(reviews) {
        listContainer.innerHTML = '';

        if (reviews.length === 0) {
            listContainer.innerHTML = '<p style="text-align: center; color: #6b7280;">No reviews yet.</p>';
            return;
        }

        reviews.forEach(review => {
            // Create review card
            const card = document.createElement('div');
            card.className = 'review-item';

            const date = new Date(review.created_at).toLocaleString();

            card.innerHTML = `
                <div class="review-header">
                    <span class="rating-badge">${review.rating} / 5</span>
                    <span style="color: #6b7280; font-size: 0.85rem;">${date}</span>
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Review:</strong>
                    <p style="margin: 0.25rem 0;">${escapeHtml(review.review)}</p>
                </div>
                <div class="insight-box">
                    <div style="margin-bottom: 0.5rem;">
                        <div class="insight-title">AI Summary</div>
                        <div>${review.summary || "Pending..."}</div>
                    </div>
                    <div>
                        <div class="insight-title">Recommended Action</div>
                        <div style="color: #059669; font-weight: 500;">${review.recommended_action || "Pending..."}</div>
                    </div>
                </div>
            `;
            listContainer.appendChild(card);
        });
    }

    // Helper to prevent XSS
    function escapeHtml(text) {
        if (!text) return "";
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Init
    fetchReviews();

    // Event Listeners
    refreshBtn.addEventListener('click', fetchReviews);
});
