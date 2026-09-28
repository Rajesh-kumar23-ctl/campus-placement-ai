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

        // Load Drive Placement Materials
        const materialsListEl = document.getElementById("company-drive-materials-list");
        const hubLinkEl = document.getElementById("company-materials-hub-link");
        if (materialsListEl) {
            try {
                // Try searching by company name
                const shortName = c.name.split(" ")[0].replace(/[^a-zA-Z]/g, '');
                if (hubLinkEl) {
                    hubLinkEl.href = `/pages/materials.html?company=${encodeURIComponent(shortName)}`;
                }
                const mats = await window.api.getCompanyMaterials(shortName);
                if (mats && mats.length > 0) {
                    materialsListEl.innerHTML = mats.slice(0, 6).map(m => `
                        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 14px; display: flex; flex-direction: column; justify-content: space-between;">
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <span style="font-size: 0.72rem; font-weight: 700; color: #818cf8; text-transform: uppercase;">${m.format}</span>
                                    <span style="font-size: 0.7rem; color: var(--text-muted);">${m.category}</span>
                                </div>
                                <h5 style="font-size: 0.92rem; color: #f8fafc; margin-bottom: 6px; line-height: 1.3;">${m.title}</h5>
                            </div>
                            <div style="display: flex; gap: 8px; margin-top: 12px;">
                                <a href="${m.view_url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm" style="flex: 1; text-align: center; font-size: 0.78rem; padding: 5px 8px;">
                                    View in Drive ↗
                                </a>
                                <a href="${m.download_url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" style="padding: 5px 10px; font-size: 0.78rem;" title="Download File">
                                    ⬇️
                                </a>
                            </div>
                        </div>
                    `).join("");
                } else {
                    materialsListEl.innerHTML = `
                        <div style="grid-column: 1/-1; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px;">
                            <p style="color: var(--text-muted); font-size: 0.9rem; margin: 0;">
                                Comprehensive test materials and mock exams for <b>${c.name}</b> are ready in our central repository.
                                <a href="/pages/materials.html" style="color: #818cf8; font-weight: 600; margin-left: 6px;">Browse All Placement Materials ➔</a>
                            </p>
                        </div>
                    `;
                }
            } catch (mErr) {
                console.warn("Could not load company materials:", mErr);
                materialsListEl.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem;">Check <a href="/pages/materials.html" style="color:#818cf8;">Materials Hub</a> for all drive resources.</p>`;
            }
        }

    } catch (err) {
        showToast("error", "Unable to load company details.");
    }
}
