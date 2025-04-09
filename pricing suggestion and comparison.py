import streamlit as st

# -----------------------
# Making Charges (Gold %) and Silver (Gold - 2%)
gold_making_charges = {
    "Plain Band Ring": 6,
    "Fancy/Broad Ring": 6,
    "Kada": 6,
    "Bangle": 4.5,
    "Fancy Bangle": 6,
    "Bracelets": 10,
    "Pendant": 4,
    "Studs": 3,
    "Necklace": 10,
    "Chain": 7,
    "Nose Ring": 3
}
silver_making_charges = {cat: max(0, val - 2) for cat, val in gold_making_charges.items()}

# -----------------------
# Pricing Logic
def calculate_price(metal_price, weight, making_charge_percent):
    material_cost = metal_price * weight
    making_charge = (making_charge_percent / 100) * material_cost
    base_price = material_cost + making_charge
    return material_cost, making_charge, base_price

def calculate_selling_price(base_price, profit_input=None, tier=None):
    if profit_input:
        return base_price * (1 + profit_input / 100)
    if tier == "Minimal":
        return base_price * 1.1
    elif tier == "Premium":
        return base_price * 1.8
    else:
        return base_price * 1.5  # Default to standard

# -----------------------
# Streamlit UI
st.set_page_config(page_title="Jewelry Pricing Model", page_icon="💍")
st.title("💍 Jewelry Pricing Comparison: 18K Gold vs Silver")

st.markdown("Compare pricing for **18K Gold** and **Silver** jewelry with category-wise making charges and smart selling price suggestions.")

# Metal Prices
st.markdown("### 📉 Today's Metal Prices (₹/gram)")
gold_price = st.number_input("18K Gold Price", value=5000.0, step=10.0)
silver_price = st.number_input("Silver Price", value=75.0, step=1.0)

# Jewelry Details
st.markdown("### 💎 Jewelry Details")
category = st.selectbox("Select Jewelry Category", list(gold_making_charges.keys()))
weight = st.number_input("Enter Weight (grams)", min_value=0.1, step=0.1)

# Fetch Making Charges
gold_making = gold_making_charges.get(category, 10)
silver_making = silver_making_charges.get(category, 8)

st.info(f"💡 Making Charges for {category}:\n- 18K Gold: {gold_making}%\n- Silver: {silver_making}%")

# Custom Profit Margin
st.markdown("### 💰 Selling Price Strategy")

use_custom_profit = st.checkbox("I want to enter custom profit %")
custom_profit = None
if use_custom_profit:
    custom_profit = st.number_input("Enter custom profit percentage (%)", min_value=0.0, max_value=100.0, step=0.5)
else:
    tier = st.radio("Select Profit Tier (if not using custom)", ["Minimal", "Standard", "Premium"], index=1)

# Calculate Prices
if st.button("🔍 Compare Pricing"):
    gold_material, gold_making_amt, gold_base = calculate_price(gold_price, weight, gold_making)
    silver_material, silver_making_amt, silver_base = calculate_price(silver_price, weight, silver_making)

    gold_sp = calculate_selling_price(gold_base, custom_profit, tier if not use_custom_profit else None)
    silver_sp = calculate_selling_price(silver_base, custom_profit, tier if not use_custom_profit else None)

    st.subheader("📊 Price Comparison")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🟨 18K Gold")
        st.write(f"**Material Cost:** ₹{gold_material:.2f}")
        st.write(f"**Making Charge ({gold_making}%):** ₹{gold_making_amt:.2f}")
        st.write(f"**Base Price:** ₹{gold_base:.2f}")
        st.success(f"**Suggested Selling Price:** ₹{gold_sp:.2f}")

    with col2:
        st.markdown("### ⚪ Silver")
        st.write(f"**Material Cost:** ₹{silver_material:.2f}")
        st.write(f"**Making Charge ({silver_making}%):** ₹{silver_making_amt:.2f}")
        st.write(f"**Base Price:** ₹{silver_base:.2f}")
        st.success(f"**Suggested Selling Price:** ₹{silver_sp:.2f}")

    st.markdown("---")
    if use_custom_profit:
        st.markdown(f"📌 Using **custom profit margin**: `{custom_profit}%` on both metals")
    else:
        st.markdown(f"📌 Using **standard tier pricing**: `{tier}`")

