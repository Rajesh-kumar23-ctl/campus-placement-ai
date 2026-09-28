/**
 * Group Discussion Simulator Arena Controller
 */

let simState = {
    sessionId: null,
    topic: "",
    durationSeconds: 300,
    timeRemaining: 300,
    timerInterval: null,
    isRecording: false,
    recognizer: null,
    turnCount: 0
};

document.addEventListener("DOMContentLoaded", () => {
    if (!requireAuth()) return;

    const urlParams = new URLSearchParams(window.location.search);
    const topicParam = urlParams.get("topic");

    if (topicParam) {
        document.getElementById("sim-topic-input").value = decodeURIComponent(topicParam);
    }

    setupStartModal();
    setupControls();
});

function setupStartModal() {
    const startBtn = document.getElementById("btn-begin-simulation");
    if (startBtn) {
        startBtn.addEventListener("click", async () => {
            const topic = document.getElementById("sim-topic-input").value.trim();
            const duration = parseInt(document.getElementById("sim-duration-select").value, 10) || 5;
            const diff = document.getElementById("sim-diff-select").value;

            if (!topic) {
                showToast("warning", "Please provide a topic for discussion.");
                return;
            }

            startBtn.disabled = true;
            startBtn.innerHTML = `<span class="spinner"></span> Assembling Participants...`;

            try {
                const res = await window.api.startGD({
                    topic: topic,
                    duration_minutes: duration,
                    difficulty: diff,
                    num_participants: 3
                });

                simState.sessionId = res.session_id;
                simState.topic = res.topic;
                simState.durationSeconds = duration * 60;
                simState.timeRemaining = duration * 60;

                // Hide setup, show arena
                document.getElementById("gd-setup-card").style.display = "none";
                document.getElementById("gd-arena-container").style.display = "flex";

                document.getElementById("arena-topic-heading").textContent = simState.topic;

                // Render initial moderator and participant 1 messages
                const chatWindow = document.getElementById("gd-chat-window");
                chatWindow.innerHTML = "";

                for (const msg of res.initial_messages) {
                    appendMessage(msg.speaker, msg.message);
                }

                // Speak moderator opening
                if (res.initial_messages.length > 0) {
                    highlightSpeaker("Moderator");
                    speakText(res.initial_messages[0].message, null, () => {
                        highlightSpeaker("Participant 1 (Aarav)");
                    });
                }

                startTimer();

            } catch (err) {
                showToast("error", err.message || "Failed to start simulation.");
                startBtn.disabled = false;
                startBtn.textContent = "Enter Discussion Arena";
            }
        });
    }
}

function startTimer() {
    updateTimerText();
    simState.timerInterval = setInterval(() => {
        simState.timeRemaining--;
        updateTimerText();
        if (simState.timeRemaining <= 0) {
            clearInterval(simState.timerInterval);
            showToast("warning", "Discussion time completed! Generating evaluation...");
            evaluateDiscussion();
        }
    }, 1000);
}

function updateTimerText() {
    const timerEl = document.getElementById("gd-timer-display");
    if (!timerEl) return;
    const mins = Math.floor(simState.timeRemaining / 60);
    const secs = simState.timeRemaining % 60;
    timerEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function setupControls() {
    const micBtn = document.getElementById("btn-toggle-mic");
    const sendBtn = document.getElementById("btn-send-message");
    const inputField = document.getElementById("gd-user-input");
    const endBtn = document.getElementById("btn-end-gd");

    // Speech Recognition Setup
    simState.recognizer = createSpeechRecognizer(
        (transcript) => {
            if (inputField) inputField.value = transcript;
        },
        () => {
            simState.isRecording = false;
            micBtn?.classList.remove("recording");
        },
        (error) => {
            simState.isRecording = false;
            micBtn?.classList.remove("recording");
            showToast("warning", "Voice recognition stopped or unavailable. You can type your points.");
        }
    );

    if (micBtn) {
        micBtn.addEventListener("click", () => {
            if (!simState.recognizer) {
                showToast("info", "Voice recognition is unavailable in this browser. Use text mode instead.");
                return;
            }

            if (!simState.isRecording) {
                try {
                    simState.recognizer.start();
                    simState.isRecording = true;
                    micBtn.classList.add("recording");
                    showToast("info", "Listening... Speak your point clearly.");
                } catch (e) {
                    console.warn(e);
                }
            } else {
                simState.recognizer.stop();
                simState.isRecording = false;
                micBtn.classList.remove("recording");
            }
        });
    }

    if (sendBtn) {
        sendBtn.addEventListener("click", () => submitUserPoint());
    }

    if (inputField) {
        inputField.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submitUserPoint();
            }
        });
    }

    if (endBtn) {
        endBtn.addEventListener("click", () => {
            if (confirm("Are you ready to conclude the discussion and receive your AI evaluation?")) {
                evaluateDiscussion();
            }
        });
    }
}

