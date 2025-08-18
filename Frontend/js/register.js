document.addEventListener("DOMContentLoaded", () => {
  const registerBtn = document.getElementById("registerBtn");
  const errorMessage = document.getElementById("errormessage");
  const loader = document.getElementById("loader");

  registerBtn.addEventListener("click", async () => {
    // Clear messages
    errorMessage.textContent = "";

    // Get input values
    const username = document.getElementById("username").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    // Simple validation
    if (!username || !phone || !email || !password) {
      errorMessage.textContent = "All fields are required!";
      return;
    }

    // Show loader
    loader.style.display = "block";
    registerBtn.disabled = true;

    try {
      const response = await fetch("http://127.0.0.1:8000/api/accounts/register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          phone,
          email,
          password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        alert("✅ Registration successful! Please login.");
        window.location.href = "/frontend/login.html"; // redirect to login
      } else {
        errorMessage.textContent = data.error || "❌ Registration failed!";
      }
    } catch (error) {
      errorMessage.textContent = "⚠️ Network error. Please try again.";
    } finally {
      loader.style.display = "none";
      registerBtn.disabled = false;
    }
  });
});
