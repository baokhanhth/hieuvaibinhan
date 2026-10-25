# Hệ thống Quản lý Bán hàng và Kho hàng - Hiệu Vải Bình An

🔗 **Live Demo:** https://hieuvaibinhan.vercel.app/

## 📖 Giới thiệu dự án

### 🚨 Bối cảnh & Vấn đề (As-Is)
Hiện nay, Hiệu vải Bình An vận hành hoàn toàn bằng phương pháp thủ công. Mọi hoạt động từ lập hóa đơn, theo dõi lượng vải bán ra, quản lý tồn kho đến tính toán doanh thu đều được thực hiện qua sổ ghi chép hoặc ghi nhớ cá nhân. Phương thức này tồn tại nhiều điểm nghẽn:
* Dễ xảy ra sai sót, nhầm lẫn trong tính toán tổng tiền, đặc biệt vào giờ cao điểm.
* Dữ liệu tồn kho không chính xác do ghi tay không kịp thời, dẫn đến tình trạng thiếu hụt hoặc thừa hàng hóa tại quầy.
* Gây mất nhiều thời gian để đối soát doanh thu và kiểm tra lịch sử giao dịch.

### 💡 Giải pháp & Mục tiêu (To-Be)
Hệ thống Quản lý Kho và Bán hàng ra đời nhằm **số hóa và tự động hóa quy trình vận hành cốt lõi**. Dự án giải quyết bài toán trọng tâm: **Lên đơn hàng nhanh chóng - Tính tiền chuẩn xác - Khấu trừ kho tự động**.
* **Tăng hiệu suất:** Dự kiến giảm 50-70% thời gian tính tiền và lên đơn cho một giao dịch bán lẻ trực tiếp.
* **Quản lý kho thời gian thực:** Tự động trừ kho khi bán, cộng kho khi nhập và hiển thị cảnh báo khi số lượng hàng hóa dưới ngưỡng quy định.
* **Minh bạch dữ liệu:** Lưu trữ toàn bộ lịch sử đơn hàng, hỗ trợ hệ thống báo cáo thống kê trực quan để chủ cửa hàng có căn cứ nhập hàng và ra quyết định kinh doanh.

## 📊 Giải quyết nghiệp vụ
Dự án được phát triển theo quy trình chuẩn, trong đó khâu Phân tích Nghiệp vụ (BA) đóng vai trò định hình toàn bộ luồng hoạt động của hệ thống:
* **Khảo sát & Đặc tả yêu cầu (SRS):** Xây dựng tài liệu Software Requirements Specification (SRS) chi tiết, định nghĩa rõ ràng các User Stories (từ US01 đến US15) phục vụ cho từng đối tượng người dùng (Stakeholders).
* **Mô hình hóa quy trình (BPMN & UML):** Sử dụng mô hình BPMN để rà soát quy trình hiện tại (As-Is) và tái thiết kế quy trình kinh doanh cải tiến (To-Be). Ứng dụng UML (Use Case Diagram, Activity Diagram) để rẽ nhánh chi tiết các luồng xử lý ngoại lệ (Exception flows) và luồng thay thế (Alternative flows) cho từng chức năng.
* **Thiết lập Quy tắc nghiệp vụ (Business Rules):** Định nghĩa chặt chẽ các ràng buộc như: tự động hoàn trả tồn kho khi hủy đơn, cảnh báo khi tồn kho <= 5m, không cho phép nhập số lượng âm, và chỉ áp dụng hình thức "xóa mềm" (chuyển trạng thái ngừng kinh doanh) đối với sản phẩm để bảo toàn lịch sử dữ liệu.
* **Thiết kế Trải nghiệm (UI/UX):** Phác thảo Wireframe và Mockup bằng Figma, thiết kế Screen Flow trực quan giúp tối ưu hóa luồng thao tác của người dùng không chuyên về kỹ thuật.

## 🔐 Tài khoản Demo

* **Chủ cửa hàng (Toàn quyền):** `chucuahang` | Mật khẩu: `Demo@123`
* **Nhân viên (Chỉ bán hàng):** `nhanvien1` | Mật khẩu: `Demo@123`
* **Admin (Quản trị hệ thống):** `admin` | Mật khẩu: `Demo@123`

## 🚀 Tính năng nổi bật
* **Quản lý bán hàng (POS):** Tạo đơn hàng nháp, tự động tính tổng tiền, ngăn chặn thanh toán khi số lượng mua vượt tồn kho và xuất hóa đơn PDF trực tiếp.
* **Quản lý kho hàng & Nhập hàng:** Quản lý danh mục vải, tạo phiếu nhập hàng thông qua chức năng tìm kiếm nhanh, lưu trữ chi tiết lịch sử cập nhật và thay đổi giá vốn.
* **Cảnh báo tồn kho tự động:** Gửi cảnh báo ngay lập tức trên hệ thống khi có mặt hàng tồn kho chạm ngưỡng tối thiểu (<= 5 mét).
* **Báo cáo & Thống kê:** Dashboard trực quan hiển thị tổng doanh thu, số lượng đơn bán, top mặt hàng bán chạy/bán chậm với biểu đồ Chart.js.
* **Đảm bảo chất lượng (QA/QC):** Hệ thống trải qua kiểm thử thủ công (Manual Testing) nghiêm ngặt với 305 Test Cases (bao phủ các trường hợp Positive, Negative, Value Boundary), đạt tỷ lệ Pass 97.4%.

## 🛠 Công nghệ sử dụng
* **Backend:** Python, Django Framework. Triển khai kiến trúc RESTful API và Django ORM.
* **Frontend:** HTML5, CSS3, JavaScript, Chart.js.
* **Cơ sở dữ liệu:** SQLite (Local) / Neon PostgreSQL (Production).
* **Triển khai (Deployment):** Vercel tích hợp WhiteNoise.

## ⚙️ Hướng dẫn cài đặt (Local)
```bash
# 1. Clone repository
git clone https://github.com/baokhanhth/hieuvaibinhan.git
cd hieuvaibinhan

# 2. Tạo & Kích hoạt môi trường ảo
python -m venv venv
venv\Scripts\activate  # Dành cho Windows
# source venv/bin/activate # Dành cho macOS/Linux

# 3. Cài đặt thư viện
pip install -r requirements.txt

# 4. Khởi tạo Database
python manage.py migrate

# 5. Chạy Server
python manage.py runserver
