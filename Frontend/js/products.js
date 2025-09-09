// products.js

document.addEventListener("DOMContentLoaded", function () {
  const token = localStorage.getItem("access");
  const username = localStorage.getItem("username"); // ✅ unique identifier

  if (!token) {
    alert("You must login to view products.");
    window.location.href = "login.html";
    return;
  }

  fetch("http://127.0.0.1:8000/api/accounts/products/", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  })
    .then((res) => {
      if (!res.ok) {
        return res.text().then((text) => {
          throw new Error(`Failed to load products: ${res.status} ${text}`);
        });
      }
      return res.json();
    })
    .then((products) => {
      const productGrid = document.getElementById("productGrid");

      if (!products || products.length === 0) {
        productGrid.innerHTML = "<p>No products available.</p>";
        return;
      }

      products.forEach((product) => {
        const card = document.createElement("div");
        card.className = "col";

        const price = parseFloat(product.price).toLocaleString();
        const commission = parseFloat(product.commission_amount).toLocaleString();

        // ✅ Now point to frontend details page
        const affiliateLink = `product_details.html?product_id=${product.id}&ref=${username}`;

        const imageUrl = product.picture
          ? product.picture
          : "https://via.placeholder.com/300x200?text=No+Image";

        card.innerHTML = `
          <div class="card h-100">
            <img src="${imageUrl}" class="card-img-top" alt="${product.name}" style="height:200px; object-fit:cover;">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title">${product.name}</h5>
              <p class="card-text"><strong>Price:</strong> ₦${price}</p>
              <p class="card-text"><strong>Commission:</strong> ₦${commission}</p>
              <p class="affiliate-link mt-auto"><strong>Link:</strong><br>
                <a href="${affiliateLink}" target="_blank">${affiliateLink}</a>
              </p>
              <a href="${affiliateLink}" class="btn btn-primary mt-2">Promote</a>
            </div>
          </div>
        `;

        productGrid.appendChild(card);
      });
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Could not load products. Please try again.");
    });
});
