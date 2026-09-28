/**
 * Full Placement Simulation State Machine Controller
 * Flagship feature executing sequential 4-round placement drive:
 * Round 1: Aptitude -> Round 2: GD -> Round 3: Technical -> Round 4: HR -> Final Certificate Report
 */

let simDriveState = {
    simulationId: null,
    currentRound: "aptitude",
    targetRole: "Software Developer",
    scores: {
        aptitude: 0,
        gd: 0,
        technical: 0,
        hr: 0,
        communication: 0,
        overall: 0
    }
};

document.addEventListener("DOMContentLoaded", () => {
    if (!requireAuth()) return;

    setupSimulationInitiation();
});

function setupSimulationInitiation() {
    const startBtn = document.getElementById("btn-start-drive");
    if (!startBtn) return;

    startBtn.addEventListener("click", async () => {
        const role = document.getElementById("drive-role-select").value;
        const company = document.getElementById("drive-company-select").value;

        startBtn.disabled = true;
        startBtn.innerHTML = `<span class="spinner"></span> Launching Placement Drive...`;

        try {
            const res = await window.api.startSimulation({
                target_role: role,
                company_focus: company
            });

            simDriveState.simulationId = res.simulation_id;
            simDriveState.currentRound = res.current_round;
            simDriveState.targetRole = res.target_role;

            // Transition UI to Active Round Container
            document.getElementById("drive-intro-card").style.display = "none";
            document.getElementById("drive-active-container").style.display = "block";

            updateStepperUI("aptitude");
            loadRoundInterface("aptitude");

        } catch (err) {
            showToast("error", err.message || "Failed to start placement simulation.");
            startBtn.disabled = false;
            startBtn.textContent = "Begin Full Simulation";
        }
    });
}

function updateStepperUI(roundKey) {
    const steps = ["aptitude", "gd", "technical", "hr"];
    const currentIdx = steps.indexOf(roundKey);

    steps.forEach((s, idx) => {
        const stepEl = document.getElementById(`step-${s}`);
        if (!stepEl) return;

        stepEl.classList.remove("active", "completed");
        if (idx < currentIdx || roundKey === "completed") {
            stepEl.classList.add("completed");
        } else if (idx === currentIdx) {
            stepEl.classList.add("active");
        }
    });
}

async function loadRoundInterface(roundKey) {
    const roundContent = document.getElementById("round-content-area");
    if (!roundContent) return;

    if (roundKey === "aptitude") {
        renderSimAptitudeRound(roundContent);
    } else if (roundKey === "gd") {
        renderSimGDRound(roundContent);
    } else if (roundKey === "technical") {
        renderSimTechRound(roundContent);
    } else if (roundKey === "hr") {
        renderSimHRRound(roundContent);
    }
}

