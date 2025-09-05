// dashboard.js

const API_BASE = "http://127.0.0.1:8000/api/accounts"; 
const token = localStorage.getItem("access");

// 🚨 Redirect if not logged in
if (!token) {
  window.location.href = "/Frontend/login.html";
}

// Attach Authorization header helper
function authHeaders(extra = {}) {
  return {
    "Authorization": `Bearer ${token}`,
    ...extra
  };
}

// ================= PROFILE =================
async function loadProfile() {
  try {
    const res = await fetch(`${API_BASE}/profile/`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error("Failed to fetch profile");

    const profile = await res.json();

    document.getElementById("affiliateName").textContent = profile.full_name || profile.username;
    document.getElementById("updateName").value = profile.full_name || "";
    document.getElementById("updateEmail").value = profile.email || "";
    document.getElementById("bankName").value = profile.bank_name || "";
    document.getElementById("accountNumber").value = profile.bank_account || "";
    document.getElementById("accountName").value = profile.beneficiary_name || "";

    if (profile.profile_picture) {
      document.getElementById("profile-image").src = profile.profile_picture;
    }
  } catch (err) {
    console.error(err);
  }
}

async function updateProfile() {
  const name = document.getElementById("updateName").value;
  const email = document.getElementById("updateEmail").value;
  const bankName = document.getElementById("bankName").value;
  const accountNumber = document.getElementById("accountNumber").value;
  const accountName = document.getElementById("accountName").value;
  const profilePic = document.getElementById("uploadPic").files[0];

  const formData = new FormData();
  if (name) formData.append("full_name", name);
  if (email) formData.append("email", email);
  if (bankName) formData.append("bank_name", bankName);
  if (accountNumber) formData.append("bank_account", accountNumber);
  if (accountName) formData.append("beneficiary_name", accountName);
  if (profilePic) formData.append("profile_picture", profilePic);

  try {
    const response = await fetch(`${API_BASE}/profile/`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to update profile");
    }

    alert("Profile updated successfully!");
    loadProfile();
  } catch (err) {
    alert(err.message);
  }
}

// ================= DASHBOARD OVERVIEW =================
async function loadDashboard() {
  try {
    const res = await fetch(`${API_BASE}/dashboard/`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error("Failed to fetch dashboard data");
    const data = await res.json();

    document.getElementById("totalCashout").textContent = data.total_cashout || 0;

    if (data.commission_history) {
      renderCommissionChart(data.commission_history);
    }
  } catch (err) {
    console.error(err);
  }
}

// ================= CASHOUT =================
async function loadCashoutHistory() {
  try {
    const res = await fetch(`${API_BASE}/cashout/`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error("Failed to fetch cashout history");

    const data = await res.json(); // contains commission_balance + cashout_history
    const history = data.cashout_history || [];

    const tbody = document.getElementById("cashoutTableBody");
    tbody.innerHTML = "";
    history.forEach(row => {
      tbody.innerHTML += `
        <tr>
          <td>${row.requested_amount}</td>
          <td>${row.processing_fee}</td>
          <td>${row.net_amount}</td>
          <td>${row.date}</td>
          <td>${row.status}</td>
        </tr>
      `;
    });

  } catch (err) {
    console.error("Error loading history", err);
  }
}

document.getElementById("cashoutForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const amount = document.getElementById("cashoutAmount").value;
  try {
    const res = await fetch(`${API_BASE}/cashout/`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ requested_amount: amount }) // ✅ must match backend
    });
    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Cashout request failed");
    }
    alert("Cashout requested successfully!");
    loadDashboard();
    loadCashoutHistory();
  } catch (err) {
    alert(err.message);
  }
});

// ================= MARKETING MATERIAL =================
async function loadMarketingMaterials() {
  try {
    const res = await fetch(`${API_BASE}/marketing-materials/`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error("Failed to fetch marketing materials");
    const data = await res.json();

    const videoList = document.getElementById("videoList");
    const pictureList = document.getElementById("pictureList");

    videoList.innerHTML = "";
    pictureList.innerHTML = "";

    (data.video || []).forEach(v => {
      videoList.innerHTML += `<video controls src="${v.file}"></video>`;
    });

    (data.image || []).forEach(p => {
      pictureList.innerHTML += `<img src="${p.file}" alt="Material" />`;
    });
  } catch (err) {
    console.error("Error loading materials", err);
  }
}

// ================= COMMISSION CHART =================
function renderCommissionChart(history) {
  const ctx = document.getElementById("commissionChart").getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: history.map(h => h.date),
      datasets: [{
        label: "Commission",
        data: history.map(h => h.amount),
        borderWidth: 2,
        fill: false,
        borderColor: "blue"
      }]
    }
  });
}

// ================= LOGOUT =================
function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  window.location.href = "/Frontend/login.html";
}
window.logout = logout;

// ================= INIT =================
window.onload = () => {
  loadProfile();
  loadDashboard();
  loadCashoutHistory();
  loadMarketingMaterials();
};
