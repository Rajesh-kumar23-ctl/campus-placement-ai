/**
 * Final Interview Report Controller
 */

document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuth()) return;

    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get("id");

    if (!sessionId) {
        showToast("error", "No interview session ID provided.");
        setTimeout(() => window.location.href = "/pages/interview.html", 1000);
        return;
    }

    try {
        const session = await window.api.getInterviewSession(sessionId);
        renderReport(session);
    } catch (err) {
        console.error("Error loading interview report:", err);
        showToast("error", "Unable to load interview report.");
    }
});

function renderReport(s) {
    document.getElementById("report-role").textContent = `${s.target_role} (${s.interview_type.toUpperCase()})`;
    document.getElementById("report-score-number").textContent = `${Math.round(s.score)}%`;

    // Metrics breakdown
    document.getElementById("metric-tech").textContent = `${s.technical_accuracy || 7.5}/10`;
    document.getElementById("metric-content").textContent = `${s.content || 7.0}/10`;
    document.getElementById("metric-relevance").textContent = `${s.relevance || 8.0}/10`;
    document.getElementById("metric-clarity").textContent = `${s.clarity || 7.5}/10`;
    document.getElementById("metric-comm").textContent = `${s.communication || 7.5}/10`;

    // Summary assessment
    if (s.feedback) {
        document.getElementById("report-summary-text").textContent = s.feedback;
    }

    // Strengths
    const strengthsEl = document.getElementById("report-strengths-list");
    if (strengthsEl && s.strengths) {
        strengthsEl.innerHTML = s.strengths.map(st => `<li>${st}</li>`).join("");
    }

    // Areas to Improve
    const improveEl = document.getElementById("report-improvements-list");
    if (improveEl && s.improvements) {
        improveEl.innerHTML = s.improvements.map(im => `<li>${im}</li>`).join("");
    }

    // Topics to Revise
    const topicsEl = document.getElementById("report-topics-list");
    if (topicsEl && s.topics_to_revise) {
        topicsEl.innerHTML = s.topics_to_revise.map(t => `<span class="badge badge-warning" style="margin: 4px; font-size: 0.85rem;">${t}</span>`).join("");
    }

    // Full Q&A Transcript
    const transcriptEl = document.getElementById("report-transcript-list");
    if (transcriptEl && s.questions) {
        transcriptEl.innerHTML = s.questions.map((q, idx) => `
            <div class="card" style="margin-bottom: 16px; padding: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span class="badge badge-primary">Q${q.question_number} • ${q.category}</span>
                    <span style="font-weight: 700; color: var(--success);">${q.answer ? Math.round(q.answer.overall_score) + '%' : 'N/A'}</span>
                </div>
                <h4 style="font-size: 1.05rem; margin-bottom: 12px; color: #ffffff;">${q.question}</h4>
                <div style="background: var(--bg-surface); padding: 14px; border-radius: var(--radius-md); font-size: 0.95rem; line-height: 1.5; color: var(--text-primary); margin-bottom: 12px;">
                    <strong>Your Response:</strong> ${q.answer ? q.answer.answer : 'No answer submitted'}
                </div>
                ${q.answer && q.answer.feedback ? `
                    <div style="font-size: 0.85rem; color: var(--info);">
                        <strong>Feedback:</strong> ${q.answer.feedback}
                    </div>
                ` : ''}
            </div>
        `).join("");
    }
}