// Round 1: Fast Aptitude Screening
async function renderSimAptitudeRound(container) {
    container.innerHTML = `
        <div class="card" style="padding: 32px; text-align: center;">
            <span class="badge badge-primary" style="margin-bottom: 12px;">Round 1 of 4</span>
            <h2 style="font-size: 1.6rem; color: #ffffff; margin-bottom: 10px;">Aptitude & Cognitive Screening</h2>
            <p style="max-width: 540px; margin: 0 auto 24px;">Complete 5 high-yield quantitative, logical, and verbal screening questions.</p>
            <div id="sim-apt-runner" style="text-align: left; max-width: 650px; margin: 0 auto;">
                <div style="text-align: center; padding: 20px;"><span class="spinner"></span> Preparing test questions...</div>
            </div>
        </div>
    `;

    try {
        const questions = await window.api.startAptitude({
            category: "all",
            difficulty: "medium",
            num_questions: 5,
            timer_minutes: 5
        });

        let qIndex = 0;
        const answers = {};

        function showQ(idx) {
            const q = questions[idx];
            const runner = document.getElementById("sim-apt-runner");
            if (!runner) return;

            runner.innerHTML = `
                <div style="background: var(--bg-surface); padding: 24px; border-radius: var(--radius-lg); border: 1px solid var(--border-subtle); margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span class="badge badge-secondary">${q.category_display || q.category}</span>
                        <span style="font-size: 0.85rem; color: var(--text-muted);">Question ${idx + 1} of ${questions.length}</span>
                    </div>
                    <div style="font-size: 1.15rem; font-weight: 600; color: #ffffff; margin-bottom: 20px;">${q.question}</div>
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        ${q.options.map(opt => `
                            <button class="btn btn-outline" style="text-align: left; justify-content: flex-start; padding: 12px 18px; ${answers[q.id] === opt ? 'border-color: var(--primary); background: var(--primary-light);' : ''}" onclick="selectSimAptAnswer('${q.id}', '${opt.replace(/'/g, "\\'")}', ${idx})">
                                ${opt}
                            </button>
                        `).join("")}
                    </div>
                </div>
                <div style="display: flex; justify-content: flex-end;">
                    ${idx < questions.length - 1 ? `
                        <button class="btn btn-primary" onclick="window.nextSimApt(${idx + 1})">Next Question ➔</button>
                    ` : `
                        <button class="btn btn-success" onclick="window.submitSimApt()">Submit Round 1</button>
                    `}
                </div>
            `;
        }

        window.selectSimAptAnswer = (qId, optText, idx) => {
            answers[qId] = optText;
            showQ(idx);
        };

        window.nextSimApt = (nextIdx) => {
            qIndex = nextIdx;
            showQ(nextIdx);
        };

        window.submitSimApt = async () => {
            const runner = document.getElementById("sim-apt-runner");
            if (runner) runner.innerHTML = `<div style="text-align: center; padding: 20px;"><span class="spinner"></span> Grading Round 1...</div>`;

            const sub = await window.api.submitAptitude({
                category: "all",
                difficulty: "medium",
                time_taken: 120,
                answers: questions.map(q => ({
                    question_id: q.id,
                    selected_answer: answers[q.id] || null,
                    time_taken: 0
                }))
            });

            simDriveState.scores.aptitude = sub.score;
            showToast("success", `Round 1 Complete! Aptitude Score: ${sub.score}%`);

            // Advance to Round 2 (GD)
            await window.api.completeSimulationRound({
                simulation_id: simDriveState.simulationId,
                round_type: "aptitude",
                round_score: sub.score
            });

            simDriveState.currentRound = "gd";
            updateStepperUI("gd");
            loadRoundInterface("gd");
        };

        showQ(0);

    } catch (err) {
        showToast("error", "Unable to load aptitude questions.");
    }
}

// Round 2: Group Discussion
async function renderSimGDRound(container) {
    const topic = "Will Artificial Intelligence replace human jobs or create new opportunities?";
    container.innerHTML = `
        <div class="card" style="padding: 32px;">
            <div style="text-align: center; margin-bottom: 24px;">
                <span class="badge badge-warning" style="margin-bottom: 8px;">Round 2 of 4</span>
                <h2 style="font-size: 1.6rem; color: #ffffff;">Group Discussion Round</h2>
                <p style="font-size: 0.95rem; color: var(--text-secondary);">Topic: <strong>"${topic}"</strong></p>
            </div>
            <div style="background: var(--bg-surface); padding: 20px; border-radius: var(--radius-lg); margin-bottom: 20px;">
                <div style="font-weight: 700; color: var(--secondary); margin-bottom: 6px;">Moderator Opening:</div>
                <p style="font-size: 0.95rem; color: var(--text-primary); margin-bottom: 12px;">"Welcome to this evaluation round. Please contribute your core stance on whether AI will lead to net labor displacement or unprecedented skill evolution."</p>
                <div style="font-weight: 700; color: #a5b4fc; margin-bottom: 6px;">Participant 1 (Aarav):</div>
                <p style="font-size: 0.95rem; color: var(--text-secondary);">"Historical tech cycles show repetitive tasks vanish while high-level analytical roles multiply. However, educational institutions are struggling to keep up with curriculum reforms."</p>
            </div>
            <div class="form-group">
                <label class="form-label">Articulate Your Contribution (Type or speak):</label>
                <textarea id="sim-gd-input" class="form-control" rows="4" placeholder="Present a structured argument with reasoning or a concrete example..."></textarea>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 12px;">
                <button class="btn btn-success" id="btn-submit-sim-gd">Submit GD Argument ➔</button>
            </div>
        </div>
    `;

    document.getElementById("btn-submit-sim-gd")?.addEventListener("click", async () => {
        const text = document.getElementById("sim-gd-input").value.trim();
        if (!text) {
            showToast("warning", "Please write your argument before proceeding.");
            return;
        }

        const btn = document.getElementById("btn-submit-sim-gd");
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner"></span> Evaluating GD Contribution...`;

        // Calculate heuristic score for the round
        const words = text.split(" ").length;
        const gdScore = Math.min(95, Math.max(65, 65 + Math.round(words / 4)));
        simDriveState.scores.gd = gdScore;

        showToast("success", `Round 2 Complete! GD Score: ${gdScore}%`);

        await window.api.completeSimulationRound({
            simulation_id: simDriveState.simulationId,
            round_type: "gd",
            round_score: gdScore,
            round_data: { contribution: text }
        });

        simDriveState.currentRound = "technical";
        updateStepperUI("technical");
        loadRoundInterface("technical");
    });
}

