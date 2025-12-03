import streamlit as st
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Prototype Ongkir GEM", layout="wide")

# --- DATA DUMMY (PENGGANTI DATABASE SEMENTARA) ---
# Nanti bagian ini kita ganti dengan koneksi Google Sheet
data_lokasi = {
    'City': ['Kab. Bandung', 'Kab. Bandung', 'Kota Bandung', 'Kota Bandung'],
    'Postal Code': ['40229', '40375', '40111', '40115'],
    'Blibli Elektronik - Banjaran Bandung': [7, 15, 25, 30], # Jarak KM
    'Minimum Charge': ['ZONE 1', 'ZONE 2', 'ZONE 3', 'ZONE 3']
}
df_lokasi = pd.DataFrame(data_lokasi)

data_harga = [
    {'Kategori': 'Dispenser', 'ZONE 1': 150000, 'ZONE 2': 200000, 'ZONE 3': 250000},
    {'Kategori': 'Home Theater', 'ZONE 1': 150000, 'ZONE 2': 200000, 'ZONE 3': 250000},
    {'Kategori': 'TV (<= 43")', 'ZONE 1': 150000, 'ZONE 2': 200000, 'ZONE 3': 250000},
    {'Kategori': 'Mesin Cuci', 'ZONE 1': 200000, 'ZONE 2': 300000, 'ZONE 3': 400000},
    {'Kategori': 'Kulkas 1 Pintu', 'ZONE 1': 300000, 'ZONE 2': 400000, 'ZONE 3': 500000},
    {'Kategori': 'Kulkas Side by Side', 'ZONE 1': 700000, 'ZONE 2': 850000, 'ZONE 3': 950000},
]
df_harga = pd.DataFrame(data_harga)

# --- JUDUL APLIKASI ---
st.title("🚛 Kalkulator Ongkir GEM (Prototype)")
st.caption("Cabang: Blibli Elektronik - Banjaran Bandung")
st.markdown("---")

# --- SIDEBAR: FLOW INPUT USER ---
with st.sidebar:
    st.header("📍 Pengaturan Kirim")
    
    # 1. Pilih Kota
    list_kota = sorted(df_lokasi['City'].unique())
    pilih_kota = st.selectbox("1. Pilih Kota/Kabupaten", list_kota)
    
    # 2. Pilih Kode Pos (Difilter sesuai Kota)
    df_filtered_kota = df_lokasi[df_lokasi['City'] == pilih_kota]
    list_kodepos = sorted(df_filtered_kota['Postal Code'].unique())
    pilih_kodepos = st.selectbox("2. Pilih Kode Pos", list_kodepos)
    
    # 3. Tipe Layanan
    tipe_layanan = st.radio("3. Tipe Layanan", ["Regular Delivery", "Trade In Delivery"])
    
    st.info("ℹ️ Pilih Kode Pos untuk otomatis set Zona & Jarak.")
    
    if st.button("🔄 Reset Kalkulator"):
        st.rerun()

# --- LOGIC PENENTUAN ZONA (OTOMATIS) ---
# Ambil data baris yang sesuai dengan Kode Pos yang dipilih user
row_data = df_filtered_kota[df_filtered_kota['Postal Code'] == pilih_kodepos].iloc[0]

zona_aktif = row_data['Minimum Charge']
jarak_aktif = row_data['Blibli Elektronik - Banjaran Bandung']

# --- TAMPILAN HEADER INFO ---
# Menampilkan info Zona dan Jarak di bagian atas agar User yakin
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("Tujuan Kirim", f"{pilih_kota}")
with col_info2:
    st.metric("Zona Tarif", zona_aktif)
with col_info3:
    st.metric("Jarak Tempuh", f"{jarak_aktif} Km")

st.markdown("---")

# --- AREA INPUT BARANG & HASIL ---
col_input, col_result = st.columns([2, 1.2])

cart = [] # List untuk menyimpan barang yang dipilih

with col_input:
    st.subheader("📦 Input Barang")
    st.write("Masukkan jumlah barang yang akan dikirim:")
    
    # Container agar terlihat rapi
    with st.container(border=True):
        # Header Tabel Input
        c1, c2, c3 = st.columns([3, 1.5, 2])
        c1.markdown("**Nama Barang**")
        c2.markdown("**Qty**")
        c3.markdown("**Subtotal (Internal)**")
        
        # Loop semua barang dari data dummy
        for index, row in df_harga.iterrows():
            nama_barang = row['Kategori']
            harga_per_unit = row[zona_aktif] # Ambil harga sesuai Zona Aktif
            
            # Baris Input
            cols = st.columns([3, 1.5, 2])
            with cols[0]:
                st.write(f"{nama_barang}")
                st.caption(f"(@ Rp {harga_per_unit:,.0f})") # Info harga satuan
            with cols[1]:
                qty = st.number_input(f"qty_{index}", min_value=0, step=1, label_visibility="collapsed")
            with cols[2]:
                subtotal = qty * harga_per_unit
                st.write(f"**Rp {subtotal:,.0f}**")
            
            if qty > 0:
                cart.append({
                    "Barang": nama_barang,
                    "Qty": qty,
                    "Harga": harga_per_unit,
                    "Total": subtotal
                })
            
            st.write("") # Spacer dikit

with col_result:
    # --- KARTU RINGKASAN BIAYA ---
    st.subheader("💰 Total Biaya")
    
    total_gdpa = sum(item['Total'] for item in cart)
    
    # Logic Diskon / Free Shipping
    biaya_customer = total_gdpa
    diskon_text = ""
    is_free = False
    
    if tipe_layanan == "Trade In Delivery":
        biaya_customer = 0
        is_free = True
        diskon_text = "✅ PROMO: Trade In (Gratis Ongkir)"
    
    # Styling CSS untuk Kartu Harga
    st.markdown(f"""
    <div style="
        background-color: #f0f8ff; 
        padding: 20px; 
        border-radius: 12px; 
        border: 2px solid #cce5ff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h4 style="margin:0; color:#555;">Biaya Internal (GDPa)</h4>
        <h2 style="margin:0; color:#333;">Rp {total_gdpa:,.0f}</h2>
        <hr style="border-top: 1px dashed #bbb;">
        
        <h4 style="margin:0; color:#555;">Tagihan Customer</h4>
        {'<h1 style="margin:0; color:green; font-size:36px;">GRATIS</h1>' if is_free else f'<h1 style="margin:0; color:#004085;">Rp {biaya_customer:,.0f}</h1>'}
        <p style="margin-top:5px; color:green; font-weight:bold;">{diskon_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tampilkan Detail List Barang jika ada isinya
    if cart:
        st.write("---")
        st.write("**Rincian Barang:**")
        df_cart = pd.DataFrame(cart)
        st.dataframe(df_cart, hide_index=True, use_container_width=True)
    else:
        st.info("Belum ada barang dipilih.")
