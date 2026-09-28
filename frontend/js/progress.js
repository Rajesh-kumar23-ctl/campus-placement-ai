/**
 * Progress & Performance Analytics Controller (Chart.js)
 */

let performanceChart = null;
let radarChart = null;
let activityChart = null;

document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuth()) return;

    await loadAnalytics();
});

async function loadAnalytics() {
    try {
        const data = await window.api.getProgress();

        // 1. Metric Cards
        document.getElementById("stat-total-tests").textContent = data.total_tests;
        document.getElementById("stat-total-interviews").textContent = data.total_interviews;
        document.getElementById("stat-total-gd").textContent = data.total_gd_sessions;
        document.getElementById("stat-total-sims").textContent = data.total_simulations;

        document.getElementById("stat-avg-apt").textContent = `${Math.round(data.average_aptitude)}%`;
        document.getElementById("stat-avg-gd").textContent = `${Math.round(data.average_gd)}%`;
        document.getElementById("stat-avg-int").textContent = `${Math.round(data.average_interview)}%`;

        document.getElementById("stat-best-skill").textContent = data.best_skill;
        document.getElementById("stat-weakest-skill").textContent = data.weakest_skill;

        // 2. Charts
        renderPerformanceChart(data.performance_over_time);
        renderRadarChart(data.skill_radar);
        renderActivityChart(data.practice_activity);

        // 3. Recommendations
        renderRecommendations(data.recommendations, data.weak_areas);

    } catch (err) {
        console.error("Analytics load error:", err);
        showToast("error", "Unable to load progress analytics.");
    }
}

function renderPerformanceChart(timeline) {
    const ctx = document.getElementById("performanceOverTimeChart")?.getContext("2d");
    if (!ctx) return;

    if (performanceChart) performanceChart.destroy();

    const labels = timeline.map(t => t.label);
    const scores = timeline.map(t => t.score);

    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Performance Score %',
                data: scores,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.12)',
                fill: true,
                tension: 0.35,
                pointBackgroundColor: '#38bdf8',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#f8fafc',
                    bodyColor: '#38bdf8',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 10
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                }
            }
        }
    });
}

function renderRadarChart(radarData) {
    const ctx = document.getElementById("skillRadarChart")?.getContext("2d");
    if (!ctx) return;

    if (radarChart) radarChart.destroy();

    const labels = Object.keys(radarData);
    const values = Object.values(radarData);

    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Preparation Level %',
                data: values,
                backgroundColor: 'rgba(6, 182, 212, 0.2)',
                borderColor: '#06b6d4',
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#ffffff',
                pointHoverRadius: 6,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
                    grid: { color: 'rgba(255, 255, 255, 0.08)' },
                    pointLabels: {
                        color: '#f8fafc',
                        font: { family: 'Outfit', size: 12, weight: '600' }
                    },
                    ticks: {
                        display: false,
                        min: 0,
                        max: 100
                    }
                }
            }
        }
    });
}

function renderActivityChart(activity) {
    const ctx = document.getElementById("practiceActivityChart")?.getContext("2d");
    if (!ctx) return;

    if (activityChart) activityChart.destroy();

    const labels = activity.map(a => a.day);
    const counts = activity.map(a => a.count);

    activityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Sessions Completed',
                data: counts,
                backgroundColor: 'rgba(99, 102, 241, 0.7)',
                hoverBackgroundColor: '#6366f1',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1, color: '#94a3b8' },
                    grid: { color: 'rgba(255, 255, 255, 0.06)' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

function renderRecommendations(recommendations, weakAreas) {
    const container = document.getElementById("progress-recs-container");
    if (!container) return;

    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = `<p class="text-muted">Keep practicing to generate updated diagnostic insights.</p>`;
        return;
    }

    container.innerHTML = recommendations.map(rec => `
        <div class="card" style="margin-bottom: 16px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="badge ${rec.priority === 'high' ? 'badge-danger' : 'badge-warning'}">${rec.priority.toUpperCase()} PRIORITY</span>
                <span style="font-weight: 700; color: var(--secondary);">${rec.category}</span>
            </div>
            <p style="font-size: 0.92rem; color: #ffffff; margin-bottom: 10px;">${rec.insight}</p>
            <ul style="list-style: disc inside; font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6;">
                ${rec.action_items.map(a => `<li>${a}</li>`).join("")}
            </ul>
        </div>
    `).join("");
}
