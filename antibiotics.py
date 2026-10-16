import sqlite3
from tabulate import tabulate

class SmartAntibioticManager:
    def __init__(self, db_name="smart_antibiotics.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.seed_initial_data()

    def create_tables(self):
        """Tạo các bảng cơ sở dữ liệu cần thiết"""
        self.cursor.execute('''
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

        self.cursor.execute('''
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

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pathogen_guidelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pathogen_name TEXT NOT NULL,
                gram_type TEXT,
                recommended_drugs TEXT,
                notes TEXT
            )
        ''')
        self.conn.commit()

    def seed_initial_data(self):
        """Nạp dữ liệu mẫu cho thuốc và hướng dẫn điều trị"""
        self.cursor.execute("SELECT COUNT(*) FROM antibiotics")
        if self.cursor.fetchone()[0] == 0:
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
            self.cursor.executemany('INSERT INTO antibiotics (name, category, spectrum, indication, dosage, side_effects) VALUES (?, ?, ?, ?, ?, ?)', initial_drugs)

        self.cursor.execute("SELECT COUNT(*) FROM pathogen_guidelines")
        if self.cursor.fetchone()[0] == 0:
            initial_guidelines = [
                ("Staphylococcus aureus (MSSA)", "Gram dương", "Amoxicillin/Clavulanate, Ceftriaxone", "Nhạy cảm với nhóm Beta-lactam thông thường."),
                ("Staphylococcus aureus kháng Methicillin (MRSA)", "Gram dương", "Vancomycin, Linezolid", "Tuyệt đối không dùng nhóm Beta-lactam thông thường."),
                ("Pseudomonas aeruginosa (Trực khuẩn mủ xanh)", "Gram âm", "Cefepime, Meropenem, Ciprofloxacin, Levofloxacin", "Vi khuẩn kháng tự nhiên nhiều loại thuốc."),
                ("Escherichia coli (E. coli)", "Gram âm", "Ceftriaxone, Ciprofloxacin, Amoxicillin/Clavulanate", "Thường gây nhiễm trùng tiết niệu, ổ bụng."),
                ("Acinetobacter baumannii", "Gram âm", "Meropenem, Colistin", "Thường gặp trong nhiễm trùng bệnh viện."),
                ("Streptococcus pneumoniae (Phế cầu)", "Gram dương", "Amoxicillin/Clavulanate, Ceftriaxone, Levofloxacin", "Nguyên nhân hàng đầu gây viêm phổi cộng đồng.")
            ]
            self.cursor.executemany('INSERT INTO pathogen_guidelines (pathogen_name, gram_type, recommended_drugs, notes) VALUES (?, ?, ?, ?)', initial_guidelines)
            self.conn.commit()

    def view_drugs(self):
        print("\n--- DANH MỤC THUỐC KHÁNG SINH ---")
        self.cursor.execute("SELECT id, name, category, spectrum, indication, dosage FROM antibiotics")
        rows = self.cursor.fetchall()
        headers = ["ID", "Tên thuốc", "Phân nhóm", "Phổ", "Chỉ định", "Liều dùng"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def add_patient_test(self):
        print("\n--- NHẬP KẾT QUẢ XÉT NGHIỆM / CHIẾU CHỤP ---")
        patient_name = input("Họ tên bệnh nhân: ").strip()
        test_type = input("Loại xét nghiệm/CĐHA (Cấy đờm, X-quang...): ").strip()
        sample_source = input("Nguồn mẫu (Đờm, Máu, Nước tiểu...): ").strip()
        identified_pathogen = input("Tên vi khuẩn phát hiện (Ví dụ: Pseudomonas, MRSA...): ").strip()
        conclusion = input("Kết luận chẩn đoán: ").strip()

        if not patient_name or not test_type:
            print("[Lỗi] Tên bệnh nhân và loại xét nghiệm không được để trống!")
            return

        self.cursor.execute('''
            INSERT INTO patient_tests (patient_name, test_type, sample_source, identified_pathogen, conclusion)
            VALUES (?, ?, ?, ?, ?)
        ''', (patient_name, test_type, sample_source, identified_pathogen, conclusion))
        self.conn.commit()
        print(f"[Thành công] Đã lưu kết quả xét nghiệm cho bệnh nhân '{patient_name}'!")

        if identified_pathogen:
            self.suggest_antibiotic_by_pathogen(identified_pathogen)

    def view_patient_tests(self):
        print("\n--- DANH SÁCH KẾT QUẢ XÉT NGHIỆM & VI SINH ---")
        self.cursor.execute("SELECT id, patient_name, test_type, sample_source, identified_pathogen, conclusion, test_date FROM patient_tests")
        rows = self.cursor.fetchall()

        if not rows:
            print("Chưa có dữ liệu xét nghiệm nào.")
            return

        headers = ["ID", "Bệnh nhân", "Loại XN", "Nguồn mẫu", "Vi khuẩn phát hiện", "Kết luận", "Thời gian"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def suggest_antibiotic_by_pathogen(self, keyword=None):
        print("\n--- HỆ THỐNG ĐỀ XUẤT KHÁNG SINH THEO VI KHUẨN ---")
        if not keyword:
            keyword = input("Nhập tên vi khuẩn cần tra cứu: ").strip()

        self.cursor.execute('''
            SELECT pathogen_name, gram_type, recommended_drugs, notes 
            FROM pathogen_guidelines 
            WHERE pathogen_name LIKE ?
        ''', (f'%{keyword}%',))
        results = self.cursor.fetchall()

        if not results:
            print(f"Không tìm thấy hướng dẫn chuẩn cụ thể cho vi khuẩn: '{keyword}'.")
            return

        print(f"\nKẾT QUẢ ĐỀ XUẤT ĐIỀU TRỊ CHO: '{keyword.upper()}'")
        headers = ["Tên vi khuẩn", "Đặc điểm (Gram)", "Kháng sinh đề xuất", "Lưu ý lâm sàng"]
        print(tabulate(results, headers=headers, tablefmt="grid"))

    def add_drug(self):
        print("\n--- THÊM THUỐC MỚI ---")
        name = input("Tên thuốc: ").strip()
        category = input("Phân nhóm: ").strip()
        spectrum = input("Phổ kháng khuẩn: ").strip()
        indication = input("Chỉ định: ").strip()
        dosage = input("Liều dùng: ").strip()
        side_effects = input("Tác dụng phụ: ").strip()

        self.cursor.execute('''
            INSERT INTO antibiotics (name, category, spectrum, indication, dosage, side_effects)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, category, spectrum, indication, dosage, side_effects))
        self.conn.commit()
        print(f"[Thành công] Đã thêm thuốc '{name}'!")

    def show_payment_info(self):
        """Hiển thị thông tin tài khoản thanh toán không cần QR"""
        print("\n==============================================")
        print("       THÔNG TIN TÀI KHOẢN THANH TOÁN         ")
        print("==============================================")
        payment_data = [
            ["Ngân hàng", "MB (Ngân hàng Quân đội)"],
            ["Chủ tài khoản", "HOANG HAI AN"],
            ["Số tài khoản", "0030132291981"],
            ["Nội dung mẫu", "Thanh toan vien phi / Mua thuoc"]
        ]
        print(tabulate(payment_data, headers=["Thông tin", "Chi tiết"], tablefmt="grid"))
        print("\n* Lưu ý: Vui lòng kiểm tra kỹ thông tin trước khi chuyển khoản.")

    def close(self):
        self.conn.close()

