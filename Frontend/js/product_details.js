const params = new URLSearchParams(window.location.search);
const productId = params.get("id");
const ref = params.get("ref");

if (!productId || !ref) {
    alert("Invalid product link");
    window.location.href = "products.html";
}

fetch(`http://localhost:8000/api/affiliate-products/${productId}/`)
    .then(res => res.json())
    .then(product => {
        document.getElementById("productName").innerText = product.name;
        document.getElementById("productImage").src = product.image || "placeholder.jpg";
        document.getElementById("productCategory").innerText = `Category: ${product.category_name}`;
        document.getElementById("productPrice").innerText = `Price: ₦${product.price}`;
        document.getElementById("productCommission").innerText = `Commission: ${product.commission_value} (${product.commission_type})`;

        document.getElementById("payOnlineBtn").addEventListener("click", () => {
            window.location.href = `http://localhost:8000/order?product=${productId}&ref=${ref}`;
        });
    })
    .catch(err => console.error(err));
