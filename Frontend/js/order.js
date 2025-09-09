// order.js

document.addEventListener("DOMContentLoaded", function () {
  const params = new URLSearchParams(window.location.search);
  const productId = params.get("product_id");
  const ref = params.get("ref"); // affiliate username
  const token = localStorage.getItem("access");

  if (!productId || !ref) {
    alert("Invalid order link.");
    window.location.href = "products.html";
    return;
  }

  const productNameEl = document.getElementById("productName");
  const productPriceEl = document.getElementById("productPrice");
  const bankDetailsEl = document.getElementById("bankDetails");

  // ✅ Fetch product details
  fetch(`http://127.0.0.1:8000/api/accounts/products/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
    .then((res) => res.json())
    .then((products) => {
      const product = products.find((p) => p.id == productId);
      if (product) {
        productNameEl.textContent = product.name;
        productPriceEl.textContent = parseFloat(product.price).toLocaleString();
      } else {
        productNameEl.textContent = "Product not found";
      }
    })
    .catch((err) => console.error("Error fetching product:", err));

  // ✅ Show bank details only when "bank" selected
  document.getElementById("paymentMethod").addEventListener("change", function () {
    if (this.value === "bank") {
      bankDetailsEl.style.display = "block";
    } else {
      bankDetailsEl.style.display = "none";
    }
  });

  // ✅ Handle form submission
  const orderForm = document.getElementById("orderForm");
  const messageDiv = document.getElementById("message");

  orderForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const buyerPhone = document.getElementById("buyerPhone").value.trim();
    const paymentMethod = document.getElementById("paymentMethod").value;
    const proofOfPayment = document.getElementById("proofOfPayment").files[0];

    if (!buyerPhone || !paymentMethod || !proofOfPayment) {
      alert("Please fill all fields.");
      return;
    }

    const formData = new FormData();
    formData.append("product", productId);
    formData.append("buyer_phone", buyerPhone);
    formData.append("payment_method", paymentMethod);
    formData.append("proof_of_payment", proofOfPayment);
    formData.append("affiliate_username", ref);

    fetch("http://127.0.0.1:8000/api/accounts/orders/", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    })
      .then((res) => res.json().then((data) => ({ status: res.status, body: data })))
      .then(({ status, body }) => {
        if (status === 201) {
          messageDiv.innerHTML = `<div class="alert alert-success">✅ Order placed successfully! We will confirm payment and your order will be processed.</div>`;
          orderForm.reset();
          bankDetailsEl.style.display = "none";
        } else {
          messageDiv.innerHTML = `<div class="alert alert-danger">❌ Failed: ${JSON.stringify(body)}</div>`;
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        messageDiv.innerHTML = `<div class="alert alert-danger">❌ An error occurred. Please try again.</div>`;
      });
  });
});
