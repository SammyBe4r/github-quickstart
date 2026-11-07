const products = [
  {
    id: "margherita",
    name: "Margherita da Nona",
    category: "Pizzas",
    description: "Tomate italiano, fior di latte, manjericão fresco.",
    price: 49,
    unit: "grande · 8 fatias",
    rating: "★ 4,9",
    badge: "A QUERIDINHA",
    image: "https://images.unsplash.com/photo-1579751626657-72bc17010498?auto=format&fit=crop&w=800&q=80",
    alt: "Pizza margherita com tomate, queijo e folhas de manjericão"
  },
  {
    id: "funghi",
    name: "Funghi & Mel",
    category: "Pizzas",
    description: "Cogumelos salteados, mel trufado, parmesão.",
    price: 56,
    unit: "grande · 8 fatias",
    rating: "★ 4,8",
    badge: "DA ESTAÇÃO",
    image: "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
    alt: "Pizza artesanal assada em forno a lenha"
  },
  {
    id: "calabresa",
    name: "Calabresa da Vila",
    category: "Pizzas",
    description: "Linguiça artesanal, cebola roxa, mel de pimenta.",
    price: 52,
    unit: "grande · 8 fatias",
    rating: "★ 4,9",
    badge: "MAIS PEDIDA",
    image: "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?auto=format&fit=crop&w=800&q=80",
    alt: "Pizza de calabresa com molho de tomate e queijo"
  },
  {
    id: "combo",
    name: "Noite de Nona",
    category: "Combos",
    description: "Pizza Margherita + tiramisù para dividir.",
    price: 68,
    unit: "para 2 pessoas",
    rating: "★ 5,0",
    badge: "COMBO ESPECIAL",
    image: "https://images.unsplash.com/photo-1571407970349-bc81e7e96d47?auto=format&fit=crop&w=800&q=80",
    alt: "Pizza redonda recém-saída do forno"
  },
  {
    id: "limonada",
    name: "Limonada da Casa",
    category: "Bebidas",
    description: "Limão siciliano, hortelã e um toque de mel.",
    price: 12,
    unit: "300 ml",
    rating: "★ 4,8",
    badge: "FEITA NA HORA",
    image: "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=800&q=80",
    alt: "Bebidas cítricas servidas com gelo e fatia de limão"
  },
  {
    id: "tiramisù",
    name: "Tiramisù da Nona",
    category: "Sobremesas",
    description: "Café coado, mascarpone e cacau 70%.",
    price: 19,
    unit: "porção individual",
    rating: "★ 5,0",
    badge: "RECEITA DE FAMÍLIA",
    image: "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=800&q=80",
    alt: "Tiramisù cremoso polvilhado com cacau"
  }
];

const categories = ["Tudo", "Pizzas", "Combos", "Bebidas", "Sobremesas"];
const cart = new Map();
const deliveryFeeBase = 7.9;
const freeDeliveryThreshold = 80;
let activeCategory = "Tudo";
let searchTerm = "";
let deliveryAddress = "Rua Harmonia, 510 · ap. 32";
let couponApplied = false;
let toastTimeout;

const money = (value) => value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const getSubtotal = () => [...cart.entries()].reduce((total, [id, quantity]) => {
  const product = products.find((item) => item.id === id);
  return total + product.price * quantity;
}, 0);
const getItemCount = () => [...cart.values()].reduce((total, quantity) => total + quantity, 0);
const getDeliveryFee = () => getSubtotal() >= freeDeliveryThreshold || getSubtotal() === 0 ? 0 : deliveryFeeBase;
const getDiscount = () => couponApplied ? Math.min(getSubtotal() * 0.1, 15) : 0;
const getTotal = () => getSubtotal() + getDeliveryFee() - getDiscount();

function renderCategories() {
  const list = document.querySelector("#categoryList");
  list.innerHTML = categories.map((category) => `
    <button type="button" class="category-button" data-category="${category}" aria-pressed="${activeCategory === category}">
      ${category === "Tudo" ? "Ver tudo" : category}
    </button>
  `).join("");
}

