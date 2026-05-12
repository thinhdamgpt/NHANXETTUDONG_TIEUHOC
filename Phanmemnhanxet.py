import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import io
import random
import uuid

# --- CẤU HÌNH TRANG & GIAO DIỆN PREMIUM (ĐƯA LÊN TRÊN CÙNG) ---
st.set_page_config(layout="wide", page_title="Đổi mới cùng thầy Thịnh", page_icon="✨")

st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #1A73E8, #34A853); padding: 15px 25px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); flex-wrap: wrap; gap: 15px;">
    <div style="text-align: left; min-width: 300px;">
        <h1 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">✨ Đổi mới cùng thầy Thịnh ✨</h1>
        <p style="color: #e8f0fe; font-size: 1.1rem; font-style: italic; margin-top: 5px; margin-bottom: 0; font-weight: 500;">Hệ thống Nhận xét Học bạ Tự động AI - Chuẩn TT27</p>
    </div>
    <div style="text-align: right; border-left: 2px solid rgba(255,255,255,0.3); padding-left: 20px; flex: 1; min-width: 300px;">
        <p style="font-size: 1rem; font-style: italic; color: white; margin: 0; line-height: 1.4;">"Học tập là hạt giống của kiến thức,<br>kiến thức là hạt giống của hạnh phúc."</p>
        <p style="font-size: 0.85rem; font-weight: 700; color: #e8f0fe; margin: 5px 0 0 0;">– Ngạn ngữ Gruzia –</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""<style>
