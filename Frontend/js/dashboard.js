document.addEventListener("DOMContentLoaded", function () {
  const token = localStorage.getItem("access");

  if (!token) {
    alert("You must login to view products.");
    window.location.href = "login.html";
    return;
  }

  fetch("http://localhost:8000/api/affiliate-products/", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  })
    .then((res) => {
      if (!res.ok) {
        return res.text().then(text => {
          throw new Error(`Failed to load products: ${res.status} ${text}`);
        });
      }
      return res.json();
    })
    .then((products) => {
      const productGrid = document.getElementById("productGrid");
      const username = localStorage.getItem("username") || "affiliate";

      if (products.length === 0) {
        productGrid.innerHTML = "<p>No products available.</p>";
        return;
      }

      products.forEach((product) => {
        const card = document.createElement("div");
        card.className = "col";

        const price = parseFloat(product.price).toFixed(2);
        const commissionValue = parseFloat(product.commission_value).toFixed(2);
        const commissionLabel =
          product.commission_type === "percent"
            ? `${commissionValue}%`
            : `₦${commissionValue}`;

        const affiliateLink = `http://localhost:8000/product/${product.id}/?ref=${username}`;

        // Use product.image if available, else use placeholder
        const imageUrl = product.image
          ? `http://localhost:8000${product.image}`
          : "https://via.placeholder.com/300x200?text=No+Image";

        card.innerHTML = `
          <div class="card h-100">
            <img src="${imageUrl}" class="card-img-top" alt="${product.name}" style="height:200px; object-fit:cover;">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title">${product.name}</h5>
              <p class="card-text"><strong>Category:</strong> ${product.category_name}</p>
              <p class="card-text"><strong>Price:</strong> ₦${price}</p>
              <p class="card-text"><strong>Commission:</strong> ${commissionLabel}</p>
              <p class="affiliate-link mt-auto"><strong>Link:</strong><br><a href="${affiliateLink}" target="_blank">${affiliateLink}</a></p>
              <a href="${affiliateLink}" target="_blank" class="btn btn-primary mt-2">Promote</a>
            </div>
          </div>
        `;

        productGrid.appendChild(card);
      });
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Failed to load products.");
    });
});
