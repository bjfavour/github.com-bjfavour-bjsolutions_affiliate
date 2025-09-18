const API_URL = "http://127.0.0.1:8000/api/accounts/login/";
const errormessage = document.getElementById("errormessage");

document.addEventListener("DOMContentLoaded", () => {
  const loginButton = document.querySelector(".button1");

  // ✅ LOGIN FUNCTIONALITY
  loginButton.addEventListener("click", async (e) => {
    e.preventDefault();

    const username = document.querySelectorAll(".userinput")[0].value.trim();
    const password = document.querySelectorAll(".userinput")[1].value.trim();

    errormessage.textContent = "";

    if (!username || !password) {
      errormessage.style.color = "red";
      errormessage.textContent = "Please enter both username and password.";
      return;
    }

    try {
      errormessage.style.color = "blue";
      errormessage.textContent = "Logging in, please wait...";

      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ identifier: username, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Login failed.");
      }

      // ✅ Save tokens
      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);

      // ✅ Save user info and username separately
      if (data.user) {
        localStorage.setItem("user", JSON.stringify(data.user));
        localStorage.setItem("username", data.user.username);
      }

      errormessage.style.color = "green";
      errormessage.textContent = "Login successful! Redirecting...";

      // ✅ Redirect to dashboard
      window.location.href = "/Frontend/dashboard.html";

    } catch (err) {
      errormessage.style.color = "red";
      errormessage.textContent = err.message;
    }
  });

  // ✅ Trigger login on Enter key
  document.querySelectorAll(".userinput").forEach((input) => {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        loginButton.click(); // simulate button click
      }
    });
  });

  // ✅ HAMBURGER MENU TOGGLE
  const menuBtn = document.querySelector(".bi-list");
  const navMenu = document.querySelector(".nav_display2");

  if (menuBtn && navMenu) {
    menuBtn.addEventListener("click", () => {
      navMenu.style.display = (navMenu.style.display === "block") ? "none" : "block";
    });
  }
});
