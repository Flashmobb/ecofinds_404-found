import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { getProducts } from "./api";

function App() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    getProducts()
      .then((res) => {
        setProducts(res.data);
      })
      .catch((err) => console.error("API error:", err));
  }, []);

  return (
    <div>
      <h1>EcoFinds Marketplace 🌍</h1>
      <h2>Product Listings</h2>
      <ul>
        {products.map((p, i) => (
          <li key={i}>
            {p.title} — ${p.price}
          </li>
        ))}
      </ul>
    </div>
  );
}

const root = createRoot(document.getElementById("root"));
root.render(<App />);
