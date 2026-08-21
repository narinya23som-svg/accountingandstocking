import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าเว็บเป็น Wide Mode
st.set_page_config(
    page_title="Coop Management System",
    page_icon="🏛️",
    layout="wide"
)

# 2. ใส่ Custom CSS แต่งสไตล์การ์ด สี และเมนูข้าง
st.markdown("""
<style>
    /* ปรับแต่งส่วน Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0b192c;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    /* ปรับแต่ง Metric Cards ให้เหมือนในรูปภาพ */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
    
    /* การ์ดเน้นสีน้ำเงินเข้มสำหรับยอดสำคัญ */
    .highlight-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);
    }
    .highlight-card h3 { color: #93c5fd !important; margin: 0; font-size: 14px; }
    .highlight-card h1 { color: white !important; margin: 5px 0 0 0; font-size: 28px; }

    /* ปรับแต่งปุ่มกด */
    .stButton>button {
        background-color: #10b981;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #059669;
        color: white;
    }

    /* ตาราง Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if "products" not in st.session_state:
    st.session_state.products = {
        "P001": {"name": "สมุดโน้ต", "cost": 15.0, "price": 25.0, "qty": 50},
        "P002": {"name": "ปากกาลูกลื่น", "cost": 5.0, "price": 10.0, "qty": 100},
        "P003": {"name": "ดินสอ 2B", "cost": 3.0, "price": 7.0, "qty": 80},
    }

if "sales_history" not in st.session_state:
    st.session_state.sales_history = []

if "expenses_history" not in st.session_state:
    st.session_state.expenses_history = []

# คำนวณยอด
total_rev = sum(s["total_price"] for s in st.session_state.sales_history)
total_cogs = sum(s["total_cost"] for s in st.session_state.sales_history)
other_exp = sum(e["amount"] for e in st.session_state.expenses_history)
total_exp = total_cogs + other_exp
net_profit = total_rev - total_exp

# ------------------ SIDEBAR NAVIGATION ------------------
st.sidebar.title("🏛️ Coop Management")
st.sidebar.caption("ระบบจัดการสต็อกและบัญชี")

menu = st.sidebar.radio(
    "NAVIGATION",
    [
        "📊 Overview Dashboard",
        "📦 Inventory Management",
        "🛒 Sales Record",
        "💸 Expense Record",
        "📈 Annual Summary"
    ]
)

# ------------------ MENU 1: OVERVIEW DASHBOARD ------------------
if menu == "📊 Overview Dashboard":
    st.title("📊 Overview Dashboard")
    st.caption("ภาพรวมข้อมูลสต็อกสินค้า ยอดขาย และกำไรประจำปี")
    st.markdown("<br>", unsafe_allow_html=True)

    # Metric Cards Top Row (ดีไซน์การ์ดตามรูป)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
        <div class="highlight-card">
            <h3>สินค้าคงคลังรวม (Stock)</h3>
            <h1>{:,.0f} ชิ้น</h1>
        </div>
        """.format(sum(item["qty"] for item in st.session_state.products.values())), unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="highlight-card">
            <h3>รายรับรวม (Sales)</h3>
            <h1>฿{:,.2f}</h1>
        </div>
        """.format(total_rev), unsafe_allow_html=True)

    with c3:
        st.metric("รายจ่ายรวม (Expenses)", f"฿{total_exp:,.2f}")

    with c4:
        st.metric("กำไรสุทธิ (Net Profit)", f"฿{net_profit:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts and Alerts Row
    col_chart, col_alert = st.columns([2, 1])

    with col_chart:
        st.subheader("📦 Product Stock Level")
        if st.session_state.products:
            df_prod = pd.DataFrame.from_dict(st.session_state.products, orient="index")
            st.bar_chart(df_prod.set_index("name")["qty"], height=250)

    with col_alert:
        st.subheader("🚨 Low Stock Alert")
        low_stock = [
            {"Product": item["name"], "Stock": item["qty"]}
            for item in st.session_state.products.values()
            if item["qty"] < 10
        ]
        if low_stock:
            st.dataframe(pd.DataFrame(low_stock), use_container_width=True, hide_index=True)
        else:
            st.info("สินค้าในสต็อกทุกรายการมีเพียงพอ")

    st.divider()

    # Form ด้านล่างสำหรับเพิ่มสินค้าแบบรวดเร็ว
    st.subheader("➕ ADD NEW PRODUCT")
    with st.form("quick_add"):
        fa, fb, fc = st.columns(3)
        p_id = fa.text_input("รหัสสินค้า (Product ID)")
        p_name = fb.text_input("ชื่อสินค้า (Product Name)")
        p_qty = fc.number_input("จำนวน (Qty)", min_value=1, value=10)
        
        fd, fe = st.columns(2)
        p_cost = fd.number_input("ต้นทุน (Cost)", min_value=0.0)
        p_price = fe.number_input("ราคาขาย (Price)", min_value=0.0)

        if st.form_submit_button("Add New Product"):
            if p_id and p_name:
                st.session_state.products[p_id] = {
                    "name": p_name, "cost": p_cost, "price": p_price, "qty": p_qty
                }
                st.success("เพิ่มสินค้าเรียบร้อยแล้ว!")
                st.rerun()

# ------------------ MENU 2: INVENTORY ------------------
elif menu == "📦 Inventory Management":
    st.title("📦 Inventory Management")
    df_inv = pd.DataFrame.from_dict(st.session_state.products, orient="index")
    st.dataframe(df_inv, use_container_width=True)

# ------------------ MENU 3: SALES ------------------
elif menu == "🛒 Sales Record":
    st.title("🛒 Sales Record")
    st.write("บันทึกการขายสินค้า")

# ------------------ MENU 4: EXPENSES ------------------
elif menu == "💸 Expense Record":
    st.title("💸 Expense Record")
    st.write("บันทึกรายจ่ายอื่นๆ")

# ------------------ MENU 5: SUMMARY ------------------
elif menu == "📈 Annual Summary":
    st.title("📈 Annual Summary & Coop Dividend")
    st.write(f"**กำไรสุทธิ:** ฿{net_profit:,.2f}")
    st.write("**ภาษีเงินได้:** ฿0.00 (ยกเว้นภาษีสำหรับสหกรณ์)")