async function submitUserPoint() {
    const inputField = document.getElementById("gd-user-input");
    const userText = inputField.value.trim();
    if (!userText) {
        showToast("warning", "Please articulate a point before submitting.");
        return;
    }

    // Stop recording if active
    if (simState.isRecording && simState.recognizer) {
        simState.recognizer.stop();
        simState.isRecording = false;
        document.getElementById("btn-toggle-mic")?.classList.remove("recording");
    }

    // Append User speech to chat
    appendMessage("User", userText);
    inputField.value = "";
    highlightSpeaker("User");

    // Call API for participants reaction
    const sendBtn = document.getElementById("btn-send-message");
    if (sendBtn) sendBtn.disabled = true;

    try {
        const res = await window.api.submitGDResponse({
            session_id: simState.sessionId,
            user_response: userText,
            turn: ++simState.turnCount
        });

        // Queue simulated participant responses
        if (res.ai_responses && res.ai_responses.length > 0) {
            playParticipantTurns(res.ai_responses);
        }

    } catch (err) {
        showToast("error", "Failed to register point. Please try again.");
    } finally {
        if (sendBtn) sendBtn.disabled = false;
    }
}

function playParticipantTurns(responses) {
    let delay = 600;
    responses.forEach((r, idx) => {
        setTimeout(() => {
            appendMessage(r.speaker, r.message);
            highlightSpeaker(r.speaker);
            speakText(r.message, null, () => {
                highlightSpeaker(null);
            });
        }, delay * (idx + 1));
    });
}

function appendMessage(speaker, message) {
    const chatWindow = document.getElementById("gd-chat-window");
    if (!chatWindow) return;

    const wrap = document.createElement("div");
    const isUser = speaker.toLowerCase().includes("user");
    const isMod = speaker.toLowerCase().includes("moderator");

    wrap.className = `chat-bubble-wrap ${isUser ? "user" : (isMod ? "moderator" : "ai")}`;

    wrap.innerHTML = `
        <div class="chat-bubble">
            <div class="bubble-speaker">${speaker}</div>
            <div class="bubble-text">${message}</div>
        </div>
    `;

    chatWindow.appendChild(wrap);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function highlightSpeaker(speakerName) {
    const badges = document.querySelectorAll(".participant-badge");
    badges.forEach(b => {
        if (speakerName && b.dataset.speaker && b.dataset.speaker.toLowerCase().includes(speakerName.toLowerCase())) {
            b.classList.add("active-speaker");
        } else {
            b.classList.remove("active-speaker");
        }
    });
}

async function evaluateDiscussion() {
    clearInterval(simState.timerInterval);
    stopSpeaking();

    const endBtn = document.getElementById("btn-end-gd");
    if (endBtn) {
        endBtn.disabled = true;
        endBtn.innerHTML = `<span class="spinner"></span> Evaluating Performance...`;
    }

    try {
        const evalData = await window.api.evaluateGD(simState.sessionId);
        renderEvaluationModal(evalData);
    } catch (err) {
        showToast("error", err.message || "Failed to evaluate GD session.");
        if (endBtn) {
            endBtn.disabled = false;
            endBtn.textContent = "Conclude & Evaluate";
        }
    }
}

function renderEvaluationModal(data) {
    document.getElementById("eval-score-overall").textContent = `${Math.round(data.overall)}%`;
    document.getElementById("eval-content").textContent = `${data.content}/10`;
    document.getElementById("eval-relevance").textContent = `${data.relevance}/10`;
    document.getElementById("eval-clarity").textContent = `${data.clarity}/10`;
    document.getElementById("eval-structure").textContent = `${data.structure}/10`;
    document.getElementById("eval-fluency").textContent = `${data.fluency}/10`;

    const strengthsEl = document.getElementById("eval-strengths-list");
    if (strengthsEl) {
        strengthsEl.innerHTML = (data.strengths || []).map(s => `<li>${s}</li>`).join("");
    }

    const improvementsEl = document.getElementById("eval-improvements-list");
    if (improvementsEl) {
        improvementsEl.innerHTML = (data.improvements || []).map(i => `<li>${i}</li>`).join("");
    }

    const betterEl = document.getElementById("eval-better-response");
    if (betterEl) {
        betterEl.textContent = data.better_response || "";
    }

    document.getElementById("gd-eval-modal").classList.add("active");
}
