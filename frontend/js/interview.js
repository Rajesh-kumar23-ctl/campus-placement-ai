/**
 * AI Mock Interview Room Controller
 */

let interviewState = {
    sessionId: null,
    currentQuestionId: null,
    questionNumber: 1,
    totalQuestions: 5,
    interviewType: "technical",
    targetRole: "Software Developer",
    difficulty: "medium",
    isRecording: false,
    recognizer: null,
    startTime: null,
    answeredHistory: []
};

document.addEventListener("DOMContentLoaded", () => {
    if (!requireAuth()) return;

    setupInterviewModal();
    setupAnswerControls();
});

function setupInterviewModal() {
    const startBtn = document.getElementById("btn-start-interview-session");
    if (!startBtn) return;

    // Check query params for quick pre-selected track or resume
    const urlParams = new URLSearchParams(window.location.search);
    const trackParam = urlParams.get("track");
    const resumeParam = urlParams.get("resume_id");

    if (trackParam) {
        const typeSelect = document.getElementById("interview-type-select");
        if (typeSelect) typeSelect.value = trackParam;
    }

    startBtn.addEventListener("click", async () => {
        const interviewType = document.getElementById("interview-type-select").value;
        const targetRole = document.getElementById("target-role-input").value.trim() || "Software Developer";
        const difficulty = document.getElementById("interview-diff-select").value;
        const useResume = document.getElementById("use-resume-checkbox")?.checked || false;

        startBtn.disabled = true;
        startBtn.innerHTML = `<span class="spinner"></span> AI is preparing your interview...`;

        try {
            const res = await window.api.startInterview({
                interview_type: interviewType,
                target_role: targetRole,
                difficulty: difficulty,
                use_resume: useResume,
                resume_id: resumeParam || null,
                total_questions: 5
            });

            interviewState.sessionId = res.session_id;
            interviewState.interviewType = res.interview_type;
            interviewState.targetRole = res.target_role;
            interviewState.difficulty = res.difficulty;
            interviewState.totalQuestions = res.total_questions || 5;

            // Transition UI from Setup to Interview Room
            document.getElementById("interview-setup-card").style.display = "none";
            document.getElementById("interview-room-stage").style.display = "grid";

            document.getElementById("stage-role-text").textContent = `${res.target_role} • ${res.interview_type.toUpperCase()}`;

            // Load Question 1
            loadQuestion(res.first_question);

        } catch (err) {
            showToast("error", err.message || "Failed to start interview.");
            startBtn.disabled = false;
            startBtn.textContent = "Start AI Interview";
        }
    });
}

function loadQuestion(qData) {
    interviewState.currentQuestionId = qData.question_id;
    interviewState.questionNumber = qData.question_number;
    interviewState.startTime = Date.now();

    // UI Updates
    document.getElementById("question-counter-badge").textContent = `Question ${qData.question_number} / ${interviewState.totalQuestions}`;
    document.getElementById("question-category-tag").textContent = qData.category || "General";
    document.getElementById("active-question-text").textContent = qData.question;

    // Reset Answer Area
    const answerField = document.getElementById("interview-answer-text");
    if (answerField) answerField.value = "";

    // Speak Question with AI Voice
    playAiSpeech(qData.question);
}

function playAiSpeech(text) {
    const avatarFrame = document.querySelector(".ai-avatar-frame");
    const visualizer = document.getElementById("voice-visualizer");

    avatarFrame?.classList.add("speaking");
    visualizer?.classList.add("active");

    speakText(text, null, () => {
        avatarFrame?.classList.remove("speaking");
        visualizer?.classList.remove("active");
    });
}

