/**
 * Aptitude Test Taker Controller
 */

let testState = {
    questions: [],
    currentIndex: 0,
    userAnswers: {}, // questionId -> selectedOptionText
    flagged: {}, // questionId -> boolean
    timeRemaining: 0,
    timerInterval: null,
    totalTimeTaken: 0,
    category: "all",
    difficulty: "all"
};

document.addEventListener("DOMContentLoaded", () => {
    if (!requireAuth()) return;

    // Check if test is being started or if setup modal should be shown
    initSetupModal();
});

function initSetupModal() {
    const startBtn = document.getElementById("start-test-btn");
    if (startBtn) {
        startBtn.addEventListener("click", async () => {
            const cat = document.getElementById("select-category").value;
            const diff = document.getElementById("select-difficulty").value;
            const numQ = parseInt(document.getElementById("select-count").value, 10) || 10;
            const timeMins = parseInt(document.getElementById("select-timer").value, 10) || 15;

            startBtn.disabled = true;
            startBtn.innerHTML = `<span class="spinner"></span> Loading Questions...`;

            try {
                const questions = await window.api.startAptitude({
                    category: cat,
                    difficulty: diff,
                    num_questions: numQ,
                    timer_minutes: timeMins
                });

                if (!questions || questions.length === 0) {
                    showToast("error", "No questions found for selected criteria.");
                    startBtn.disabled = false;
                    startBtn.textContent = "Start Assessment";
                    return;
                }

                // Initialize test state
                testState.questions = questions;
                testState.currentIndex = 0;
                testState.userAnswers = {};
                testState.flagged = {};
                testState.timeRemaining = timeMins * 60;
                testState.totalTimeTaken = 0;
                testState.category = cat;
                testState.difficulty = diff;

                // Hide setup modal, show test interface
                document.getElementById("test-setup-container").style.display = "none";
                document.getElementById("test-runner-container").style.display = "block";

                renderPalette();
                loadQuestion(0);
                startTimer();

            } catch (err) {
                showToast("error", err.message || "Failed to start test.");
                startBtn.disabled = false;
                startBtn.textContent = "Start Assessment";
            }
        });
    }

    // Question Navigation Buttons
    document.getElementById("btn-prev")?.addEventListener("click", () => {
        if (testState.currentIndex > 0) {
            loadQuestion(testState.currentIndex - 1);
        }
    });

    document.getElementById("btn-next")?.addEventListener("click", () => {
        if (testState.currentIndex < testState.questions.length - 1) {
            loadQuestion(testState.currentIndex + 1);
        }
    });

    document.getElementById("btn-flag")?.addEventListener("click", () => {
        const q = testState.questions[testState.currentIndex];
        testState.flagged[q.id] = !testState.flagged[q.id];
        updatePaletteItem(testState.currentIndex);
        updateFlagButton();
    });

    document.getElementById("btn-submit-test")?.addEventListener("click", () => {
        confirmSubmission();
    });
}

