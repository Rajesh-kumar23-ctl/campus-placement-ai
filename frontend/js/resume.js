/**
 * Resume AI Upload & Analysis Controller
 */

let currentResumeId = null;

document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuth()) return;

    setupUploadZone();
    await checkExistingResume();
});

async function checkExistingResume() {
    try {
        const resume = await window.api.getLatestResume();
        if (resume) {
            renderResumeAnalysis(resume);
        }
    } catch {
        // No resume yet
    }
}

function setupUploadZone() {
    const dropzone = document.getElementById("resume-dropzone");
    const fileInput = document.getElementById("resume-file-input");

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    const dropzone = document.getElementById("resume-dropzone");
    const originalContent = dropzone.innerHTML;

    // Check extension
    const name = file.name.toLowerCase();
    if (!name.endsWith(".pdf") && !name.endsWith(".docx")) {
        showToast("error", "Invalid file type. Please upload a PDF or DOCX file.");
        return;
    }

    dropzone.innerHTML = `
        <div style="padding: 20px;">
            <span class="spinner" style="width: 36px; height: 36px; margin-bottom: 12px;"></span>
            <h3 style="font-size: 1.1rem; color: #ffffff;">AI is analyzing your resume...</h3>
            <p style="font-size: 0.85rem; color: var(--text-secondary);">Extracting skills, projects, and interview questions...</p>
        </div>
    `;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const resumeData = await window.api.uploadResume(formData);
        showToast("success", "Resume parsed successfully!");
        renderResumeAnalysis(resumeData);
    } catch (err) {
        showToast("error", err.message || "Failed to analyze resume.");
        dropzone.innerHTML = originalContent;
    }
}

function renderResumeAnalysis(data) {
    currentResumeId = data.id;

    // Show analysis section
    const analysisContainer = document.getElementById("resume-analysis-container");
    if (analysisContainer) analysisContainer.style.display = "block";

    // Summary
    document.getElementById("resume-filename-tag").textContent = data.filename;
    document.getElementById("resume-summary-text").textContent = data.summary || "Candidate profile extracted successfully.";

    // Skills
    const skillsCloud = document.getElementById("skills-cloud");
    if (skillsCloud && data.skills) {
        skillsCloud.innerHTML = data.skills.map(s => `<span class="skill-tag">${s}</span>`).join("");
    }

    // Projects
    const projectsList = document.getElementById("projects-list");
    if (projectsList && data.projects) {
        projectsList.innerHTML = data.projects.map(p => `
            <div class="parsed-project-card">
                <div class="parsed-project-header">
                    <h4 style="font-size: 1rem; color: #ffffff; font-weight: 600;">${p.title}</h4>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0;">
                    ${(p.technologies || []).map(t => `<span class="badge badge-secondary" style="font-size: 0.72rem;">${t}</span>`).join("")}
                </div>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">${p.description}</p>
            </div>
        `).join("");
    }

    // Questions Generated from Resume
    const questionsList = document.getElementById("potential-questions-list");
    if (questionsList && data.potential_questions) {
        questionsList.innerHTML = data.potential_questions.map((q, idx) => `
            <div style="padding: 12px 16px; background: var(--bg-surface); border-radius: var(--radius-md); border-left: 3px solid var(--primary); margin-bottom: 8px; font-size: 0.92rem;">
                <strong>Q${idx + 1}:</strong> ${q}
            </div>
        `).join("");
    }

    // Link Resume Interview button
    const interviewBtn = document.getElementById("btn-resume-interview");
    if (interviewBtn) {
        interviewBtn.onclick = () => {
            window.location.href = `/pages/interview.html?use_resume=1&resume_id=${data.id}`;
        };
    }
}
