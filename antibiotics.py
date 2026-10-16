import sqlite3
import streamlit as st
import pandas as pd

# Khởi tạo cơ sở dữ liệu
def init_db():
    conn = sqlite3.connect("smart_antibiotics.db", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS antibiotics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            spectrum TEXT,
            indication TEXT,
            dosage TEXT,
            side_effects TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            test_type TEXT NOT NULL,
            sample_source TEXT,
            identified_pathogen TEXT,
            conclusion TEXT,
            test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pathogen_guidelines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pathogen_name TEXT NOT NULL,
            gram_type TEXT,
            recommended_drugs TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# Seed dữ liệu mẫu nếu bảng trống
cursor.execute("SELECT COUNT(*) FROM antibiotics")
if cursor.fetchone()[0] == 0:
    initial_drugs = [
        ("Amoxicillin/Clavulanate (Augmentin)", "Beta-lactam", "Phổ rộng", "Nhiễm khuẩn hô hấp, tiết niệu", "1000mg x 2 lần/ngày", "Tiêu chảy, buồn nôn"),
        ("Ceftriaxone", "Beta-lactam (Gen 3)", "Phổ rộng (Gram +, Gram -)", "Viêm màng não, nhiễm trùng huyết, lậu", "1g - 2g/ngày", "Đau chỗ tiêm, bùn mật"),
        ("Cefepime", "Beta-lactam (Gen 4)", "Phổ rất rộng (Kể cả P. aeruginosa)", "Nhiễm trùng bệnh viện nặng", "1g - 2g x 2-3 lần/ngày", "Phát ban, tiêu chảy"),
        ("Meropenem", "Beta-lactam (Carbapenem)", "Phổ siêu rộng (Đa kháng thuốc)", "Nhiễm trùng nặng, ổ bụng, huyết", "500mg - 1g x 3 lần/ngày", "Buồn nôn, động kinh hiếm gặp"),
        ("Azithromycin", "Macrolide", "Gram (+), Vi khuẩn không điển hình", "Viêm phổi cộng đồng, hô hấp", "500mg/ngày", "Đau bụng, kéo dài QT"),
        ("Ciprofloxacin", "Fluoroquinolone", "Chủ yếu Gram (-), P. aeruginosa", "Nhiễm trùng tiết niệu, tiêu hóa", "500mg x 2 lần/ngày", "Đứt gân Cót, nhạy cảm ánh sáng"),
        ("Levofloxacin", "Fluoroquinolone", "Phổ rộng", "Viêm phổi, viêm xoang, tiết niệu", "500mg - 750mg x 1 lần/ngày", "Mất ngủ, chóng mặt"),
        ("Vancomycin", "Glycopeptide", "Gram (+) đa kháng (MRSA)", "Nhiễm trùng MRSA nặng", "15-20 mg/kg x 2-3 lần/ngày", "Hội chứng người đỏ, độc thận"),
        ("Metronidazole", "Nitroimidazole", "Vi khuẩn kỵ khí, Ký sinh trùng", "Nhiễm trùng ổ bụng, phụ khoa", "500mg x 3 lần/ngày", "Vị kim loại, buồn nôn"),
        ("Colistin", "Polymyxin", "Gram (-) siêu đa kháng (Acinetobacter, P. aeruginosa)", "Nhiễm trùng nặng do vi khuẩn kháng Carbapenem", "Theo chỉ định chuyên khoa", "Độc thận, độc thần kinh")
    ]
    cursor.executemany('INSERT INTO antibiotics (name, category, spectrum, indication, dosage, side_effects) VALUES (?, ?, ?, ?, ?, ?)', initial_drugs)
    conn.commit()

cursor.execute("SELECT COUNT(*) FROM pathogen_guidelines")
if cursor.fetchone()[0] == 0:
    initial_guidelines = [
        ("Staphylococcus aureus (MSSA)", "Gram dương", "Amoxicillin/Clavulanate, Ceftriaxone", "Nhạy cảm với nhóm Beta-lactam thông thường."),
        ("Staphylococcus aureus kháng Methicillin (MRSA)", "Gram dương", "Vancomycin, Linezolid", "Tuyệt đối không dùng nhóm Beta-lactam thông thường."),
        ("Pseudomonas aeruginosa (Trực khuẩn mủ xanh)", "Gram âm", "Cefepime, Meropenem, Ciprofloxacin, Levofloxacin", "Vi khuẩn kháng tự nhiên nhiều loại thuốc."),
        ("Escherichia coli (E. coli)", "Gram âm", "Ceftriaxone, Ciprofloxacin, Amoxicillin/Clavulanate", "Thường gây nhiễm trùng tiết niệu, ổ bụng."),
        ("Acinetobacter baumannii", "Gram âm", "Meropenem, Colistin", "Thường gặp trong nhiễm trùng bệnh viện."),
        ("Streptococcus pneumoniae (Phế cầu)", "Gram dương", "Amoxicillin/Clavulanate, Ceftriaxone, Levofloxacin", "Nguyên nhân hàng đầu gây viêm phổi cộng đồng.")
    ]
    cursor.executemany('INSERT INTO pathogen_guidelines (pathogen_name, gram_type, recommended_drugs, notes) VALUES (?, ?, ?, ?)', initial_guidelines)
    conn.commit()

# Giao diện Web Streamlit
st.set_page_config(page_title="Hệ thống Quản lý Kháng sinh", page_icon="💊", layout="wide")

st.title("💊 Hệ thống Quản lý Kháng sinh & Đề xuất Lâm sàng thông minh")
st.markdown("Ứng dụng hỗ trợ tra cứu danh mục thuốc, ghi nhận kết quả xét nghiệm vi sinh và đề xuất phác đồ điều trị.")

menu = [
    "Xem danh mục thuốc", 
    "Nhập xét nghiệm & Đề xuất", 
    "Lịch sử xét nghiệm bệnh nhân", 
    "Tra cứu theo vi khuẩn", 
    "Thêm thuốc mới", 
    "Thông tin thanh toán"
]
choice = st.sidebar.selectbox("Chọn chức năng", menu)

if choice == "Xem danh mục thuốc":
    st.subheader("📚 Danh mục thuốc kháng sinh hiện có")
    df = pd.read_sql("SELECT * FROM antibiotics", conn)
    st.dataframe(df, use_container_width=True)

elif choice == "Nhập xét nghiệm & Đề xuất":
    st.subheader("🔬 Nhập kết quả xét nghiệm / Vi sinh / Chiếu chụp")
    with st.form("test_form"):
        patient_name = st.text_input("Họ tên bệnh nhân")
        test_type = st.text_input("Loại xét nghiệm / CĐHA (Ví dụ: Cấy đờm, X-quang...)")
        sample_source = st.text_input("Nguồn mẫu (Đờm, Máu, Nước tiểu...)")
        identified_pathogen = st.text_input("Tên vi khuẩn định danh (Ví dụ: Pseudomonas, MRSA...)")
        conclusion = st.text_area("Kết luận chẩn đoán")
        submitted = st.form_submit_button("Lưu và Đề xuất kháng sinh")
        
        if submitted:
            if patient_name and test_type:
                cursor.execute('''
                    INSERT INTO patient_tests (patient_name, test_type, sample_source, identified_pathogen, conclusion)
                    VALUES (?, ?, ?, ?, ?)
                ''', (patient_name, test_type, sample_source, identified_pathogen, conclusion))
                conn.commit()
                st.success(f"Đã lưu kết quả xét nghiệm cho bệnh nhân '{patient_name}'!")
                
                if identified_pathogen:
                    st.info(f"Hệ thống đề xuất kháng sinh cho vi khuẩn: **{identified_pathogen}**")
                    df_guide = pd.read_sql(f"SELECT * FROM pathogen_guidelines WHERE pathogen_name LIKE '%{identified_pathogen}%'", conn)
                    if not df_guide.empty:
                        st.dataframe(df_guide, use_container_width=True)
                    else:
                        st.warning("Không tìm thấy hướng dẫn cụ thể cho vi khuẩn này trong cơ sở dữ liệu.")
            else:
                st.error("Vui lòng điền đầy đủ Tên bệnh nhân và Loại xét nghiệm!")

elif choice == "Lịch sử xét nghiệm bệnh nhân":
    st.subheader("📋 Lịch sử xét nghiệm & Vi sinh")
    df = pd.read_sql("SELECT * FROM patient_tests ORDER BY test_date DESC", conn)
    st.dataframe(df, use_container_width=True)

elif choice == "Tra cứu theo vi khuẩn":
    st.subheader("🔍 Tra cứu đề xuất kháng sinh theo loại vi khuẩn")
    keyword = st.text_input("Nhập tên vi khuẩn cần tìm (Ví dụ: Pseudomonas, E. coli, MRSA...)")
    if keyword:
        df = pd.read_sql(f"SELECT * FROM pathogen_guidelines WHERE pathogen_name LIKE '%{keyword}%'", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Không tìm thấy kết quả phù hợp.")

elif choice == "Thêm thuốc mới":
    st.subheader("➕ Thêm thuốc kháng sinh mới vào hệ thống")
    with st.form("add_drug_form"):
        name = st.text_input("Tên thuốc")
        category = st.text_input("Phân nhóm (Ví dụ: Beta-lactam...)")
        spectrum = st.text_input("Phổ kháng khuẩn")
        indication = st.text_input("Chỉ định")
        dosage = st.text_input("Liều dùng")
        side_effects = st.text_input("Tác dụng phụ")
        submit_drug = st.form_submit_button("Thêm thuốc")
        
        if submit_drug:
            if name and category:
                cursor.execute('''
                    INSERT INTO antibiotics (name, category, spectrum, indication, dosage, side_effects)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, category, spectrum, indication, dosage, side_effects))
                conn.commit()
                st.success(f"Đã thêm thuốc '{name}' thành công!")
            else:
                st.error("Tên thuốc và phân nhóm không được để trống!")

elif choice == "Thông tin thanh toán":
    st.subheader("💳 Thông tin tài khoản thanh toán")
    st.markdown("Quý khách hoặc đối tác có thể chuyển khoản thanh toán qua thông tin dưới đây:")
    
    pay_data = {
        "Thông tin": ["Ngân hàng", "Chủ tài khoản", "Số tài khoản", "Nội dung mẫu"],
        "Chi tiết": [
            "MB (Ngân hàng Quân đội)",[span_2](start_span)[span_2](end_span)
            "HOANG HAI AN",[span_3](start_span)[span_3](end_span)
            "0030132291981",[span_4](start_span)[span_4](end_span)
            "Thanh toan vien phi / Mua thuoc"
        ]
    }
    df_pay = pd.DataFrame(pay_data)
    st.table(df_pay)
    st.info("Vui lòng kiểm tra kỹ thông tin tài khoản trước khi thực hiện giao dịch chuyển khoản.")
