/**
 * Companies Directory & Detail Controller
 */

document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuth()) return;

    // Check if on directory page or detail page
    const urlParams = new URLSearchParams(window.location.search);
    const companyId = urlParams.get("id");

    if (companyId) {
        await loadCompanyDetail(companyId);
    } else {
        await loadCompaniesList();
    }
});

async function loadCompaniesList() {
    const grid = document.getElementById("companies-grid");
    if (!grid) return;

    grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px;"><span class="spinner"></span> Loading companies...</div>`;

    try {
        const companies = await window.api.getCompanies();
        renderCompanies(companies);

        // Search bar
        const searchInput = document.getElementById("company-search-input");
        if (searchInput) {
            let debounceTimer;
            searchInput.addEventListener("input", () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(async () => {
                    const filtered = await window.api.getCompanies(searchInput.value.trim());
                    renderCompanies(filtered);
                }, 300);
            });
        }

    } catch (err) {
        grid.innerHTML = `<p class="text-danger" style="grid-column: 1/-1; text-align: center;">Failed to load companies.</p>`;
    }
}

function renderCompanies(companies) {
    const grid = document.getElementById("companies-grid");
    if (!grid) return;

    if (!companies || companies.length === 0) {
        grid.innerHTML = `<p class="text-muted" style="grid-column: 1/-1; text-align: center;">No matching companies found.</p>`;
        return;
    }

    grid.innerHTML = companies.map(c => `
        <div class="company-card">
            <div>
                <div class="company-badge-header">
                    <span class="badge badge-primary">${c.tier}</span>
                    <span style="font-size: 0.8rem; color: var(--text-muted);">${c.hiring_pattern?.rounds?.length || 3} Rounds</span>
                </div>
                <h3 class="company-title">${c.name}</h3>
                <p class="company-desc">${c.description}</p>
                <div class="company-prep-tags">
                    ${(c.preparation_areas || []).slice(0, 3).map(p => `<span class="company-tag">${p.slice(0, 25)}...</span>`).join("")}
                </div>
            </div>
            <a href="/pages/company-detail.html?id=${c.id}" class="btn btn-outline btn-sm" style="width: 100%; margin-top: 12px;">
                View Preparation Guide ➔
            </a>
        </div>
    `).join("");
}

async function loadCompanyDetail(id) {
    try {
        const c = await window.api.getCompany(id);

        document.getElementById("company-detail-name").textContent = c.name;
        document.getElementById("company-detail-tier").textContent = c.tier;
        document.getElementById("company-detail-desc").textContent = c.description;

        // Hiring Pattern
        const pattern = c.hiring_pattern || {};
        document.getElementById("pattern-eligibility").textContent = pattern.eligibility || "Standard academic criteria";

        const roundsList = document.getElementById("pattern-rounds-list");
        if (roundsList && pattern.rounds) {
            roundsList.innerHTML = pattern.rounds.map((r, i) => `
                <li style="margin-bottom: 8px;">
                    <strong style="color: var(--secondary);">Round ${i + 1}:</strong> ${r}
                </li>
            `).join("");
        }

        const rolesList = document.getElementById("pattern-roles-list");
        if (rolesList && pattern.roles) {
            rolesList.innerHTML = pattern.roles.map(role => `<span class="badge badge-secondary" style="margin: 3px;">${role}</span>`).join("");
        }

        // Technical Topics
        const techList = document.getElementById("company-tech-topics");
        if (techList && c.technical_topics) {
            techList.innerHTML = c.technical_topics.map(t => `<li>${t}</li>`).join("");
        }

        // HR Topics
        const hrList = document.getElementById("company-hr-topics");
        if (hrList && c.hr_topics) {
            hrList.innerHTML = c.hr_topics.map(h => `<li>${h}</li>`).join("");
        }

        // Sample Questions
        const samplesList = document.getElementById("company-sample-questions");
        if (samplesList && c.sample_questions) {
            samplesList.innerHTML = c.sample_questions.map(q => `
                <div class="card" style="margin-bottom: 12px; padding: 18px;">
                    <span class="badge badge-primary" style="margin-bottom: 8px;">${q.type.toUpperCase()}</span>
                    <h4 style="font-size: 1rem; color: #ffffff; margin-bottom: 8px;">${q.question}</h4>
                    <p style="font-size: 0.85rem; color: var(--info); margin: 0;">${q.concept || q.explanation || ''}</p>
                </div>
            `).join("");
        }

    } catch (err) {
        showToast("error", "Unable to load company details.");
    }
}