function renderProducts() {
  const filtered = products.filter((product) => {
    const matchesCategory = activeCategory === "Tudo" || product.category === activeCategory;
    const matchesSearch = `${product.name} ${product.description} ${product.category}`.toLocaleLowerCase("pt-BR").includes(searchTerm);
    return matchesCategory && matchesSearch;
  });
  const grid = document.querySelector("#productGrid");
  document.querySelector("#categoryTitle").textContent = searchTerm
    ? "Encontramos pra você"
    : activeCategory === "Tudo" ? "Os favoritos da Nona" : activeCategory;
  document.querySelector("#resultCount").textContent = `${filtered.length} ${filtered.length === 1 ? "opção" : "opções"}`;
  grid.innerHTML = filtered.length ? filtered.map((product) => `
    <article class="product-card">
      <div class="product-image">
        <img src="${product.image}" alt="${product.alt}" loading="lazy">
        <span class="product-badge">${product.badge}</span>
      </div>
      <div class="product-card-body">
        <div class="product-meta"><h4>${product.name}</h4><span class="product-rating">${product.rating}</span></div>
        <p class="product-description">${product.description}</p>
        <div class="product-actions">
          <span class="product-price">${money(product.price)}<small>${product.unit}</small></span>
          <button type="button" class="add-button" data-add="${product.id}" aria-label="Adicionar ${product.name} à sacola">
            Adicionar <span aria-hidden="true">+</span>
          </button>
        </div>
      </div>
    </article>
  `).join("") : `<p class="empty-results">Não encontramos esse sabor. Tente outra busca ou categoria.</p>`;
}

function renderCart() {
  const items = [...cart.entries()];
  document.querySelector("#cartItems").innerHTML = items.length ? items.map(([id, quantity]) => {
    const product = products.find((item) => item.id === id);
    return `
      <div class="cart-item">
        <div>
          <div class="cart-item-main"><span>${product.name}</span><span class="cart-item-price">${money(product.price * quantity)}</span></div>
          <div class="quantity-control" aria-label="Quantidade de ${product.name}">
            <button type="button" data-quantity="${id}" data-change="-1" aria-label="Remover uma unidade de ${product.name}">−</button>
            <span>${quantity}</span>
            <button type="button" data-quantity="${id}" data-change="1" aria-label="Adicionar uma unidade de ${product.name}">+</button>
          </div>
        </div>
      </div>
    `;
  }).join("") : `<div class="cart-empty"><span class="cart-empty-icon" aria-hidden="true">♧</span><span>Sua sacola está esperando uma coisa gostosa.</span></div>`;

  const subtotal = getSubtotal();
  const discount = getDiscount();
  const count = getItemCount();
  document.querySelector("#cartCount").textContent = count;
  document.querySelector("#subtotal").textContent = money(subtotal);
  document.querySelector("#deliveryFee").textContent = getDeliveryFee() === 0 && subtotal > 0 ? "Grátis" : money(getDeliveryFee());
  document.querySelector("#discountRow").hidden = discount === 0;
  document.querySelector("#discount").textContent = `− ${money(discount)}`;
  document.querySelector("#total").textContent = money(getTotal());
  document.querySelector("#checkoutButton").disabled = count === 0;
  document.querySelector("#mobileCartCount").textContent = `${count} ${count === 1 ? "item" : "itens"}`;
  document.querySelector("#mobileCartTotal").textContent = money(getTotal());
  document.querySelector("#mobileCartButton").setAttribute("aria-label", `Abrir sacola com ${count} ${count === 1 ? "item" : "itens"}, total ${money(getTotal())}`);
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.add("is-visible");
  window.clearTimeout(toastTimeout);
  toastTimeout = window.setTimeout(() => toast.classList.remove("is-visible"), 2300);
}

function setCartOpen(isOpen) {
  const panel = document.querySelector("#orderPanel");
  const backdrop = document.querySelector("#cartBackdrop");
  const button = document.querySelector("#mobileCartButton");
  panel.classList.toggle("is-open", isOpen);
  backdrop.classList.toggle("is-visible", isOpen);
  backdrop.tabIndex = isOpen ? 0 : -1;
  button.setAttribute("aria-expanded", String(isOpen));
  document.body.classList.toggle("cart-open", isOpen);
}

document.querySelector("#categoryList").addEventListener("click", (event) => {
  const button = event.target.closest("[data-category]");
  if (!button) return;
  activeCategory = button.dataset.category;
  renderCategories();
  renderProducts();
});

