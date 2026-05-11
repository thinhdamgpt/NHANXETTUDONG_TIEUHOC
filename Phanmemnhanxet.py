import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import io
import random
import uuid

# --- 1. MA TRẬN PHÂN PHỐI CHƯƠNG TRÌNH GDPT 2018 ĐƯỢC CHIA CHI TIẾT THEO KỲ HỌC ---
PHAN_PHOI_CHUONG_TRINH = {
    "Tiếng Việt": {
        "Khối 1": {
            "Giữa học kì I": ["âm và chữ cái", "đọc và ghép các vần", "cầm bút và viết nét cơ bản"],
            "Cuối học kì I": ["đọc trơn từ và câu ngắn", "viết đúng các vần khó", "nghe hiểu và trả lời câu hỏi"],
            "Giữa học kì II": ["đọc trơn đoạn văn ngắn", "tô chữ hoa và viết đúng ô ly", "đọc thành tiếng rõ ràng"],
            "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Việt", "kỹ năng đọc hiểu văn bản", "năng lực viết chính tả và kể chuyện"]
        },
        "Khối 2": {
            "Giữa học kì I": ["đọc ngắt nghỉ đúng dấu câu", "từ chỉ sự vật, hoạt động", "nghe viết chính tả"],
            "Cuối học kì I": ["viết đoạn văn ngắn 4-5 câu", "mở rộng vốn từ theo chủ điểm", "kể chuyện theo tranh"],
            "Giữa học kì II": ["đọc hiểu và trả lời câu hỏi chi tiết", "từ chỉ đặc điểm", "viết câu chuẩn ngữ pháp"],
            "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Việt", "năng lực đọc hiểu và tóm tắt", "kỹ năng viết đoạn văn miêu tả"]
        },
        "Khối 3": {
            "Giữa học kì I": ["đọc diễn cảm", "nhận biết hình ảnh so sánh", "viết đoạn văn tả sự vật"],
            "Cuối học kì I": ["viết thư hoặc đoạn văn kể chuyện", "từ ngữ về cộng đồng, quê hương", "đọc hiểu văn bản truyện"],
            "Giữa học kì II": ["nhận biết hình ảnh nhân hóa", "đọc hiểu văn bản thông tin", "mở rộng vốn từ sáng tạo"],
            "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Việt", "năng lực đọc hiểu đa dạng văn bản", "kỹ năng viết văn miêu tả chi tiết"]
        },
        "Khối 4": {
            "Giữa học kì I": ["đọc hiểu văn bản sâu", "nhận biết danh từ, động từ", "viết bài văn kể chuyện", "cấu tạo của tiếng"],
            "Cuối học kì I": ["viết bài văn miêu tả đồ vật", "hiểu và vận dụng biện pháp tu từ", "đọc diễn cảm bài thơ", "nhận biết câu hỏi, câu kể"],
            "Giữa học kì II": ["đọc diễn cảm và tóm tắt bài", "nhận biết tính từ, câu khiến", "viết bài văn miêu tả cây cối", "xác định chủ ngữ, vị ngữ"],
            "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Việt", "năng lực đọc diễn cảm và cảm thụ", "kỹ năng viết bài văn hoàn chỉnh"]
        },
        "Khối 5": {
            "Giữa học kì I": ["đọc diễn cảm văn bản dài", "từ đồng nghĩa, từ trái nghĩa", "viết bài văn tả cảnh", "từ nhiều nghĩa"],
            "Cuối học kì I": ["sử dụng đại từ, quan hệ từ", "viết đơn từ", "đọc hiểu văn bản đa phương thức", "viết văn tả người"],
            "Giữa học kì II": ["hiểu ý nghĩa biện pháp nghệ thuật", "câu ghép và cách nối các vế câu", "viết bài văn tả đồ vật"],
            "Cuối học kì II": ["kiến thức toàn chương trình Tiếng Việt", "năng lực cảm thụ văn học", "kỹ năng tổng kết vốn từ và liên kết câu"]
        }
    },
    "Toán": {
        "Khối 1": {
            "Giữa học kì I": ["các số đến 10", "so sánh số phạm vi 10", "đếm và cấu tạo số"],
            "Cuối học kì I": ["phép cộng, trừ trong phạm vi 10", "nhận biết hình vuông, tròn, tam giác", "giải bài toán cơ bản"],
            "Giữa học kì II": ["các số đến 100", "phép cộng trừ không nhớ phạm vi 100", "đo độ dài bằng gang tay, bước chân"],
            "Cuối học kì II": ["kiến thức toàn chương trình Toán học", "kỹ năng thực hiện phép tính cơ bản", "năng lực giải toán có lời văn"]
        },
        "Khối 2": {
            "Giữa học kì I": ["phép cộng có nhớ phạm vi 100", "bài toán nhiều hơn, ít hơn", "đơn vị đo độ dài cm, dm"],
            "Cuối học kì I": ["phép trừ có nhớ phạm vi 100", "đơn vị đo khối lượng kg, dung tích l", "xem lịch, xem đồng hồ"],
            "Giữa học kì II": ["bảng nhân, chia 2 và 5", "nhận biết khối trụ, khối cầu", "giải toán có lời văn"],
            "Cuối học kì II": ["kiến thức toàn chương trình Toán học", "kỹ năng tính toán phạm vi 1000", "năng lực vận dụng đại lượng đo lường"]
        },
        "Khối 3": {
            "Giữa học kì I": ["bảng nhân chia 6-9", "nhân chia số có hai chữ số", "giải toán bằng một phép tính"],
            "Cuối học kì I": ["số trong phạm vi 10.000", "tính giá trị biểu thức", "nhận biết góc vuông, không vuông"],
            "Giữa học kì II": ["số trong phạm vi 100.000", "tính chu vi, diện tích hình chữ nhật, hình vuông", "thống kê số liệu"],
            "Cuối học kì II": ["kiến thức toàn chương trình Toán học", "kỹ năng thực hiện 4 phép tính", "năng lực giải toán bằng hai phép tính"]
        },
        "Khối 4": {
            "Giữa học kì I": ["số có nhiều chữ số", "các phép toán với số tự nhiên", "tìm số trung bình cộng"],
            "Cuối học kì I": ["tính chất giao hoán, kết hợp", "góc và hai đường thẳng song song, vuông góc", "chia cho số có 2 chữ số"],
            "Giữa học kì II": ["phân số và tính chất cơ bản", "rút gọn và quy đồng phân số", "phép cộng, trừ phân số"],
            "Cuối học kì II": ["kiến thức toàn chương trình Toán học", "kỹ năng giải toán phân số", "năng lực tư duy logic và tính toán tổng hợp"]
        },
        "Khối 5": {
            "Giữa học kì I": ["khái niệm số thập phân", "phép cộng, trừ số thập phân", "giải toán về số thập phân"],
            "Cuối học kì I": ["phép nhân, chia số thập phân", "tỉ số phần trăm", "giải toán tỉ số phần trăm"],
            "Giữa học kì II": ["diện tích hình tam giác, hình thang", "diện tích xung quanh và toàn phần", "hình hộp chữ nhật, hình lập phương"],
            "Cuối học kì II": ["kiến thức toàn chương trình Toán học", "năng lực giải toán chuyển động, thể tích", "kỹ năng tính toán số thập phân tổng hợp"]
        }
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

# --- KHO DỮ LIỆU OFFLINE ---
def sinh_nhan_xet_offline(loai_nx, mdd, focus_kt, phong_cach="Ngắn gọn", xung_ho="Thầy", bat_xung_ho=True, mon="", thoi_diem=""):
    xh = f"{xung_ho} " if bat_xung_ho else ""
    is_nang_khieu = mon in ["Đạo đức", "Âm nhạc", "Mĩ thuật", "GDTC", "HĐGD", "Hoạt động trải nghiệm"]
    is_cuoi_nam = thoi_diem == "Cuối học kì II"
    
    def cap_first(s):
        if not s: return s
        s = s.strip()
        return s[0].upper() + s[1:] if s else ""

    if loai_nx == "PC-NL":
        kho_pcnl = {
            "T": {
                "Ngắn gọn": [
                    "Năng lực đặc thù các môn rất nổi trội. Tự học và giao tiếp xuất sắc. Luôn nỗ lực, trách nhiệm và hòa đồng.",
                    "Đạt kết quả xuất sắc ở các năng lực chuyên biệt. Tự chủ và sáng tạo cao. Biết quan tâm, chia sẻ và trung thực.",
                    "Thể hiện năng lực học tập rất tốt. Giao tiếp linh hoạt. Rèn luyện 5 phẩm chất đạo đức gương mẫu."
                ],
                "Gần gũi": [
                    cap_first(f"{xh}đánh giá cao năng lực các môn học. Kỹ năng giao tiếp và tự học đạt mức xuất sắc. Chăm chỉ, ngoan ngoãn."),
                    cap_first(f"{xh}ghi nhận sự phát triển toàn diện ở các năng lực. Hợp tác nhóm linh hoạt. Yêu thương bạn bè, nề nếp tốt.")
                ],
                "Khích lệ": [
                    f"Cần tiếp tục phát huy năng lực học tập xuất sắc! Kỹ năng tự chủ và giao tiếp rất vững vàng. Cần duy trì tinh thần trách nhiệm.",
                    f"Kết quả rèn luyện năng lực rất xuất sắc. Khả năng giải quyết vấn đề linh hoạt. Cần giữ vững thái độ học tập tích cực."
                ],
                "Đầy đủ": [
                    "Năng lực đặc thù các môn vô cùng nổi trội. Kỹ năng tự học và giải quyết vấn đề xuất sắc. Giao tiếp tự tin, linh hoạt. Thể hiện rõ tinh thần yêu nước, nhân ái, trung thực và biết chia sẻ với bạn bè.", 
                    "Sự tiến bộ ở các năng lực cốt lõi được thể hiện rõ rệt. Năng lực tự chủ và tính sáng tạo rất cao. Thể hiện trọn vẹn 5 phẩm chất đạo đức tốt đẹp, là tấm gương sáng về sự chăm chỉ và tinh thần trách nhiệm."
                ]
            },
            "H_Kha": {
                 "Ngắn gọn": [
                     "Nắm vững kiến thức đặc thù các môn. Ý thức tự học và giao tiếp khá. Chăm chỉ và trung thực trong học tập.",
                     "Thực hiện khá tốt các năng lực bộ môn. Kỹ năng hợp tác nhóm linh hoạt. Có trách nhiệm với nhiệm vụ.",
                     "Đạt mức khá ở các năng lực học tập. Tự chủ trong giải quyết vấn đề. Luôn tuân thủ nội quy lớp học."
                 ],
                 "Gần gũi": [
                     cap_first(f"{xh}đánh giá tốt mức độ tiếp thu bài. Giao tiếp và làm việc nhóm khá linh hoạt. Hòa đồng, yêu thương bạn bè."),
                     f"Khả năng học tập các môn khá chắc chắn. Ý thức tự học có tiến bộ rõ rệt. {cap_first(xh + 'ghi nhận sự rèn luyện nghiêm túc mỗi ngày.')}"
                 ],
                 "Khích lệ": [
                     f"Đã nắm chắc năng lực các môn, cần phát huy mạnh mẽ hơn! Kỹ năng giải quyết vấn đề khá tốt. Ghi nhận sự nỗ lực bền bỉ.",
                     f"Sự tiến bộ ở các môn rất đáng ghi nhận. Kỹ năng giao tiếp đang tự tin hơn. Cần tiếp tục tập trung rèn luyện."
                 ],
                 "Đầy đủ": [
                     "Phát huy khá tốt các năng lực chuyên biệt. Kỹ năng tự học và giao tiếp đạt mức khá vững vàng. Có ý thức rèn luyện tốt 5 phẩm chất, tuy nhiên cần chú ý rèn tính chủ động và sáng tạo hơn nữa trong học tập.", 
                     "Tiếp thu vững vàng các năng lực cốt lõi. Kỹ năng làm việc nhóm linh hoạt. Chăm chỉ, trung thực và có trách nhiệm với tập thể, tuy nhiên cần nỗ lực mạnh dạn hơn trong việc tự giải quyết vấn đề cá nhân."
                 ]
            },
            "H_TrungBinh": {
                 "Ngắn gọn": [
                     "Đạt yêu cầu về năng lực các môn học. Cần mạnh dạn hơn trong giao tiếp. Biết yêu thương và tuân thủ nội quy.",
                     "Mức độ hoàn thành các nội dung đặc thù ở mức cơ bản. Cần chủ động hơn khi làm việc nhóm. Chăm chỉ nhưng thiếu tính tự giác.",
                     "Kết quả đánh giá năng lực đạt yêu cầu. Cần rèn luyện thêm tính trung thực và trách nhiệm."
                 ],
                 "Gần gũi": [
                     f"Năng lực các môn đạt yêu cầu cơ bản. Cần mạnh dạn hơn khi làm việc nhóm. {cap_first(xh + 'nhắc nhở cần tăng cường sự tự giác học tập.')}",
                     f"Kiến thức các môn ở mức cơ bản. Cần rèn luyện sự tự tin trong giao tiếp. Giữ vững thái độ trung thực, hòa đồng."
                 ],
                 "Khích lệ": [
                     f"Cần nâng cao ý thức tự giác để cải thiện kết quả. Năng lực bộ môn cơ bản ổn định. Tăng cường rèn luyện tính trung thực.",
                     f"Cần mạnh dạn thể hiện năng lực bản thân trong lớp. Kỹ năng giao tiếp cần cởi mở hơn. Cần tập trung tối đa cho việc học."
                 ],
                 "Đầy đủ": [
                     "Đạt mức cơ bản về các năng lực chung và đặc thù. Kỹ năng giao tiếp và tự học còn chưa thực sự nổi bật. Biết vâng lời và yêu thương bạn bè nhưng cần nâng cao tinh thần tự giác và kỷ luật cá nhân.", 
                     "Tiếp thu các năng lực cốt lõi ở mức đạt. Chưa chủ động trong làm việc nhóm và giải quyết khó khăn. Cần tích cực trau dồi 5 phẩm chất, đặc biệt là tính trung thực và tinh thần trách nhiệm trong các môn học."
                 ]
            },
            "C": {
                 "Ngắn gọn": [
                     "Chưa hoàn thành tốt năng lực đặc thù. Kỹ năng tự học và giao tiếp còn hạn chế. Cần cố gắng khắc phục tính trách nhiệm.",
                     "Kỹ năng tiếp thu kiến thức chậm. Chưa chủ động trong hợp tác và giải quyết vấn đề. Cần nghiêm túc rèn luyện kỷ luật.",
                     "Mức độ rèn luyện phẩm chất, năng lực còn hạn chế. Cần tập trung nghiêm túc vào việc học."
                 ],
                 "Gần gũi": [
                     f"Năng lực các môn học còn nhiều hạn chế. Cần cởi mở và chủ động hơn khi giao tiếp. {cap_first(xh + 'nhắc nhở cần có thái độ học tập nghiêm túc hơn.')}",
                     f"Khả năng học bộ môn còn yếu, cần tập trung ôn tập kỹ lưỡng. Kỹ năng hợp tác nhóm chưa cao. Cần thực hiện đúng nội quy."
                 ],
                 "Khích lệ": [
                     f"Cần rèn luyện chăm chỉ hơn để cải thiện kết quả các môn. Cần chủ động và tự tin khi giao tiếp. Chấn chỉnh thái độ học tập.",
                     f"Khắc phục khó khăn bằng sự rèn luyện bền bỉ mỗi ngày. Cố gắng hợp tác cùng bạn bè. Cần tập trung cải thiện ý thức học tập."
                 ],
                 "Đầy đủ": [
                     "Chưa hoàn thành yêu cầu về các năng lực đặc thù và năng lực chung. Kỹ năng tự học, giao tiếp còn nhiều hạn chế. Việc rèn luyện phẩm chất chưa tốt, thiếu sự chăm chỉ, chưa trung thực và cần nhanh chóng khắc phục ý thức trách nhiệm.", 
                     "Mức độ tiếp thu kiến thức và giải quyết vấn đề còn rất yếu. Thường xuyên thiếu tập trung, chưa tích cực trong làm việc nhóm. Cần thay đổi ngay thái độ học tập, tuân thủ nội quy và nâng cao đạo đức nhiều hơn."
                 ]
            }
        }
        bo_cau = kho_pcnl.get(mdd, kho_pcnl["H_Kha"])
        cau_chon = bo_cau.get(phong_cach, bo_cau["Ngắn gọn"])
        return random.choice(cau_chon)
        
    elif loai_nx == "HĐGD":
        kho_hdgd = {
             "T": {
                 "Ngắn gọn": ["Tích cực tham gia phong trào, hoàn thành xuất sắc hoạt động giáo dục.", "Thể hiện tính sáng tạo và nhiệt tình trong trải nghiệm, kỹ năng sống tốt.", "Đạt kết quả xuất sắc trong các tiết hoạt động chung."],
                 "Gần gũi": [cap_first(f"{xh}đánh giá cao sự tích cực tham gia các phong trào."), cap_first(f"{xh}khen ngợi sự nhiệt tình và sáng tạo trong hoạt động.")],
                 "Khích lệ": [f"Cần tiếp tục giữ vững tinh thần tham gia phong trào nhiệt huyết này!", f"Sự năng nổ trong các hoạt động trải nghiệm rất đáng biểu dương!"],
                 "Đầy đủ": ["Hoàn thành xuất sắc các nội dung hoạt động giáo dục và trải nghiệm suốt năm học. Chủ động, sáng tạo, thể hiện năng lực tổ chức và kỹ năng sống tuyệt vời trong mọi phong trào của lớp và trường."]
             },
             "H_Kha": {
                 "Ngắn gọn": ["Hoàn thành tốt các hoạt động giáo dục theo yêu cầu, nề nếp tốt.", "Nhiệt tình tham gia hoạt động trải nghiệm cùng tập thể lớp."],
                 "Gần gũi": [cap_first(f"{xh}ghi nhận ý thức tham gia các hoạt động giáo dục một cách nghiêm túc.")],
                 "Khích lệ": [f"Cần tiếp tục phát huy sự nhiệt tình trong các hoạt động trải nghiệm thực tế."],
                 "Đầy đủ": ["Thực hiện khá tốt các nhiệm vụ trong hoạt động giáo dục suốt năm. Có ý thức tham gia phong trào, hòa đồng với bạn bè, tuy nhiên cần chủ động và tự tin phát biểu ý kiến cá nhân hơn nữa."]
             },
             "H_TrungBinh": {
                 "Ngắn gọn": ["Có tham gia các hoạt động giáo dục, cần mạnh dạn và tự tin hơn.", "Mức độ hoàn thành nội dung trải nghiệm cơ bản."],
                 "Gần gũi": [cap_first(f"{xh}lưu ý cần mạnh dạn tham gia tích cực hơn trong các hoạt động phong trào.")],
                 "Khích lệ": [f"Cần tự tự tin thể hiện bản thân trong các hoạt động trải nghiệm nhiều hơn nữa."],
                 "Đầy đủ": ["Đạt mức cơ bản trong các tiết hoạt động giáo dục. Đã tham gia cùng tập thể nhưng còn rụt rè, chưa mạnh dạn và thiếu tính sáng tạo. Cần tích cực và năng nổ hơn trong phong trào chung."]
             },
             "C": {
                 "Ngắn gọn": ["Chưa hoàn thành nội dung trải nghiệm, cần chủ động tham gia phong trào.", "Thái độ tham gia các tiết trải nghiệm còn chưa thực sự nghiêm túc."],
                 "Gần gũi": [f"Cần tích cực và chủ động hơn trong các giờ trải nghiệm thực tế."],
                 "Khích lệ": [f"Cần tham gia phong trào tích cực hơn để rèn luyện kỹ năng sống."],
                 "Đầy đủ": ["Chưa hoàn thành các mục tiêu trải nghiệm và hoạt động giáo dục. Ít tham gia các phong trào, thái độ tham gia chưa nghiêm túc. Cần phải tích cực, tự giác và nâng cao kỹ năng sống nhiều hơn."]
             }
        }
        bo_cau = kho_hdgd.get(mdd, kho_hdgd["H_Kha"])
        return random.choice(bo_cau.get(phong_cach, bo_cau["Ngắn gọn"]))
        
    else: # Môn học
        if is_cuoi_nam:
            list_mo_bai_T = ["", "Tổng kết năm học, nắm rất vững ", "Thực hiện xuất sắc ", "Hoàn thành xuất sắc chương trình, đặc biệt ở ", "Xuyên suốt năm học, tiếp thu cực kỳ nhạy bén "]
            list_mo_bai_Kha = ["", "Tổng kết năm học, nắm vững ", "Thực hiện tốt ", "Hoàn thành tốt chương trình, nắm vững ", "Xuyên suốt năm học, tiếp thu khá tốt "]
            list_mo_bai_TB = ["", "Tổng kết năm học, nắm được ", "Thực hiện được cơ bản ", "Đạt mức cơ bản chương trình "]
            list_mo_bai_C = ["", "Tổng kết năm học, chưa nắm vững ", "Thực hiện chưa tốt chương trình ", "Chưa hoàn thành "]
        else:
            list_mo_bai_T = ["", "Nắm rất vững ", "Thực hiện xuất sắc ", "Hoàn thành xuất sắc ", "Tiếp thu cực kỳ nhạy bén "]
            list_mo_bai_Kha = ["", "Nắm vững ", "Thực hiện tốt ", "Hoàn thành tốt ", "Tiếp thu khá tốt "]
            list_mo_bai_TB = ["", "Nắm được ", "Thực hiện được cơ bản ", "Đạt mức cơ bản "]
            list_mo_bai_C = ["", "Chưa nắm vững ", "Thực hiện chưa tốt ", "Chưa hoàn thành "]
        
        prefix = random.choice(list_mo_bai_T if mdd == "T" else (list_mo_bai_Kha if mdd == "H_Kha" else (list_mo_bai_TB if mdd == "H_TrungBinh" else list_mo_bai_C)))

        if phong_cach == "Đầy đủ":
            if mdd == "T":
                if mon == "Tiếng Việt": return f"{prefix}nội dung {focus_kt}. Đọc ngắt nghỉ đúng nhịp, chữ viết nắn nót, đúng chính tả, biết viết câu đúng ngữ pháp và giàu hình ảnh."
                elif mon == "Toán": return f"{prefix}phần {focus_kt}. Kĩ năng tính toán nhanh, chính xác; tư duy logic nhạy bén và giải quyết trọn vẹn các bài toán có lời văn."
                elif mon == "Lịch sử & Địa lý": return f"{prefix}kiến thức {focus_kt}. Kĩ năng học tập vô cùng thành thạo. Ghi nhớ tốt các sự kiện lịch sử và đặc điểm vùng miền."
                elif mon == "Công nghệ": return f"{prefix}vai trò của công nghệ, thực hiện nội dung {focus_kt} rất xuất sắc. Có tư duy thiết kế tốt, hoàn thành các sản phẩm thực hành cực kì khéo léo."
                elif mon == "Tiếng Anh": return f"{prefix}phần {focus_kt}. Phát âm tiếng Anh chuẩn xác, phản xạ giao tiếp trôi chảy. Nắm vững từ vựng, cấu trúc ngữ pháp."
                elif mon == "Khoa học": return f"{prefix}kiến thức về {focus_kt}. Tư duy nhạy bén, biết giải thích các hiện tượng và vận dụng linh hoạt vào thực tế."
                elif mon == "Tin học": return f"{prefix}các thao tác ở nội dung {focus_kt}. Nắm rất vững lý thuyết, hoàn thành xuất sắc các bài thực hành với tư duy logic cao."
                elif mon == "Đạo đức": return f"{prefix}các chuẩn mực đạo đức trong bài {focus_kt}. Luôn tự giác, gương mẫu trong học tập, ứng xử lễ phép và biết chia sẻ."
                elif mon == "Âm nhạc": return f"{prefix}kỹ năng {focus_kt}. Thể hiện năng khiếu âm nhạc xuất sắc. Hát đúng giai điệu, thuộc lời ca và biết kết hợp vận động."
                elif mon == "Mĩ thuật": return f"{prefix}nội dung {focus_kt}. Năng khiếu tạo hình rất tốt. Thể hiện sự sáng tạo cao trong bố cục, màu sắc. Hoàn thành sản phẩm vô cùng đẹp mắt."
                elif mon == "GDTC": return f"{prefix}nội dung {focus_kt}. Thể lực rất tốt, thực hiện thành thạo các động tác. Tích cực, năng nổ trong mọi hoạt động vận động."
                elif mon == "Hoạt động trải nghiệm": return f"{prefix}nội dung {focus_kt}. Thể hiện sự tự tin, chủ động và sáng tạo trong các hoạt động phong trào. Kỹ năng sống rất xuất sắc."
                else: return f"{prefix}nội dung {focus_kt}. Vận dụng vô cùng linh hoạt kiến thức vào thực tiễn, kĩ năng thực hành thành thạo và tư duy rất nhạy bén."
            
            elif mdd == "H_Kha":
                if mon == "Tiếng Việt": return f"{prefix}nội dung {focus_kt}. Chữ viết khá cẩn thận, biết cách đặt câu đúng chủ - vị và hoàn thành tốt các bài tập đọc hiểu."
                elif mon == "Toán": return f"{prefix}nội dung {focus_kt}. Thực hiện các phép tính khá nhanh, cẩn thận. Kĩ năng giải toán có lời văn tốt, cần chú ý nâng cao tốc độ ở bài toán khó."
                elif mon == "Lịch sử & Địa lý": return f"{prefix}nội dung {focus_kt}. Hiểu và ghi nhớ tốt các kiến thức trọng tâm. Kĩ năng quan sát, tìm hiểu khá vững vàng, cần mạnh dạn phát biểu."
                elif mon == "Công nghệ": return f"{prefix}nội dung {focus_kt}. Thực hiện khá tốt quy trình tạo ra các sản phẩm. Có ý thức giữ an toàn khi sử dụng dụng cụ, cần chăm chút thẩm mỹ."
                elif mon == "Tiếng Anh": return f"{prefix}nội dung {focus_kt}. Ghi nhớ được từ vựng cơ bản và biết cách vận dụng vào giao tiếp, cần trau dồi cách phát âm tự nhiên hơn."
                elif mon == "Khoa học": return f"{prefix}nội dung {focus_kt}. Thực hiện khá tốt các yêu cầu bài học, hiểu bản chất hiện tượng, cần chủ động phát biểu ý kiến hơn."
                elif mon == "Tin học": return f"{prefix}nội dung {focus_kt}. Biết sử dụng các công cụ phần mềm cơ bản, cần rèn luyện để thao tác nhanh nhẹn và chính xác hơn."
                elif mon == "Đạo đức": return f"{prefix}bài học {focus_kt}. Có ý thức tuân thủ nội quy, hành xử hòa nhã, cần rèn luyện sự tự tin khi giao tiếp."
                elif mon == "Âm nhạc": return f"{prefix}nội dung {focus_kt}. Nắm được nhịp điệu, kỹ năng hát ở mức khá, cần mạnh dạn biểu diễn trước lớp."
                elif mon == "Mĩ thuật": return f"{prefix}bài {focus_kt}. Sản phẩm có bố cục tương đối, có cố gắng trong thể hiện ý tưởng, cần chú ý để thực hiện chuẩn xác hơn."
                elif mon == "GDTC": return f"{prefix}nội dung {focus_kt}. Nắm được kỹ thuật động tác, thái độ học tập tích cực, cần phát huy sự nhanh nhẹn hơn nữa."
                elif mon == "Hoạt động trải nghiệm": return f"{prefix}nội dung {focus_kt}. Có ý thức tham gia các hoạt động phong trào, hòa đồng với bạn bè, cần mạnh dạn phát biểu ý kiến hơn."
                else: return f"{prefix}nội dung {focus_kt}. Có ý thức tự giác học tập, kĩ năng thực hành và vận dụng kiến thức đạt mức khá tốt, cần phát huy."
            
            elif mdd == "H_TrungBinh":
                if mon == "Tiếng Việt": return f"{prefix}nội dung {focus_kt}, tuy nhiên trả lời câu hỏi đọc hiểu chưa trọn vẹn. Cần nâng cao tính cẩn thận, hạn chế lỗi chính tả."
                elif mon == "Toán": return f"{prefix}nội dung {focus_kt} nhưng tính toán đôi khi còn nhầm lẫn do thiếu cẩn thận. Cần dành thêm thời gian ôn tập kỹ hơn các công thức và các bước giải bài tập."
                elif mon == "Lịch sử & Địa lý": return f"{prefix}nội dung {focus_kt}. Kĩ năng khai thác thông tin còn lúng túng, cần tập trung hơn trong giờ học và tích cực học hỏi."
                elif mon == "Công nghệ": return f"{prefix}nội dung {focus_kt} nhưng thao tác còn chậm và lúng túng. Cần nâng cao tính cẩn thận, tuân thủ quy trình và rèn luyện sự khéo léo."
                elif mon == "Tiếng Anh": return f"{prefix}nội dung {focus_kt}. Kĩ năng thực hành ngoại ngữ còn nhiều hạn chế, cần mạnh dạn, chủ động và cố gắng trau dồi mỗi ngày."
                elif mon == "Khoa học": return f"{prefix}nội dung {focus_kt} nhưng còn lúng túng khi giải thích hiện tượng. Cần chú ý nghe giảng và học bài cũ nghiêm túc."
                elif mon == "Tin học": return f"{prefix}lý thuyết {focus_kt} nhưng kỹ năng thực hành còn lúng túng, chậm chạp. Cần tập trung theo dõi thao tác mẫu."
                elif mon == "Đạo đức": return f"{prefix}nội dung {focus_kt}. Đôi lúc chưa tự giác thực hiện đúng nội quy, cần nghiêm túc khắc phục thái độ và hành vi trong lớp."
                elif mon == "Âm nhạc": return f"{prefix}lý thuyết nhưng thực hành {focus_kt} còn yếu. Cần chú ý lắng nghe giai điệu và rèn luyện sự tự tin khi hát."
                elif mon == "Mĩ thuật": return f"{prefix}bài {focus_kt} nhưng sản phẩm chưa cân đối. Sản phẩm thiếu sự tinh tế, cần chú ý quan sát và cẩn thận hơn để hoàn thiện."
                elif mon == "GDTC": return f"{prefix}nội dung {focus_kt} nhưng thao tác còn chậm, chưa dứt khoát. Cần tích cực trau dồi thể lực và tập trung rèn luyện."
                elif mon == "Hoạt động trải nghiệm": return f"{prefix}nội dung {focus_kt}. Đã tham gia cùng tập thể nhưng còn rụt rè, chưa thực sự chủ động. Cần tích cực và năng nổ hơn."
                else: return f"{prefix}nội dung {focus_kt}, tuy nhiên việc vận dụng kiến thức còn nhiều lúng túng. Cần cố gắng khắc phục điểm này bằng việc làm bài tập đầy đủ."
                     
            else: # mdd == "C"
                if mon == "Tiếng Việt": return f"{prefix}nội dung {focus_kt}. Kiến thức và kỹ năng đọc viết còn hạn chế, sai lỗi chính tả nhiều. Cần chú ý luyện tập thường xuyên cách viết câu đúng ngữ pháp."
                elif mon == "Toán": return f"{prefix}nội dung {focus_kt}. Kĩ năng tính toán còn yếu, thường xuyên sai sót các phép tính cơ bản. Cần nỗ lực khắc phục ngay các lỗ hổng kiến thức."
                elif mon == "Lịch sử & Địa lý": return f"{prefix}nội dung {focus_kt}. Thiếu tập trung, chưa biết cách khai thác thông tin địa lý, lịch sử. Cần thay đổi thái độ học tập và tích cực ôn luyện."
                elif mon == "Công nghệ": return f"{prefix}nội dung {focus_kt}. Thao tác thực hành rất chậm, chưa hoàn thành sản phẩm theo yêu cầu. Cần chú ý quan sát hướng dẫn để thực hành tốt hơn."
                elif mon == "Tiếng Anh": return f"{prefix}nội dung {focus_kt}. Vốn từ vựng còn quá ít, kĩ năng giao tiếp ngoại ngữ rất yếu. Cần tích cực trau dồi và ôn tập củng cố kiến thức mỗi ngày."
                elif mon == "Khoa học": return f"{prefix}nội dung {focus_kt}. Khả năng ghi nhớ và vận dụng yếu, thiếu tập trung quan sát các hiện tượng, cần chấn chỉnh ngay thái độ học tập."
                elif mon == "Tin học": return f"{prefix}nội dung {focus_kt}. Kỹ năng thực hành rất yếu, thường xuyên mất tập trung. Cần chủ động thực hành mỗi ngày trên máy tính."
                elif mon == "Đạo đức": return f"{prefix}nội dung {focus_kt}. Cần thay đổi thái độ, nghiêm túc tuân thủ nội quy lớp học, rèn luyện ý thức kỷ luật và tu dưỡng đạo đức thường xuyên."
                elif mon == "Âm nhạc": return f"{prefix}kỹ năng {focus_kt}. Thái độ học tập chưa tốt, cần nghiêm túc luyện tập, tập trung hơn trong giờ và chủ động học tập tích cực hơn."
                elif mon == "Mĩ thuật": return f"{prefix}nội dung {focus_kt}. Kỹ năng tạo hình và sử dụng màu yếu. Thái độ học tập thiếu tập trung, cần nghiêm túc trau dồi thêm."
                elif mon == "GDTC": return f"{prefix}nội dung {focus_kt}. Thể lực còn hạn chế, thái độ học tập chưa tích cực, thiếu ý thức kỷ luật trong giờ học, cần nỗ lực cải thiện thể chất."
                elif mon == "Hoạt động trải nghiệm": return f"{prefix}nội dung {focus_kt}. Ít tham gia các phong trào, thái độ trải nghiệm chưa nghiêm túc. Cần phải tích cực và tự giác hơn."
                else: return f"{prefix}nội dung {focus_kt}, kĩ năng thực hành còn rất yếu và thiếu chính xác. Cần nỗ lực rèn luyện, tự giác học bài nghiêm túc và tập trung hoàn thiện."

        else: 
            if mdd == "T":
                if is_nang_khieu:
                    mau_ngan_gon = [f"{prefix}nội dung {focus_kt}.", f"Kỹ năng và thái độ học tập phần {focus_kt} rất tốt.", f"Mục tiêu bài {focus_kt} được thực hiện rất xuất sắc."]
                    mau_gan_gui = [cap_first(f"{xh}đánh giá cao kỹ năng thực hành nội dung {focus_kt}."), cap_first(f"{xh}ghi nhận thái độ tích cực và kỹ năng rất tốt trong phần {focus_kt}.")]
                    mau_khich_le = [f"Kỹ năng {focus_kt} rất tốt, cần tiếp tục phát huy năng lực này.", f"Thái độ học tập xuất sắc ở phần {focus_kt}, cần duy trì phong độ."]
                else:
                    mau_ngan_gon = [
                        f"{prefix}nội dung {focus_kt}.",
                        f"Kỹ năng thực hành phần {focus_kt} rất vững vàng.",
                        f"Tư duy nhạy bén, xử lý chính xác phần {focus_kt}."
                    ]
                    mau_gan_gui = [
                         cap_first(f"{xh}đánh giá cao kỹ năng xử lý kiến thức {focus_kt}."),
                         cap_first(f"{xh}ghi nhận sự nhạy bén và kiến thức vững chắc trong phần {focus_kt}.")
                    ]
                    mau_khich_le = [
                         f"Khả năng tiếp thu {focus_kt} rất tốt, cần tiếp tục phát huy năng lực này.",
                         f"Kết quả đạt được rất xuất sắc ở phần {focus_kt}, cần duy trì phong độ môn học."
                    ]
            elif mdd == "H_Kha":
                if is_nang_khieu:
                    mau_ngan_gon = [f"{prefix}nội dung {focus_kt}.", f"Kỹ năng phần {focus_kt} khá vững, có tiến bộ.", f"Bài {focus_kt} được thực hiện tốt."]
                    mau_gan_gui = [cap_first(f"{xh}ghi nhận sự tiến bộ khi thực hành {focus_kt}, cần tích cực trau dồi hơn."), cap_first(f"{xh}đánh giá tốt việc nắm khá chắc kỹ năng {focus_kt}.")]
                    mau_khich_le = [f"Sự tiến bộ ở bài học {focus_kt} rất đáng ghi nhận, cần tiếp tục luyện tập.", f"Kỹ năng phần {focus_kt} khá tốt, cần nỗ lực để đạt mức xuất sắc."]
                else:
                    mau_ngan_gon = [
                        f"{prefix}nội dung {focus_kt}, vận dụng khá tốt.",
                        f"Kỹ năng học tập phần {focus_kt} khá vững.",
                        f"Đạt kết quả khả quan ở bài học {focus_kt}, kỹ năng ổn định."
                    ]
                    mau_gan_gui = [
                         cap_first(f"{xh}ghi nhận kỹ năng thực hành {focus_kt} có tiến bộ, cần cẩn thận để chính xác hơn."),
                         cap_first(f"{xh}đánh giá tốt việc nắm khá chắc nội dung bài {focus_kt}.")
                    ]
                    mau_khich_le = [
                         f"Sự tiến bộ ở bài học {focus_kt} rất đáng ghi nhận, cần duy trì sự cố gắng này.",
                         f"Kết quả môn học phần {focus_kt} khá tốt, cần nỗ lực hơn để hoàn thiện."
                    ]
            elif mdd == "H_TrungBinh":
                if is_nang_khieu:
                    mau_ngan_gon = [f"{prefix}phần {focus_kt}, cần cố gắng hơn.", f"Kỹ năng {focus_kt} ở mức đạt, thao tác còn chậm.", f"Thái độ học tập phần {focus_kt} cần tích cực hơn."]
                    mau_gan_gui = [f"Việc thực hành bài {focus_kt} còn hạn chế, {cap_first(xh + 'cần dành thêm thời gian ôn tập.')}", f"Cần chủ động thực hành phần {focus_kt} để trau dồi kỹ năng."]
                    mau_khich_le = [f"Cần tập trung khắc phục kỹ năng {focus_kt} để cải thiện kết quả.", f"Cần dành thời gian thực hành bài {focus_kt} để thành thạo hơn."]
                else:
                    mau_ngan_gon = [
                        f"{prefix}nội dung {focus_kt}, cần làm bài cẩn thận hơn.",
                        f"Thao tác giải quyết bài {focus_kt} còn chậm.",
                        f"Mức độ nắm bắt kiến thức {focus_kt} trung bình, cần chú ý ôn tập."
                    ]
                    mau_gan_gui = [
                         f"Kỹ năng xử lý bài {focus_kt} còn hạn chế, {cap_first(xh + 'cần nâng cao tính chính xác.')}",
                         f"Cần ôn tập kỹ hơn về {focus_kt} để củng cố nền tảng kiến thức."
                    ]
                    mau_khich_le = [
                         f"Cần tập trung ôn tập kỹ hơn về nội dung {focus_kt} để cải thiện kết quả.",
                         f"Cần dành nhiều thời gian hơn để khắc phục kỹ năng {focus_kt} tại nhà."
                    ]
            else: # mdd == "C"
                if is_nang_khieu:
                    mau_ngan_gon = [f"{prefix}kỹ năng {focus_kt}, cần nỗ lực cải thiện.", f"Thực hành {focus_kt} còn rất yếu, thái độ chưa tập trung.", f"Phần {focus_kt} chưa đạt, cần chấn chỉnh ý thức."]
                    mau_gan_gui = [f"Kỹ năng {focus_kt} chưa đạt, cần nghiêm túc thực hành thêm.", f"Cần chăm chỉ và tập trung rèn luyện nội dung {focus_kt} mỗi ngày."]
                    mau_khich_le = [f"Kỹ năng phần {focus_kt} còn rất nhiều hạn chế, cần nỗ lực thực hành thường xuyên.", f"Nội dung {focus_kt} cần chủ động khắc phục tích cực."]
                else:
                    mau_ngan_gon = [
                        f"{prefix}nội dung {focus_kt}, mức độ tiếp thu kiến thức yếu.",
                        f"Kỹ năng thực hành {focus_kt} còn hạn chế, cần tích cực học hỏi.",
                        f"Thiếu hụt kiến thức phần {focus_kt}, cần nghiêm túc chấn chỉnh thái độ."
                    ]
                    mau_gan_gui = [
                         f"Nội dung {focus_kt} chưa được nắm vững, cần nghiêm túc ôn tập thêm.",
                         f"Cần chăm chỉ và tập trung ôn luyện nội dung {focus_kt} hơn nữa."
                    ]
                    mau_khich_le = [
                         f"Phần {focus_kt} còn rất nhiều hạn chế, cần nỗ lực rèn luyện thường xuyên.",
                         f"Kiến thức {focus_kt} chưa đạt yêu cầu, cần chủ động rèn luyện và chú ý nghe giảng."
                    ]
                
            if phong_cach == "Ngắn gọn":
                return random.choice(mau_ngan_gon)
            elif phong_cach == "Gần gũi":
                return random.choice(mau_gan_gui)
            elif phong_cach == "Khích lệ":
                return random.choice(mau_khich_le)
            else: # Ngẫu nhiên
                 return random.choice(mau_ngan_gon + mau_gan_gui + mau_khich_le)

# --- 2. GIAO DIỆN PREMIUM 2026 ---
st.set_page_config(layout="wide", page_title="Đổi mới cùng thầy Thịnh", page_icon="✨")

st.markdown("""
<div style="background: linear-gradient(135deg, #1A73E8, #34A853); padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 30px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);">
    <h1 style="color: white; margin: 0; font-size: 3.2rem; font-weight: 900; letter-spacing: 3px; text-transform: uppercase; text-shadow: 2px 2px 5px rgba(0,0,0,0.3);">✨ Đổi mới cùng thầy Thịnh ✨</h1>
    <p style="color: #e8f0fe; font-size: 1.3rem; font-style: italic; margin-top: 8px; margin-bottom: 0; font-weight: 500;">Hệ thống Nhận xét Học bạ Tự động AI - Chuẩn TT27 (Phiên bản 2026)</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""<style>
.main { background-color: #f0f4f8; font-family: 'Inter', sans-serif; } 
.copy-area { background-color: #ffffff; padding: 18px; border-radius: 8px; border: 1px solid #d1d9e6; margin-top: 20px; max-height: 300px; overflow-y: auto; white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 14.5px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); line-height: 1.6;}
div[data-testid="stSidebar"] { background-color: #ffffff; box-shadow: 2px 0 12px rgba(0,0,0,0.06); }
.stButton>button { background-color: #1A73E8; color: white; border-radius: 6px; border: none; font-weight: 600; padding: 10px 20px; transition: all 0.3s ease; }
.stButton>button:hover { background-color: #1557b0; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(26,115,232,0.3); }
</style>""", unsafe_allow_html=True)

KEYS_15_PCNL = [f"nl{i}" for i in range(1, 11)] + [f"pc{i}" for i in range(1, 6)]

def check_col_has_data(df, col_idx, start_row, check_type="level"):
    for r in range(start_row, min(start_row + 3, len(df))):
        val = str(df.iloc[r, col_idx]).strip().upper()
        if val in ['NAN', 'NONE', '']: continue
        if check_type == "score" and val.replace('.','',1).isdigit(): return True
        if check_type == "level" and val in ['T', 'Đ', 'C', 'HTT', 'HT', 'CHT', 'H', 'K']: return True
    return False

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
        nl_col, pc_col = -1, -1
        detailed_cands = {k: [] for k in KEYS_15_PCNL}
        
        current_term_context = None # Trí nhớ lưu trữ học kì hiện tại để xử lý gộp ô (Merge Cells)
        
        for j in range(n_col + 1, len(df.columns)):
            # Mở rộng vùng quét lên trên 4 dòng để không bỏ sót tiêu đề lớn của Học kì bị gộp ô
            header_area = " ".join([str(df.iloc[r, j]).lower() for r in range(max(0, h_row - 4), s_row)])
            header_clean = header_area.replace(" ", "").replace("_", "").replace("-", "")
            
            # 1. NHẬN DIỆN VÀ GHI NHỚ HỌC KÌ VÀO CONTEXT
            if any(kw in header_clean for kw in ['ghk1', 'gk1', 'giữahk1', 'giữahọckì1', 'giữahọckỳ1', 'giữakì1', 'giữakỳ1', 'gki', 'giữakỳi', 'giữakìi', 'giữahọckỳi', 'giữahọckìi']) or ('ghki' in header_clean and 'ghkii' not in header_clean):
                current_term_context = "Giữa học kì I"
            elif any(kw in header_clean for kw in ['chk1', 'ck1', 'cuốihk1', 'cuốihọckì1', 'cuốihọckỳ1', 'cuốikì1', 'cuốikỳ1', 'hk1', 'cki', 'cuốikỳi', 'cuốikìi', 'cuốihọckỳi', 'cuốihọckìi']) or ('chki' in header_clean and 'chkii' not in header_clean) or ('hki' in header_clean and 'hkii' not in header_clean):
                current_term_context = "Cuối học kì I"
            elif any(kw in header_clean for kw in ['ghkii', 'ghk2', 'gk2', 'giữahk2', 'giữahọckì2', 'giữahọckỳ2', 'giữakì2', 'giữakỳ2', 'gkii', 'giữakỳii', 'giữakìii', 'giữahọckỳii', 'giữahọckìii']):
                current_term_context = "Giữa học kì II"
            elif any(kw in header_clean for kw in ['chkii', 'chk2', 'ck2', 'cuốihk2', 'cuốihọckì2', 'cuốihọckỳ2', 'cuốikì2', 'cuốikỳ2', 'hkii', 'hk2', 'cuốinăm', 'cn', 'ckii', 'cuốikỳii', 'cuốikìii', 'cuốihọckỳii', 'cuốihọckìii']):
                current_term_context = "Cuối học kì II"

            is_my_term = (current_term_context == thoi_diem)
            is_other_term = (current_term_context is not None and current_term_context != thoi_diem)

            # 2. KHÓA CHẶT: Bỏ qua hoàn toàn nếu cột này thuộc về kì khác (Không đưa vào list ứng viên)
            if is_other_term:
                continue
            
            # 3. PHÂN LOẠI CỘT CHO KÌ HIỆN TẠI
            is_diem = "điểm" in header_area or "đg" in header_area
            is_muc = "mức" in header_area or "đạt được" in header_area or "đánh giá" in header_area or "kết quả" in header_area
            is_nx = "nhận xét" in header_area or "lời phê" in header_area or "nx" in header_area
            
            # Tránh cột Nhận Xét bị hiểu nhầm thành cột Điểm/Mức
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
            
            if "năng lực" in header_area and ("chung" in header_area or "đặc thù" in header_area) and nl_col == -1: nl_col = j
            if "phẩm chất" in header_area and pc_col == -1: pc_col = j
            
            for r in range(max(0, h_row - 1), s_row):
                cell_val = str(df.iloc[r, j]).strip().lower().replace(" ", "")
                if cell_val in detailed_cands:
                    detailed_cands[cell_val].append(j)
                    
        # --- CHỐT CỘT ĐIỂM/MỨC CHÍNH XÁC ---
        diem_col, muc_col = -1, -1
        
        def get_best_col(cands, check_type):
            if not cands: return -1
            best_col = cands[-1]
            for j in reversed(cands):
                if check_col_has_data(df, j, s_row, check_type): 
                    return j
            return best_col

        if explicit_diem_cands:
            diem_col = get_best_col(explicit_diem_cands, "score")
        elif diem_cands:
            diem_col = get_best_col(diem_cands, "score")
                
        if explicit_muc_cands:
            muc_col = get_best_col(explicit_muc_cands, "level")
        elif muc_cands:
            muc_col = get_best_col(muc_cands, "level")
            
        # Giải quyết xung đột nếu Mức và Điểm cùng trỏ vào 1 cột do từ khóa trùng lặp
        if diem_col == muc_col and diem_col != -1:
            if check_col_has_data(df, diem_col, s_row, "score"):
                muc_col = -1
            else:
                diem_col = -1
                
        detailed_cols = {}
        for k, j_list in detailed_cands.items():
            if j_list:
                chosen_j = j_list[-1]
                for j in reversed(j_list):
                    if check_col_has_data(df, j, s_row, "level"): chosen_j = j; break
                detailed_cols[k] = chosen_j
            
        # Fallback phụ: Nếu file quá "kín" không lộ tiêu đề
        if diem_col == -1 or muc_col == -1:
            if s_row < len(df):
                current_term_context = None
                for j in range(n_col + 1, len(df.columns)):
                    header_area = " ".join([str(df.iloc[r, j]).lower() for r in range(max(0, h_row - 4), s_row)])
                    header_clean = header_area.replace(" ", "").replace("_", "").replace("-", "")
                    
                    if any(kw in header_clean for kw in ['ghk1', 'gk1', 'giữahk1', 'giữahọckì1', 'giữahọckỳ1', 'giữakì1', 'giữakỳ1', 'gki', 'giữakỳi', 'giữakìi', 'giữahọckỳi', 'giữahọckìi']) or ('ghki' in header_clean and 'ghkii' not in header_clean):
                        current_term_context = "Giữa học kì I"
                    elif any(kw in header_clean for kw in ['chk1', 'ck1', 'cuốihk1', 'cuốihọckì1', 'cuốihọckỳ1', 'cuốikì1', 'cuốikỳ1', 'hk1', 'cki', 'cuốikỳi', 'cuốikìi', 'cuốihọckỳi', 'cuốihọckìi']) or ('chki' in header_clean and 'chkii' not in header_clean) or ('hki' in header_clean and 'hkii' not in header_clean):
                        current_term_context = "Cuối học kì I"
                    elif any(kw in header_clean for kw in ['ghkii', 'ghk2', 'gk2', 'giữahk2', 'giữahọckì2', 'giữahọckỳ2', 'giữakì2', 'giữakỳ2', 'gkii', 'giữakỳii', 'giữakìii', 'giữahọckỳii', 'giữahọckìii']):
                        current_term_context = "Giữa học kì II"
                    elif any(kw in header_clean for kw in ['chkii', 'chk2', 'ck2', 'cuốihk2', 'cuốihọckì2', 'cuốihọckỳ2', 'cuốikì2', 'cuốikỳ2', 'hkii', 'hk2', 'cuốinăm', 'cn', 'ckii', 'cuốikỳii', 'cuốikìii', 'cuốihọckỳii', 'cuốihọckìii']):
                        current_term_context = "Cuối học kì II"
                    
                    is_other_term = (current_term_context is not None and current_term_context != thoi_diem)
                    if is_other_term: continue
                    
                    cell_val = str(df.iloc[s_row, j]).strip().upper()
                    if diem_col == -1 and (cell_val.replace('.','',1).isdigit()): diem_col = j
                    elif muc_col == -1 and cell_val in ['T', 'Đ', 'C', 'HTT', 'HT', 'CHT', 'H', 'K']: muc_col = j
                
        # --- ĐỒNG BỘ CỘT NHẬN XÉT VỚI KHỐI DỮ LIỆU ĐƯỢC CHỌN ---
        ref_cols = []
        if diem_col != -1: ref_cols.append(diem_col)
        if muc_col != -1: ref_cols.append(muc_col)
        for val in detailed_cols.values():
            if val != -1: ref_cols.append(val)
        
        ref_max = max(ref_cols) if ref_cols else -1
        
        c_col = -1
        if c_cands:
            valid_c = [c for c in c_cands if c > ref_max]
            if valid_c:
                c_col = valid_c[0]
            else:
                c_col = c_cands[-1]
                
        if c_col == -1: 
            c_col = len(df.columns)
            df[c_col] = ""
            df.iloc[h_row, c_col] = "Nhận xét"
        
        return df, n_col, diem_col, muc_col, c_col, s_row, nl_col, pc_col, detailed_cols
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

if f_hs:
    df_raw, n_col, d_col, m_col, c_col, s_row, nl_col, pc_col, detailed_cols = phan_tich_file(f_hs, thoi_diem)
    
    if df_raw is not None:
        data_list = []
        mapping_indices = []
        
        has_detailed_pcnl = all(k in detailed_cols for k in KEYS_15_PCNL)

        for i in range(s_row, len(df_raw)):
            ten = str(df_raw.iloc[i, n_col]).strip()
            if ten.lower() not in ['nan', 'none', '']:
                if loai_nx == "PC-NL":
                    if has_detailed_pcnl:
                        nl_vals = [str(df_raw.iloc[i, detailed_cols[f"nl{k}"]]).strip().upper() for k in range(1, 11)]
                        pc_vals = [str(df_raw.iloc[i, detailed_cols[f"pc{k}"]]).strip().upper() for k in range(1, 6)]
                        
                        # Không tự động gán 'Đ' nếu trống hoàn toàn, để trống luôn cho chuyên nghiệp
                        if all(v in ['NAN', 'NONE', ''] for v in nl_vals + pc_vals):
                            nl_vals = [''] * 10
                            pc_vals = [''] * 5
                        else:
                            nl_vals = [v if v not in ['NAN', 'NONE', ''] else 'Đ' for v in nl_vals]
                            pc_vals = [v if v not in ['NAN', 'NONE', ''] else 'Đ' for v in pc_vals]
                        
                        row_data = {"Họ và tên": ten}
                        for k in range(1, 11): row_data[f"NL{k}"] = nl_vals[k-1]
                        for k in range(1, 6): row_data[f"PC{k}"] = pc_vals[k-1]
                        row_data["Nhận xét"] = ""
                        data_list.append(row_data)
                    else:
                        nl_v = str(df_raw.iloc[i, nl_col]).strip().upper() if nl_col != -1 else ""
                        pc_v = str(df_raw.iloc[i, pc_col]).strip().upper() if pc_col != -1 else ""
                        if nl_v in ['NAN', 'NONE']: nl_v = ""
                        if pc_v in ['NAN', 'NONE']: pc_v = ""
                        data_list.append({"Họ và tên": ten, "Năng lực": nl_v, "Phẩm chất": pc_v, "Nhận xét": ""})
                else:
                    v_diem = str(df_raw.iloc[i, d_col]).strip() if d_col != -1 else ""
                    v_muc = str(df_raw.iloc[i, m_col]).strip().upper() if m_col != -1 else ""
                    if v_diem.upper() in ['NAN', 'NONE']: v_diem = ""
                    if v_muc.upper() in ['NAN', 'NONE']: v_muc = ""
                    data_list.append({"Họ và tên": ten, "Điểm": v_diem, "Mức": v_muc, "Nhận xét": ""})
                mapping_indices.append(i)
        
        if not data_list:
            if loai_nx == "PC-NL":
                if has_detailed_pcnl:
                    cols = ["Họ và tên"] + [f"NL{i}" for i in range(1,11)] + [f"PC{i}" for i in range(1,6)] + ["Nhận xét"]
                    df_view = pd.DataFrame(columns=cols)
                else:
                    df_view = pd.DataFrame(columns=["Họ và tên", "Năng lực", "Phẩm chất", "Nhận xét"])
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
            if has_detailed_pcnl:
                config.update({
                    "NL1": st.column_config.Column("T.Học", width="small"),
                    "NL2": st.column_config.Column("G.Tiếp", width="small"),
                    "NL3": st.column_config.Column("GQVĐ", width="small"),
                    "NL4": st.column_config.Column("N.Ngữ", width="small"),
                    "NL5": st.column_config.Column("Toán", width="small"),
                    "NL6": st.column_config.Column("K.Học", width="small"),
                    "NL7": st.column_config.Column("C.Nghệ", width="small"),
                    "NL8": st.column_config.Column("Tin", width="small"),
                    "NL9": st.column_config.Column("T.Mỹ", width="small"),
                    "NL10": st.column_config.Column("T.Chất", width="small"),
                    "PC1": st.column_config.Column("Y.Nước", width="small"),
                    "PC2": st.column_config.Column("N.Ái", width="small"),
                    "PC3": st.column_config.Column("C.Chỉ", width="small"),
                    "PC4": st.column_config.Column("T.Thực", width="small"),
                    "PC5": st.column_config.Column("T.Nhiệm", width="small")
                })
            else:
                config["Năng lực"] = st.column_config.Column(width="small")
                config["Phẩm chất"] = st.column_config.Column(width="small")
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

                # KIỂM TRA HỌC SINH CÓ DỮ LIỆU ĐỂ NHẬN XÉT KHÔNG
                is_empty_row = False
                
                if loai_nx == "PC-NL":
                    if has_detailed_pcnl:
                        raw_nls = [str(row.get(f"NL{k}", "")).strip() for k in range(1, 11)]
                        raw_pcs = [str(row.get(f"PC{k}", "")).strip() for k in range(1, 6)]
                        if all(v == "" for v in raw_nls + raw_pcs): is_empty_row = True
                    else:
                        raw_nl = str(row.get("Năng lực", "")).strip()
                        raw_pc = str(row.get("Phẩm chất", "")).strip()
                        if raw_nl == "" and raw_pc == "": is_empty_row = True
                else:
                    d_val = str(row.get("Điểm", "")).strip()
                    m_val = str(row.get("Mức", "")).strip()
                    if d_val == "" and m_val == "": is_empty_row = True

                # Nếu học sinh chưa được nhập điểm -> Để trống nhận xét
                if is_empty_row:
                    nx_text = ""
                else:
                    # Nếu có dữ liệu thì tiến hành sinh nhận xét
                    d_val = str(row.get("Điểm", "")).strip()
                    m_val = str(row.get("Mức", "")).strip()
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
                        chk_val = chk_val.upper()
                        if chk_val in ["T", "HTT", "TỐT", "A", "A+"]: mdd = "T"
                        elif chk_val in ["K", "KHÁ", "B", "B+"]: mdd = "H_Kha"
                        elif chk_val in ["Đ", "HT", "ĐẠT"]: mdd = "H_TrungBinh"
                        elif chk_val in ["C", "CHT", "CHƯA ĐẠT", "D", "E"]: mdd = "C"

                    if loai_nx == "PC-NL":
                        if has_detailed_pcnl:
                            nl_str_detail = f"Tự học:{row.get('NL1', 'Đ')}, G.Tiếp:{row.get('NL2', 'Đ')}, GQVĐ:{row.get('NL3', 'Đ')}, N.Ngữ:{row.get('NL4', 'Đ')}, Toán:{row.get('NL5', 'Đ')}, KH:{row.get('NL6', 'Đ')}, CN:{row.get('NL7', 'Đ')}, Tin:{row.get('NL8', 'Đ')}, T.Mỹ:{row.get('NL9', 'Đ')}, T.Chất:{row.get('NL10', 'Đ')}"
                            pc_str_detail = f"Yêu nước:{row.get('PC1', 'Đ')}, Nhân ái:{row.get('PC2', 'Đ')}, Chăm chỉ:{row.get('PC3', 'Đ')}, Trung thực:{row.get('PC4', 'Đ')}, Trách nhiệm:{row.get('PC5', 'Đ')}"
                            
                            if api_key:
                                try:
                                    prompt = f"Mã:{salt}. Đóng vai chuyên gia giáo dục. Nhận xét theo TT27 thời điểm {thoi_diem}. Chi tiết: {nl_str_detail}. {pc_str_detail}. YÊU CẦU PHONG CÁCH: {style_prompt}. BẮT BUỘC NHẬN XÉT ĐỦ 3 PHẦN THEO THỨ TỰ: 1. Năng lực đặc thù -> 2. Năng lực chung -> 3. Phẩm chất. {lenh_xung_ho} {lenh_cam_cam_xuc} Nếu có C bắt buộc bắt đầu 'Chưa hoàn thành...'. Khen điểm T (Tốt), nhắc nhở khắc phục điểm C (Cần cố gắng).\n{lenh_do_dai}\n{lenh_chong_lap}\nLưu ý: Viết thành một đoạn văn trôi chảy, không gạch đầu dòng."
                                    res = model.generate_content(prompt); nx_text = res.text.strip()
                                except: nx_text = ""
                            if not nx_text:
                                nx_text = sinh_nhan_xet_offline("PC-NL", mdd, "", style_key, xung_ho, bat_xung_ho, mon, thoi_diem)
                        else:
                            nl_s = str(row.get("Năng lực", "Đ")).upper()
                            pc_s = str(row.get("Phẩm chất", "Đ")).upper()
                            
                            if api_key:
                                try:
                                    prompt = f"Mã:{salt}. Đóng vai giáo viên/chuyên gia. Viết 1 nhận xét học bạ Năng lực({nl_s}) và Phẩm chất({pc_s}) theo TT27 vào {thoi_diem}.\nPHONG CÁCH: {style_prompt}.\nBẮT BUỘC 3 PHẦN: Đặc thù -> Chung -> Phẩm chất.\n{lenh_xung_ho}\n{lenh_cam_cam_xuc}\nNếu có C bắt buộc bắt đầu 'Chưa hoàn thành...'.\n{lenh_do_dai}\n{lenh_chong_lap}\nLưu ý: Viết thành đoạn văn trôi chảy."
                                    res = model.generate_content(prompt); nx_text = res.text.strip()
                                except: nx_text = ""
                                
                            if not nx_text:
                                nx_text = sinh_nhan_xet_offline("PC-NL", mdd, "", style_key, xung_ho, bat_xung_ho, mon, thoi_diem)
                    else:
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
                time.sleep(1.5 if api_key else 0.01)

            st.balloons()
            status.success(f"✅ Hoàn thành xuất sắc bộ học bạ môn {mon}!")
            
            if st.session_state.ket_qua_nhan_xet:
                st.markdown("### 📋 KẾT QUẢ COPY NHANH (DÁN TRỰC TIẾP VÀO EXCEL)")
                copy_text = "\n".join(st.session_state.ket_qua_nhan_xet)
                st.text_area("Bấm chuột vào khung dưới đây, ấn Ctrl+A để chọn tất cả, rồi ấn Ctrl+C để Copy:", value=copy_text, height=350)
                st.warning("🚨 **LỖI DÁN 1 DÒNG DÀI NGOẰNG VÀ CÁCH KHẮC PHỤC:**\nNguyên nhân là do thầy/cô đã click đúp (nhấn chuột 2 lần) vào ô Excel khiến con trỏ nhấp nháy bên trong ô.\n\n👉 **CÁCH LÀM ĐÚNG:** Chỉ **CLICK CHUỘT 1 LẦN DUY NHẤT** vào ô đầu tiên (sao cho ô đó hiện viền màu xanh, TUYỆT ĐỐI KHÔNG có con trỏ nháy nháy bên trong). Sau đó ấn **Ctrl + V**, Excel sẽ tự động rải đều mỗi em 1 dòng!")

            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as writer:
                df_raw.to_excel(writer, index=False, header=False)
            st.download_button("📥 Tải file kết quả dự phòng", data=out.getvalue(), file_name=f"SDGHS_ThinhDam.xlsx")
