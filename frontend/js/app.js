/**
 * AI Placement Coach - App Common Utilities & Helpers
 */

// Toast Notifications System
function showToast(type = "info", message = "") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let iconSvg = "";
    if (type === "success") {
        iconSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;
    } else if (type === "error") {
        iconSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`;
    } else if (type === "warning") {
        iconSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
    } else {
        iconSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
    }

    toast.innerHTML = `
        ${iconSvg}
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(20px)";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Auth State Protections
function getUser() {
    try {
        const u = localStorage.getItem("user");
        return u ? JSON.parse(u) : null;
    } catch {
        return null;
    }
}

function requireAuth() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/pages/login.html";
        return false;
    }
    return true;
}

function redirectIfAuth() {
    const token = localStorage.getItem("token");
    if (token) {
        window.location.href = "/pages/dashboard.html";
        return true;
    }
    return false;
}

async function handleLogout() {
    try {
        await window.api.logout();
    } catch (e) {
        // ignore
    }
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/pages/login.html";
}

// Text-to-Speech (SpeechSynthesis API)
function speakText(text, onStart = null, onEnd = null) {
    if (!('speechSynthesis' in window)) {
        console.warn("SpeechSynthesis is not supported in this browser.");
        if (onEnd) onEnd();
        return;
    }

    window.speechSynthesis.cancel(); // cancel any active speech

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    // Pick English natural voice if available
    const voices = window.speechSynthesis.getVoices();
    const naturalVoice = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("English")));
    if (naturalVoice) {
        utterance.voice = naturalVoice;
    }

    if (onStart) utterance.onstart = onStart;
    if (onEnd) utterance.onend = onEnd;
    utterance.onerror = (e) => {
        console.warn("TTS Error:", e);
        if (onEnd) onEnd();
    };

    window.speechSynthesis.speak(utterance);
}

function stopSpeaking() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
}

// Speech Recognition Helper
function createSpeechRecognizer(onResult, onEnd, onError) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        return null;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        if (onResult) onResult(transcript);
    };

    recognition.onerror = (event) => {
        console.error("Speech Recognition Error:", event.error);
        if (onError) onError(event.error);
    };

    recognition.onend = () => {
        if (onEnd) onEnd();
    };

    return recognition;
}

// Global active navigation link updater
document.addEventListener("DOMContentLoaded", () => {
    // Populate user profile info in navbar if present
    const user = getUser();
    const userNameEls = document.querySelectorAll(".user-name-display");
    if (user && userNameEls) {
        userNameEls.forEach(el => el.textContent = user.name || "Student");
    }

    // Logout buttons
    const logoutBtns = document.querySelectorAll(".logout-btn");
    logoutBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            handleLogout();
        });
    });

    // Check query params for expired session
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("expired")) {
        showToast("warning", "Your session has expired. Please log in again.");
    }
});
