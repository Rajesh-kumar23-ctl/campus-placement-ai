/**
 * AI Placement Coach - Materials Hub Controller
 * Manages Google Drive placement materials repository, filtering, search, and pagination.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Current query state
    const state = {
        search: "",
        company: "all",
        category: "all",
        format: "all",
        page: 1,
        limit: 24,
        totalPages: 1,
        totalItems: 0
    };

    // DOM Elements
    const searchInput = document.getElementById("materialSearchInput");
    const companySelect = document.getElementById("companySelect");
    const formatSelect = document.getElementById("formatSelect");
    const categoryChips = document.querySelectorAll(".category-chip");
    const materialsContainer = document.getElementById("materialsGrid");
    const totalCountEl = document.getElementById("resultsTotalCount");
    const prevBtn = document.getElementById("prevPageBtn");
    const nextBtn = document.getElementById("nextPageBtn");
    const pageIndicator = document.getElementById("pageIndicator");
    const driveFolderBtn = document.getElementById("openDriveFolderBtn");
    const statTotalEl = document.getElementById("statTotalMaterials");
    const statCompaniesEl = document.getElementById("statCompaniesCount");

    // Initialize
    initMaterialsPage();

    async function initMaterialsPage() {
        // Parse URL query parameters if navigated from company page (e.g. ?company=Infosys)
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has("company")) {
            state.company = urlParams.get("company");
        }
        if (urlParams.has("category")) {
            state.category = urlParams.get("category");
        }

        // Load company dropdown options
        await loadCompanyDropdown();

        // Load materials
        await loadMaterials();

        // Setup Event Listeners
        setupEventListeners();
    }

    async function loadCompanyDropdown() {
        try {
            const companies = await window.api.getMaterialCompanies();
            if (companies && Array.isArray(companies)) {
                if (companySelect) {
                    companySelect.innerHTML = '<option value="all">🏢 All Companies & Platforms</option>';
                    companies.forEach(c => {
                        const opt = document.createElement("option");
                        opt.value = c.company;
                        opt.textContent = `${c.company} (${c.count} items)`;
                        if (state.company.toLowerCase() === c.company.toLowerCase()) {
                            opt.selected = true;
                        }
                        companySelect.appendChild(opt);
                    });
                }
                if (statCompaniesEl) {
                    statCompaniesEl.textContent = companies.length;
                }
            }
        } catch (err) {
            console.error("Error loading companies list:", err);
        }
    }

    async function loadMaterials() {
        if (!materialsContainer) return;

        materialsContainer.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem 1rem;">
                <div class="spinner" style="margin: 0 auto 1rem;"></div>
                <p style="color: var(--text-muted);">Loading verified Drive placement materials...</p>
            </div>
        `;

        try {
            const res = await window.api.getMaterials({
                search: state.search,
                company: state.company,
                category: state.category,
                format: state.format,
                page: state.page,
                limit: state.limit
            });

            state.totalItems = res.total;
            state.totalPages = res.total_pages || 1;

            if (statTotalEl) {
                statTotalEl.textContent = res.total;
            }
            if (totalCountEl) {
                totalCountEl.textContent = `Showing ${(state.page - 1) * state.limit + 1} - ${Math.min(state.page * state.limit, res.total)} of ${res.total} study resources`;
            }
            if (pageIndicator) {
                pageIndicator.textContent = `Page ${state.page} of ${state.totalPages}`;
            }

            if (prevBtn) prevBtn.disabled = (state.page <= 1);
            if (nextBtn) nextBtn.disabled = (state.page >= state.totalPages);

            // Configure Master Drive Folder button
            if (driveFolderBtn && res.drive_root_url) {
                driveFolderBtn.href = res.drive_root_url;
                driveFolderBtn.target = "_blank";
            }

            renderMaterials(res.materials);

        } catch (err) {
            console.error("Failed to fetch materials:", err);
            materialsContainer.innerHTML = `
                <div class="materials-empty-state" style="grid-column: 1/-1;">
                    <div class="empty-icon">⚠️</div>
                    <h3>Unable to load materials</h3>
                    <p style="color: var(--text-muted); margin-bottom: 1.5rem;">Could not connect to the materials repository. Please refresh or try again.</p>
                    <button class="btn btn-outline" onclick="location.reload()">Retry Loading</button>
                </div>
            `;
        }
    }

    function renderMaterials(items) {
        if (!items || items.length === 0) {
            materialsContainer.innerHTML = `
                <div class="materials-empty-state" style="grid-column: 1/-1;">
                    <div class="empty-icon">📂</div>
                    <h3>No materials found matching your filter</h3>
                    <p style="color: var(--text-muted); margin-bottom: 1.5rem;">Try adjusting your search keyword or clearing company/category filters.</p>
                    <button class="btn btn-outline" id="resetFiltersBtn">Reset All Filters</button>
                </div>
            `;
            const resetBtn = document.getElementById("resetFiltersBtn");
            if (resetBtn) {
                resetBtn.addEventListener("click", () => {
                    state.search = "";
                    state.company = "all";
                    state.category = "all";
                    state.format = "all";
                    state.page = 1;
                    if (searchInput) searchInput.value = "";
                    if (companySelect) companySelect.value = "all";
                    if (formatSelect) formatSelect.value = "all";
                    categoryChips.forEach(c => c.classList.toggle("active", c.dataset.category === "all"));
                    loadMaterials();
                });
            }
            return;
        }

        materialsContainer.innerHTML = items.map(m => {
            const formatClass = getFormatBadgeClass(m.format);
            const formatIcon = getFormatIcon(m.format);

            return `
                <div class="material-card">
                    <div>
                        <div class="material-card-top">
                            <span class="format-badge ${formatClass}">
                                ${formatIcon} ${m.format}
                            </span>
                            <span class="company-pill">${escapeHTML(m.company)}</span>
                        </div>
                        <h3 class="material-title" title="${escapeHTML(m.title)}">${escapeHTML(m.title)}</h3>
                        <p class="material-desc">${escapeHTML(m.description)}</p>
                        <div class="material-meta-tags">
                            <span class="meta-tag">🏷️ ${escapeHTML(m.category)}</span>
                            ${m.subfolder ? `<span class="meta-tag">📁 ${escapeHTML(m.subfolder)}</span>` : ""}
                        </div>
                    </div>
                    <div class="material-card-actions">
                        <a href="${m.view_url}" target="_blank" rel="noopener noreferrer" class="btn-preview" title="Open and preview directly on Google Drive">
                            <i data-lucide="external-link" style="width:16px;height:16px;"></i> View on Drive
                        </a>
                        <a href="${m.download_url}" target="_blank" rel="noopener noreferrer" class="btn-download-icon" title="Direct Download via Google Drive">
                            <i data-lucide="download" style="width:18px;height:18px;"></i>
                        </a>
                        <a href="/pages/aptitude.html?company=${encodeURIComponent(m.company)}" class="btn-download-icon" title="Practice Mock Test for ${escapeHTML(m.company)}" style="color:#818cf8;">
                            <i data-lucide="play" style="width:18px;height:18px;"></i>
                        </a>
                    </div>
                </div>
            `;
        }).join("");

        // Reinitialize icons if lucide is active
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    function getFormatBadgeClass(fmt) {
        if (!fmt) return "format-other";
        const f = fmt.toLowerCase();
        if (f.includes("pdf")) return "format-pdf";
        if (f.includes("word") || f.includes("docx")) return "format-docx";
        if (f.includes("zip")) return "format-zip";
        if (f.includes("bundle") || f.includes("folder")) return "format-bundle";
        return "format-other";
    }

    function getFormatIcon(fmt) {
        if (!fmt) return "📄";
        const f = fmt.toLowerCase();
        if (f.includes("pdf")) return "📕";
        if (f.includes("word")) return "📘";
        if (f.includes("zip")) return "📦";
        if (f.includes("bundle") || f.includes("folder")) return "📁";
        if (f.includes("handwritten") || f.includes("scan")) return "📝";
        if (f.includes("code")) return "💻";
        return "📄";
    }

    function setupEventListeners() {
        // Search Input with Debounce
        let debounceTimer;
        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    state.search = e.target.value.trim();
                    state.page = 1;
                    loadMaterials();
                }, 300);
            });
        }

        // Company Select
        if (companySelect) {
            companySelect.addEventListener("change", (e) => {
                state.company = e.target.value;
                state.page = 1;
                loadMaterials();
            });
        }

        // Format Select
        if (formatSelect) {
            formatSelect.addEventListener("change", (e) => {
                state.format = e.target.value;
                state.page = 1;
                loadMaterials();
            });
        }

        // Category Chips
        categoryChips.forEach(chip => {
            chip.addEventListener("click", () => {
                categoryChips.forEach(c => c.classList.remove("active"));
                chip.classList.add("active");
                state.category = chip.dataset.category || "all";
                state.page = 1;
                loadMaterials();
            });
        });

        // Pagination
        if (prevBtn) {
            prevBtn.addEventListener("click", () => {
                if (state.page > 1) {
                    state.page--;
                    loadMaterials();
                    window.scrollTo({ top: 300, behavior: 'smooth' });
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener("click", () => {
                if (state.page < state.totalPages) {
                    state.page++;
                    loadMaterials();
                    window.scrollTo({ top: 300, behavior: 'smooth' });
                }
            });
        }
    }

    function escapeHTML(str) {
        if (!str) return "";
        return str.replace(/[&<>'"]/g, tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag));
    }
});