// Round 3: Technical Interview
async function renderSimTechRound(container) {
    const qText = "How do you optimize a relational database experiencing slow read queries, and what is the difference between Clustered and Non-Clustered Indexes?";
    container.innerHTML = `
        <div class="card" style="padding: 32px;">
            <div style="text-align: center; margin-bottom: 24px;">
                <span class="badge badge-primary" style="margin-bottom: 8px;">Round 3 of 4</span>
                <h2 style="font-size: 1.6rem; color: #ffffff;">Technical Interview Round</h2>
                <p style="font-size: 0.95rem; color: var(--text-secondary);">Role: <strong>${simDriveState.targetRole}</strong></p>
            </div>
            <div style="background: var(--bg-surface); padding: 22px; border-radius: var(--radius-lg); border-left: 4px solid var(--primary); margin-bottom: 20px;">
                <div style="font-weight: 700; color: var(--info); margin-bottom: 6px;">Technical Lead:</div>
                <div style="font-size: 1.15rem; font-weight: 600; color: #ffffff;">"${qText}"</div>
            </div>
            <div class="form-group">
                <label class="form-label">Your Technical Explanation:</label>
                <textarea id="sim-tech-input" class="form-control" rows="5" placeholder="Detail your indexing strategy, B+ trees, query caching, and index trade-offs..."></textarea>
            </div>
            <div style="display: flex; justify-content: flex-end;">
                <button class="btn btn-success" id="btn-submit-sim-tech">Submit Technical Answer ➔</button>
            </div>
        </div>
    `;

    document.getElementById("btn-submit-sim-tech")?.addEventListener("click", async () => {
        const text = document.getElementById("sim-tech-input").value.trim();
        if (!text) {
            showToast("warning", "Please provide your technical explanation.");
            return;
        }

        const btn = document.getElementById("btn-submit-sim-tech");
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner"></span> Evaluating Technical Depth...`;

        const words = text.split(" ").length;
        const techScore = Math.min(94, Math.max(70, 70 + Math.round(words / 5)));
        simDriveState.scores.technical = techScore;

        showToast("success", `Round 3 Complete! Technical Score: ${techScore}%`);

        await window.api.completeSimulationRound({
            simulation_id: simDriveState.simulationId,
            round_type: "technical",
            round_score: techScore,
            round_data: { answer: text }
        });

        simDriveState.currentRound = "hr";
        updateStepperUI("hr");
        loadRoundInterface("hr");
    });
}

// Round 4: HR & Behavioral Round
async function renderSimHRRound(container) {
    const qText = "Tell me about a time you faced a difficult team conflict or missed a critical deadline. How did you handle the situation?";
    container.innerHTML = `
        <div class="card" style="padding: 32px;">
            <div style="text-align: center; margin-bottom: 24px;">
                <span class="badge badge-success" style="margin-bottom: 8px;">Final Round (4 of 4)</span>
                <h2 style="font-size: 1.6rem; color: #ffffff;">HR & Culture Fit Round</h2>
                <p style="font-size: 0.95rem; color: var(--text-secondary);">Assessing teamwork, accountability, and communication</p>
            </div>
            <div style="background: var(--bg-surface); padding: 22px; border-radius: var(--radius-lg); border-left: 4px solid var(--success); margin-bottom: 20px;">
                <div style="font-weight: 700; color: var(--success); margin-bottom: 6px;">HR Manager:</div>
                <div style="font-size: 1.15rem; font-weight: 600; color: #ffffff;">"${qText}"</div>
            </div>
            <div class="form-group">
                <label class="form-label">Your STAR Response (Situation, Task, Action, Result):</label>
                <textarea id="sim-hr-input" class="form-control" rows="5" placeholder="Describe the context, your specific action, and the positive resolution..."></textarea>
            </div>
            <div style="display: flex; justify-content: flex-end;">
                <button class="btn btn-success" id="btn-submit-sim-hr">Conclude Simulation & Generate Report 🎓</button>
            </div>
        </div>
    `;

    document.getElementById("btn-submit-sim-hr")?.addEventListener("click", async () => {
        const text = document.getElementById("sim-hr-input").value.trim();
        if (!text) {
            showToast("warning", "Please provide your answer.");
            return;
        }

        const btn = document.getElementById("btn-submit-sim-hr");
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner"></span> Synthesizing Comprehensive Placement Report...`;

        const words = text.split(" ").length;
        const hrScore = Math.min(95, Math.max(72, 72 + Math.round(words / 5)));
        simDriveState.scores.hr = hrScore;

        const completeRes = await window.api.completeSimulationRound({
            simulation_id: simDriveState.simulationId,
            round_type: "hr",
            round_score: hrScore,
            round_data: { answer: text, communication: 78.0 }
        });

        updateStepperUI("completed");
        renderFinalSimulationCertificate(container, simDriveState.simulationId);
    });
}

