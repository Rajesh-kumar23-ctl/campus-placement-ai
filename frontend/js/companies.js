/**
 * Companies Directory & Real-Time Job Hunts Controller
 * Google Jobs Engine & Official Career Portals Integration
 */

document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuth()) return;

    // Check if on directory page or detail page
    const urlParams = new URLSearchParams(window.location.search);
    const companyId = urlParams.get("id");

    if (companyId) {
        await loadCompanyDetail(companyId);
    } else {
        await initCompaniesPage();
    }
});

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function initCompaniesPage() {
    // Wire up tab switching
    const tabTracks = document.getElementById("tab-company-tracks");
    const tabLiveJobs = document.getElementById("tab-live-jobs");
    const viewTracks = document.getElementById("company-tracks-view");
    const viewLiveJobs = document.getElementById("live-jobs-view");

    if (tabTracks && tabLiveJobs && viewTracks && viewLiveJobs) {
        tabTracks.addEventListener("click", () => {
            tabTracks.classList.add("active");
            tabLiveJobs.classList.remove("active");
            viewTracks.style.display = "block";
            viewLiveJobs.style.display = "none";
        });

        tabLiveJobs.addEventListener("click", () => {
            tabLiveJobs.classList.add("active");
            tabTracks.classList.remove("active");
            viewTracks.style.display = "none";
            viewLiveJobs.style.display = "block";
            loadLiveJobs();
        });

        // Check if url specifies tab=jobs
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get("tab") === "jobs") {
            tabLiveJobs.click();
        }
    }

    // Initialize company tracks
    await loadCompaniesList();

    // Wire up live jobs search bar & filters
    const btnSearchJobs = document.getElementById("btn-search-jobs");
    const inputRole = document.getElementById("jobs-search-role");
    const selectCompany = document.getElementById("jobs-filter-company");
    const selectLocation = document.getElementById("jobs-filter-location");

    if (btnSearchJobs) {
        btnSearchJobs.addEventListener("click", () => loadLiveJobs());
    }

    if (inputRole) {
        inputRole.addEventListener("keydown", (e) => {
            if (e.key === "Enter") loadLiveJobs();
        });
    }

    if (selectCompany) {
        selectCompany.addEventListener("change", () => loadLiveJobs());
    }

    if (selectLocation) {
        selectLocation.addEventListener("change", () => loadLiveJobs());
    }
}

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
                    <span class="badge badge-primary">${escapeHtml(c.tier)}</span>
                    <span class="live-pulse-badge" title="Live Google Jobs & Career Portal tracking active"><span class="pulse-dot"></span> Live Drives</span>
                </div>
                <h3 class="company-title">${escapeHtml(c.name)}</h3>
                <p class="company-desc">${escapeHtml(c.description)}</p>
                <div class="company-prep-tags">
                    ${(c.preparation_areas || []).slice(0, 3).map(p => `<span class="company-tag">${escapeHtml(p.slice(0, 25))}...</span>`).join("")}
                </div>
            </div>
            <div style="display: flex; gap: 8px; margin-top: 12px;">
                <a href="/pages/company-detail.html?id=${encodeURIComponent(c.id)}" class="btn btn-primary btn-sm" style="flex: 1; text-align: center;">
                    Preparation Track ➔
                </a>
                <button type="button" class="btn btn-outline btn-sm" onclick="switchTabToLiveCompany('${encodeURIComponent(c.id)}')" title="View Live Openings for ${escapeHtml(c.name)}">
                    🔴 Openings
                </button>
            </div>
        </div>
    `).join("");
}

window.switchTabToLiveCompany = function(companyId) {
    const tabLiveJobs = document.getElementById("tab-live-jobs");
    const selectCompany = document.getElementById("jobs-filter-company");
    if (tabLiveJobs) {
        tabLiveJobs.click();
    }
    if (selectCompany) {
        selectCompany.value = companyId;
    }
    loadLiveJobs();
};

async function loadLiveJobs() {
    const liveGrid = document.getElementById("live-jobs-grid");
    if (!liveGrid) return;

    liveGrid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 48px;">
            <span class="spinner"></span> Querying Google Jobs & verified recruitment portals...
        </div>
    `;

    const inputRole = document.getElementById("jobs-search-role");
    const selectCompany = document.getElementById("jobs-filter-company");
    const selectLocation = document.getElementById("jobs-filter-location");
    const masterLink = document.getElementById("btn-master-google-jobs");

    const role = inputRole ? inputRole.value.trim() : "";
    const company = selectCompany ? selectCompany.value : "all";
    const location = selectLocation ? selectLocation.value : "all";

    try {
        const res = await window.api.getLiveJobs({
            role: role || undefined,
            company: company !== "all" ? company : undefined,
            location: location !== "all" ? location : undefined,
            limit: 20
        });

        if (masterLink && res.google_jobs_search_url) {
            masterLink.href = res.google_jobs_search_url;
        }

        if (!res.jobs || res.jobs.length === 0) {
            liveGrid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 48px; background: rgba(255,255,255,0.02); border-radius: 12px;">
                    <p style="color: var(--text-muted); font-size: 1rem; margin-bottom: 12px;">No active openings matched your specific filters.</p>
                    <a href="${res.google_jobs_search_url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm">
                        Search Live on Google Jobs Interface ↗
                    </a>
                </div>
            `;
            return;
        }

        liveGrid.innerHTML = res.jobs.map(job => `
            <div class="live-job-card">
                <div>
                    <div class="live-job-header">
                        <div>
                            <span style="font-size: 0.78rem; font-weight: 700; color: #818cf8; text-transform: uppercase; display: block; margin-bottom: 2px;">
                                ${escapeHtml(job.company_name)}
                            </span>
                            <h4 class="live-job-title">${escapeHtml(job.title)}</h4>
                        </div>
                        <span class="live-pulse-badge"><span class="pulse-dot"></span> Active</span>
                    </div>

                    <span style="font-size: 0.75rem; color: var(--text-muted); display: block; margin-bottom: 8px;">
                        ${escapeHtml(job.via)}
                    </span>

                    <div class="live-job-meta">
                        <span class="meta-chip">📍 ${escapeHtml(job.location)}</span>
                        <span class="meta-chip highlight">🎓 ${escapeHtml(job.batch_eligibility)}</span>
                        <span class="meta-chip">💼 ${escapeHtml(job.schedule_type)}</span>
                        <span class="meta-chip">⏱️ ${escapeHtml(job.posted_at)}</span>
                    </div>

                    <p class="live-job-snippet">${escapeHtml(job.description_snippet)}</p>
                </div>

                <div class="live-job-actions">
                    <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer" class="btn-apply-portal">
                        <span>🚀</span> Apply on Official Portal ↗
                    </a>
                    <a href="${job.google_jobs_url}" target="_blank" rel="noopener noreferrer" class="btn-google-jobs">
                        <span>🔍</span> Google Jobs
                    </a>
                </div>
            </div>
        `).join("");

    } catch (err) {
        console.error("Error loading live jobs:", err);
        liveGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 32px; color: var(--text-danger);">
                <p>Could not fetch live job listings. Please check back shortly or explore Google Jobs directly.</p>
            </div>
        `;
    }
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
                    <strong style="color: var(--secondary);">Round ${i + 1}:</strong> ${escapeHtml(r)}
                </li>
            `).join("");
        }

        const rolesList = document.getElementById("pattern-roles-list");
        if (rolesList && pattern.roles) {
            rolesList.innerHTML = pattern.roles.map(role => `<span class="badge badge-secondary" style="margin: 3px;">${escapeHtml(role)}</span>`).join("");
        }

        // Technical Topics
        const techList = document.getElementById("company-tech-topics");
        if (techList && c.technical_topics) {
            techList.innerHTML = c.technical_topics.map(t => `<li>${escapeHtml(t)}</li>`).join("");
        }

        // HR Topics
        const hrList = document.getElementById("company-hr-topics");
        if (hrList && c.hr_topics) {
            hrList.innerHTML = c.hr_topics.map(h => `<li>${escapeHtml(h)}</li>`).join("");
        }

        // Sample Questions
        const samplesList = document.getElementById("company-sample-questions");
        if (samplesList && c.sample_questions) {
            samplesList.innerHTML = c.sample_questions.map(q => `
                <div class="card" style="margin-bottom: 12px; padding: 18px;">
                    <span class="badge badge-primary" style="margin-bottom: 8px;">${escapeHtml(q.type.toUpperCase())}</span>
                    <h4 style="font-size: 1rem; color: #ffffff; margin-bottom: 8px;">${escapeHtml(q.question)}</h4>
                    <p style="font-size: 0.85rem; color: var(--info); margin: 0;">${escapeHtml(q.concept || q.explanation || '')}</p>
                </div>
            `).join("");
        }

        // --- REAL-TIME VACANCIES & GOOGLE JOBS INTEGRATION ---
        const liveJobsContainer = document.getElementById("company-live-jobs-list");
        const googleJobsLink = document.getElementById("company-google-jobs-live-link");
        if (liveJobsContainer) {
            try {
                const jobsData = await window.api.getCompanyJobs(id);
                if (googleJobsLink && jobsData.google_jobs_search_url) {
                    googleJobsLink.href = jobsData.google_jobs_search_url;
                }

                if (jobsData.jobs && jobsData.jobs.length > 0) {
                    liveJobsContainer.innerHTML = jobsData.jobs.map(job => `
                        <div class="live-job-card">
                            <div>
                                <div class="live-job-header">
                                    <div>
                                        <h4 class="live-job-title">${escapeHtml(job.title)}</h4>
                                        <span style="font-size: 0.78rem; color: #818cf8; font-weight: 500; display: block; margin-top: 3px;">
                                            ${escapeHtml(job.via)}
                                        </span>
                                    </div>
                                    <span class="live-pulse-badge"><span class="pulse-dot"></span> Live</span>
                                </div>
                                <div class="live-job-meta">
                                    <span class="meta-chip">📍 ${escapeHtml(job.location)}</span>
                                    <span class="meta-chip highlight">🎓 ${escapeHtml(job.batch_eligibility)}</span>
                                    <span class="meta-chip">💼 ${escapeHtml(job.schedule_type)}</span>
                                    <span class="meta-chip">⏱️ ${escapeHtml(job.posted_at)}</span>
                                </div>
                                <p class="live-job-snippet">${escapeHtml(job.description_snippet)}</p>
                            </div>
                            <div class="live-job-actions">
                                <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer" class="btn-apply-portal">
                                    <span>🚀</span> Apply on Official Portal ↗
                                </a>
                                <a href="${job.google_jobs_url}" target="_blank" rel="noopener noreferrer" class="btn-google-jobs">
                                    <span>🔍</span> Google Jobs
                                </a>
                            </div>
                        </div>
                    `).join("");
                } else {
                    liveJobsContainer.innerHTML = `
                        <div style="grid-column: 1/-1; padding: 24px; background: rgba(255,255,255,0.03); border-radius: 8px; text-align: center;">
                            <p style="color: var(--text-muted); margin-bottom: 12px;">Active openings are continuously tracked through the Google Jobs engine.</p>
                            <a href="${jobsData.google_jobs_search_url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm">
                                Explore Live ${escapeHtml(c.name)} Openings on Google Jobs ↗
                            </a>
                        </div>
                    `;
                }
            } catch (jobErr) {
                console.warn("Could not fetch live jobs for company:", jobErr);
                liveJobsContainer.innerHTML = `
                    <div style="grid-column: 1/-1; padding: 16px; background: rgba(255,255,255,0.03); border-radius: 8px;">
                        <p style="color: var(--text-muted); font-size: 0.9rem; margin: 0;">
                            Live vacancy search is active.
                            <a href="https://www.google.com/search?q=${encodeURIComponent(c.name + ' fresher software engineer jobs india')}&ibp=htl;jobs" target="_blank" style="color: #818cf8; margin-left: 6px;">Check Google Jobs Live ↗</a>
                        </p>
                    </div>
                `;
            }
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
                                    <span style="font-size: 0.72rem; font-weight: 700; color: #818cf8; text-transform: uppercase;">${escapeHtml(m.format)}</span>
                                    <span style="font-size: 0.7rem; color: var(--text-muted);">${escapeHtml(m.category)}</span>
                                </div>
                                <h5 style="font-size: 0.92rem; color: #f8fafc; margin-bottom: 6px; line-height: 1.3;">${escapeHtml(m.title)}</h5>
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
                                Comprehensive test materials and mock exams for <b>${escapeHtml(c.name)}</b> are ready in our central repository.
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