function setupAnswerControls() {
    const micBtn = document.getElementById("btn-voice-record");
    const answerField = document.getElementById("interview-answer-text");
    const submitBtn = document.getElementById("btn-submit-answer");
    const endBtn = document.getElementById("btn-force-end");

    // Speech Recognition
    interviewState.recognizer = createSpeechRecognizer(
        (transcript) => {
            if (answerField) answerField.value = transcript;
        },
        () => {
            interviewState.isRecording = false;
            micBtn?.classList.remove("btn-danger");
            micBtn?.classList.add("btn-outline");
            if (micBtn) micBtn.innerHTML = `🎙️ Start Answer`;
        },
        (error) => {
            interviewState.isRecording = false;
            micBtn?.classList.remove("btn-danger");
            micBtn?.classList.add("btn-outline");
            if (micBtn) micBtn.innerHTML = `🎙️ Start Answer`;
            showToast("info", "Voice recognition ended. You can review or edit your answer in the text box.");
        }
    );

    if (micBtn) {
        micBtn.addEventListener("click", () => {
            if (!interviewState.recognizer) {
                showToast("info", "Voice mode is unavailable in this browser. Use text mode instead.");
                return;
            }

            if (!interviewState.isRecording) {
                try {
                    stopSpeaking(); // mute AI if speaking
                    interviewState.recognizer.start();
                    interviewState.isRecording = true;
                    micBtn.classList.remove("btn-outline");
                    micBtn.classList.add("btn-danger");
                    micBtn.innerHTML = `⏹️ Stop Recording`;
                    showToast("info", "Listening to your answer... Speak clearly.");
                } catch (e) {
                    console.warn(e);
                }
            } else {
                interviewState.recognizer.stop();
                interviewState.isRecording = false;
                micBtn.classList.remove("btn-danger");
                micBtn.classList.add("btn-outline");
                micBtn.innerHTML = `🎙️ Start Answer`;
            }
        });
    }

    if (submitBtn) {
        submitBtn.addEventListener("click", () => submitCandidateAnswer());
    }

    if (endBtn) {
        endBtn.addEventListener("click", () => {
            if (confirm("Conclude this interview and view your evaluation report now?")) {
                concludeInterview();
            }
        });
    }
}

async function submitCandidateAnswer() {
    const answerField = document.getElementById("interview-answer-text");
    const answer = answerField.value.trim();

    if (!answer) {
        showToast("warning", "Please provide your answer before submitting.");
        return;
    }

    // Stop recording if active
    if (interviewState.isRecording && interviewState.recognizer) {
        interviewState.recognizer.stop();
        interviewState.isRecording = false;
        const micBtn = document.getElementById("btn-voice-record");
        micBtn?.classList.remove("btn-danger");
        micBtn?.classList.add("btn-outline");
        if (micBtn) micBtn.innerHTML = `🎙️ Start Answer`;
    }

    const submitBtn = document.getElementById("btn-submit-answer");
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner"></span> AI is analyzing your answer...`;

    const timeTaken = Math.round((Date.now() - (interviewState.startTime || Date.now())) / 1000);

    try {
        const res = await window.api.submitInterviewAnswer({
            session_id: interviewState.sessionId,
            question_id: interviewState.currentQuestionId,
            answer: answer,
            time_taken_seconds: timeTaken
        });

        // Add to history sidebar
        appendHistoryItem(interviewState.questionNumber, res.overall_score, res.feedback);

        showToast("success", `Answer evaluated: ${Math.round(res.overall_score)}%`);

        submitBtn.disabled = false;
        submitBtn.innerHTML = `Submit Answer ➔`;

        if (res.is_last_question || !res.next_question) {
            showToast("info", "All interview questions answered! Compiling your final preparation report...");
            setTimeout(() => {
                concludeInterview();
            }, 1000);
        } else {
            // Load next question
            loadQuestion(res.next_question);
        }

    } catch (err) {
        showToast("error", err.message || "Failed to submit answer.");
        submitBtn.disabled = false;
        submitBtn.innerHTML = `Submit Answer ➔`;
    }
}

function appendHistoryItem(qNum, score, feedback) {
    const list = document.getElementById("context-history-list");
    if (!list) return;

    const item = document.createElement("div");
    item.className = "context-history-item";
    item.innerHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span class="context-q">Question ${qNum}</span>
            <span class="context-score-tag">${Math.round(score)}%</span>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-secondary); margin: 0;">${feedback ? feedback.slice(0, 100) + '...' : ''}</p>
    `;
    list.appendChild(item);
}

async function concludeInterview() {
    stopSpeaking();
    try {
        const finalReport = await window.api.endInterview(interviewState.sessionId);
        window.location.href = `/pages/interview-result.html?id=${finalReport.id}`;
    } catch (err) {
        showToast("error", err.message || "Failed to finalize report.");
    }
}
