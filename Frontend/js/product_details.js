// product_details.js

document.addEventListener("DOMContentLoaded", function () {
  const params = new URLSearchParams(window.location.search);
  const productId = params.get("product_id");
  const ref = params.get("ref"); // affiliate username
  const token = localStorage.getItem("access");

  if (!productId) {
    alert("No product selected.");
    window.location.href = "products.html";
    return;
  }

  fetch(`http://127.0.0.1:8000/api/accounts/products/${productId}/`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  })
    .then((res) => {
      if (!res.ok) throw new Error("Failed to fetch product details");
      return res.json();
    })
    .then((product) => {
      const detailsDiv = document.getElementById("productDetails");

      const price = parseFloat(product.price).toLocaleString();
      const affiliateLink = `product_details.html?product_id=${product.id}&ref=${ref}`;

      const imageUrl = product.picture
        ? product.picture
        : "https://via.placeholder.com/600x400?text=No+Image";

      detailsDiv.innerHTML = `
        <div class="row g-4">
          <div class="col-md-6">
            <img src="${imageUrl}" class="img-fluid product-image rounded" alt="${product.name}">
          </div>
          <div class="col-md-6">
            <h3>${product.name}</h3>
            <p><strong>Price:</strong> ₦${price}</p>
            <p><strong>Description:</strong> ${product.description || "No description available."}</p>
            <p><strong>Affiliate Link:</strong><br>
              <a href="${affiliateLink}" target="_blank">${affiliateLink}</a>
            </p>
            <button id="orderBtn" class="btn btn-success mt-3">Order Now</button>
          </div>
        </div>
      `;

      // ✅ Handle Order button click
      document.getElementById("orderBtn").addEventListener("click", () => {
        window.location.href = `order.html?product_id=${product.id}&ref=${ref}`;
      });
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Could not load product details.");
    });
});