def main():
    manager = SmartAntibioticManager()
    
    while True:
        print("\n=======================================================")
        print("    HỆ THỐNG QUẢN LÝ & ĐỀ XUẤT KHÁNG SINH THÔNG MINH    ")
        print("=======================================================")
        print("1. Xem danh mục thuốc kháng sinh")
        print("2. Nhập kết quả xét nghiệm / Vi sinh / Chiếu chụp")
        print("3. Xem lịch sử kết quả xét nghiệm bệnh nhân")
        print("4. Tra cứu đề xuất kháng sinh theo loại vi khuẩn")
        print("5. Thêm thuốc kháng sinh mới vào hệ thống")
        print("6. Xem thông tin tài khoản thanh toán (Chuyển khoản)")
        print("7. Thoát")
        
        choice = input("\nChọn chức năng (1-7): ").strip()
        
        if choice == '1':
            manager.view_drugs()
        elif choice == '2':
            manager.add_patient_test()
        elif choice == '3':
            manager.view_patient_tests()
        elif choice == '4':
            manager.suggest_antibiotic_by_pathogen()
        elif choice == '5':
            manager.add_drug()
        elif choice == '6':
            manager.show_payment_info()
        elif choice == '7':
            print("\nTạm biệt bác sĩ/Dược sĩ!")
            manager.close()
            break
        else:
            print("[Lỗi] Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()
