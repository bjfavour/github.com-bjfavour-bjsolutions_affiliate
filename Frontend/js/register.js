document.addEventListener("DOMContentLoaded", () => {
  const registerBtn = document.getElementById("registerBtn");
  const errorMessage = document.getElementById("errormessage");
  const loader = document.getElementById("loader");

  registerBtn.addEventListener("click", async () => {
    const username = document.getElementById("username").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    // Reset UI
    errorMessage.style.color = "red";
    errorMessage.textContent = "";
    loader.style.display = "block";

    if (!username || !phone || !email || !password) {
      errorMessage.textContent = "All fields are required!";
      loader.style.display = "none";
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/api/accounts/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, phone, email, password }),
      });

      const data = await response.json();
      loader.style.display = "none";

      if (response.ok) {
        // ✅ Show success message briefly
        errorMessage.style.color = "green";
        errorMessage.textContent = "Registration successful! Redirecting...";
        
        // 🔑 Immediately redirect
        window.location.href = "/Frontend/login.html";
      } else {
        errorMessage.textContent = data.error || "Registration failed. Please try again.";
      }
    } catch (err) {
      loader.style.display = "none";
      errorMessage.textContent = "Network error. Please try again.";
      console.error("Error:", err);
    }
  });
});