.main { background-color: #f0f4f8; font-family: 'Inter', sans-serif; } 
.copy-area { background-color: #ffffff; padding: 18px; border-radius: 8px; border: 1px solid #d1d9e6; margin-top: 20px; max-height: 300px; overflow-y: auto; white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 14.5px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); line-height: 1.6;}
div[data-testid="stSidebar"] { background-color: #ffffff; box-shadow: 2px 0 12px rgba(0,0,0,0.06); }
.stButton>button { background-color: #1A73E8; color: white; border-radius: 6px; border: none; font-weight: 600; padding: 10px 20px; transition: all 0.3s ease; }
.stButton>button:hover { background-color: #1557b0; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(26,115,232,0.3); }
</style>""", unsafe_allow_html=True)

# --- 1. MA TRẬN PHÂN PHỐI CHƯƠNG TRÌNH GDPT 2018 ĐƯỢC CHIA CHI TIẾT THEO KỲ HỌC ---
PHAN_PHOI_CHUONG_TRINH = {
    "Tiếng Việt": {
        "Khối 1": {"Giữa học kì I": ["âm và chữ cái", "đọc và ghép các vần", "cầm bút và viết nét cơ bản"], "Cuối học kì I": ["đọc trơn từ và câu ngắn", "viết đúng các vần khó", "nghe hiểu và trả lời câu hỏi"], "Giữa học kì II": ["đọc trơn đoạn văn ngắn", "tô chữ hoa và viết đúng ô ly", "đọc thành tiếng rõ ràng"], "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Việt", "kỹ năng đọc hiểu văn bản", "năng lực viết chính tả và kể chuyện"]},
        "Khối 2": {"Giữa học kì I": ["đọc ngắt nghỉ đúng dấu câu", "từ chỉ sự vật, hoạt động", "nghe viết chính tả"], "Cuối học kì I": ["viết đoạn văn ngắn 4-5 câu", "mở rộng vốn từ theo chủ điểm", "kể chuyện theo tranh"], "Giữa học kì II": ["đọc hiểu và trả lời câu hỏi chi tiết", "từ chỉ đặc điểm", "viết câu chuẩn ngữ pháp"], "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Việt", "năng lực đọc hiểu và tóm tắt", "kỹ năng viết đoạn văn miêu tả"]},
        "Khối 3": {"Giữa học kì I": ["đọc diễn cảm", "nhận biết hình ảnh so sánh", "viết đoạn văn tả sự vật"], "Cuối học kì I": ["viết thư hoặc đoạn văn kể chuyện", "từ ngữ về cộng đồng, quê hương", "đọc hiểu văn bản truyện"], "Giữa học kì II": ["nhận biết hình ảnh nhân hóa", "đọc hiểu văn bản thông tin", "mở rộng vốn từ sáng tạo"], "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Việt", "năng lực đọc hiểu đa dạng văn bản", "kỹ năng viết văn miêu tả chi tiết"]},
        "Khối 4": {"Giữa học kì I": ["đọc hiểu văn bản sâu", "nhận biết danh từ, động từ", "viết bài văn kể chuyện", "cấu tạo của tiếng"], "Cuối học kì I": ["viết bài văn miêu tả đồ vật", "hiểu và vận dụng biện pháp tu từ", "đọc diễn cảm bài thơ", "nhận biết câu hỏi, câu kể"], "Giữa học kì II": ["đọc diễn cảm và tóm tắt bài", "nhận biết tính từ, câu khiến", "viết bài văn miêu tả cây cối", "xác định chủ ngữ, vị ngữ"], "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Việt", "năng lực đọc diễn cảm và cảm thụ", "kỹ năng viết bài văn hoàn chỉnh"]},
        "Khối 5": {"Giữa học kì I": ["đọc diễn cảm văn bản dài", "từ đồng nghĩa, từ trái nghĩa", "viết bài văn tả cảnh", "từ nhiều nghĩa"], "Cuối học kì I": ["sử dụng đại từ, quan hệ từ", "viết đơn từ", "đọc hiểu văn bản đa phương thức", "viết văn tả người"], "Giữa học kì II": ["hiểu ý nghĩa biện pháp nghệ thuật", "câu ghép và cách nối các vế câu", "viết bài văn tả đồ vật"], "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Việt", "năng lực cảm thụ văn học", "kỹ năng tổng kết vốn từ và liên kết câu"]}
    },
    "Toán": {
        "Khối 1": {"Giữa học kì I": ["các số đến 10", "so sánh số phạm vi 10", "đếm và cấu tạo số"], "Cuối học kì I": ["phép cộng, trừ trong phạm vi 10", "nhận biết hình vuông, tròn, tam giác", "giải bài toán cơ bản"], "Giữa học kì II": ["các số đến 100", "phép cộng trừ không nhớ phạm vi 100", "đo độ dài bằng gang tay, bước chân"], "Cuối học kì II": ["kiến thức toàn chương trình Toán học", "kỹ năng thực hiện phép tính cơ bản", "năng lực giải toán có lời văn"]},
        "Khối 2": {"Giữa học kì I": ["phép cộng có nhớ phạm vi 100", "bài toán nhiều hơn, ít hơn", "đơn vị đo độ dài cm, dm"], "Cuối học kì I": ["phép trừ có nhớ phạm vi 100", "đơn vị đo khối lượng kg, dung tích l", "xem lịch, xem đồng hồ"], "Giữa học kì II": ["bảng nhân, chia 2 và 5", "nhận biết khối trụ, khối cầu", "giải toán có lời văn"], "Cuối học kì II": ["kiến thức toàn chương trình Toán học", "kỹ năng tính toán phạm vi 1000", "năng lực vận dụng đại lượng đo lường"]},
        "Khối 3": {"Giữa học kì I": ["bảng nhân chia 6-9", "nhân chia số có hai chữ số", "giải toán bằng một phép tính"], "Cuối học kì I": ["số trong phạm vi 10.000", "tính giá trị biểu thức", "nhận biết góc vuông, không vuông"], "Giữa học kì II": ["số trong phạm vi 100.000", "tính chu vi, diện tích hình chữ nhật, hình vuông", "thống kê số liệu"], "Cuối học kì II": ["kiến thức toàn chương trình Toán học", "kỹ năng thực hiện 4 phép tính", "năng lực giải toán bằng hai phép tính"]},
        "Khối 4": {"Giữa học kì I": ["số có nhiều chữ số", "các phép toán với số tự nhiên", "tìm số trung bình cộng"], "Cuối học kì I": ["tính chất giao hoán, kết hợp", "góc và hai đường thẳng song song, vuông góc", "chia cho số có 2 chữ số"], "Giữa học kì II": ["phân số và tính chất cơ bản", "rút gọn và quy đồng phân số", "phép cộng, trừ phân số"], "Cuối học kì II": ["kiến thức toàn chương trình Toán học", "kỹ năng giải toán phân số", "năng lực tư duy logic và tính toán tổng hợp"]},
        "Khối 5": {"Giữa học kì I": ["khái niệm số thập phân", "phép cộng, trừ số thập phân", "giải toán về số thập phân"], "Cuối học kì I": ["phép nhân, chia số thập phân", "tỉ số phần trăm", "giải toán tỉ số phần trăm"], "Giữa học kì II": ["diện tích hình tam giác, hình thang", "diện tích xung quanh và toàn phần", "hình hộp chữ nhật, hình lập phương"], "Cuối học kì II": ["kiến thức toàn chương trình Toán học", "năng lực giải toán chuyển động, thể tích", "kỹ năng tính toán số thập phân tổng hợp"]}
    },
    "Tiếng Anh": {
        "Khối 1": {"Giữa học kì I": ["từ vựng chữ cái cơ bản", "nghe hiểu chào hỏi"], "Cuối học kì I": ["phát âm chữ cái", "từ vựng màu sắc, số đếm"], "Giữa học kì II": ["từ vựng chủ đề gia đình, đồ vật"], "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Anh", "năng lực nghe hiểu cơ bản", "kỹ năng phát âm từ vựng quen thuộc"]},
        "Khối 2": {"Giữa học kì I": ["từ vựng chủ đề trường học", "hỏi đáp tên, tuổi"], "Cuối học kì I": ["từ vựng chủ đề động vật, cơ thể"], "Giữa học kì II": ["mẫu câu nói về sở thích"], "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Anh", "kỹ năng nghe hội thoại ngắn", "năng lực vận dụng mẫu câu giao tiếp"]},
        "Khối 3": {"Giữa học kì I": ["mẫu câu giới thiệu cơ bản", "từ vựng chủ đề gia đình, nghề nghiệp"], "Cuối học kì I": ["đọc hiểu đoạn văn ngắn", "hỏi đáp thời gian"], "Giữa học kì II": ["từ vựng môn học, hoạt động giải trí"], "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Anh", "kỹ năng viết câu đơn giản", "năng lực phản xạ giao tiếp cơ bản"]},
        "Khối 4": {"Giữa học kì I": ["ngữ pháp hiện tại đơn", "từ vựng chủ đề ngoại hình, tính cách"], "Cuối học kì I": ["nghe hội thoại", "mô tả hoạt động thường ngày"], "Giữa học kì II": ["từ vựng thực phẩm, nơi chốn"], "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Anh", "kỹ năng đọc hiểu văn bản", "năng lực viết đoạn văn ngắn"]},
        "Khối 5": {"Giữa học kì I": ["ngữ pháp thì quá khứ đơn", "hỏi đường, địa điểm"], "Cuối học kì I": ["thuyết trình ngắn", "từ vựng nghề nghiệp tương lai"], "Giữa học kì II": ["ngữ pháp thì tương lai đơn", "đọc hiểu văn bản dài"], "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Anh", "kỹ năng giao tiếp tự tin", "năng lực vận dụng ngữ pháp tổng hợp"]}
    },
    "Khoa học": {
        "Khối 4": {"Giữa học kì I": ["nhu cầu sống của thực vật, động vật", "trao đổi chất ở người"], "Cuối học kì I": ["chuỗi thức ăn", "vai trò của nước, không khí"], "Giữa học kì II": ["sự chuyển thể của các chất", "âm thanh và ánh sáng"], "Cuối học kì II": ["kiến thức toàn chương trình Khoa học", "năng lực tìm hiểu tự nhiên", "kỹ năng vận dụng kiến thức bảo vệ môi trường"]},
        "Khối 5": {"Giữa học kì I": ["sự sinh sản của động vật, thực vật", "đặc điểm sinh lý của con người"], "Cuối học kì I": ["bệnh truyền nhiễm và cách phòng tránh", "chất liệu quanh ta (tre, mây, sắt,...)"], "Giữa học kì II": ["sự biến đổi hóa học của các chất", "sử dụng năng lượng (mặt trời, gió, điện)"], "Cuối học kì II": ["kiến thức toàn chương trình Khoa học", "năng lực giải thích sự vật hiện tượng", "ý thức bảo vệ tài nguyên thiên nhiên"]}
    },
    "Lịch sử & Địa lý": {
        "Khối 4": {"Giữa học kì I": ["đặc điểm địa hình, khí hậu, sông ngòi Việt Nam", "làm quen với bản đồ, lược đồ"], "Cuối học kì I": ["lịch sử thời Hùng Vương, Âu Lạc", "các vùng đồng bằng Bắc Bộ, Nam Bộ"], "Giữa học kì II": ["thời kỳ Bắc thuộc và đấu tranh giành độc lập", "khởi nghĩa Hai Bà Trưng, Lý Bí"], "Cuối học kì II": ["kiến thức toàn chương trình Lịch sử & Địa lý", "kỹ năng sử dụng bản đồ, lược đồ", "năng lực nắm bắt đặc điểm các vùng miền"]},
        "Khối 5": {"Giữa học kì I": ["thời kỳ Trịnh - Nguyễn phân tranh", "khởi nghĩa Tây Sơn", "đặc điểm địa hình, khoáng sản Việt Nam"], "Cuối học kì I": ["nhà Nguyễn suy vong, Pháp xâm lược", "dân cư, hoạt động kinh tế Việt Nam"], "Giữa học kì II": ["phong trào Cần Vương, Xô Viết Nghệ Tĩnh", "chiến dịch Điện Biên Phủ", "châu Á, châu Âu"], "Cuối học kì II": ["kiến thức toàn chương trình Lịch sử & Địa lý", "năng lực phân tích sự kiện lịch sử", "kỹ năng tổng hợp đặc điểm địa lý các châu lục"]}
    },
    "Tin học": {
        "Khối 3": {"Giữa học kì I": ["nhận biết các bộ phận máy tính", "thao tác chuột cơ bản"], "Cuối học kì I": ["sử dụng bàn phím", "phần mềm vẽ cơ bản"], "Giữa học kì II": ["phần mềm học tập đơn giản", "lưu trữ tệp"], "Cuối học kì II": ["kiến thức toàn chương trình Tin học", "kỹ năng thao tác máy tính cơ bản", "ý thức an toàn khi sử dụng máy tính"]},
        "Khối 4": {"Giữa học kì I": ["gõ phím mười ngón", "quản lý thư mục và tệp"], "Cuối học kì I": ["soạn thảo văn bản tiếng Việt", "chỉnh sửa phông chữ"], "Giữa học kì II": ["tìm kiếm thông tin an toàn trên internet", "chèn hình ảnh trong văn bản"], "Cuối học kì II": ["kiến thức toàn chương trình Tin học", "kỹ năng soạn thảo văn bản", "năng lực sử dụng phần mềm trình chiếu"]},
        "Khối 5": {"Giữa học kì I": ["định dạng văn bản nâng cao", "chèn bảng biểu"], "Cuối học kì I": ["tạo bài trình chiếu đa phương tiện", "sử dụng hiệu ứng động"], "Giữa học kì II": ["làm quen với lập trình trực quan", "các câu lệnh cơ bản"], "Cuối học kì II": ["kiến thức toàn chương trình Tin học", "năng lực tư duy lập trình trực quan", "kỹ năng ứng dụng công nghệ thông tin"]}
    },
    "GDTC": {
        "Khối 1": {"Giữa học kì I": ["tư thế đứng, ngồi cơ bản", "đội hình hàng dọc, hàng ngang"], "Cuối học kì I": ["bài thể dục phát triển chung cơ bản", "trò chơi vận động rèn sự khéo léo"], "Giữa học kì II": ["vận động phối hợp tay chân", "đi theo vạch kẻ thẳng"], "Cuối học kì II": ["toàn bộ chương trình vận động cơ bản", "kỹ năng rèn luyện tư thế đúng", "tinh thần tham gia trò chơi tập thể"]},
        "Khối 2": {"Giữa học kì I": ["đội hình vòng tròn", "động tác vươn thở, tay, chân"], "Cuối học kì I": ["động tác vặn mình, bụng, toàn thân", "trò chơi rèn sức nhanh"], "Giữa học kì II": ["đi kiễng gót, đi nhanh dần", "nhảy dây cơ bản"], "Cuối học kì II": ["toàn bộ chương trình thể dục phát triển chung", "kỹ năng phối hợp vận động", "ý thức rèn luyện sức bền"]},
        "Khối 3": {"Giữa học kì I": ["đội hình di chuyển", "động tác nhảy, điều hòa"], "Cuối học kì I": ["hoàn thiện bài thể dục liên hoàn", "trò chơi rèn luyện phản xạ"], "Giữa học kì II": ["nhảy dây kiểu chụm hai chân", "bật xa cơ bản"], "Cuối học kì II": ["toàn bộ chương trình rèn luyện thể chất", "kỹ năng vận động khéo léo", "tinh thần phối hợp đồng đội"]},
        "Khối 4": {"Giữa học kì I": ["đội hình chạy đều, đứng lại", "bài tập rèn sức bền nhẹ"], "Cuối học kì I": ["động tác thể dục nhịp điệu", "bật cao, bật xa"], "Giữa học kì II": ["tâng bóng, chuyền bóng", "nhảy dây bền"], "Cuối học kì II": ["toàn bộ chương trình rèn luyện thể lực", "kỹ năng thực hiện môn thể thao tự chọn", "tinh thần tự giác tập luyện"]},
        "Khối 5": {"Giữa học kì I": ["bài thể dục với cờ hoặc gậy", "đội hình phức hợp"], "Cuối học kì I": ["phối hợp chạy, nhảy, ném", "rèn luyện sức bền"], "Giữa học kì II": ["kỹ thuật bóng rổ, bóng đá cơ bản (tự chọn)", "bật nhảy nâng cao"], "Cuối học kì II": ["toàn bộ chương trình GDTC", "năng lực hoàn thiện kỹ năng vận động", "ý thức tổ chức kỷ luật trong thể thao"]}
    },
    "Âm nhạc": {
        "Khối 1": {"Giữa học kì I": ["nghe và vỗ tay theo nhịp", "hát đúng giai điệu đơn giản"], "Cuối học kì I": ["vận động phụ họa theo bài hát", "nhận biết âm thanh cao thấp"], "Giữa học kì II": ["hát kết hợp gõ đệm", "biểu diễn bài hát ngắn"], "Cuối học kì II": ["toàn bộ chương trình Âm nhạc cơ bản", "kỹ năng cảm thụ âm nhạc", "sự tự tin khi hát và biểu diễn"]},
        "Khối 2": {"Giữa học kì I": ["hát đúng giai điệu và lời ca", "phân biệt âm thanh nhạc cụ"], "Cuối học kì I": ["vận động theo nhịp điệu bài hát", "đọc tên nốt nhạc cơ bản"], "Giữa học kì II": ["gõ đệm theo phách, nhịp", "biểu diễn tự tin trước lớp"], "Cuối học kì II": ["toàn bộ chương trình Âm nhạc", "kỹ năng hát diễn cảm", "năng lực kết hợp hát và gõ đệm"]},
        "Khối 3": {"Giữa học kì I": ["hát diễn cảm", "nhận biết nốt nhạc trên khuông nhạc"], "Cuối học kì I": ["thực hành nhạc cụ gõ cơ bản", "đọc nhạc theo ký hiệu bàn tay"], "Giữa học kì II": ["hát bè đơn giản", "phân biệt các loại nhịp"], "Cuối học kì II": ["toàn bộ chương trình Âm nhạc", "kỹ năng biểu diễn nhạc cụ theo nhóm", "năng lực phân tích tác phẩm ngắn"]},
        "Khối 4": {"Giữa học kì I": ["đọc nhạc đúng cao độ, trường độ", "hát kết hợp vận động tinh tế"], "Cuối học kì I": ["nhận biết các nhạc cụ dân tộc", "thực hành gõ đệm phức tạp"], "Giữa học kì II": ["hát theo hình thức lĩnh xướng, hòa giọng", "viết nốt nhạc cơ bản"], "Cuối học kì II": ["toàn bộ chương trình Âm nhạc", "kỹ năng biểu diễn tự tin", "năng lực cảm thụ âm nhạc có chiều sâu"]},
        "Khối 5": {"Giữa học kì I": ["hát chuẩn xác các kỹ thuật luyến láy", "đọc nhạc kết hợp gõ phách"], "Cuối học kì I": ["nhận biết các thể loại âm nhạc", "thực hành hòa tấu nhạc cụ gõ"], "Giữa học kì II": ["hát bè phức tạp hơn", "sáng tạo động tác phụ họa"], "Cuối học kì II": ["toàn bộ chương trình Âm nhạc", "năng lực tổ chức biểu diễn", "kỹ năng phân tích thông điệp tác phẩm"]}
    },
    "Mĩ thuật": {
        "Khối 1": {"Giữa học kì I": ["nhận biết màu sắc cơ bản", "vẽ nét thẳng, nét cong"], "Cuối học kì I": ["vẽ hình đơn giản (tròn, vuông)", "tô màu theo ý thích"], "Giữa học kì II": ["vẽ tranh theo chủ đề tự do", "nặn đất sét cơ bản"], "Cuối học kì II": ["toàn bộ chương trình Mĩ thuật cơ bản", "kỹ năng sắp xếp bố cục tranh", "năng lực nhận xét sản phẩm mỹ thuật"]},
        "Khối 2": {"Giữa học kì I": ["pha màu cơ bản", "vẽ hình khối quen thuộc"], "Cuối học kì I": ["vẽ tranh phong cảnh đơn giản", "tạo hình từ lá cây"], "Giữa học kì II": ["nặn, xé dán tranh", "trang trí hình cơ bản"], "Cuối học kì II": ["toàn bộ chương trình Mĩ thuật", "kỹ năng thể hiện cảm xúc qua tranh", "tinh thần hợp tác làm việc nhóm"]},
        "Khối 3": {"Giữa học kì I": ["vẽ theo mẫu đơn giản", "kết hợp màu sắc hài hòa"], "Cuối học kì I": ["vẽ tranh đề tài gia đình, trường học", "tạo hình 3D từ giấy"], "Giữa học kì II": ["trang trí hình tròn, hình vuông", "vẽ họa tiết dân tộc"], "Cuối học kì II": ["toàn bộ chương trình Mĩ thuật", "kỹ năng vẽ tranh có chiều sâu", "năng lực phân tích sản phẩm mỹ thuật"]},
        "Khối 4": {"Giữa học kì I": ["vẽ theo mẫu đồ vật phức tạp", "hiểu về đậm nhạt, sáng tối"], "Cuối học kì I": ["vẽ tranh đề tài sinh hoạt", "tạo hình từ vật liệu tái chế"], "Giữa học kì II": ["trang trí ứng dụng thực tế", "vẽ tranh tĩnh vật"], "Cuối học kì II": ["toàn bộ chương trình Mĩ thuật", "kỹ năng thiết kế sản phẩm", "năng lực trình bày ý tưởng sáng tạo"]},
        "Khối 5": {"Giữa học kì I": ["vẽ theo mẫu cấu trúc phức tạp", "vẽ tranh phong cảnh có luật xa gần"], "Cuối học kì I": ["thiết kế poster, áp phích", "tạo hình khối 3D nâng cao"], "Giữa học kì II": ["vẽ tranh đề tài ước mơ, bảo vệ môi trường", "vẽ trang trí phông nền"], "Cuối học kì II": ["toàn bộ chương trình Mĩ thuật", "năng lực tổ chức triển lãm mỹ thuật", "kỹ năng phân tích và đánh giá tác phẩm"]}
    },
    "Công nghệ": {
        "Khối 3": {"Giữa học kì I": ["nhận biết các dụng cụ học tập", "quy tắc an toàn khi sử dụng kéo, hồ dán"], "Cuối học kì I": ["cắt, gấp, dán hình đơn giản", "làm mô hình bằng giấy"], "Giữa học kì II": ["nhận biết các vật liệu thủ công", "sáng tạo đồ chơi từ giấy"], "Cuối học kì II": ["toàn bộ chương trình Công nghệ", "kỹ năng hoàn thiện sản phẩm thủ công", "năng lực trình bày ý tưởng sản phẩm"]},
        "Khối 4": {"Giữa học kì I": ["nhận biết các chi tiết lắp ghép", "sử dụng dụng cụ lắp ráp"], "Cuối học kì I": ["lắp ráp mô hình đơn giản (xe, nhà)", "sáng tạo mẫu lắp ghép"], "Giữa học kì II": ["chăm sóc chậu hoa, cây cảnh", "trồng cây trong chậu"], "Cuối học kì II": ["toàn bộ chương trình Công nghệ", "kỹ năng thiết kế mô hình kỹ thuật", "năng lực lắp ráp ứng dụng linh hoạt"]},
        "Khối 5": {"Giữa học kì I": ["đính khuy, thêu mũi cơ bản", "chăm sóc vật nuôi nhỏ (gia cầm)"], "Cuối học kì I": ["lắp ráp mô hình cần cẩu, ròng rọc", "sử dụng dụng cụ gia đình"], "Giữa học kì II": ["lắp ráp mạch điện đơn giản", "sử dụng mô tơ điện"], "Cuối học kì II": ["toàn bộ chương trình Công nghệ", "kỹ năng thiết kế mô hình tự do", "năng lực thuyết trình về sản phẩm công nghệ"]}
    },
    "Đạo đức": {
        "Khối 1": {"Giữa học kì I": ["hành vi yêu thương gia đình", "chào hỏi lễ phép"], "Cuối học kì I": ["giữ gìn vệ sinh cá nhân, trường lớp", "thực hiện nội quy lớp học"], "Giữa học kì II": ["chia sẻ, giúp đỡ bạn bè", "nhận biết lỗi và xin lỗi"], "Cuối học kì II": ["toàn bộ chuẩn mực đạo đức", "ý thức bảo vệ của công", "thái độ nghiêm túc trong học tập"]},
        "Khối 2": {"Giữa học kì I": ["kính trọng thầy cô giáo", "nhận biết đúng sai trong giao tiếp"], "Cuối học kì I": ["giúp đỡ người khuyết tật, người già", "trách nhiệm với công việc được giao"], "Giữa học kì II": ["thật thà trong học tập và sinh hoạt", "giữ gìn đồ dùng học tập"], "Cuối học kì II": ["toàn bộ chuẩn mực hành vi", "ý thức tôn trọng sự khác biệt của bạn bè", "kỹ năng thực hiện quy tắc an toàn giao thông"]},
        "Khối 3": {"Giữa học kì I": ["ý thức tự giác học tập", "tôn trọng thư từ, tài sản người khác"], "Cuối học kì I": ["biết ơn thương binh liệt sĩ", "bảo vệ nguồn nước, môi trường"], "Giữa học kì II": ["tôn trọng phụ nữ", "chăm sóc cây xanh, vật nuôi"], "Cuối học kì II": ["toàn bộ chuẩn mực hành vi đạo đức", "kỹ năng giải quyết xung đột", "trách nhiệm với cộng đồng xung quanh"]},
        "Khối 4": {"Giữa học kì I": ["trung thực trong học tập, thi cử", "thương người như thể thương thân"], "Cuối học kì I": ["tôn trọng, bảo vệ di tích lịch sử", "vượt khó trong học tập"], "Giữa học kì II": ["tôn trọng luật giao thông", "hiếu thảo với ông bà cha mẹ"], "Cuối học kì II": ["toàn bộ nội dung rèn luyện đạo đức", "ý thức bảo vệ quyền trẻ em", "trách nhiệm với lời nói và việc làm"]},
        "Khối 5": {"Giữa học kì I": ["tôn trọng sự khác biệt về văn hóa, dân tộc", "ý chí vươn lên trong cuộc sống"], "Cuối học kì I": ["biết ơn người lao động", "bảo vệ môi trường sống xung quanh"], "Giữa học kì II": ["ý thức công dân, tuân thủ pháp luật", "hợp tác và làm việc nhóm"], "Cuối học kì II": ["toàn bộ chương trình rèn luyện đạo đức", "thái độ tôn trọng bình đẳng giới", "lòng tự hào về truyền thống dân tộc"]}
    },
    "Hoạt động trải nghiệm": {
        "Khối 1": {"Giữa học kì I": ["khám phá bản thân", "nội quy trường lớp"], "Cuối học kì I": ["sinh hoạt gia đình", "an toàn cho bản thân"], "Giữa học kì II": ["bảo vệ môi trường", "giúp đỡ bạn bè"], "Cuối học kì II": ["toàn bộ chương trình trải nghiệm", "ý thức tự phục vụ", "tình yêu quê hương"]},
        "Khối 2": {"Giữa học kì I": ["tự chăm sóc bản thân", "sinh hoạt sao nhi đồng"], "Cuối học kì I": ["tìm hiểu nghề nghiệp bố mẹ", "giữ gìn vệ sinh chung"], "Giữa học kì II": ["phòng tránh rủi ro", "bảo vệ cảnh quan"], "Cuối học kì II": ["toàn bộ chương trình trải nghiệm", "kỹ năng chia sẻ yêu thương", "năng lực giao tiếp"]},
        "Khối 3": {"Giữa học kì I": ["phát huy điểm mạnh bản thân", "truyền thống nhà trường"], "Cuối học kì I": ["lập kế hoạch cá nhân", "an toàn giao thông"], "Giữa học kì II": ["tham gia hoạt động thiện nguyện", "bảo vệ môi trường sống"], "Cuối học kì II": ["toàn bộ chương trình trải nghiệm", "kỹ năng làm việc nhóm", "tinh thần tự hào quê hương"]},
        "Khối 4": {"Giữa học kì I": ["hoạt động cộng đồng", "tự hào về trường em"], "Cuối học kì I": ["quản lý chi tiêu", "lập thời gian biểu"], "Giữa học kì II": ["phòng tránh xâm hại", "chăm sóc cảnh quan"], "Cuối học kì II": ["toàn bộ chương trình trải nghiệm", "kỹ năng sinh tồn cơ bản", "phát huy truyền thống quê hương"]},
        "Khối 5": {"Giữa học kì I": ["tự hoàn thiện bản thân", "xây dựng tình bạn đẹp"], "Cuối học kì I": ["tìm hiểu nghề nghiệp tương lai", "ý thức công dân"], "Giữa học kì II": ["ứng phó với thiên tai", "kỹ năng tổ chức sự kiện"], "Cuối học kì II": ["toàn bộ chương trình trải nghiệm", "năng lực tự chủ", "chuẩn bị sẵn sàng chuyển cấp"]}
    }
}

def lay_mach_kien_thuc(mon, khoi, thoi_diem):
    kho_mon = PHAN_PHOI_CHUONG_TRINH.get(mon, {})
    if khoi in kho_mon: 
        if isinstance(kho_mon[khoi], dict):
            return kho_mon[khoi].get(thoi_diem, ["kiến thức trọng tâm", "kỹ năng thực hành"])
        return kho_mon[khoi]
    if "Chung" in kho_mon: 
        if isinstance(kho_mon["Chung"], dict):
            return kho_mon["Chung"].get(thoi_diem, ["kiến thức trọng tâm", "kỹ năng thực hành"])
        return kho_mon["Chung"]
    return ["kiến thức cơ bản", "kỹ năng thực hành"]

# --- HỆ THỐNG GHÉP CÂU TỔ HỢP OFFLINE (TẠO HÀNG TRĂM BIẾN THỂ VÔ HẠN) ---
def sinh_nhan_xet_pcnl_offline(mdd_nlc, mdd_nldt, mdd_pc, phong_cach, xung_ho, bat_xung_ho):
    xh = f"{xung_ho} " if bat_xung_ho else ""
    def cap_first(s):
        if not s: return ""
        s = s.strip()
        return s[0].upper() + s[1:]
        
    nlc_kho = {
        "T": ["tự học và giao tiếp cực kỳ xuất sắc", "tiếp thu nhạy bén các kỹ năng chung", "có kỹ năng giải quyết vấn đề linh hoạt", "năng lực tự chủ và giao tiếp rất tốt"],
        "H_Kha": ["có ý thức tự học và giao tiếp khá", "có kỹ năng hợp tác nhóm linh hoạt", "tự chủ trong giải quyết vấn đề khá tốt", "năng lực chung đạt mức khá"],
        "H_TrungBinh": ["kỹ năng giao tiếp và tự học chưa thực sự nổi bật", "đạt mức cơ bản về các năng lực chung", "cần chủ động hơn khi làm việc nhóm", "năng lực tự học đạt mức cơ bản"],
        "C": ["còn hạn chế trong kỹ năng tự học và giao tiếp", "chưa chủ động trong hợp tác và giải quyết vấn đề", "kỹ năng làm việc nhóm còn yếu", "còn rụt rè, chưa mạnh dạn giao tiếp"]
    }
    nldt_kho = {
        "T": ["có năng lực đặc thù vô cùng nổi trội", "tiếp thu rất tốt kiến thức các môn học", "phát huy xuất sắc năng lực chuyên biệt", "thể hiện tính sáng tạo rất cao trong học tập"],
        "H_Kha": ["nắm vững kiến thức đặc thù các môn", "phát huy khá tốt các năng lực bộ môn", "đạt kết quả khá ở các môn học", "kỹ năng thực hành bộ môn khá vững"],
        "H_TrungBinh": ["đạt yêu cầu cơ bản về năng lực các môn", "mức độ hoàn thành các môn học ở mức cơ bản", "tiếp thu kiến thức ở mức đạt", "cần tập trung hơn trong các giờ học"],
        "C": ["chưa hoàn thành tốt các năng lực đặc thù", "tiếp thu kiến thức bộ môn còn chậm", "còn rất yếu trong việc rèn luyện năng lực môn học", "chưa nắm vững kiến thức trọng tâm"]
    }
    pc_kho = {
        "T": ["luôn nỗ lực, trách nhiệm và hòa đồng", "biết quan tâm, chia sẻ và trung thực", "thể hiện rõ sự chăm chỉ, kỷ luật và ngoan ngoãn", "có tinh thần yêu nước, nhân ái tuyệt vời"],
        "H_Kha": ["chăm chỉ và trung thực trong học tập", "có trách nhiệm với nhiệm vụ tập thể", "luôn tuân thủ nội quy lớp học", "có ý thức rèn luyện khá tốt các phẩm chất"],
        "H_TrungBinh": ["biết yêu thương và tuân thủ nội quy", "chăm chỉ nhưng đôi khi thiếu tính tự giác", "biết vâng lời nhưng cần nâng cao kỷ luật cá nhân", "có ý thức đạo đức tốt nhưng cần mạnh dạn hơn"],
        "C": ["cần cố gắng khắc phục tính trách nhiệm", "cần nghiêm túc rèn luyện kỷ luật hơn nữa", "còn hạn chế nhiều về mặt phẩm chất", "thiếu sự chăm chỉ, chưa trung thực"]
    }
    
    khuyen_nlc = {"T": "Hãy tiếp tục phát huy.", "H_Kha": "Cần tự tin hơn nữa để bứt phá.", "H_TrungBinh": "Cần năng nổ hơn trong các hoạt động.", "C": "Cần mạnh dạn và cởi mở hơn."}
    khuyen_nldt = {"T": "Kết quả rèn luyện rất xứng đáng.", "H_Kha": "Chỉ cần cố gắng thêm chút nữa em sẽ rất xuất sắc.", "H_TrungBinh": "Hãy tập trung tối đa cho việc học.", "C": "Cần nỗ lực gấp đôi để khắc phục."}
    khuyen_pc = {"T": "Là tấm gương sáng cho cả lớp.", "H_Kha": "Sự rèn luyện của em rất đáng khen.", "H_TrungBinh": "Cần chấn chỉnh lại ý thức kỷ luật.", "C": "Yêu cầu nghiêm túc tuân thủ nội quy."}
    
    nx_nlc, nx_nldt, nx_pc = "", "", ""
    if mdd_nlc:
        if phong_cach == "Ngắn gọn": nx_nlc = cap_first(random.choice(nlc_kho[mdd_nlc])) + "."
        else: nx_nlc = cap_first(f"{xh}nhận thấy em {random.choice(nlc_kho[mdd_nlc])}. {khuyen_nlc[mdd_nlc]}")
    if mdd_nldt:
        if phong_cach == "Ngắn gọn": nx_nldt = cap_first(random.choice(nldt_kho[mdd_nldt])) + "."
        else: nx_nldt = cap_first(f"Em {random.choice(nldt_kho[mdd_nldt])}. {khuyen_nldt[mdd_nldt]}")
    if mdd_pc:
        if phong_cach == "Ngắn gọn": nx_pc = cap_first(random.choice(pc_kho[mdd_pc])) + "."
        else: nx_pc = cap_first(f"Về phẩm chất, em {random.choice(pc_kho[mdd_pc])}. {khuyen_pc[mdd_pc]}")
        
    return nx_nlc.replace("Thầy/Cô", xh.strip() if xh else "Giáo viên"), nx_nldt.replace("Thầy/Cô", xh.strip() if xh else "Giáo viên"), nx_pc.replace("Thầy/Cô", xh.strip() if xh else "Giáo viên")


def sinh_nhan_xet_offline(loai_nx, mdd, focus_kt, phong_cach="Ngắn gọn", xung_ho="Thầy", bat_xung_ho=True, mon="", thoi_diem=""):
    xh = f"{xung_ho} " if bat_xung_ho else ""
    is_cuoi_nam = thoi_diem == "Cuối học kì II"
    
    def cap_first(s):
        if not s: return s
        s = s.strip()
        return s[0].upper() + s[1:] if s else ""

    if loai_nx == "HĐGD":
        hdgd_thamgia = {
            "T": ["Tích cực tham gia các phong trào", "Nhiệt tình và năng nổ trong trải nghiệm", "Luôn đi đầu trong các hoạt động chung", "Có ý thức tổ chức kỷ luật rất cao", "Hăng hái tham gia mọi hoạt động giáo dục"],
            "H_Kha": ["Tham gia khá tốt các hoạt động giáo dục", "Nhiệt tình với các phong trào của lớp", "Có nề nếp tốt trong giờ trải nghiệm", "Hòa đồng và tham gia đầy đủ các hoạt động", "Ý thức tham gia sinh hoạt tập thể khá nghiêm túc"],
            "H_TrungBinh": ["Có tham gia các hoạt động giáo dục", "Mức độ hoàn thành nội dung trải nghiệm cơ bản", "Đã tham gia cùng tập thể nhưng còn rụt rè", "Hoàn thành các nhiệm vụ được giao ở mức cơ bản", "Có ý thức tham gia nhưng chưa thực sự năng nổ"],
            "C": ["Chưa hoàn thành nội dung trải nghiệm", "Thái độ tham gia chưa thực sự nghiêm túc", "Ít tham gia các phong trào của trường lớp", "Hay mất tập trung trong giờ sinh hoạt chung", "Chưa chủ động tham gia hoạt động giáo dục"]
        }
        hdgd_kynang = {
            "T": ["thể hiện kỹ năng sống tuyệt vời", "năng lực tổ chức và làm việc nhóm xuất sắc", "tính sáng tạo và linh hoạt rất cao", "khả năng lãnh đạo và kết nối bạn bè tốt", "xử lý tình huống trải nghiệm rất thông minh"],
            "H_Kha": ["kỹ năng hợp tác nhóm khá tốt", "biết cách hòa nhập và chia sẻ với bạn bè", "thực hiện khá tốt các kỹ năng thực tế", "có sự cố gắng trong giao tiếp", "hoàn thành các kỹ năng sống cơ bản"],
            "H_TrungBinh": ["kỹ năng giao tiếp và làm việc nhóm còn hạn chế", "chưa mạnh dạn phát biểu ý kiến cá nhân", "cần mạnh dạn và tự tin hơn nữa", "còn rụt rè khi xử lý các tình huống", "tính sáng tạo trong hoạt động chưa cao"],
            "C": ["kỹ năng sống còn rất nhiều hạn chế", "không thể tự xử lý tình huống cơ bản", "chưa biết cách làm việc cùng tập thể", "thiếu kỹ năng giao tiếp và hay rụt rè", "chưa nắm được các kỹ năng trải nghiệm cốt lõi"]
        }
        hdgd_khuyen = {
            "T": ["Là nhân tố tích cực của lớp.", "Cần tiếp tục giữ vững tinh thần này!", "Thầy/Cô rất tự hào về sự năng nổ của em.", "Hãy lan tỏa năng lượng này cho các bạn.", "Kỹ năng hoạt động cực kỳ xuất sắc."],
            "H_Kha": ["Cần chủ động và tự tin phát biểu hơn.", "Tiếp tục phát huy sự nhiệt tình này nhé.", "Hãy mạnh dạn dẫn dắt nhóm trong tương lai.", "Chỉ cần tự tin hơn chút là rất tuyệt vời.", "Sự cố gắng của em rất đáng khen."],
            "H_TrungBinh": ["Cần tự tin thể hiện bản thân nhiều hơn nữa.", "Hãy tích cực giao tiếp với bạn bè xung quanh.", "Cần năng nổ hơn trong phong trào chung.", "Đừng ngại ngùng, hãy chủ động tham gia nhé.", "Thầy/Cô mong em sẽ mạnh dạn hơn ở kì sau."],
            "C": ["Cần tham gia phong trào tích cực hơn để rèn kỹ năng.", "Yêu cầu em nghiêm túc và chủ động hơn.", "Cần thay đổi thái độ khi sinh hoạt tập thể.", "Hãy mở lòng và hòa đồng cùng các bạn.", "Cần rèn luyện tính kỷ luật và sự tự giác."]
        }
        tg = random.choice(hdgd_thamgia[mdd])
        kn = random.choice(hdgd_kynang[mdd])
        kh = random.choice(hdgd_khuyen[mdd]).replace("Thầy/Cô", xh.strip() if xh else "Giáo viên")

        if phong_cach == "Ngắn gọn":
            return f"{cap_first(tg)}. Về thực tiễn, em {kn}."
        elif phong_cach == "Gần gũi":
            return cap_first(f"{xh}khen ngợi em {tg.lower()}. Trong hoạt động, em {kn}. {kh}")
        elif phong_cach == "Khích lệ":
            return f"{cap_first(tg)}. Tuy nhiên, em {kn}. {kh}"
        else:
            return cap_first(f"{tg}. Em {kn}. {kh}")
            
    else: # Môn học
        if is_cuoi_nam:
            mo_T = ["Tổng kết năm học, em nắm rất vững", "Thực hiện xuất sắc cả năm", "Hoàn thành xuất sắc chương trình, đặc biệt ở", "Xuyên suốt năm học, em tiếp thu cực kỳ nhạy bén", "Đạt kết quả cuối năm nổi trội ở"]
            mo_Kha = ["Tổng kết năm học, em nắm vững", "Thực hiện tốt chương trình", "Hoàn thành tốt năm học, hiểu rõ", "Xuyên suốt năm học, em tiếp thu khá tốt", "Đạt kết quả khá khả quan ở"]
            mo_TB = ["Tổng kết năm học, em nắm được cơ bản", "Thực hiện được nội dung", "Đạt mức cơ bản chương trình năm học ở", "Hiểu được mức độ cơ bản của", "Hoàn thành các yêu cầu cơ bản ở"]
            mo_C = ["Tổng kết năm học, em chưa nắm vững", "Thực hiện chưa tốt chương trình", "Còn nhiều lỗ hổng kiến thức ở", "Mức độ tiếp thu còn rất chậm ở", "Chưa hoàn thành mục tiêu năm học ở"]
        else:
            mo_T = ["Nắm rất vững", "Thực hiện xuất sắc", "Hoàn thành xuất sắc", "Tiếp thu cực kỳ nhạy bén", "Thể hiện năng lực nổi bật ở"]
            mo_Kha = ["Nắm vững", "Thực hiện tốt", "Hoàn thành tốt", "Tiếp thu khá tốt", "Thể hiện sự cố gắng rõ rệt ở"]
            mo_TB = ["Nắm được cơ bản", "Thực hiện được nội dung", "Đạt mức cơ bản", "Mức độ tiếp thu vừa đủ ở", "Hoàn thành các yêu cầu của"]
            mo_C = ["Chưa nắm vững", "Thực hiện chưa tốt", "Còn nhiều hạn chế ở", "Mức độ tiếp thu còn chậm ở", "Chưa hoàn thành tốt"]

        kynang_mon = {
            "Tiếng Việt": {
                "T": ["đọc diễn cảm và lưu loát, chữ viết nắn nót", "viết câu đúng ngữ pháp, giàu hình ảnh", "cảm thụ văn bản rất sâu sắc, sáng tạo", "kỹ năng đọc hiểu xuất sắc, tư duy ngôn ngữ tốt", "diễn đạt trôi chảy, cách dùng từ phong phú"],
                "H_Kha": ["đọc to, rõ ràng, chữ viết tương đối cẩn thận", "biết cách đặt câu đúng chủ - vị", "hiểu nội dung bài đọc khá tốt", "trình bày bài sạch sẽ, diễn đạt khá trôi chảy", "kỹ năng nghe viết chính tả khá vững vàng"],
                "H_TrungBinh": ["đọc còn vấp vài chỗ, chữ viết cần nắn nót hơn", "diễn đạt câu đôi khi còn lúng túng", "trả lời câu hỏi đọc hiểu chưa trọn vẹn", "còn mắc một số lỗi chính tả cơ bản", "cần trau chuốt hơn khi viết đoạn văn"],
                "C": ["đọc còn rất chậm, đánh vần nhiều", "chữ viết cẩu thả, sai quá nhiều lỗi chính tả", "chưa biết cách đặt câu hoàn chỉnh", "kỹ năng đọc hiểu rất yếu, thiếu vốn từ", "viết văn lủng củng, sai cấu trúc ngữ pháp"]
            },
            "Toán": {
                "T": ["tính toán nhanh nhẹn, độ chính xác tuyệt đối", "tư duy logic cực kỳ nhạy bén", "giải bài toán có lời văn rất xuất sắc", "trình bày bài giải rõ ràng, khoa học", "nắm cực kì chắc các công thức toán học"],
                "H_Kha": ["thực hiện phép tính khá cẩn thận", "giải toán lời văn khá tốt", "nắm vững các quy tắc tính toán", "tư duy toán học ổn định, trình bày sạch", "áp dụng tốt công thức vào bài tập"],
                "H_TrungBinh": ["tính toán đôi khi còn nhầm lẫn do ẩu", "giải toán có lời văn còn lúng túng các bước", "chưa nhớ thật kĩ các công thức phức tạp", "trình bày bài đôi lúc chưa khoa học", "thao tác giải bài còn chậm"],
                "C": ["kỹ năng tính toán rất yếu, thường xuyên sai sót", "chưa biết cách thiết lập phép tính giải toán lời văn", "mất căn bản các công thức trọng tâm", "không tập trung khi làm bài tập tính toán", "hổng kiến thức toán học rất nhiều"]
            },
            "Tiếng Anh": {
                "T": ["phát âm chuẩn xác, phản xạ giao tiếp trôi chảy", "nắm vô cùng chắc từ vựng và ngữ pháp", "nghe hiểu và đọc hiểu tiếng Anh xuất sắc", "tự tự tin thuyết trình bằng ngoại ngữ"],
                "H_Kha": ["ghi nhớ tốt từ vựng cơ bản", "vận dụng được mẫu câu vào giao tiếp khá tốt", "kỹ năng nghe và đọc ở mức khá", "phát âm tương đối rõ ràng"],
                "H_TrungBinh": ["vốn từ vựng còn hạn chế", "kỹ năng giao tiếp và phát âm chưa tự nhiên", "cần trau dồi thêm ngữ pháp cơ bản", "khả năng nghe hiểu chưa cao"],
                "C": ["phát âm yếu, chưa phản xạ được khi giao tiếp", "lỗ hổng từ vựng lớn, chưa nắm được cấu trúc câu", "rất chậm trong việc tiếp thu ngoại ngữ", "ngại giao tiếp và không nhớ từ mới"]
            },
            "Chung": {
                "T": ["kĩ năng thực hành vô cùng thành thạo", "vận dụng cực kỳ linh hoạt kiến thức vào thực tiễn", "tư duy phân tích và giải quyết vấn đề nhạy bén", "trình bày sản phẩm/bài học xuất sắc, sáng tạo", "nắm bắt bài học vô cùng thông minh"],
                "H_Kha": ["kĩ năng thực hành đạt mức khá tốt", "vận dụng được kiến thức vào bài tập", "ghi nhớ tốt các sự kiện/nội dung trọng tâm", "biết cách giải quyết yêu cầu của bài học", "hoàn thành chỉn chu các sản phẩm thực hành"],
                "H_TrungBinh": ["kĩ năng khai thác thông tin/thực hành còn lúng túng", "vận dụng kiến thức chưa thực sự linh hoạt", "thao tác đôi khi còn chậm, cần cẩn thận hơn", "mức độ hiểu bài chỉ dừng ở mức cơ bản", "cần trau chuốt hơn khi thực hành"],
                "C": ["kỹ năng thực hành rất yếu, thiếu độ chính xác", "khả năng ghi nhớ và vận dụng kiến thức kém", "thiếu tập trung quan sát, thái độ học chưa tốt", "không tự giải quyết được các yêu cầu bài học", "hoàn toàn lúng túng khi thao tác"]
            }
        }
        
        loi_khuyen = {
            "T": ["Hãy tiếp tục duy trì phong độ xuất sắc này.", "Thái độ học tập luôn chủ động, rất đáng khen.", "Luôn hăng hái phát biểu xây dựng bài.", "Cách trình bày rất chỉn chu, khoa học.", "Cần tiếp tục phát huy năng lực nổi trội này nhé."],
            "H_Kha": ["Cần tự tin hơn nữa để đạt mức xuất sắc.", "Đã có nhiều tiến bộ, hãy tiếp tục cố gắng.", "Thái độ học tập ngoan ngoãn, chăm chỉ.", "Cần mạnh dạn phát biểu ý kiến hơn trong giờ.", "Chỉ cần cẩn thận hơn chút nữa là hoàn hảo."],
            "H_TrungBinh": ["Cần chú ý ôn tập nhiều hơn tại nhà.", "Cần tập trung nghe giảng hơn trong lớp.", "Khuyến khích rèn luyện thêm để nâng cao kỹ năng.", "Cần mạnh dạn hỏi bài khi chưa hiểu rõ.", "Nên dành nhiều thời gian hơn để làm bài tập củng cố."],
            "C": ["Cần nỗ lực ôn tập lại các kiến thức bị hổng.", "Yêu cầu nghiêm túc chấn chỉnh thái độ học tập.", "Cần chăm chỉ làm bài và chú ý nghe giảng hơn.", "Nên chủ động nhờ sự hỗ trợ từ bạn bè và thầy cô.", "Cần dành tối đa thời gian để rèn luyện lại từ căn bản."]
        }

        dict_mo = {"T": mo_T, "H_Kha": mo_Kha, "H_TrungBinh": mo_TB, "C": mo_C}
        mo_chon = random.choice(dict_mo[mdd])
        
        nguon_kynang = kynang_mon.get(mon, kynang_mon["Chung"])
        kn_chon = random.choice(nguon_kynang[mdd])
        
        lk_chon = random.choice(loi_khuyen[mdd])
        
        if phong_cach == "Ngắn gọn":
            return cap_first(f"{mo_chon} nội dung {focus_kt}. Kỹ năng {kn_chon}.")
        elif phong_cach == "Gần gũi":
            return cap_first(f"{xh}nhận thấy em {mo_chon.lower()} nội dung {focus_kt}. Biểu hiện là {kn_chon}. {lk_chon}")
        elif phong_cach == "Khích lệ":
            return cap_first(f"Qua nội dung {focus_kt}, em {mo_chon.lower()} kiến thức. Khả năng {kn_chon}. {xh}khuyên em {lk_chon.lower()}")
        else: # Đầy đủ / Ngẫu nhiên
            return cap_first(f"{mo_chon} nội dung {focus_kt}. Khả năng {kn_chon}. {lk_chon}")

def check_col_has_data(df, col_idx, start_row, check_type="level"):
    for r in range(start_row, min(start_row + 3, len(df))):
        val = str(df.iloc[r, col_idx]).strip().upper()
        if val in ['NAN', 'NONE', '']: continue
        if check_type == "score" and val.replace('.','',1).isdigit(): return True
        if check_type == "level" and val in ['T', 'Đ', 'C', 'HTT', 'HT', 'CHT', 'H', 'K']: return True
    return False

def get_best_col_strict(df, cands, s_row, check_type):
    for j in reversed(cands):
        if check_col_has_data(df, j, s_row, check_type): 
            return j
    return -1

# --- 3. HÀM PHÂN TÍCH FILE THÔNG MINH (TRÍ NHỚ NGỮ CẢNH HỌC KÌ) ---
def phan_tich_file(file, thoi_diem):
    try:
        file_bytes = io.BytesIO(file.getvalue())
        df = pd.read_excel(file_bytes, header=None) if not file.name.endswith('.csv') else pd.read_csv(file_bytes, header=None)
        n_col, h_row = -1, -1
        for i in range(min(25, len(df))):
            for j in range(min(15, len(df.columns))):
                if "họ" in str(df.iloc[i, j]).lower() and "tên" in str(df.iloc[i, j]).lower():
                    n_col, h_row = j, i; break
            if n_col != -1: break
            
        if n_col == -1: return None, None, None, None, None, None, None, None, None
        
        s_row = h_row + 1
        found_student = False
        for r in range(h_row + 1, min(h_row + 20, len(df))):
            val = str(df.iloc[r, n_col]).strip()
            if val.lower() not in ['nan', 'none', ''] and len(val) > 2 and "năng lực" not in val.lower() and "phẩm chất" not in val.lower():
                s_row = r
                found_student = True
                break
                
        if not found_student:
            s_row = min(h_row + 4, len(df))
                
        diem_cands, muc_cands, c_cands = [], [], []
        explicit_diem_cands, explicit_muc_cands = [], []
        
        pcnl_cols = {
            'muc_nlc': -1, 'nx_nlc': -1,
            'muc_nldt': -1, 'nx_nldt': -1,
            'muc_pc': -1, 'nx_pc': -1
        }
        cands_pcnl = {
            'muc_nlc': [], 'nx_nlc': [],
            'muc_nldt': [], 'nx_nldt': [],
            'muc_pc': [], 'nx_pc': []
        }
        
        current_term_context = None 
        
        # TỪ KHÓA CHUẨN XÁC, QUÉT KÌ 2 TRƯỚC, KÌ 1 SAU
        term_2_mid_kws = ['ghkii', 'ghk2', 'gk2', 'giữahk2', 'giữahkii', 'giữahọckì2', 'giữahọckỳ2', 'giữakì2', 'giữakỳ2', 'gkii', 'giữakỳii', 'giữakìii', 'giữahọckỳii', 'giữahọckìii']
        term_2_end_kws = ['chkii', 'chk2', 'ck2', 'cuốihk2', 'cuốihkii', 'cuốihọckì2', 'cuốihọckỳ2', 'cuốikì2', 'cuốikỳ2', 'hkii', 'hk2', 'họckì2', 'họckỳ2', 'họckìii', 'họckỳii', 'cuốinăm', 'cn', 'ckii', 'cuốikỳii', 'cuốikìii', 'cuốihọckỳii', 'cuốihọckìii']
        term_1_mid_kws = ['ghk1', 'gk1', 'giữahk1', 'giữahki', 'giữahọckì1', 'giữahọckỳ1', 'giữakì1', 'giữakỳ1', 'gki', 'giữakỳi', 'giữakìi', 'giữahọckỳi', 'giữahọckìi']
        term_1_end_kws = ['chk1', 'ck1', 'cuốihk1', 'cuốihki', 'cuốihọckì1', 'cuốihọckỳ1', 'cuốikì1', 'cuốikỳ1', 'hk1', 'cki', 'họckì1', 'họckỳ1', 'họckìi', 'họckỳi', 'cuốikỳi', 'cuốikìi', 'cuốihọckỳi', 'cuốihọckìi']
        
        for j in range(n_col + 1, len(df.columns)):
            header_area = " ".join([str(df.iloc[r, j]).lower() for r in range(max(0, h_row - 4), s_row)])
            header_clean = header_area.replace(" ", "").replace("_", "").replace("-", "").replace("\n", "").replace("\r", "")
            
            if any(kw in header_clean for kw in term_2_mid_kws):
                current_term_context = "Giữa học kì II"
            elif any(kw in header_clean for kw in term_2_end_kws):
                current_term_context = "Cuối học kì II"
            elif any(kw in header_clean for kw in term_1_mid_kws) or ('ghki' in header_clean and 'ghkii' not in header_clean):
                current_term_context = "Giữa học kì I"
            elif any(kw in header_clean for kw in term_1_end_kws) or ('chki' in header_clean and 'chkii' not in header_clean) or ('hki' in header_clean and 'hkii' not in header_clean):
                current_term_context = "Cuối học kì I"

            is_my_term = (current_term_context == thoi_diem)
            is_other_term = (current_term_context is not None and current_term_context != thoi_diem)

            if is_other_term:
                continue
            
            is_diem = "điểm" in header_area or "đg" in header_area
            is_muc = any(w in header_area for w in ["mức", "đạt được", "đánh giá", "kết quả", "xếp loại", "xl", "mdd"])
            is_nx = any(w in header_area for w in ["nhận xét", "lời phê", "nx"])
            
            if is_nx and not is_muc and not is_diem:
                c_cands.append(j)
            else:
                if is_nx: c_cands.append(j)
                if is_diem: 
                    diem_cands.append(j)
                    if is_my_term: explicit_diem_cands.append(j)
                if is_muc: 
                    muc_cands.append(j)
                    if is_my_term: explicit_muc_cands.append(j)
                    
                # HỖ TRỢ ĐẶC BIỆT CHO MÔN ĐẠO ĐỨC/HĐTN (Cột chỉ ghi Học kì mà không ghi Điểm/Mức)
                if is_my_term and not is_diem and not is_muc and not is_nx:
                    diem_cands.append(j)
                    muc_cands.append(j)
                    explicit_diem_cands.append(j)
                    explicit_muc_cands.append(j)
            
            # --- LUỒNG QUÉT TỪ KHÓA CHO PC-NL ---
            is_nlc = "năng lực chung" in header_area or ("chung" in header_area and "năng" in header_area) or "nlc" in header_clean
            is_nldt = "đặc thù" in header_area or ("đặc" in header_area and "năng" in header_area) or "nlđt" in header_clean or "nldt" in header_clean
            is_pc = "phẩm chất" in header_area or "pc" in header_clean
            is_nl_gen = "năng lực" in header_area and not is_nlc and not is_nldt
            
            if is_my_term:
                if is_nlc or is_nl_gen:
                    if is_muc or (not is_muc and not is_nx): cands_pcnl['muc_nlc'].append(j)
                    if is_nx: cands_pcnl['nx_nlc'].append(j)
                if is_nldt or is_nl_gen:
                    if is_muc or (not is_muc and not is_nx): cands_pcnl['muc_nldt'].append(j)
                    if is_nx: cands_pcnl['nx_nldt'].append(j)
                if is_pc:
                    if is_muc or (not is_muc and not is_nx): cands_pcnl['muc_pc'].append(j)
                    if is_nx: cands_pcnl['nx_pc'].append(j)
                    
        # --- CHỐT CỘT ĐIỂM/MỨC CHÍNH XÁC ---
        diem_col = get_best_col_strict(df, explicit_diem_cands, s_row, "score")
        muc_col = get_best_col_strict(df, explicit_muc_cands, s_row, "level")
        
        if diem_col == -1 and explicit_diem_cands: diem_col = explicit_diem_cands[-1]
        if muc_col == -1 and explicit_muc_cands: muc_col = explicit_muc_cands[-1]
        
        if diem_col == -1: diem_col = get_best_col_strict(df, diem_cands, s_row, "score")
        if muc_col == -1: muc_col = get_best_col_strict(df, muc_cands, s_row, "level")
        
        if diem_col == -1 and diem_cands:
            if "I" in thoi_diem and "II" not in thoi_diem: diem_col = diem_cands[0]
            else: diem_col = diem_cands[-1]
            
        if muc_col == -1 and muc_cands:
            if "I" in thoi_diem and "II" not in thoi_diem: muc_col = muc_cands[0]
            else: muc_col = muc_cands[-1]
            
        if diem_col == muc_col and diem_col != -1:
            if check_col_has_data(df, diem_col, s_row, "score"): muc_col = -1
            elif check_col_has_data(df, diem_col, s_row, "level"): diem_col = -1
            else: diem_col = -1 
            
        # --- CHỐT CỘT PC-NL (3 PHẦN RIÊNG BIỆT) ---
        for k in pcnl_cols:
            if 'muc' in k:
                pcnl_cols[k] = get_best_col_strict(df, cands_pcnl[k], s_row, "level")
                if pcnl_cols[k] == -1 and cands_pcnl[k]: pcnl_cols[k] = cands_pcnl[k][-1]
            else:
                if cands_pcnl[k]: pcnl_cols[k] = cands_pcnl[k][-1]
                
        # --- CHỐT CỘT NHẬN XÉT MÔN HỌC ---
        ref_cols = []
        if diem_col != -1: ref_cols.append(diem_col)
        if muc_col != -1: ref_cols.append(muc_col)
        
        ref_max = max(ref_cols) if ref_cols else -1
        
        c_col = -1
        if c_cands:
            valid_c = [c for c in c_cands if c > ref_max]
            if valid_c: c_col = valid_c[0]
            else: c_col = c_cands[-1]
                
        if c_col == -1: 
            c_col = len(df.columns)
            df[c_col] = ""
            df.iloc[h_row, c_col] = "Nhận xét"
        
        return df, n_col, diem_col, muc_col, c_col, s_row, None, None, pcnl_cols
    except: return None, None, None, None, None, None, None, None, None

# --- 4. SIDEBAR CẤU HÌNH ---
with st.sidebar:
    st.markdown("### 🖥️ HỆ THỐNG ĐIỀU KHIỂN")
    api_key = st.text_input("🔑 API Key Gemini (Bỏ trống chạy Offline)", type="password")
    
    st.markdown("**⚙️ Cấu hình Nhận xét**")
    bat_xung_ho = st.toggle("Sử dụng Xưng hô (Thầy/Cô)", value=True)
    xung_ho = st.radio("👤 Chọn danh xưng:", ["Thầy", "Cô"], horizontal=True, disabled=not bat_xung_ho)
    phong_cach = st.selectbox("🌈 Phong cách lời phê:", ["Ngẫu nhiên", "Ngắn gọn", "Gần gũi", "Khích lệ", "Đầy đủ"])
    
    st.divider()
    loai_nx = st.selectbox("📝 Loại đánh giá:", ["Môn học", "PC-NL", "HĐGD"])
    thoi_diem = st.selectbox("⏳ Thời điểm đánh giá:", ["Giữa học kì I", "Cuối học kì I", "Giữa học kì II", "Cuối học kì II"])
    
    col1, col2 = st.columns(2)
    with col1: khoi = st.selectbox("📌 Khối:", ["Khối 5", "Khối 4", "Khối 3", "Khối 2", "Khối 1"])
    with col2: mon = st.selectbox("📚 Môn:", ["Tiếng Việt", "Toán", "Tiếng Anh", "Khoa học", "Lịch sử & Địa lý", "Đạo đức", "Âm nhạc", "Mĩ thuật", "GDTC", "Công nghệ", "Tin học", "Hoạt động trải nghiệm"])
    
    st.divider()
    st.markdown("**📂 Dữ liệu đầu vào**")
    f_hs = st.file_uploader("Tải lên danh sách (.xlsx, .csv)", type=["xlsx", "csv"], label_visibility="collapsed")

# --- KHỞI TẠO STATE ĐỂ LƯU KẾT QUẢ COPY ---
if "ket_qua_nhan_xet" not in st.session_state:
    st.session_state.ket_qua_nhan_xet = []

# --- 5. NỘI DUNG CHÍNH ---
def get_mdd(val):
    val = val.strip().upper()
    if val in ["T", "HTT", "TỐT", "A", "A+"]: return "T"
    elif val in ["K", "KHÁ", "B", "B+"]: return "H_Kha"
    elif val in ["Đ", "HT", "ĐẠT"]: return "H_TrungBinh"
    elif val in ["C", "CHT", "CHƯA ĐẠT", "D", "E"]: return "C"
    return ""

if f_hs:
    df_raw, n_col, d_col, m_col, c_col, s_row, _, _, pcnl_cols = phan_tich_file(f_hs, thoi_diem)
    
    if df_raw is not None:
        data_list = []
        mapping_indices = []
        
        # Đảm bảo các cột Nhận xét PC-NL tồn tại (để chuẩn bị ghi đè)
        if loai_nx == "PC-NL":
            if pcnl_cols['nx_nlc'] == -1: pcnl_cols['nx_nlc'] = len(df_raw.columns); df_raw[pcnl_cols['nx_nlc']] = ""
            if pcnl_cols['nx_nldt'] == -1: pcnl_cols['nx_nldt'] = len(df_raw.columns); df_raw[pcnl_cols['nx_nldt']] = ""
            if pcnl_cols['nx_pc'] == -1: pcnl_cols['nx_pc'] = len(df_raw.columns); df_raw[pcnl_cols['nx_pc']] = ""

        for i in range(s_row, len(df_raw)):
            ten = str(df_raw.iloc[i, n_col]).strip()
            if ten.lower() not in ['nan', 'none', '']:
                if loai_nx == "PC-NL":
                    m_nlc = str(df_raw.iloc[i, pcnl_cols['muc_nlc']]).strip().upper() if pcnl_cols['muc_nlc'] != -1 else ""
                    m_nldt = str(df_raw.iloc[i, pcnl_cols['muc_nldt']]).strip().upper() if pcnl_cols['muc_nldt'] != -1 else ""
                    m_pc = str(df_raw.iloc[i, pcnl_cols['muc_pc']]).strip().upper() if pcnl_cols['muc_pc'] != -1 else ""
                    
                    data_list.append({
                        "Họ và tên": ten,
                        "Mức NLC": m_nlc if m_nlc not in ['NAN', 'NONE'] else "",
                        "Mức NLĐT": m_nldt if m_nldt not in ['NAN', 'NONE'] else "",
                        "Mức PC": m_pc if m_pc not in ['NAN', 'NONE'] else "",
                        "NX Năng lực chung": "",
                        "NX Năng lực đặc thù": "",
                        "NX Phẩm chất": ""
                    })
                else:
                    v_diem = str(df_raw.iloc[i, d_col]).strip() if d_col != -1 else ""
                    v_muc = str(df_raw.iloc[i, m_col]).strip().upper() if m_col != -1 else ""
                    if v_diem.upper() in ['NAN', 'NONE']: v_diem = ""
                    if v_muc.upper() in ['NAN', 'NONE']: v_muc = ""
                    data_list.append({"Họ và tên": ten, "Điểm": v_diem, "Mức": v_muc, "Nhận xét": ""})
                mapping_indices.append(i)
        
        if not data_list:
            if loai_nx == "PC-NL":
                df_view = pd.DataFrame(columns=["Họ và tên", "Mức NLC", "Mức NLĐT", "Mức PC", "NX Năng lực chung", "NX Năng lực đặc thù", "NX Phẩm chất"])
            else:
                df_view = pd.DataFrame(columns=["Họ và tên", "Điểm", "Mức", "Nhận xét"])
        else:
            df_view = pd.DataFrame(data_list)
            
        tab_place = st.empty()
        
        config = {
            "Họ và tên": st.column_config.Column(width="medium"), 
            "Nhận xét": st.column_config.Column(width="large")
        }
        
        if loai_nx == "PC-NL":
            config["Mức NLC"] = st.column_config.Column(width="small")
            config["Mức NLĐT"] = st.column_config.Column(width="small")
            config["Mức PC"] = st.column_config.Column(width="small")
            config["NX Năng lực chung"] = st.column_config.Column(width="medium")
            config["NX Năng lực đặc thù"] = st.column_config.Column(width="medium")
            config["NX Phẩm chất"] = st.column_config.Column(width="medium")
        else: 
            config["Điểm"] = st.column_config.Column(width="small")
            config["Mức"] = st.column_config.Column(width="small")
            
        tab_place.dataframe(df_view, use_container_width=True, height=450, column_config=config)
        
        if st.button("🚀 Thực hiện nhận xét Tự động"):
            if api_key: genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash') if api_key else None
            bar = st.progress(0); status = st.empty()
            
            st.session_state.ket_qua_nhan_xet = []
            
            style_dict = {
                "Ngắn gọn": "súc tích, đi thẳng vào đánh giá năng lực kiến thức, không rườm rà",
                "Gần gũi": "nhận xét trực tiếp vào kiến thức theo hướng xây dựng, khách quan",
                "Khích lệ": "tập trung vào kỹ năng học sinh cần cải thiện để đạt kết quả chuyên môn tốt hơn",
                "Đầy đủ": "đánh giá phân tích cực kỳ chi tiết, chỉ rõ ưu khuyết điểm cụ thể về kỹ năng đặc thù của môn học (ví dụ đọc vấp, sai chính tả ngữ pháp, dùng lược đồ bản đồ thành thạo, có tố chất nhà sáng chế công nghệ,...), đồng thời đưa ra giải pháp khắc phục bằng từ 'cần' hoặc 'nên'"
            }
            
            if bat_xung_ho:
                lenh_xung_ho = f"CHỈ ĐƯỢC dùng đại từ '{xung_ho}' (ví dụ: {xung_ho} nhận thấy, {xung_ho} đánh giá...). TUYỆT ĐỐI KHÔNG dùng các từ 'con', 'em', 'trò' hay gọi tên học sinh."
            else:
                lenh_xung_ho = "TUYỆT ĐỐI KHÔNG dùng bất kỳ từ xưng hô nào (không dùng Thầy, Cô, tôi, mình, con, em, trò) hay gọi tên học sinh. Chỉ nhận xét thẳng thắn, khách quan trực tiếp vào kết quả môn học."
                
            lenh_cam_cam_xuc = "TUYỆT ĐỐI KHÔNG DÙNG các từ ngữ cảm xúc, an ủi, hứa hẹn, nhắc đến gia đình hay ra lệnh cứng nhắc (như: 'Đừng lo lắng', 'Mong', 'Mong có sự', 'Mong rằng', 'Sẽ', 'Sẽ đồng hành', 'Tin kết quả sẽ tốt', 'Gia đình', 'Nhắc nhở', 'Yêu cầu'). CHỈ đánh giá khách quan, khoa học trực tiếp vào ưu/khuyết điểm của nội dung kiến thức môn học và dùng từ 'cần' hoặc 'nên' để đề xuất khắc phục."
            
            is_nang_khieu = mon in ["Đạo đức", "Âm nhạc", "Mĩ thuật", "GDTC", "HĐGD", "Hoạt động trải nghiệm"]
            if is_nang_khieu:
                lenh_mon_dac_thu = "BẮT BUỘC NHẬN XÉT ĐẶC THÙ: Đây là môn năng khiếu/đạo đức. TUYỆT ĐỐI KHÔNG KHUYÊN 'ôn tập kiến thức', 'củng cố nền tảng', 'làm bài tập'. Hãy nhận xét về việc 'rèn luyện kỹ năng', 'thái độ', 'thực hành', 'ứng xử' và 'ý thức'."
            else:
                lenh_mon_dac_thu = ""
                
            is_cuoi_nam = thoi_diem == "Cuối học kì II"
            if is_cuoi_nam:
                mang_cau_truc_mo_bai = [
                    "BẮT BUỘC MỞ CÂU: Bằng việc TỔNG KẾT NĂM HỌC (VD: Tổng kết năm học, mức độ nắm bắt kiến thức là...)",
                    "BẮT BUỘC MỞ CÂU: Bằng việc đánh giá TOÀN DIỆN KỸ NĂNG (VD: Xuyên suốt năm học, kỹ năng thực hành...)",
                    "BẮT BUỘC MỞ CÂU: Bằng sự ĐÁNH GIÁ CHUNG (VD: Hoàn thành xuất sắc/tốt/cơ bản chương trình năm học...)"
                ]
            else:
                mang_cau_truc_mo_bai = [
                    "BẮT BUỘC MỞ CÂU: Bằng việc ghi nhận MỨC ĐỘ NẮM BẮT KIẾN THỨC (VD: Nắm rất vững, Thực hiện chưa tốt, Đạt mức cơ bản...)",
                    "BẮT BUỘC MỞ CÂU: Bằng việc đánh giá KỸ NĂNG THỰC HÀNH/VẬN DỤNG (VD: Thực hiện xuất sắc, Kỹ năng thực hành yếu...)",
                    "BẮT BUỘC MỞ CÂU: Bằng sự TỔNG KẾT KẾT QUẢ (VD: Kết quả học tập xuất sắc, Chưa hoàn thành mục tiêu...)",
                    "BẮT BUỘC MỞ CÂU: Bằng việc phân tích THÁI ĐỘ/TƯ DUY (VD: Tư duy nhạy bén, Thái độ học tập thiếu tập trung...)",
                    "BẮT BUỘC MỞ CÂU: Bằng một ĐIỂM SÁNG/ĐIỂM YẾU CỤ THỂ của môn học (VD: Đọc diễn cảm rất tốt, Kỹ năng tính toán còn chậm...)",
                    "BẮT BUỘC MỞ CÂU: Bằng cụm danh từ CHỈ NĂNG LỰC (VD: Năng lực học tập môn này rất tốt, Mức độ tiếp thu còn hạn chế...)",
                    "BẮT BUỘC MỞ CÂU: Bắt đầu ngay bằng TÊN MẠCH KIẾN THỨC (VD: Đối với nội dung [Tên bài], kết quả đạt được là...)"
                ]

            for idx, row in df_view.iterrows():
                real_idx = mapping_indices[idx]; ten_hs = row["Họ và tên"]; nx_text = ""
                
                style_key = phong_cach if phong_cach != "Ngẫu nhiên" else random.choice(["Ngắn gọn", "Gần gũi", "Khích lệ", "Đầy đủ"])
                style_prompt = style_dict[style_key]
                salt = str(uuid.uuid4())[:5]
                
                if style_key == "Đầy đủ":
                    lenh_do_dai = "Khoảng 25-35 từ. Cần viết dài, chi tiết, đầy đủ câu chủ vị và phân tích sâu sát chuyên môn."
                else:
                    lenh_do_dai = "Khoảng 15-20 từ. Viết súc tích."
                    
                huong_mo_dau = random.choice(mang_cau_truc_mo_bai)
                lenh_chong_lap = f"CHỐNG LẶP CẤU TRÚC (QUAN TRỌNG NHẤT): Bắt buộc {huong_mo_dau}. TUYỆT ĐỐI KHÔNG DÙNG CHUNG 1 KIỂU MỞ CÂU CHO TẤT CẢ. Không được luôn luôn bắt đầu bằng đại từ xưng hô, hãy linh hoạt đưa đại từ (nếu có) vào giữa hoặc cuối câu để câu văn tự nhiên. CHỐNG LẶP CÂU CHỐT: TUYỆT ĐỐI KHÔNG lặp đi lặp lại cụm từ 'cần rèn luyện thêm' ở cuối các câu nhận xét. Hãy thay thế bằng đa dạng các lời khuyên chuyên môn khác (Ví dụ: cần chú ý ôn tập kỹ lưỡng, cần nỗ lực khắc phục lỗ hổng kiến thức, nên dành thêm thời gian thực hành, cần nghiêm túc trau dồi mỗi ngày...)."

                is_empty_row = False
                
                if loai_nx == "PC-NL":
                    m_nlc = str(row.get("Mức NLC", "")).strip()
                    m_nldt = str(row.get("Mức NLĐT", "")).strip()
                    m_pc = str(row.get("Mức PC", "")).strip()
                    is_empty_row = (m_nlc == "" and m_nldt == "" and m_pc == "")
                else:
                    d_val = str(row.get("Điểm", "")).strip()
                    m_val = str(row.get("Mức", "")).strip()
                    is_empty_row = (d_val == "" and m_val == "")

                if is_empty_row:
                    if loai_nx == "PC-NL":
                        df_view.at[idx, "NX Năng lực chung"] = ""
                        df_view.at[idx, "NX Năng lực đặc thù"] = ""
                        df_view.at[idx, "NX Phẩm chất"] = ""
                        df_raw.iloc[real_idx, pcnl_cols['nx_nlc']] = ""
                        df_raw.iloc[real_idx, pcnl_cols['nx_nldt']] = ""
                        df_raw.iloc[real_idx, pcnl_cols['nx_pc']] = ""
                        st.session_state.ket_qua_nhan_xet.append("")
                    else:
                        df_view.at[idx, "Nhận xét"] = ""
                        df_raw.iloc[real_idx, c_col] = ""
                        st.session_state.ket_qua_nhan_xet.append("")
                else:
                    if loai_nx == "PC-NL":
                        mdd_nlc = get_mdd(m_nlc)
                        mdd_nldt = get_mdd(m_nldt)
                        mdd_pc = get_mdd(m_pc)
                        
                        if api_key:
                            prompt = f"Mã:{salt}. Đóng vai giáo viên tiểu học. Viết 3 nhận xét ngắn gọn, riêng biệt: 1. Năng lực chung (Mức {mdd_nlc}), 2. Năng lực đặc thù (Mức {mdd_nldt}), 3. Phẩm chất (Mức {mdd_pc}). PHONG CÁCH: {style_prompt}. BẮT BUỘC TRẢ VỀ THEO ĐỊNH DẠNG: [Nhận xét 1] | [Nhận xét 2] | [Nhận xét 3]. {lenh_xung_ho} {lenh_cam_cam_xuc}"
                            try:
                                res = model.generate_content(prompt); text = res.text.strip()
                                parts = text.split('|')
                                nx_nlc = parts[0].strip() if len(parts) > 0 else ""
                                nx_nldt = parts[1].strip() if len(parts) > 1 else ""
                                nx_pc = parts[2].strip() if len(parts) > 2 else ""
                            except:
                                nx_nlc, nx_nldt, nx_pc = sinh_nhan_xet_pcnl_offline(mdd_nlc, mdd_nldt, mdd_pc, style_key, xung_ho, bat_xung_ho)
                        else:
                            nx_nlc, nx_nldt, nx_pc = sinh_nhan_xet_pcnl_offline(mdd_nlc, mdd_nldt, mdd_pc, style_key, xung_ho, bat_xung_ho)
                        
                        df_view.at[idx, "NX Năng lực chung"] = nx_nlc
                        df_view.at[idx, "NX Năng lực đặc thù"] = nx_nldt
                        df_view.at[idx, "NX Phẩm chất"] = nx_pc
                        
                        df_raw.iloc[real_idx, pcnl_cols['nx_nlc']] = nx_nlc
                        df_raw.iloc[real_idx, pcnl_cols['nx_nldt']] = nx_nldt
                        df_raw.iloc[real_idx, pcnl_cols['nx_pc']] = nx_pc
                        st.session_state.ket_qua_nhan_xet.append(f"{nx_nlc} | {nx_nldt} | {nx_pc}")
                        
                    else:
                        mdd = "H_TrungBinh"
                        if d_val.replace('.', '', 1).isdigit():
                            diem_so = float(d_val)
                            if diem_so >= 9: mdd = "T"
                            elif diem_so >= 7: mdd = "H_Kha"
                            elif diem_so >= 5: mdd = "H_TrungBinh"
                            else: mdd = "C"
                        elif m_val.replace('.', '', 1).isdigit():
                            diem_so = float(m_val)
                            if diem_so >= 9: mdd = "T"
                            elif diem_so >= 7: mdd = "H_Kha"
                            elif diem_so >= 5: mdd = "H_TrungBinh"
                            else: mdd = "C"
                        else:
                            chk_val = m_val if m_val != "" else d_val
                            mdd = get_mdd(chk_val)

                        mach_kt_list = lay_mach_kien_thuc(mon, khoi, thoi_diem)
                        focus_kt = random.choice(mach_kt_list)

                        if api_key:
                            try:
                                k_q = f"Điểm: {d_val} " if d_val else ""
                                k_q += f"Mức: {m_val}" if m_val else ""
                                prompt = f"Mã:{salt}. Đóng vai chuyên gia giáo dục. Viết 1 nhận xét học bạ môn {mon} lớp {khoi.split(' ')[1]} vào {thoi_diem}.\nKết quả: {k_q.strip()}.\nMẠCH KIẾN THỨC BẮT BUỘC (Chỉ nhận xét kiến thức này, tuyệt đối không bịa thêm kiến thức của học kì khác): '{focus_kt}'.\nPHONG CÁCH: {style_prompt}.\n{lenh_xung_ho}\n{lenh_cam_cam_xuc}\n{lenh_mon_dac_thu}\nNếu <5 hoặc C bắt buộc bắt đầu 'Chưa hoàn thành...'.\n{lenh_do_dai}\n{lenh_chong_lap}\nDiễn đạt mạch lạc, tự nhiên như giáo viên tiểu học thực thụ."
                                res = model.generate_content(prompt); nx_text = res.text.strip()
                            except: nx_text = ""
                        
                        if not nx_text:
                            nx_text = sinh_nhan_xet_offline("Môn học", mdd, focus_kt, style_key, xung_ho, bat_xung_ho, mon, thoi_diem)

                        df_view.at[idx, "Nhận xét"] = nx_text
                        df_raw.iloc[real_idx, c_col] = nx_text
                        st.session_state.ket_qua_nhan_xet.append(nx_text)
                
                tab_place.dataframe(df_view, use_container_width=True, height=450, column_config=config)
                bar.progress((idx + 1) / len(df_view))
                status.text(f"✔ Đang hoàn thiện: {ten_hs}")
                time.sleep(1.0 if api_key else 0.01)

            st.balloons()
            status.success(f"✅ Hoàn thành xuất sắc bộ học bạ!")
            
            if st.session_state.ket_qua_nhan_xet:
                if loai_nx == "PC-NL":
                    st.warning("🚨 **LƯU Ý VỚI BẢNG PC-NL:** Bảng PC-NL chứa tới 3 cột nhận xét khác nhau. Thầy/Cô vui lòng **Tải file kết quả dự phòng** (nút bên dưới) và đẩy trực tiếp lên SMAS để đảm bảo thông tin khớp 100% vào đúng từng cột, hạn chế thao tác Copy-Paste bị lệch ô!")
                else:
                    st.markdown("### 📋 KẾT QUẢ COPY NHANH (DÁN TRỰC TIẾP VÀO EXCEL)")
                    copy_text = "\n".join(st.session_state.ket_qua_nhan_xet)
                    st.text_area("Bấm chuột vào khung dưới đây, ấn Ctrl+A để chọn tất cả, rồi ấn Ctrl+C để Copy:", value=copy_text, height=350)
                    st.warning("🚨 **LỖI DÁN 1 DÒNG DÀI NGOẰNG VÀ CÁCH KHẮC PHỤC:**\nNguyên nhân là do thầy/cô đã click đúp (nhấn chuột 2 lần) vào ô Excel khiến con trỏ nhấp nháy bên trong ô.\n\n👉 **CÁCH LÀM ĐÚNG:** Chỉ **CLICK CHUỘT 1 LẦN DUY NHẤT** vào ô đầu tiên (sao cho ô đó hiện viền màu xanh, TUYỆT ĐỐI KHÔNG có con trỏ nháy nháy bên trong). Sau đó ấn **Ctrl + V**, Excel sẽ tự động rải đều mỗi em 1 dòng!")

            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as writer:
                df_raw.to_excel(writer, index=False, header=False)
            st.download_button("📥 Tải file kết quả dự phòng", data=out.getvalue(), file_name=f"SDGHS_ThinhDam.xlsx")
