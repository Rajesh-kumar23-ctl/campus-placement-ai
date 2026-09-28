/**
 * Auth JavaScript - Login and Registration Controller
 */

document.addEventListener("DOMContentLoaded", () => {
    // If user is already logged in, redirect to dashboard
    redirectIfAuth();

    // Login Form Handler
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = loginForm.querySelector("button[type='submit']");
            const originalBtnText = submitBtn.innerHTML;

            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span class="spinner"></span> Logging in...`;

                const res = await window.api.login({ email, password });
                localStorage.setItem("token", res.access_token);
                localStorage.setItem("user", JSON.stringify(res.user));

                showToast("success", `Welcome back, ${res.user.name}!`);
                setTimeout(() => {
                    window.location.href = "/pages/dashboard.html";
                }, 600);
            } catch (err) {
                showToast("error", err.message || "Login failed. Please verify your credentials.");
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }

    // Register Form Handler
    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = registerForm.querySelector("button[type='submit']");
            const originalBtnText = submitBtn.innerHTML;

            const name = document.getElementById("name").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            const college = document.getElementById("college")?.value.trim() || "";
            const degree = document.getElementById("degree")?.value.trim() || "";
            const branch = document.getElementById("branch")?.value.trim() || "";
            const gradYearVal = document.getElementById("graduation_year")?.value;
            const graduation_year = gradYearVal ? parseInt(gradYearVal, 10) : null;
            const target_role = document.getElementById("target_role")?.value || "Software Developer";

            if (password.length < 6) {
                showToast("warning", "Password must be at least 6 characters long.");
                return;
            }

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span class="spinner"></span> Creating Account...`;

                const res = await window.api.register({
                    name,
                    email,
                    password,
                    college,
                    degree,
                    branch,
                    graduation_year,
                    target_role
                });

                localStorage.setItem("token", res.access_token);
                localStorage.setItem("user", JSON.stringify(res.user));

                showToast("success", `Account created! Welcome, ${res.user.name}.`);
                setTimeout(() => {
                    window.location.href = "/pages/dashboard.html";
                }, 600);
            } catch (err) {
                showToast("error", err.message || "Registration failed. Please check inputs.");
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }
});
