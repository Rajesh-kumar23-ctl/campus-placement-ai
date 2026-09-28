/**
 * Profile Controller
 */

document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuth()) return;

    await loadProfile();
    setupProfileForm();
});

async function loadProfile() {
    try {
        const user = await window.api.getProfile();
        localStorage.setItem("user", JSON.stringify(user));

        document.getElementById("profile-name-header").textContent = user.name;
        document.getElementById("profile-email-header").textContent = user.email;

        document.getElementById("edit-name").value = user.name || "";
        document.getElementById("edit-email").value = user.email || "";
        document.getElementById("edit-college").value = user.college || "";
        document.getElementById("edit-degree").value = user.degree || "";
        document.getElementById("edit-branch").value = user.branch || "";
        document.getElementById("edit-grad-year").value = user.graduation_year || "";
        document.getElementById("edit-target-role").value = user.target_role || "Software Developer";

    } catch (err) {
        showToast("error", "Unable to load profile.");
    }
}

function setupProfileForm() {
    const form = document.getElementById("profile-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const saveBtn = document.getElementById("btn-save-profile");
        saveBtn.disabled = true;
        saveBtn.innerHTML = `<span class="spinner"></span> Saving...`;

        const name = document.getElementById("edit-name").value.trim();
        const college = document.getElementById("edit-college").value.trim();
        const degree = document.getElementById("edit-degree").value.trim();
        const branch = document.getElementById("edit-branch").value.trim();
        const gradYearVal = document.getElementById("edit-grad-year").value;
        const graduation_year = gradYearVal ? parseInt(gradYearVal, 10) : null;
        const target_role = document.getElementById("edit-target-role").value;

        try {
            const updated = await window.api.updateProfile({
                name,
                college,
                degree,
                branch,
                graduation_year,
                target_role
            });

            localStorage.setItem("user", JSON.stringify(updated));
            showToast("success", "Profile updated successfully!");

            document.getElementById("profile-name-header").textContent = updated.name;
            saveBtn.disabled = false;
            saveBtn.textContent = "Save Changes";

        } catch (err) {
            showToast("error", err.message || "Failed to update profile.");
            saveBtn.disabled = false;
            saveBtn.textContent = "Save Changes";
        }
    });
}
