/**
 * Dashboard JavaScript Controller
 */

document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuth()) return;

    await loadDashboard();
    await checkAiStatus();
});

function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 17) return "Good Afternoon";
    return "Good Evening";
}

async function loadDashboard() {
    try {
        const data = await window.api.getDashboard();

        // 1. Greeting
        const greetingEl = document.getElementById("greeting-text");
        if (greetingEl) {
            greetingEl.textContent = `${getGreeting()}, ${data.user_name} 👋`;
        }

        const roleBadge = document.getElementById("target-role-badge");
        if (roleBadge) {
            roleBadge.textContent = data.target_role;
        }

        // 2. Readiness Metric
        const readinessEl = document.getElementById("readiness-percentage");
        if (readinessEl) {
            readinessEl.textContent = `${Math.round(data.readiness_percentage)}%`;
        }

        const ringProgress = document.getElementById("readiness-ring");
        if (ringProgress) {
            const circumference = 2 * Math.PI * 45; // r=45
            const offset = circumference - (data.readiness_percentage / 100) * circumference;
            ringProgress.style.strokeDasharray = `${circumference} ${circumference}`;
            ringProgress.style.strokeDashoffset = offset;
        }

        // 3. Category Metrics
        const cat = data.category_scores || {};
        updateDomainCard("aptitude", cat.aptitude || 0);
        updateDomainCard("gd", cat.gd || 0);
        updateDomainCard("technical", cat.technical || 0);
        updateDomainCard("hr", cat.hr || 0);
        updateDomainCard("communication", cat.communication || 0);

        // 4. Streak & Sessions
        const streakEl = document.getElementById("streak-count");
        if (streakEl) streakEl.textContent = `${data.streak_days} Days`;

        const sessionsEl = document.getElementById("total-sessions-count");
        if (sessionsEl) sessionsEl.textContent = data.total_sessions;

        // 5. Recent Activity List
        renderRecentActivities(data.recent_activities);

        // 6. Weak Areas & Recommendations
        renderRecommendations(data.recommendations, data.weak_areas);

    } catch (err) {
        console.error("Dashboard load error:", err);
        showToast("error", "Unable to load dashboard data. Please try again.");
    }
}

function updateDomainCard(domainKey, score) {
    const scoreEl = document.getElementById(`score-${domainKey}`);
    const fillEl = document.getElementById(`fill-${domainKey}`);
    if (scoreEl) scoreEl.textContent = `${Math.round(score)}%`;
    if (fillEl) {
        fillEl.style.width = `${Math.min(100, Math.max(0, score))}%`;
        if (score >= 75) fillEl.style.background = "var(--success)";
        else if (score >= 60) fillEl.style.background = "var(--primary)";
        else fillEl.style.background = "var(--warning)";
    }
}

function renderRecentActivities(activities) {
    const listEl = document.getElementById("recent-activity-list");
    if (!listEl) return;

    if (!activities || activities.length === 0) {
        listEl.innerHTML = `
            <div class="empty-state" style="padding: 30px 0;">
                <p class="empty-state-text" style="margin-bottom: 0;">No sessions recorded yet. Start your first practice below!</p>
            </div>
        `;
        return;
    }

    listEl.innerHTML = activities.map(act => {
        let badgeClass = "badge-primary";
        let icon = "🎯";
        if (act.type === "gd") { badgeClass = "badge-secondary"; icon = "👥"; }
        else if (act.type === "interview") { badgeClass = "badge-success"; icon = "🎙️"; }
        else if (act.type === "simulation") { badgeClass = "badge-warning"; icon = "🚀"; }

        const dateStr = new Date(act.date).toLocaleDateString("en-US", { month: "short", day: "numeric" });

        return `
            <div class="activity-item">
                <div class="activity-left">
                    <div class="activity-icon">${icon}</div>
                    <div>
                        <div class="activity-title">${act.title}</div>
                        <div class="activity-meta">${dateStr}</div>
                    </div>
                </div>
                <div class="activity-score" style="color: ${act.score >= 70 ? 'var(--success)' : 'var(--text-primary)'}">
                    ${Math.round(act.score)}%
                </div>
            </div>
        `;
    }).join("");
}

function renderRecommendations(recommendations, weakAreas) {
    const container = document.getElementById("recommendations-container");
    if (!container) return;

    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = `<p class="text-muted">Take your first aptitude test or mock interview to receive personalized recommendations!</p>`;
        return;
    }

    let weakAreasHtml = "";
    if (weakAreas && weakAreas.length > 0) {
        weakAreasHtml = `
            <div style="margin-bottom: 16px; padding: 12px 16px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: var(--radius-md);">
                <div style="font-size: 0.85rem; font-weight: 700; color: #f87171; margin-bottom: 4px;">PRIORITY WEAK AREAS DETECTED:</div>
                <div style="font-size: 0.85rem; color: var(--text-primary);">${weakAreas.join(" • ")}</div>
            </div>
        `;
    }

    const recsHtml = recommendations.map(rec => `
        <div class="rec-item">
            <div class="rec-title">
                <span class="badge ${rec.priority === 'high' ? 'badge-danger' : 'badge-warning'}">${rec.priority}</span>
                ${rec.category} Focus
            </div>
            <div class="rec-desc">${rec.insight}</div>
            <ul class="rec-actions">
                ${rec.action_items.map(action => `<li>${action}</li>`).join("")}
            </ul>
        </div>
    `).join("");

    container.innerHTML = weakAreasHtml + recsHtml;
}

async function checkAiStatus() {
    try {
        const status = await window.api.getAiStatus();
        const banner = document.getElementById("ai-status-banner");
        if (banner) {
            if (!status.is_configured) {
                banner.style.display = "flex";
                banner.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    <span><strong>Practice Mode:</strong> AI provider is not configured in .env. Full offline preparation mode active with rich question banks & heuristic evaluators.</span>
                `;
            } else {
                banner.style.display = "none";
            }
        }
    } catch {
        // ignore
    }
}
