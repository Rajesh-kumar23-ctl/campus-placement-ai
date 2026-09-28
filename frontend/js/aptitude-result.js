/**
 * Aptitude Test Results & Review Controller
 */

document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuth()) return;

    const urlParams = new URLSearchParams(window.location.search);
    const attemptId = urlParams.get("id");

    if (!attemptId) {
        showToast("error", "No attempt ID specified.");
        setTimeout(() => window.location.href = "/pages/aptitude.html", 1000);
        return;
    }

    try {
        const result = await window.api.getAptitudeResult(attemptId);
        renderResult(result);
    } catch (err) {
        console.error("Error loading result:", err);
        showToast("error", "Failed to load test results.");
    }
});

function renderResult(result) {
    // 1. Hero Score
    document.getElementById("res-score-number").textContent = `${Math.round(result.score)}%`;
    document.getElementById("res-accuracy").textContent = `${result.accuracy}%`;
    document.getElementById("res-correct").textContent = `${result.correct_answers} / ${result.total_questions}`;
    document.getElementById("res-incorrect").textContent = result.incorrect_answers;

    const mins = Math.floor(result.time_taken / 60);
    const secs = result.time_taken % 60;
    document.getElementById("res-time").textContent = `${mins}m ${secs}s`;

    // 2. Category Breakdown
    const catContainer = document.getElementById("category-breakdown-container");
    if (catContainer && result.category_breakdown) {
        catContainer.innerHTML = Object.entries(result.category_breakdown).map(([cat, stat]) => {
            const pct = stat.total > 0 ? Math.round((stat.correct / stat.total) * 100) : 0;
            return `
                <div class="card" style="padding: 16px; text-align: center;">
                    <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 6px;">
                        ${cat.replace('_', ' ')}
                    </div>
                    <div style="font-family: var(--font-heading); font-size: 1.4rem; font-weight: 800; color: ${pct >= 70 ? 'var(--success)' : 'var(--warning)'};">
                        ${stat.correct} / ${stat.total} (${pct}%)
                    </div>
                </div>
            `;
        }).join("");
    }

    // 3. Question Reviews
    const reviewList = document.getElementById("questions-review-list");
    if (reviewList && result.review) {
        reviewList.innerHTML = result.review.map((item, idx) => {
            const isCorrect = item.is_correct;
            return `
                <div class="review-item-card ${isCorrect ? 'correct' : 'incorrect'}">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                        <span class="badge ${isCorrect ? 'badge-success' : 'badge-danger'}">
                            ${isCorrect ? '✓ Correct' : '✕ Incorrect'}
                        </span>
                        <span style="font-size: 0.85rem; color: var(--text-muted);">Question ${idx + 1} • ${item.category}</span>
                    </div>

                    <div style="font-size: 1.1rem; font-weight: 600; color: #ffffff; margin-bottom: 16px;">
                        ${item.question}
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; margin-bottom: 16px;">
                        <div style="padding: 10px 14px; background: var(--bg-surface); border-radius: var(--radius-sm); border-left: 3px solid ${isCorrect ? 'var(--success)' : 'var(--danger)'};">
                            <span style="font-size: 0.8rem; color: var(--text-muted); display: block;">Your Selection:</span>
                            <span style="font-weight: 600; color: ${item.selected_answer ? '#ffffff' : 'var(--text-muted)'};">
                                ${item.selected_answer || "Not Answered"}
                            </span>
                        </div>
                        <div style="padding: 10px 14px; background: var(--bg-surface); border-radius: var(--radius-sm); border-left: 3px solid var(--success);">
                            <span style="font-size: 0.8rem; color: var(--text-muted); display: block;">Correct Answer:</span>
                            <span style="font-weight: 600; color: var(--success);">${item.correct_answer}</span>
                        </div>
                    </div>

                    <div class="review-explanation">
                        <strong style="color: var(--info); display: block; margin-bottom: 4px;">Explanation:</strong>
                        ${item.explanation}
                    </div>

                    ${item.shortcut ? `
                        <div class="review-shortcut">
                            <strong>⚡ Shortcut / Quick Formula:</strong> ${item.shortcut}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join("");
    }
}
