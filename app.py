import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบจัดการสต็อกและบัญชีสหกรณ์",
    page_icon="🏛️",
    layout="wide"
)

# ------------------ SESSION STATE ------------------
if "products" not in st.session_state:
    st.session_state.products = {}

if "sales_history" not in st.session_state:
    st.session_state.sales_history = []

if "expenses_history" not in st.session_state:
    st.session_state.expenses_history = []

# คำนวณยอดรวม
total_rev = sum(s["total_price"] for s in st.session_state.sales_history)
total_cogs = sum(s["total_cost"] for s in st.session_state.sales_history)
other_exp = sum(e["amount"] for e in st.session_state.expenses_history)
total_exp = total_cogs + other_exp
net_profit = total_rev - total_exp

# ------------------ เมนูด้านข้าง ------------------
st.sidebar.title("🏛️ ระบบสหกรณ์")
st.sidebar.caption("จัดการสต็อกและบัญชีประจำปี")

menu = st.sidebar.radio(
    "เมนูหลัก",
    [
        "📊 แดชบอร์ดภาพรวม",
        "📦 จัดการสต็อกสินค้า",
        "🛒 บันทึกการขาย",
        "💸 บันทึกรายจ่ายอื่นๆ",
        "📈 สรุปบัญชีประจำปี & ปันผล"
    ]
)

# ------------------ 1. แดชบอร์ดภาพรวม ------------------
if menu == "📊 แดชบอร์ดภาพรวม":
    st.title("📊 แดชบอร์ดภาพรวม")
    st.caption("สรุปข้อมูลสต็อก ยอดขาย และกำไรสุทธิแบบเรียลไทม์")
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        total_stock = sum(item["จำนวนคงเหลือ"] for item in st.session_state.products.values())
        st.metric("สินค้าคงคลังรวม (ชิ้น)", f"{total_stock:,}")
        
    with c2:
        st.metric("รายรับรวมจากการขาย", f"฿{total_rev:,.2f}")

    with c3:
        st.metric("รายจ่ายรวมทั้งสิ้น", f"฿{total_exp:,.2f}")

    with c4:
        st.metric("กำไรสุทธิประจำปี", f"฿{net_profit:,.2f}")

    st.divider()

    col_chart, col_alert = st.columns([2, 1])

    with col_chart:
        st.subheader("📦 ปริมาณสินค้าคงเหลือ")
        if st.session_state.products:
            df_prod = pd.DataFrame.from_dict(st.session_state.products, orient="index")
            st.bar_chart(df_prod.set_index("ชื่อสินค้า")["จำนวนคงเหลือ"], height=250)
        else:
            st.info("ยังไม่มีข้อมูลสินค้าในระบบ (กรุณาเพิ่มสินค้าที่เมนู 'จัดการสต็อกสินค้า')")

    with col_alert:
        st.subheader("🚨 เตือนสินค้าใกล้หมด (< 10 ชิ้น)")
        low_stock = [
            {"ชื่อสินค้า": item["ชื่อสินค้า"], "คงเหลือ": item["จำนวนคงเหลือ"]}
            for item in st.session_state.products.values()
            if item["จำนวนคงเหลือ"] < 10
        ]
        if low_stock:
            st.dataframe(pd.DataFrame(low_stock), use_container_width=True, hide_index=True)
        else:
            st.success("ไม่มีสินค้ารายการใดใกล้หมด")