function startTimer() {
    updateTimerDisplay();
    testState.timerInterval = setInterval(() => {
        testState.timeRemaining--;
        testState.totalTimeTaken++;
        updateTimerDisplay();

        if (testState.timeRemaining <= 0) {
            clearInterval(testState.timerInterval);
            showToast("warning", "Time is up! Submitting test automatically...");
            submitTest();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const timerEl = document.getElementById("timer-display");
    if (!timerEl) return;

    const mins = Math.floor(testState.timeRemaining / 60);
    const secs = testState.timeRemaining % 60;
    timerEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

    if (testState.timeRemaining < 120) {
        timerEl.classList.add("timer-warning");
    }
}

function loadQuestion(index) {
    testState.currentIndex = index;
    const q = testState.questions[index];
    if (!q) return;

    // Header counter
    document.getElementById("question-counter").textContent = `Question ${index + 1} of ${testState.questions.length}`;
    document.getElementById("question-category-badge").textContent = q.category_display || q.category;
    document.getElementById("question-difficulty-badge").textContent = q.difficulty.toUpperCase();

    // Text
    document.getElementById("question-text").textContent = q.question;

    // Options
    const optionsContainer = document.getElementById("options-container");
    optionsContainer.innerHTML = "";

    const selectedAnswer = testState.userAnswers[q.id];

    q.options.forEach((optText, optIdx) => {
        const optEl = document.createElement("div");
        optEl.className = `option-item ${selectedAnswer === optText ? "selected" : ""}`;
        optEl.innerHTML = `
            <div class="option-indicator"></div>
            <div class="option-text">${optText}</div>
        `;
        optEl.addEventListener("click", () => {
            selectOption(q.id, optText);
        });
        optionsContainer.appendChild(optEl);
    });

    // Update Nav buttons
    document.getElementById("btn-prev").disabled = (index === 0);
    const nextBtn = document.getElementById("btn-next");
    if (index === testState.questions.length - 1) {
        nextBtn.style.display = "none";
    } else {
        nextBtn.style.display = "inline-flex";
    }

    updateFlagButton();
    updatePaletteCurrent();
}

function selectOption(questionId, optionText) {
    testState.userAnswers[questionId] = optionText;

    // Update options UI
    const optionEls = document.querySelectorAll(".option-item");
    optionEls.forEach(el => {
        if (el.querySelector(".option-text").textContent === optionText) {
            el.classList.add("selected");
        } else {
            el.classList.remove("selected");
        }
    });

    updatePaletteItem(testState.currentIndex);
}

function updateFlagButton() {
    const q = testState.questions[testState.currentIndex];
    const flagBtn = document.getElementById("btn-flag");
    if (!flagBtn || !q) return;

    if (testState.flagged[q.id]) {
        flagBtn.innerHTML = `🚩 Unmark Review`;
        flagBtn.classList.add("btn-secondary");
    } else {
        flagBtn.innerHTML = `🏳️ Mark for Review`;
        flagBtn.classList.remove("btn-secondary");
    }
}

function renderPalette() {
    const paletteGrid = document.getElementById("palette-grid");
    if (!paletteGrid) return;

    paletteGrid.innerHTML = "";
    testState.questions.forEach((q, idx) => {
        const btn = document.createElement("button");
        btn.className = "palette-btn";
        btn.textContent = idx + 1;
        btn.id = `palette-btn-${idx}`;
        btn.addEventListener("click", () => {
            loadQuestion(idx);
        });
        paletteGrid.appendChild(btn);
    });
}

function updatePaletteItem(idx) {
    const btn = document.getElementById(`palette-btn-${idx}`);
    const q = testState.questions[idx];
    if (!btn || !q) return;

    btn.className = "palette-btn";

    if (testState.flagged[q.id]) {
        btn.classList.add("flagged");
    } else if (testState.userAnswers[q.id]) {
        btn.classList.add("answered");
    }

    if (idx === testState.currentIndex) {
        btn.classList.add("current");
    }
}

function updatePaletteCurrent() {
    testState.questions.forEach((_, idx) => updatePaletteItem(idx));
}

function confirmSubmission() {
    const answeredCount = Object.keys(testState.userAnswers).length;
    const totalCount = testState.questions.length;
    const unanswered = totalCount - answeredCount;

    let confirmMsg = `You have answered ${answeredCount} of ${totalCount} questions.`;
    if (unanswered > 0) {
        confirmMsg += `\n${unanswered} questions are still unanswered.`;
    }
    confirmMsg += `\nAre you sure you want to finish and submit?`;

    if (confirm(confirmMsg)) {
        submitTest();
    }
}

async function submitTest() {
    clearInterval(testState.timerInterval);

    const submitBtn = document.getElementById("btn-submit-test");
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner"></span> Grading...`;
    }

    const payload = {
        category: testState.category,
        difficulty: testState.difficulty,
        time_taken: testState.totalTimeTaken,
        answers: testState.questions.map(q => ({
            question_id: q.id,
            selected_answer: testState.userAnswers[q.id] || null,
            time_taken: 0
        }))
    };

    try {
        const result = await window.api.submitAptitude(payload);
        showToast("success", `Assessment complete! Score: ${result.score}%`);
        setTimeout(() => {
            window.location.href = `/pages/aptitude-result.html?id=${result.id}`;
        }, 800);
    } catch (err) {
        showToast("error", err.message || "Submission failed. Please try again.");
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "Submit Test";
        }
    }
}
