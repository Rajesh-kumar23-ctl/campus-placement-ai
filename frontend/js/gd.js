/**
 * Group Discussion Catalog & Topic Preparation Controller
 */

let allTopics = [];

document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuth()) return;

    await loadTopics();
    setupFilters();
    setupCustomTopicModal();
});

async function loadTopics(search = null, category = null) {
    const grid = document.getElementById("gd-topics-grid");
    if (!grid) return;

    grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px;"><span class="spinner"></span> Loading topics...</div>`;

    try {
        allTopics = await window.api.getGDTopics(search, category);
        renderTopics(allTopics);
    } catch (err) {
        grid.innerHTML = `<p class="text-danger" style="grid-column: 1/-1; text-align: center;">Unable to load topics.</p>`;
    }
}

function renderTopics(topics) {
    const grid = document.getElementById("gd-topics-grid");
    if (!grid) return;

    if (!topics || topics.length === 0) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <div class="empty-state-icon">💭</div>
                <h3 class="empty-state-title">No matching topics found</h3>
                <p class="empty-state-text">Try adjusting your search or generate a custom topic with AI.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = topics.map(t => `
        <div class="topic-card">
            <div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span class="badge badge-secondary">${t.category}</span>
                    <span class="badge ${t.difficulty === 'Hard' ? 'badge-danger' : (t.difficulty === 'Medium' ? 'badge-warning' : 'badge-success')}">
                        ${t.difficulty}
                    </span>
                </div>
                <h3 class="topic-title">${t.topic}</h3>
                <p class="topic-overview">${t.overview}</p>
            </div>
            <div style="display: flex; gap: 10px; margin-top: 16px;">
                <button class="btn btn-outline btn-sm" style="flex: 1;" onclick="openPrepModal('${t.id}')">
                    📖 Prep Guide
                </button>
                <a href="/pages/gd-simulator.html?topic=${encodeURIComponent(t.topic)}" class="btn btn-primary btn-sm" style="flex: 1;">
                    🎙️ Simulate
                </a>
            </div>
        </div>
    `).join("");
}

function setupFilters() {
    const searchInput = document.getElementById("gd-search-input");
    const categorySelect = document.getElementById("gd-category-filter");

    let debounceTimer;
    if (searchInput) {
        searchInput.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const search = searchInput.value.trim();
                const category = categorySelect?.value;
                loadTopics(search, category);
            }, 300);
        });
    }

    if (categorySelect) {
        categorySelect.addEventListener("change", () => {
            const search = searchInput?.value.trim();
            const category = categorySelect.value;
            loadTopics(search, category);
        });
    }
}

async function openPrepModal(topicId) {
    const topic = allTopics.find(t => t.id === topicId);
    if (!topic) return;

    document.getElementById("modal-topic-title").textContent = topic.topic;
    document.getElementById("modal-topic-category").textContent = topic.category;
    document.getElementById("modal-topic-difficulty").textContent = topic.difficulty;
    document.getElementById("modal-topic-overview").textContent = topic.overview;
    document.getElementById("modal-topic-opening").textContent = topic.opening_statement;

    // Arguments For & Against
    const argsForEl = document.getElementById("modal-args-for");
    if (argsForEl) {
        argsForEl.innerHTML = (topic.key_arguments_for || []).map(a => `<li>${a}</li>`).join("");
    }
    const argsAgainstEl = document.getElementById("modal-args-against");
    if (argsAgainstEl) {
        argsAgainstEl.innerHTML = (topic.key_arguments_against || []).map(a => `<li>${a}</li>`).join("");
    }

    // Real World Examples
    const examplesEl = document.getElementById("modal-examples");
    if (examplesEl) {
        examplesEl.innerHTML = (topic.real_world_examples || []).map(e => `<li>${e}</li>`).join("");
    }

    // Speeches
    document.getElementById("modal-30s-speech").textContent = topic.thirty_sec_speech || "";
    document.getElementById("modal-1m-speech").textContent = topic.one_min_speech || "";
    document.getElementById("modal-conclusion").textContent = topic.conclusion || "";

    // Mistakes to avoid
    const avoidEl = document.getElementById("modal-avoid");
    if (avoidEl) {
        avoidEl.innerHTML = (topic.things_to_avoid || []).map(m => `<li>${m}</li>`).join("");
    }

    // Follow-ups
    const followupsEl = document.getElementById("modal-followups");
    if (followupsEl) {
        followupsEl.innerHTML = (topic.follow_up_questions || []).map(q => `<li>${q}</li>`).join("");
    }

    // Practice button link
    const simLink = document.getElementById("modal-practice-link");
    if (simLink) {
        simLink.href = `/pages/gd-simulator.html?topic=${encodeURIComponent(topic.topic)}`;
    }

    document.getElementById("gd-prep-modal").classList.add("active");
}

function closePrepModal() {
    document.getElementById("gd-prep-modal").classList.remove("active");
}

function setupCustomTopicModal() {
    const customBtn = document.getElementById("btn-custom-topic");
    const customModal = document.getElementById("custom-topic-modal");
    const generateBtn = document.getElementById("btn-generate-prep");

    if (customBtn && customModal) {
        customBtn.addEventListener("click", () => customModal.classList.add("active"));
    }

    const cancelBtn = document.getElementById("btn-cancel-custom");
    if (cancelBtn && customModal) {
        cancelBtn.addEventListener("click", () => customModal.classList.remove("active"));
    }

    if (generateBtn) {
        generateBtn.addEventListener("click", async () => {
            const topicInput = document.getElementById("custom-topic-input").value.trim();
            const cat = document.getElementById("custom-category-input").value;
            const diff = document.getElementById("custom-difficulty-input").value;

            if (!topicInput) {
                showToast("warning", "Please enter a topic title.");
                return;
            }

            generateBtn.disabled = true;
            generateBtn.innerHTML = `<span class="spinner"></span> Generating Preparation Guide...`;

            try {
                const prep = await window.api.generateGD({
                    topic: topicInput,
                    category: cat,
                    difficulty: diff
                });

                customModal.classList.remove("active");
                generateBtn.disabled = false;
                generateBtn.textContent = "Generate Prep Material";

                allTopics.unshift(prep);
                renderTopics(allTopics);
                openPrepModal(prep.id);
                showToast("success", "Topic guide generated successfully!");

            } catch (err) {
                showToast("error", err.message || "Failed to generate topic guide.");
                generateBtn.disabled = false;
                generateBtn.textContent = "Generate Prep Material";
            }
        });
    }
}