async function renderFinalSimulationCertificate(container, simId) {
    try {
        const report = await window.api.getSimulationReport(simId);

        container.innerHTML = `
            <div class="simulation-report-card">
                <div style="text-align: center; margin-bottom: 28px;">
                    <span class="badge badge-success" style="font-size: 0.9rem; padding: 6px 16px; margin-bottom: 12px;">SIMULATION COMPLETE</span>
                    <h1 style="font-size: 2.2rem; color: #ffffff; margin-bottom: 8px;">Full Placement Simulation Report</h1>
                    <p style="color: var(--text-secondary);">Target Track: <strong>${report.target_role}</strong> • Completed On: ${new Date(report.completed_at || Date.now()).toLocaleDateString()}</p>
                </div>

                <div style="text-align: center; margin-bottom: 24px;">
                    <div style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted);">Overall Preparation Performance</div>
                    <div style="font-family: var(--font-heading); font-size: 3.8rem; font-weight: 800; color: #ffffff; line-height: 1.1; margin: 8px 0;">
                        ${Math.round(report.overall_score)}%
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-muted);">* Metric reflects preparation performance across simulated rounds. Does not guarantee placement.</p>
                </div>

                <div class="round-score-cards-grid">
                    <div class="round-score-box">
                        <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Aptitude Round</div>
                        <div class="round-score-val" style="color: var(--primary);">${Math.round(report.aptitude_score)}%</div>
                    </div>
                    <div class="round-score-box">
                        <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">GD Round</div>
                        <div class="round-score-val" style="color: var(--secondary);">${Math.round(report.gd_score)}%</div>
                    </div>
                    <div class="round-score-box">
                        <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Technical Interview</div>
                        <div class="round-score-val" style="color: #a855f7;">${Math.round(report.technical_score)}%</div>
                    </div>
                    <div class="round-score-box">
                        <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">HR Round</div>
                        <div class="round-score-val" style="color: var(--success);">${Math.round(report.hr_score)}%</div>
                    </div>
                </div>

                <div style="background: var(--bg-surface); padding: 24px; border-radius: var(--radius-lg); margin-bottom: 24px;">
                    <h3 style="font-size: 1.15rem; color: #ffffff; margin-bottom: 12px;">Diagnostic Strengths</h3>
                    <ul style="list-style: disc inside; color: var(--text-secondary); line-height: 1.6; margin-bottom: 16px;">
                        ${(report.strengths || []).map(s => `<li>${s}</li>`).join("")}
                    </ul>

                    <h3 style="font-size: 1.15rem; color: #f87171; margin-bottom: 12px;">Areas to Strengthen</h3>
                    <ul style="list-style: disc inside; color: var(--text-secondary); line-height: 1.6; margin-bottom: 16px;">
                        ${(report.weak_areas || []).map(w => `<li>${w}</li>`).join("")}
                    </ul>

                    <h3 style="font-size: 1.15rem; color: var(--info); margin-bottom: 12px;">Recommended Preparation Strategy</h3>
                    <ul style="list-style: disc inside; color: var(--text-secondary); line-height: 1.6;">
                        ${(report.recommendations || []).map(r => `<li>${r}</li>`).join("")}
                    </ul>
                </div>

                <div style="display: flex; justify-content: center; gap: 16px; margin-top: 24px;">
                    <a href="/pages/dashboard.html" class="btn btn-primary btn-lg">Return to Dashboard ➔</a>
                    <button class="btn btn-outline btn-lg" onclick="window.print()">Print Report / Save PDF</button>
                </div>
            </div>
        `;

    } catch (err) {
        showToast("error", "Failed to render final simulation report.");
    }
}