# ------------------ 2. จัดการสต็อกสินค้า ------------------
elif menu == "📦 จัดการสต็อกสินค้า":
    st.title("📦 จัดการสต็อกสินค้า")
    
    tab1, tab2, tab3 = st.tabs(["📋 รายการสินค้าทั้งหมด", "➕ เพิ่มสินค้าใหม่", "✏️ แก้ไข/ลบสินค้า"])

    with tab1:
        if st.session_state.products:
            df_inv = pd.DataFrame.from_dict(st.session_state.products, orient="index")
            st.dataframe(df_inv, use_container_width=True)
        else:
            st.info("ยังไม่มีสินค้าในระบบ กรุณาเพิ่มสินค้าใหม่")

    with tab2:
        st.subheader("เพิ่มสินค้าใหม่เข้าคลัง")
        with st.form("add_product_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            p_id = f1.text_input("รหัสสินค้า (เช่น P001)").strip()
            p_name = f2.text_input("ชื่อสินค้า").strip()

            f3, f4, f5 = st.columns(3)
            p_cost = f3.number_input("ต้นทุนต่อชิ้น (บาท)", min_value=0.0, step=1.0)
            p_price = f4.number_input("ราคาขายต่อชิ้น (บาท)", min_value=0.0, step=1.0)
            p_qty = f5.number_input("จำนวนเข้าสต็อก", min_value=1, step=1)

            if st.form_submit_button("บันทึกสินค้าใหม่"):
                if not p_id or not p_name:
                    st.error("กรุณากรอกรหัสและชื่อสินค้าให้ครบถ้วน")
                elif p_id in st.session_state.products:
                    st.error("รหัสสินค้านี้มีอยู่แล้วในระบบ")
                else:
                    st.session_state.products[p_id] = {
                        "ชื่อสินค้า": p_name,
                        "ต้นทุนต่อชิ้น (บาท)": p_cost,
                        "ราคาขายต่อชิ้น (บาท)": p_price,
                        "จำนวนคงเหลือ": p_qty
                    }
                    st.success(f"เพิ่มสินค้า '{p_name}' เรียบร้อยแล้ว!")
                    st.rerun()

    with tab3:
        st.subheader("แก้ไขหรือลบสินค้า")
        if not st.session_state.products:
            st.info("ไม่มีสินค้าให้แก้ไข")
        else:
            select_p_id = st.selectbox(
                "เลือกรหัสสินค้าที่ต้องการปรับปรุง",
                list(st.session_state.products.keys())
            )
            curr_item = st.session_state.products[select_p_id]

            col_edit, col_del = st.columns([2, 1])

            with col_edit:
                with st.form("edit_form"):
                    e_name = st.text_input("ชื่อสินค้า", value=curr_item["ชื่อสินค้า"])
                    e_cost = st.number_input("ต้นทุน (บาท)", value=float(curr_item["ต้นทุนต่อชิ้น (บาท)"]))
                    e_price = st.number_input("ราคาขาย (บาท)", value=float(curr_item["ราคาขายต่อชิ้น (บาท)"]))
                    e_qty = st.number_input("จำนวนคงเหลือ", value=int(curr_item["จำนวนคงเหลือ"]))

                    if st.form_submit_button("บันทึกการแก้ไข"):
                        st.session_state.products[select_p_id] = {
                            "ชื่อสินค้า": e_name,
                            "ต้นทุนต่อชิ้น (บาท)": e_cost,
                            "ราคาขายต่อชิ้น (บาท)": e_price,
                            "จำนวนคงเหลือ": e_qty
                        }
                        st.success("อัปเดตข้อมูลสินค้าเรียบร้อย!")
                        st.rerun()

            with col_del:
                st.write("**การดำเนินการลบ**")
                if st.button("🗑️ ลบสินค้านี้ออกจากระบบ", use_container_width=True):
                    del st.session_state.products[select_p_id]
                    st.success("ลบสินค้าเรียบร้อยแล้ว!")
                    st.rerun()

# ------------------ 3. บันทึกการขาย ------------------
elif menu == "🛒 บันทึกการขาย":
    st.title("🛒 บันทึกการขายสินค้า")

    if not st.session_state.products:
        st.warning("กรุณาเพิ่มสินค้าในเมนู 'จัดการสต็อกสินค้า' ก่อนทำการขาย")
    else:
        col_sell, col_hist = st.columns([1, 1])

        with col_sell:
            st.subheader("ทำรายการขาย")
            p_opts = {f"{k} - {v['ชื่อสินค้า']} (เหลือ: {v['จำนวนคงเหลือ']})": k for k, v in st.session_state.products.items()}
            sel_opt = st.selectbox("เลือกสินค้า", list(p_opts.keys()))
            sel_id = p_opts[sel_opt]
            sel_item = st.session_state.products[sel_id]

            sell_qty = st.number_input("จำนวนที่ขาย", min_value=1, max_value=max(1, sel_item["จำนวนคงเหลือ"]))
            tot_price = sel_item["ราคาขายต่อชิ้น (บาท)"] * sell_qty

            st.write(f"**ยอดรวมทั้งสิ้น:** ฿{tot_price:,.2f}")

            if st.button("✅ ยืนยันการขาย"):
                if sel_item["จำนวนคงเหลือ"] < sell_qty:
                    st.error("สินค้าในสต็อกไม่พอ!")
                else:
                    sel_item["จำนวนคงเหลือ"] -= sell_qty
                    st.session_state.sales_history.append({
                        "รหัสสินค้า": sel_id,
                        "ชื่อสินค้า": sel_item["ชื่อสินค้า"],
                        "จำนวน": sell_qty,
                        "total_price": tot_price,
                        "total_cost": sel_item["ต้นทุนต่อชิ้น (บาท)"] * sell_qty
                    })
                    st.success("บันทึกการขายสำเร็จ!")
                    st.rerun()

        with col_hist:
            st.subheader("ประวัติการขาย")
            if st.session_state.sales_history:
                df_s = pd.DataFrame(st.session_state.sales_history)[["รหัสสินค้า", "ชื่อสินค้า", "จำนวน", "total_price"]]
                df_s.columns = ["รหัสสินค้า", "ชื่อสินค้า", "จำนวน", "ยอดขายรวม (บาท)"]
                st.dataframe(df_s, use_container_width=True)

                if st.button("🗑️ ลบประวัติการขายทั้งหมด"):
                    st.session_state.sales_history = []
                    st.rerun()
            else:
                st.info("ยังไม่มีประวัติการขาย")

# ------------------ 4. บันทึกรายจ่ายอื่นๆ ------------------
elif menu == "💸 บันทึกรายจ่ายอื่นๆ":
    st.title("💸 บันทึกรายจ่ายอื่นๆ")
    st.caption("สำหรับค่าน้ำ ค่าไฟ ค่าเช่า หรือค่าใช้จ่ายทั่วไป")

    c_exp1, c_exp2 = st.columns([1, 1])

    with c_exp1:
        st.subheader("บันทึกรายจ่ายใหม่")
        with st.form("exp_form", clear_on_submit=True):
            exp_title = st.text_input("รายละเอียดรายจ่าย").strip()
            exp_val = st.number_input("จำนวนเงิน (บาท)", min_value=1.0, step=10.0)

            if st.form_submit_button("บันทึกรายจ่าย"):
                if exp_title:
                    st.session_state.expenses_history.append({
                        "รายการ": exp_title,
                        "amount": exp_val
                    })
                    st.success("บันทึกรายจ่ายเรียบร้อย!")
                    st.rerun()

    with c_exp2:
        st.subheader("ประวัติรายจ่าย")
        if st.session_state.expenses_history:
            df_e = pd.DataFrame(st.session_state.expenses_history)
            df_e.columns = ["รายการ", "จำนวนเงิน (บาท)"]
            st.dataframe(df_e, use_container_width=True)

            if st.button("🗑️ ลบประวัติรายจ่ายทั้งหมด"):
                st.session_state.expenses_history = []
                st.rerun()
        else:
            st.info("ยังไม่มีบันทึกรายจ่าย")

# ------------------ 5. สรุปบัญชีประจำปี & ปันผล ------------------
elif menu == "📈 สรุปบัญชีประจำปี & ปันผล":
    st.title("📈 สรุปผลการดำเนินงานประจำปีและภาษีสหกรณ์")

    st.subheader("📋 งบกำไรขาดทุนเบื้องต้น")
    summary_data = [
        {"รายการ": "1. รายรับรวมจากการขาย", "จำนวนเงิน (บาท)": f"฿{total_rev:,.2f}"},
        {"รายการ": "2.1 ต้นทุนสินค้าที่ขาย (COGS)", "จำนวนเงิน (บาท)": f"฿{total_cogs:,.2f}"},
        {"รายการ": "2.2 รายจ่ายอื่นๆ", "จำนวนเงิน (บาท)": f"฿{other_exp:,.2f}"},
        {"รายการ": "2. รวมรายจ่ายทั้งสิ้น", "จำนวนเงิน (บาท)": f"฿{total_exp:,.2f}"},
        {"รายการ": "3. กำไรสุทธิประจำปี", "จำนวนเงิน (บาท)": f"฿{net_profit:,.2f}"},
        {"รายการ": "4. ภาษีเงินได้นิติบุคคล (0%)", "จำนวนเงิน (บาท)": "฿0.00 (ได้รับการยกเว้นตามกฎหมาย)"}
    ]
    st.table(pd.DataFrame(summary_data))

    st.divider()

    st.subheader("🏛️ การจัดสรรกำไรสุทธิประจำปีของสหกรณ์")
    if net_profit > 0:
        rate = st.slider("เปอร์เซ็นต์หักเข้า 'ทุนสำรองสหกรณ์' (ขั้นต่ำ 10%)", 10, 100, 10)
        res_val = net_profit * (rate / 100.0)
        div_val = net_profit - res_val

        r1, r2 = st.columns(2)
        with r1:
            st.success(f"🏛️ **หักเข้าทุนสำรอง ({rate}%):**\n### ฿{res_val:,.2f}")
        with r2:
            st.info(f"🎁 **คงเหลือจัดสรรปันผลให้สมาชิก:**\n### ฿{div_val:,.2f}")
    else:
        st.warning("ไม่มีกำไรสุทธิในปีนี้ ไม่ต้องจัดสรรเงินปันผล")