document.querySelector("#searchInput").addEventListener("input", (event) => {
  searchTerm = event.target.value.trim().toLocaleLowerCase("pt-BR");
  renderProducts();
});

document.querySelector("#productGrid").addEventListener("click", (event) => {
  const button = event.target.closest("[data-add]");
  if (!button) return;
  const product = products.find((item) => item.id === button.dataset.add);
  cart.set(product.id, (cart.get(product.id) || 0) + 1);
  renderCart();
  showToast(`${product.name} foi pra sua sacola.`);
});

document.querySelector("#cartItems").addEventListener("click", (event) => {
  const button = event.target.closest("[data-quantity]");
  if (!button) return;
  const id = button.dataset.quantity;
  const nextQuantity = (cart.get(id) || 0) + Number(button.dataset.change);
  if (nextQuantity <= 0) cart.delete(id);
  else cart.set(id, nextQuantity);
  if (couponApplied && getSubtotal() < 50) {
    couponApplied = false;
    document.querySelector("#couponMessage").textContent = "Cupom removido: o pedido ficou abaixo de R$ 50.";
    document.querySelector("#couponMessage").classList.add("error");
  }
  renderCart();
});

document.querySelector("#couponForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const message = document.querySelector("#couponMessage");
  const code = document.querySelector("#couponInput").value.trim().toUpperCase();
  message.classList.remove("error");
  if (code !== "NONA10") {
    couponApplied = false;
    message.textContent = "Esse cupom não é válido. Tente NONA10.";
    message.classList.add("error");
  } else if (getSubtotal() < 50) {
    couponApplied = false;
    message.textContent = "Adicione itens até chegar a R$ 50 para usar este cupom.";
    message.classList.add("error");
  } else {
    couponApplied = true;
    message.textContent = "Cupom aplicado: 10% de desconto (até R$ 15).";
  }
  renderCart();
});

function openAddressDialog() {
  document.querySelector("#addressInput").value = deliveryAddress;
  document.querySelector("#addressDialog").showModal();
}

document.querySelector("#openAddress").addEventListener("click", openAddressDialog);
document.querySelector("#editAddress").addEventListener("click", openAddressDialog);
document.querySelector("#addressForm").addEventListener("submit", (event) => {
  event.preventDefault();
  deliveryAddress = document.querySelector("#addressInput").value.trim();
  document.querySelector("#headerAddress").textContent = deliveryAddress.split("·")[0].trim();
  document.querySelector("#deliveryAddress").textContent = deliveryAddress;
  document.querySelector("#addressDialog").close();
  showToast("Endereço atualizado.");
});

document.querySelector("#checkoutButton").addEventListener("click", () => {
  if (cart.size === 0) return;
  document.querySelector("#checkoutDialog").showModal();
});

document.querySelector("#checkoutForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const customerName = document.querySelector("#customerName").value.trim().split(/\s+/)[0];
  const payment = document.querySelector("#paymentMethod").value;
  document.querySelector("#successName").textContent = customerName;
  document.querySelector("#successDetails").textContent = `Pedido de ${money(getTotal())} registrado para ${deliveryAddress}. Pagamento: ${payment}.`;
  document.querySelector("#checkoutDialog").close();
  document.querySelector("#successDialog").showModal();
  cart.clear();
  couponApplied = false;
  document.querySelector("#couponInput").value = "";
  document.querySelector("#couponMessage").textContent = "";
  renderCart();
  setCartOpen(false);
});

document.querySelector("#finishButton").addEventListener("click", () => {
  document.querySelector("#successDialog").close();
  document.querySelector("#customerName").value = "";
  document.querySelector("#searchInput").focus();
});

document.querySelector("#mobileCartButton").addEventListener("click", () => {
  setCartOpen(!document.querySelector("#orderPanel").classList.contains("is-open"));
});
document.querySelector("#cartBackdrop").addEventListener("click", () => setCartOpen(false));
document.querySelectorAll("dialog").forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "/" && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
    event.preventDefault();
    document.querySelector("#searchInput").focus();
  }
  if (event.key === "Escape") setCartOpen(false);
});

renderCategories();
renderProducts();
renderCart();
