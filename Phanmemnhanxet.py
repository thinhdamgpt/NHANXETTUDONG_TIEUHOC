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

# --- 1. MA TRẬN PHÂN PHỐI CHƯƠNG TRÌNH KNTT ĐƯỢC CHIA CHI TIẾT THEO TUẦN & KỲ HỌC ---
import sys
from pathlib import Path
_curr_dir = str(Path(__file__).resolve().parent)
if _curr_dir not in sys.path:
    sys.path.insert(0, _curr_dir)

from curriculum_matrix import PHAN_PHOI_CHUONG_TRINH, TUAN_THEO_THOI_DIEM

def lay_mach_kien_thuc(mon, khoi, thoi_diem):
    mon_key = mon
    if mon in ["Tự nhiên và xã hội", "TNXH"]:
        mon_key = "Khoa học"
    elif "Lịch sử" in mon or "Địa l" in mon:
        mon_key = "Lịch sử & Địa lý"
        
    kho_mon = PHAN_PHOI_CHUONG_TRINH.get(mon_key, {})
    if khoi in kho_mon: 
        if isinstance(kho_mon[khoi], dict):
            return kho_mon[khoi].get(thoi_diem, ["kiến thức trọng tâm", "kỹ năng thực hành"])
        return kho_mon[khoi]
    if "Chung" in kho_mon: 
        if isinstance(kho_mon["Chung"], dict):
            return kho_mon["Chung"].get(thoi_diem, ["kiến thức trọng tâm", "kỹ năng thực hành"])
        return kho_mon["Chung"]
    return ["kiến thức cơ bản", "kỹ năng thực hành"]

# --- HỆ THỐNG XỬ LÝ ĐIỂM SỐ & SINH NHẬN XÉT OFFLINE TỰ NHIÊN (CHUẨN THÔNG TƯ 27) ---
import math

def lam_tron_diem(val):
    try:
        val_str = str(val).strip().replace(',', '.')
        if val_str and val_str.replace('.', '', 1).isdigit():
            d = float(val_str)
            # Theo TT27: phần thập phân >= 0.5 làm tròn lên 1, < 0.5 làm tròn xuống
            d_rounded = int(math.floor(d + 0.5))
            return str(max(1, min(10, d_rounded)))
    except:
        pass
    return str(val).strip()

def get_mdd(val, is_pcnl=False):
    val = str(val).strip().upper()
    # Tốt / Hoàn thành tốt
    if val in ["T", "HTT", "TỐT", "A", "A+"]:
        return "T"
    # Hoàn thành (H đối với môn học) / Đạt (Đ đối với PC-NL). TUYỆT ĐỐI không dùng Khá hay Trung bình.
    elif val in ["Đ", "HT", "ĐẠT", "H", "K", "KHÁ", "B", "B+"]:
        return "Đ" if is_pcnl else "H"
    # Chưa hoàn thành (C đối với môn học) / Cần cố gắng (C đối với PC-NL)
    elif val in ["C", "CHT", "CHƯA ĐẠT", "CHƯA HOÀN THÀNH", "CẦN CỐ GẮNG", "CCG", "D", "E"]:
        return "C"
    return "Đ" if is_pcnl else "H"

def calc_overall_mdd(vals):
    valid_vals = [str(v).strip().upper() for v in vals if str(v).strip() != '']
    if not valid_vals: return "Đ"
    mapped = [get_mdd(v, is_pcnl=True) for v in valid_vals]
    if "C" in mapped: return "C"
    if all(v == "T" for v in mapped): return "T"
    return "Đ"

def sinh_nhan_xet_pcnl_offline(mdd_nlc, mdd_nldt, mdd_pc, student_idx=None):
    def cap_first(s):
        if not s: return ""
        s = s.strip()
        return s[0].upper() + s[1:]
        
    # Chuẩn Thông tư 27: Chỉ có 3 mức T (Tốt), Đ (Đạt), C (Cần cố gắng).
    # TUYỆT ĐỐI CẤM các từ: khá, giỏi, trung bình, yếu, kém.
    nlc_kho = {
        "T": [
            "tự chủ trong học tập và giao tiếp rất tốt",
            "ý thức tự giác cao, luôn chủ động chuẩn bị bài và đồ dùng học tập chu đáo",
            "giao tiếp tự tin, diễn đạt rõ ràng, biết lắng nghe và tôn trọng ý kiến bạn bè",
            "hợp tác nhóm tích cực, có kỹ năng chia sẻ và phối hợp cùng bạn rất hiệu quả",
            "có tinh thần tự học tốt, biết tìm tòi tài liệu và hoàn thành nhiệm vụ nhanh nhẹn",
            "xử lý tình huống linh hoạt, tư duy giải quyết vấn đề sáng tạo và nhạy bén",
            "chủ động trong mọi hoạt động học tập, tích cực tương tác và xây dựng bài",
            "tự giác hoàn thành tốt nhiệm vụ học tập, biết tự kiểm tra và chỉnh sửa bài làm",
            "biết cách lập kế hoạch học tập cá nhân và thực hiện rất nghiêm túc",
            "tự tin bày tỏ chính kiến, có kỹ năng hợp tác và điều hành nhóm tốt",
            "tiếp thu nhạy bén các kỹ năng chung, luôn năng nổ trong các hoạt động lớp",
            "kỹ năng làm việc nhóm xuất sắc, luôn đoàn kết và hỗ trợ bạn bè cùng tiến bộ"
        ],
        "Đ": [
            "giao tiếp và tự học đạt yêu cầu của lứa tuổi",
            "có ý thức tự giác học tập và hoàn thành các nhiệm vụ được giao",
            "biết hợp tác với bạn bè khi làm việc nhóm, chuẩn bị bài tương đối đầy đủ",
            "giao tiếp rõ ràng, biết lắng nghe thầy cô và trao đổi ý kiến cùng bạn",
            "thực hiện đạt chuẩn các nhiệm vụ tự học và giải quyết vấn đề",
            "có tinh thần học hỏi, tích cực tham gia các hoạt động tập thể",
            "biết lắng nghe góp ý từ thầy cô, bạn bè và có ý thức sửa sai",
            "hoàn thành nhiệm vụ học tập theo hướng dẫn của giáo viên",
            "chăm chú lắng nghe bài giảng và chấp hành tốt các quy định chung",
            "biết phối hợp cùng các bạn trong nhóm để hoàn thành bài tập",
            "có cố gắng trong học tập, giao tiếp thân thiện và hòa đồng với bạn bè",
            "biết tự quản lý đồ dùng học tập và thời gian cá nhân tương đối tốt"
        ],
        "C": [
            "cần chủ động và tự giác hơn trong học tập cũng như giao tiếp",
            "cần mạnh dạn trao đổi và tự tin chia sẻ ý kiến trước lớp",
            "cần rèn luyện thêm kỹ năng tự học và tập trung hơn trong giờ học",
            "còn rụt rè khi tham gia các hoạt động nhóm, cần mở lòng hơn với bạn",
            "cần nâng cao ý thức tự giác chuẩn bị sách vở và đồ dùng học tập",
            "kỹ năng giải quyết vấn đề còn chậm, cần chủ động nhờ thầy cô hỗ trợ",
            "cần tập trung lắng nghe hướng dẫn để hoàn thành bài đúng thời gian",
            "cần tích cực tương tác hơn với bạn bè trong các hoạt động tập thể",
            "cần rèn luyện thêm thói quen tự giác và tính chủ động khi học tập"
        ]
    }
    nldt_kho = {
        "T": [
            "năng lực đặc thù môn học rất nổi trội, tiếp thu bài nhanh và vận dụng sáng tạo",
            "khả năng ngôn ngữ phong phú, diễn đạt lưu loát và cảm thụ bài học rất tốt",
            "tư duy tính toán nhanh nhẹn, suy luận logic và giải quyết bài tập chính xác",
            "kỹ năng thực hành bộ môn rất thành thạo, phát huy tốt năng khiếu thẩm mĩ và vận động",
            "thao tác thực hành máy tính và dụng cụ học tập khéo léo, an toàn và chuẩn xác",
            "tiếp thu bài rất nhanh nhạy, biết liên hệ kiến thức bộ môn vào thực tế đời sống",
            "phát huy xuất sắc năng lực bộ môn, luôn có những ý tưởng thực hành độc đáo",
            "thể hiện năng khiếu nổi bật ở các môn học và hoạt động giáo dục",
            "vận dụng linh hoạt các phương pháp học tập để đạt kết quả xuất sắc",
            "quan sát tinh tế, tư duy khoa học và giải thích hiện tượng rất tự nhiên, mạch lạc",
            "sản phẩm thực hành bộ môn chỉn chu, giàu tính thẩm mĩ và sáng tạo",
            "có tố chất nổi bật về khả năng phân tích và tổng hợp kiến thức chuyên môn"
        ],
        "Đ": [
            "nắm được kiến thức đặc thù các môn học và hoàn thành bài tập đạt yêu cầu",
            "diễn đạt câu từ tương đối rõ ràng, biết áp dụng quy tắc vào giải bài tập",
            "thực hiện được các kỹ năng tính toán và thực hành cơ bản của bộ môn",
            "có cố gắng trong học tập, hoàn thành các sản phẩm thực hành đúng tiến độ",
            "thao tác sử dụng dụng cụ học tập và thiết bị cơ bản đúng quy trình",
            "biết vận dụng kiến thức bài học để giải quyết các bài tập trong sách giáo khoa",
            "tiếp thu bài đạt chuẩn, có sự tiến bộ trong kỹ năng thực hành môn học",
            "thực hiện đúng yêu cầu các bài tập và nhiệm vụ thực hành trên lớp",
            "kỹ năng đọc, viết và tính toán đáp ứng tốt yêu cầu chương trình",
            "biết liên hệ kiến thức môn học vào một số tình huống quen thuộc",
            "có ý thức rèn luyện kỹ năng thực hành bộ môn theo hướng dẫn",
            "hoàn thành các bài tập ứng dụng ở mức độ cơ bản"
        ],
        "C": [
            "cần nỗ lực hơn để nắm chắc kiến thức và rèn luyện kỹ năng thực hành bộ môn",
            "khả năng diễn đạt và trình bày bài còn hạn chế, cần rèn luyện thêm mỗi ngày",
            "thao tác thực hành và giải bài còn chậm, cần được giáo viên hỗ trợ thêm",
            "cần chú ý nghe giảng và ôn luyện nhiều hơn để theo kịp tiến độ bộ môn",
            "kỹ năng tính toán hoặc thực hành còn lúng túng, cần chăm chỉ rèn luyện",
            "chưa nắm vững kiến thức trọng tâm, cần dành thêm thời gian ôn tập",
            "cần cẩn thận hơn khi làm bài và rèn luyện thêm kỹ năng bộ môn",
            "mức độ tiếp thu còn chậm, cần tích cực hỏi thầy cô khi chưa hiểu bài"
        ]
    }
    pc_kho = {
        "T": [
            "chăm chỉ, trung thực, lễ phép với thầy cô và luôn đoàn kết, yêu thương bạn bè",
            "ý thức tổ chức kỷ luật rất cao, gương mẫu thực hiện tốt nội quy, giàu lòng nhân ái",
            "luôn có tinh thần trách nhiệm với công việc chung, tích cực giúp đỡ bạn cùng tiến bộ",
            "thật thà, khiêm tốn, biết giữ gìn của công và bảo vệ môi trường lớp học sạch đẹp",
            "kính trọng thầy cô, thân thiện với bạn bè, là tấm gương sáng về nền nếp của lớp",
            "chuyên cần trong học tập, dũng cảm nhận lỗi và có tinh thần tự giác rất cao",
            "giàu lòng nhân ái, nhiệt tình tham gia các phong trào thi đua và hoạt động tập thể",
            "có lòng yêu quê hương, đất nước, luôn tự hào về truyền thống dân tộc",
            "biết quan tâm, chia sẻ và luôn sẵn sàng hỗ trợ các bạn gặp khó khăn",
            "trách nhiệm cao trong các buổi trực nhật và giữ gìn nề nếp lớp học",
            "lời nói và hành động luôn chuẩn mực, được thầy cô và bạn bè quý mến",
            "luôn nêu cao tinh thần trung thực trong học tập và đời sống hàng ngày"
        ],
        "Đ": [
            "chăm chỉ đi học chuyên cần, ngoan ngoãn và lễ phép với thầy cô giáo",
            "trung thực trong học tập, hòa đồng và thân thiện với bạn bè trong lớp",
            "có ý thức chấp hành tốt nội quy trường lớp và các quy định chung",
            "có tinh thần trách nhiệm với các nhiệm vụ vệ sinh, trực nhật được phân công",
            "biết vâng lời thầy cô, biết chia sẻ và giúp đỡ bạn khi gặp khó khăn",
            "thật thà, ngoan ngoãn, có ý thức giữ gìn sách vở và đồ dùng cá nhân cẩn thận",
            "thực hiện đầy đủ nhiệm vụ của người học sinh, có thái độ học tập nghiêm túc",
            "biết chào hỏi lễ phép, tôn trọng người lớn tuổi và thân ái với bạn bè",
            "có tinh thần tập thể, tham gia đầy đủ các phong trào của lớp và trường",
            "biết nhận lỗi khi làm sai và có ý thức sửa chữa khuyết điểm",
            "có ý thức bảo vệ của công và giữ gìn vệ sinh môi trường học tập",
            "luôn cư xử đúng mực, chan hòa với tất cả các bạn trong lớp"
        ],
        "C": [
            "cần nâng cao hơn nữa ý thức kỷ luật, tự giác chấp hành đúng nội quy lớp học",
            "cần chăm chỉ, tập trung nghe giảng hơn và hạn chế nói chuyện riêng trong giờ học",
            "cần nghiêm túc hơn trong việc thực hiện các nhiệm vụ trực nhật và bảo vệ của công",
            "cần hòa đồng, cởi mở hơn với bạn bè và mạnh dạn nhận khuyết điểm để sửa chữa",
            "cần rèn luyện tính trung thực và tinh thần trách nhiệm trong học tập cũng như sinh hoạt",
            "cần lễ phép hơn khi giao tiếp với thầy cô và người lớn tuổi",
            "cần có ý thức giữ gìn sách vở, đồ dùng học tập và vệ sinh chung của lớp",
            "cần kiên trì, chăm chỉ hơn để hoàn thành tốt các nhiệm vụ được giao"
        ]
    }
    
    khuyen_nlc = {
        "T": ["Rất đáng khen ngợi.", "Hãy tiếp tục phát huy năng lực này nhé.", "Luôn giữ vững tinh thần tự giác này.", "Kỹ năng rất xuất sắc.", "Là nhân tố tích cực của lớp."],
        "Đ": ["Cần tiếp tục cố gắng phát huy.", "Hãy chủ động hơn nữa nhé.", "Duy trì tinh thần học tập này nhé.", "Cố gắng tự tin hơn chút nữa là rất tốt.", "Thầy/Cô ghi nhận sự tiến bộ của em."],
        "C": ["Cần mạnh dạn và cởi mở hơn.", "Chú ý rèn luyện thêm mỗi ngày.", "Cố gắng tự tin hơn nhé.", "Cần nỗ lực hơn nữa để tiến bộ.", "Hãy tích cực học hỏi từ bạn bè."]
    }
    khuyen_nldt = {
        "T": ["Kết quả rèn luyện rất xứng đáng.", "Tuyệt vời, tiếp tục phát huy nhé!", "Năng lực bộ môn rất đáng tự hào.", "Thầy/Cô rất khen ngợi em.", "Hãy lan tỏa niềm đam mê này đến các bạn."],
        "Đ": ["Tiếp tục nỗ lực để đạt kết quả cao hơn.", "Cố gắng duy trì phong độ này nhé.", "Hãy chăm chỉ rèn luyện hơn nữa nhé.", "Chỉ cần chú ý hơn một chút là rất tốt.", "Sự cố gắng của em rất đáng khích lệ."],
        "C": ["Cần nỗ lực nhiều hơn để khắc phục.", "Cần chú ý ôn tập thêm tại nhà.", "Hãy kiên trì rèn luyện mỗi ngày.", "Thầy/Cô tin em sẽ tiến bộ hơn nếu chăm chỉ.", "Cần chủ động trao đổi khi gặp bài khó."]
    }
    khuyen_pc = {
        "T": ["Là tấm gương sáng cho cả lớp noi theo.", "Rất đáng tự hào.", "Thầy/Cô rất khen ngợi em.", "Hãy luôn giữ gìn nét đẹp này nhé.", "Xứng đáng là con ngoan trò giỏi."],
        "Đ": ["Cần duy trì thái độ tích cực này.", "Ý thức rèn luyện rất tốt.", "Hãy tiếp tục chăm ngoan nhé.", "Biết vâng lời và phát huy hơn nữa nhé.", "Thầy/Cô rất quý mến em."],
        "C": ["Cần nghiêm túc tuân thủ nội quy trường lớp.", "Cần chú ý sửa đổi để tiến bộ hơn.", "Cố gắng rèn luyện nền nếp mỗi ngày nhé.", "Hãy biết lắng nghe lời khuyên bảo của thầy cô.", "Cần nỗ lực thay đổi để trở thành học sinh ngoan."]
    }
    
    m_nlc_key = "T" if mdd_nlc == "T" else ("C" if mdd_nlc == "C" else "Đ")
    m_nldt_key = "T" if mdd_nldt == "T" else ("C" if mdd_nldt == "C" else "Đ")
    m_pc_key = "T" if mdd_pc == "T" else ("C" if mdd_pc == "C" else "Đ")
    
    if student_idx is not None:
        idx_nlc = student_idx % len(nlc_kho[m_nlc_key])
        idx_nldt = (student_idx + 3) % len(nldt_kho[m_nldt_key])
        idx_pc = (student_idx + 7) % len(pc_kho[m_pc_key])
        
        k_idx_nlc = student_idx % len(khuyen_nlc[m_nlc_key])
        k_idx_nldt = (student_idx + 2) % len(khuyen_nldt[m_nldt_key])
        k_idx_pc = (student_idx + 4) % len(khuyen_pc[m_pc_key])
        
        nx_nlc = f"{cap_first(nlc_kho[m_nlc_key][idx_nlc])}. {khuyen_nlc[m_nlc_key][k_idx_nlc]}"
        nx_nldt = f"{cap_first(nldt_kho[m_nldt_key][idx_nldt])}. {khuyen_nldt[m_nldt_key][k_idx_nldt]}"
        nx_pc = f"{cap_first(pc_kho[m_pc_key][idx_pc])}. {khuyen_pc[m_pc_key][k_idx_pc]}"
    else:
        nx_nlc = f"{cap_first(random.choice(nlc_kho[m_nlc_key]))}. {random.choice(khuyen_nlc[m_nlc_key])}"
        nx_nldt = f"{cap_first(random.choice(nldt_kho[m_nldt_key]))}. {random.choice(khuyen_nldt[m_nldt_key])}"
        nx_pc = f"{cap_first(random.choice(pc_kho[m_pc_key]))}. {random.choice(khuyen_pc[m_pc_key])}"
            
    return nx_nlc, nx_nldt, nx_pc

def sinh_nhan_xet_offline(loai_nx, mdd, focus_kt, phong_cach="Ngắn gọn", xung_ho="Thầy", bat_xung_ho=True, mon="", thoi_diem=""):
    xh = f"{xung_ho} " if bat_xung_ho else ""
    is_cuoi_nam = thoi_diem == "Cuối học kì II"
    
    def cap_first(s):
        if not s: return s
        s = s.strip()
        return s[0].upper() + s[1:] if s else ""

    # Chuẩn hóa mức đánh giá chuẩn TT27: T (Tốt), H (Hoàn thành - với môn học) / Đ (Đạt - với PC-NL, HĐGD), C (Chưa hoàn thành / Cần cố gắng)
    if mdd in ["T", "HTT", "TỐT"]:
        mdd_clean = "T"
    elif mdd in ["C", "CHT", "CHƯA ĐẠT", "CHƯA HOÀN THÀNH", "CẦN CỐ GẮNG"]:
        mdd_clean = "C"
    else:
        mdd_clean = "Đ" if loai_nx in ["PC-NL", "HĐGD"] else "H"

    if loai_nx == "HĐGD":
        hdgd_thamgia = {
            "T": ["Tích cực tham gia các phong trào", "Nhiệt tình và năng nổ trong hoạt động trải nghiệm", "Luôn đi đầu trong các hoạt động chung", "Có ý thức tổ chức kỷ luật rất cao", "Hăng hái tham gia mọi hoạt động giáo dục"],
            "Đ": ["Tham gia đầy đủ các hoạt động giáo dục", "Nhiệt tình với các phong trào của lớp", "Có nề nếp tốt trong giờ trải nghiệm", "Hòa đồng và tham gia tích cực cùng tập thể", "Ý thức tham gia sinh hoạt tập thể nghiêm túc"],
            "C": ["Chưa hoàn thành nội dung trải nghiệm", "Thái độ tham gia cần nghiêm túc hơn", "Ít tham gia các phong trào của trường lớp", "Cần tập trung hơn trong giờ sinh hoạt chung", "Chưa chủ động tham gia hoạt động giáo dục"]
        }
        hdgd_kynang = {
            "T": ["thể hiện kỹ năng sống rất tốt", "năng lực tổ chức và làm việc nhóm xuất sắc", "tính sáng tạo và linh hoạt rất cao", "khả năng kết nối bạn bè tốt", "xử lý tình huống trải nghiệm rất thông minh"],
            "Đ": ["kỹ năng hợp tác nhóm đạt yêu cầu", "biết cách hòa nhập và chia sẻ với bạn bè", "thực hiện tốt các kỹ năng thực tế", "có sự cố gắng trong giao tiếp", "hoàn thành các kỹ năng sống cơ bản"],
            "C": ["kỹ năng giao tiếp và làm việc nhóm cần rèn luyện thêm", "cần mạnh dạn và tự tin hơn nữa", "còn rụt rè khi xử lý các tình huống", "tính chủ động trong hoạt động chưa cao", "cần rèn luyện thêm kỹ năng sống"]
        }
        hdgd_khuyen = {
            "T": ["Là nhân tố tích cực của lớp.", "Cần tiếp tục giữ vững tinh thần này!", "Thầy/Cô rất tự hào về sự năng nổ của em.", "Hãy lan tỏa năng lượng này cho các bạn.", "Kỹ năng hoạt động rất đáng khen ngợi."],
            "Đ": ["Cần chủ động và tự tin phát biểu hơn.", "Tiếp tục phát huy sự nhiệt tình này nhé.", "Hãy mạnh dạn dẫn dắt nhóm trong tương lai.", "Chỉ cần tự tin hơn chút là rất tốt.", "Sự cố gắng của em rất đáng khen."],
            "C": ["Cần tham gia phong trào tích cực hơn để rèn kỹ năng.", "Yêu cầu em nghiêm túc và chủ động hơn.", "Cần thay đổi thái độ khi sinh hoạt tập thể.", "Hãy mở lòng và hòa đồng cùng các bạn.", "Cần rèn luyện tính kỷ luật và sự tự giác."]
        }
        k_hdgd = mdd_clean if mdd_clean in hdgd_thamgia else "Đ"
        tg = random.choice(hdgd_thamgia[k_hdgd])
        kn = random.choice(hdgd_kynang[k_hdgd])
        kh = random.choice(hdgd_khuyen[k_hdgd]).replace("Thầy/Cô", xh.strip() if xh else "Giáo viên")

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
            mo_T = [
                "Tổng kết năm học, em hoàn thành xuất sắc nội dung",
                "Xuyên suốt cả năm học, em nắm rất chắc kiến thức về",
                "Đạt kết quả cuối năm nổi trội ở nội dung",
                "Tiếp thu bài rất nhanh và vận dụng linh hoạt bài học về",
                "Hoàn thành xuất sắc mục tiêu năm học đối với"
            ]
            mo_H = [
                "Tổng kết năm học, em hoàn thành tốt nội dung",
                "Nắm được kiến thức cơ bản của chương trình về",
                "Đạt mức hoàn thành chuẩn kiến thức đối với",
                "Hoàn thành các yêu cầu của năm học về",
                "Nắm được kiến thức trọng tâm và biết vận dụng bài học về"
            ]
            mo_C = [
                "Tổng kết năm học, em chưa hoàn thành tốt nội dung",
                "Còn chưa nắm vững kiến thức, cần rèn luyện thêm về",
                "Chưa đạt yêu cầu chuẩn kiến thức kỹ năng về",
                "Mức độ tiếp thu còn chậm, cần được hỗ trợ thêm về",
                "Cần nỗ lực ôn tập lại để nắm chắc kiến thức về"
            ]
        else:
            mo_T = [
                "Nắm rất chắc kiến thức và hoàn thành xuất sắc bài học về",
                "Tiếp thu bài rất nhanh, thực hiện thành thạo nội dung",
                "Thể hiện năng lực nổi bật khi học về",
                "Hoàn thành xuất sắc yêu cầu bài học về",
                "Hiểu bài sâu sắc và vận dụng rất linh hoạt kiến thức về"
            ]
            mo_H = [
                "Nắm được kiến thức trọng tâm về",
                "Thực hiện đạt yêu cầu bài học về",
                "Hiểu bài và biết vận dụng nội dung",
                "Có sự tiến bộ khi thực hành bài học về",
                "Hoàn thành các nhiệm vụ học tập về"
            ]
            mo_C = [
                "Chưa hoàn thành yêu cầu bài học về",
                "Còn lúng túng và cần rèn luyện thêm ở nội dung",
                "Chưa nắm chắc kiến thức trọng tâm về",
                "Mức độ tiếp thu còn chậm khi học về",
                "Cần cố gắng nhiều hơn và chú ý ôn tập phần"
            ]

        # Kỹ năng đặc thù từng môn: TUYỆT ĐỐI KHÔNG dùng giỏi, khá, trung bình, yếu, kém
        kynang_mon = {
            "Tiếng Việt": {
                "T": ["đọc diễn cảm và lưu loát, chữ viết nắn nót, vốn từ phong phú", "viết câu đúng ngữ pháp, giàu hình ảnh, cảm thụ bài đọc rất sâu sắc", "kỹ năng đọc hiểu xuất sắc, tư duy ngôn ngữ tốt, trình bày bài sạch đẹp", "diễn đạt trôi chảy, nói và nghe tự tin trước tập thể"],
                "H": ["đọc to, rõ ràng, chữ viết cẩn thận", "biết cách đặt câu đúng cấu trúc, dùng từ phù hợp", "hiểu nội dung bài đọc, nghe viết chính tả đạt yêu cầu", "trình bày bài sạch sẽ, diễn đạt gãy gọn"],
                "C": ["đọc còn chậm, còn phải đánh vần nhiều", "chữ viết cần rèn nắn nót hơn, còn mắc lỗi chính tả", "kỹ năng đọc hiểu cần cố gắng hơn, diễn đạt câu cần trau chuốt"]
            },
            "Toán": {
                "T": ["tính toán nhanh nhẹn, độ chính xác cao, tư duy logic nhạy bén", "giải bài toán có lời văn rất xuất sắc, trình bày bài giải khoa học", "nắm rất chắc các công thức và quy tắc tính toán", "vận dụng linh hoạt kiến thức toán học vào bài tập thực tế"],
                "H": ["thực hiện phép tính cẩn thận, nắm được các bước giải toán", "trình bày bài sạch sẽ, khoa học, thực hiện đúng các phép tính", "áp dụng được công thức và quy tắc tính toán vào bài tập"],
                "C": ["kỹ năng tính toán còn lúng túng, cần cẩn thận hơn khi làm bài", "cần rèn luyện thêm các bước tóm tắt và giải bài toán có lời văn", "thao tác giải bài còn chậm, cần chú ý nghe giảng"]
            },
            "Tiếng Anh": {
                "T": ["phát âm chuẩn xác, phản xạ giao tiếp trôi chảy, tự tin", "ghi nhớ tốt từ vựng và vận dụng linh hoạt các mẫu câu giao tiếp", "kỹ năng nghe hiểu và đọc hiểu tiếng Anh xuất sắc"],
                "H": ["ghi nhớ được từ vựng cơ bản, phát âm tương đối rõ ràng", "vận dụng được mẫu câu vào giao tiếp ngắn đạt yêu cầu", "kỹ năng nghe và đọc hiểu đạt mức chuẩn"],
                "C": ["phát âm chưa chuẩn, cần mạnh dạn hơn khi luyện nói", "cần dành thời gian ôn lại từ vựng và mẫu câu cơ bản"]
            },
            "Khoa học": {
                "T": ["quan sát tỉ mỉ, hiểu sâu sắc bản chất sự vật hiện tượng, biết liên hệ thực tế tốt", "có ý thức cao trong việc bảo vệ môi trường và chăm sóc sức khỏe", "tư duy tìm tòi khoa học nhạy bén, trình bày ý kiến rõ ràng"],
                "H": ["nắm được các kiến thức khoa học cơ bản, biết cách quan sát và giải thích hiện tượng", "có ý thức giữ gìn vệ sinh và bảo vệ thiên nhiên"],
                "C": ["cần chú ý quan sát và rèn tính cẩn thận khi thực hành", "cần dành thêm thời gian tìm hiểu và nắm chắc kiến thức bài học"]
            },
            "Lịch sử & Địa lý": {
                "T": ["ghi nhớ tốt các sự kiện lịch sử, kỹ năng khai thác lược đồ và bản đồ rất thành thạo", "có lòng tự hào dân tộc sâu sắc, nắm chắc đặc điểm địa lí các vùng miền"],
                "H": ["nắm được các mốc lịch sử chính, biết chỉ vị trí địa lí trên bản đồ", "hiểu được nét đặc trưng về văn hóa, thiên nhiên các vùng miền"],
                "C": ["kỹ năng sử dụng bản đồ, lược đồ còn lúng túng, cần ôn tập thêm các mốc thời gian", "cần chú ý liên hệ các sự kiện lịch sử để ghi nhớ tốt hơn"]
            },
            "Tin học": {
                "T": ["thao tác máy tính nhanh nhẹn, tư duy logic tốt, thực hành bài tập thành thạo", "sử dụng phần mềm học tập linh hoạt và có ý thức an toàn thông tin cao"],
                "H": ["thao tác bàn phím và chuột tương đối tốt, hoàn thành các bài thực hành đúng hạn", "nắm được các bước thao tác trên phần mềm cơ bản"],
                "C": ["thao tác gõ phím và sử dụng chuột còn chậm, cần rèn luyện thêm tại phòng máy", "cần tập trung quan sát các bước hướng dẫn của thầy cô"]
            },
            "Công nghệ": {
                "T": ["khéo tay, thực hiện đúng quy trình kỹ thuật, sản phẩm hoàn thiện đẹp và sáng tạo", "sử dụng dụng cụ thực hành an toàn, có tính thẩm mĩ cao"],
                "H": ["thực hành đúng các bước kỹ thuật, sản phẩm hoàn thành chỉn chu", "có ý thức giữ gìn vệ sinh và an toàn trong giờ thực hành"],
                "C": ["thao tác lắp ráp hoặc cắt dán còn lúng túng, cần cẩn thận hơn", "cần chú ý rèn luyện kỹ năng thực hành"]
            },
            "GDTC": {
                "T": ["thực hiện động tác chuẩn xác, nhanh nhẹn, tinh thần rèn luyện thể chất rất tích cực", "có tinh thần đồng đội cao, chấp hành tốt kỷ luật sân tập"],
                "H": ["thuộc các động tác thể dục, tích cực tham gia các trò chơi vận động", "thể lực tốt, có ý thức rèn luyện thân thể"],
                "C": ["thực hiện động tác đôi khi chưa chuẩn nhịp, cần tích cực vận động và rèn sức bền", "cần tập trung chú ý hơn khi nghe hiệu lệnh"]
            },
            "Âm nhạc": {
                "T": ["hát đúng giai điệu và lời ca, cảm thụ âm nhạc tốt, biểu diễn tự tin trước lớp", "gõ đệm đúng nhịp phách, đọc nhạc chuẩn xác cao độ"],
                "H": ["thuộc bài hát, biết gõ đệm theo phách, tự tin hát cùng các bạn", "có hứng thú và tham gia đầy đủ các hoạt động học tập"],
                "C": ["hát còn nhỏ, gõ đệm đôi chỗ chưa đúng nhịp, cần mạnh dạn hơn", "cần chú ý lắng nghe và luyện tập nhiều hơn"]
            },
            "Mĩ thuật": {
                "T": ["tranh vẽ có bố cục cân đối, phối màu hài hòa, trí tưởng tượng và sáng tạo rất phong phú", "kỹ năng tạo hình và hoàn thiện sản phẩm mĩ thuật xuất sắc"],
                "H": ["vẽ hình và tô màu cẩn thận, sản phẩm mĩ thuật đạt yêu cầu", "biết thể hiện cảm xúc qua màu sắc và đường nét"],
                "C": ["tô màu đôi chỗ còn lem, cần chú ý sắp xếp bố cục tranh cân đối hơn", "cần rèn luyện thêm kỹ năng vẽ nét và phối màu"]
            },
            "Đạo đức": {
                "T": ["hiểu rõ chuẩn mực hành vi, luôn lễ phép, gương mẫu và ứng xử văn minh", "biết chia sẻ, giúp đỡ mọi người và có tinh thần trách nhiệm cao"],
                "H": ["ngoan ngoãn, biết vâng lời, có ý thức thực hiện tốt nội quy trường lớp", "thân thiện và hòa đồng với bạn bè"],
                "C": ["cần chủ động và tự giác hơn trong việc thực hiện các hành vi chuẩn mực", "cần nghiêm túc rèn luyện và lắng nghe lời nhắc nhở"]
            },
            "Chung": {
                "T": ["kĩ năng thực hành vô cùng thành thạo, tư duy phân tích nhạy bén", "vận dụng cực kỳ linh hoạt kiến thức vào thực tiễn, sản phẩm chỉn chu sáng tạo"],
                "H": ["kĩ năng thực hành đạt yêu cầu, vận dụng được kiến thức vào bài tập", "ghi nhớ tốt các nội dung trọng tâm, hoàn thành chỉn chu các sản phẩm"],
                "C": ["kĩ năng thực hành còn lúng túng, thao tác còn chậm", "cần cố gắng nhiều hơn và dành thời gian ôn luyện"]
            }
        }
        
        loi_khuyen = {
            "T": ["Hãy tiếp tục duy trì phong độ xuất sắc này.", "Thái độ học tập luôn chủ động, rất đáng khen.", "Luôn hăng hái phát biểu xây dựng bài.", "Cách trình bày rất chỉn chu, khoa học.", "Cần tiếp tục phát huy năng lực nổi trội này nhé."],
            "H": ["Đã có nhiều tiến bộ, hãy tiếp tục cố gắng.", "Thái độ học tập ngoan ngoãn, chăm chỉ.", "Cần mạnh dạn phát biểu ý kiến hơn trong giờ học.", "Chỉ cần cẩn thận hơn chút nữa là rất tốt.", "Hãy duy trì tinh thần học tập tích cực này nhé."],
            "C": ["Cần nỗ lực ôn tập lại các kiến thức chưa vững.", "Yêu cầu nghiêm túc chấn chỉnh thái độ học tập.", "Cần chăm chỉ làm bài và chú ý nghe giảng hơn.", "Nên chủ động nhờ sự hỗ trợ từ bạn bè và thầy cô.", "Cần dành thêm thời gian để rèn luyện mỗi ngày."]
        }

        k_mon = "T" if mdd_clean == "T" else ("C" if mdd_clean == "C" else "H")
        dict_mo = {"T": mo_T, "H": mo_H, "C": mo_C}
        mo_chon = random.choice(dict_mo[k_mon])
        
        mon_kn_key = mon
        if mon in ["Tự nhiên và xã hội", "TNXH"]:
            mon_kn_key = "Khoa học"
        elif "Lịch sử" in mon or "Địa l" in mon:
            mon_kn_key = "Lịch sử & Địa lý"
            
        nguon_kynang = kynang_mon.get(mon_kn_key, kynang_mon["Chung"])
        kn_chon = random.choice(nguon_kynang[k_mon])
        lk_chon = random.choice(loi_khuyen[k_mon])
        
        if phong_cach == "Ngắn gọn":
            return cap_first(f"{mo_chon} {focus_kt}. Kỹ năng {kn_chon}.")
        elif phong_cach == "Gần gũi":
            return cap_first(f"{xh}nhận thấy em {mo_chon.lower()} {focus_kt}. Biểu hiện là {kn_chon}. {lk_chon}")
        elif phong_cach == "Khích lệ":
            mo_clean = mo_chon.lower().replace(" về", "").replace(" đối với", "").replace(" nội dung", "")
            return cap_first(f"Qua bài học {focus_kt}, em {mo_clean}. Khả năng {kn_chon}. {xh}khuyên em {lk_chon.lower()}")
        else: # Đầy đủ / Ngẫu nhiên
            return cap_first(f"{mo_chon} {focus_kt}. Khả năng {kn_chon}. {lk_chon}")

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
        nl_cands, pc_cands = [], []
        explicit_nl_cands, explicit_pc_cands = [], []
        
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
        
        valid_eval_cols = []
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
                
            # Đánh dấu các cột điểm chi tiết cho PC-NL (T, H, C, Đ) của kì hiện tại
            if is_my_term and check_col_has_data(df, j, s_row, "level"):
                valid_eval_cols.append(j)
            
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
                    
                if is_my_term and not is_diem and not is_muc and not is_nx:
                    diem_cands.append(j)
                    muc_cands.append(j)
                    explicit_diem_cands.append(j)
                    explicit_muc_cands.append(j)
            
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
            
        for k in pcnl_cols:
            if 'muc' in k:
                pcnl_cols[k] = get_best_col_strict(df, cands_pcnl[k], s_row, "level")
                if pcnl_cols[k] == -1 and cands_pcnl[k]: pcnl_cols[k] = cands_pcnl[k][-1]
            else:
                if cands_pcnl[k]: pcnl_cols[k] = cands_pcnl[k][-1]
                
        ref_cols = []
        if diem_col != -1: ref_cols.append(diem_col)
        if muc_col != -1: ref_cols.append(muc_col)
        
        ref_max = max(ref_cols) if ref_cols else -1
        
        c_col = -1
        if c_cands:
            valid_c = [c for c in c_cands if c > ref_max]
            if valid_c: c_col = valid_c[0]
            else: c_col = c_cands[-1]
                
        # SỬ DỤNG .insert ĐỂ ĐẢM BẢO KHÔNG BỊ LỖI PANDAS INDEX (Tránh KeyError)
        if c_col == -1: 
            c_col = len(df.columns)
            df.insert(c_col, f"NX_MON_{uuid.uuid4().hex[:4]}", "")
            df.iat[max(0, s_row - 1), c_col] = "Nhận xét"
        
        return df, n_col, diem_col, muc_col, c_col, s_row, pcnl_cols, valid_eval_cols
    except: return None, None, None, None, None, None, None, None

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
    with col2:
        if khoi in ["Khối 1", "Khối 2"]:
            ds_mon = ["Tiếng Việt", "Toán", "Tiếng Anh", "Tự nhiên và xã hội", "Đạo đức", "Âm nhạc", "Mĩ thuật", "GDTC", "Hoạt động trải nghiệm"]
        elif khoi == "Khối 3":
            ds_mon = ["Tiếng Việt", "Toán", "Tiếng Anh", "Tự nhiên và xã hội", "Tin học", "Công nghệ", "Đạo đức", "Âm nhạc", "Mĩ thuật", "GDTC", "Hoạt động trải nghiệm"]
        else:
            ds_mon = ["Tiếng Việt", "Toán", "Tiếng Anh", "Khoa học", "Lịch sử & Địa lý", "Tin học", "Công nghệ", "Đạo đức", "Âm nhạc", "Mĩ thuật", "GDTC", "Hoạt động trải nghiệm"]
        mon = st.selectbox("📚 Môn:", ds_mon)
    
    st.divider()
    st.markdown("**📂 Dữ liệu đầu vào**")
    f_hs = st.file_uploader("Tải lên danh sách (.xlsx, .csv)", type=["xlsx", "csv"], label_visibility="collapsed")

# --- KHỞI TẠO STATE ĐỂ LƯU KẾT QUẢ COPY ---
if "ket_qua_nhan_xet" not in st.session_state:
    st.session_state.ket_qua_nhan_xet = []
if "ket_qua_nlc" not in st.session_state:
    st.session_state.ket_qua_nlc = []
if "ket_qua_nldt" not in st.session_state:
    st.session_state.ket_qua_nldt = []
if "ket_qua_pc" not in st.session_state:
    st.session_state.ket_qua_pc = []

# --- 5. NỘI DUNG CHÍNH ---

if f_hs:
    df_raw, n_col, d_col, m_col, c_col, s_row, pcnl_cols, valid_eval_cols = phan_tich_file(f_hs, thoi_diem)
    
    if df_raw is not None:
        data_list = []
        mapping_indices = []
        header_r = max(0, s_row - 1)
        
        # BỐC CÁC CỘT CHI TIẾT CỦA PC-NL RA GIAO DIỆN (Lấy 15 cột T,H,C,Đ)
        pcnl_headers = []
        if loai_nx == "PC-NL" and valid_eval_cols:
            for j in valid_eval_cols:
                h_name = str(df_raw.iloc[max(0, s_row-1), j]).strip().replace("\n", " ")
                if h_name.lower() in ['nan', 'none', '']: 
                    h_name = str(df_raw.iloc[max(0, s_row-2), j]).strip().replace("\n", " ")
                if h_name.lower() in ['nan', 'none', '']: h_name = f"Cột {j}"
                
                orig = h_name
                count = 1
                while h_name in [n for _, n in pcnl_headers]:
                    h_name = f"{orig} ({count})"
                    count += 1
                pcnl_headers.append((j, h_name))
        
        # Đảm bảo các cột Nhận xét PC-NL tồn tại và CÓ TIÊU ĐỀ RÕ RÀNG để giáo viên dễ copy
        if loai_nx == "PC-NL":
            if pcnl_cols['nx_nlc'] == -1: 
                pcnl_cols['nx_nlc'] = len(df_raw.columns)
                df_raw.insert(pcnl_cols['nx_nlc'], f"NX_NLC_{uuid.uuid4().hex[:4]}", "")
                df_raw.iat[header_r, pcnl_cols['nx_nlc']] = "NX Năng lực chung"
            if pcnl_cols['nx_nldt'] == -1: 
                pcnl_cols['nx_nldt'] = len(df_raw.columns)
                df_raw.insert(pcnl_cols['nx_nldt'], f"NX_NLDT_{uuid.uuid4().hex[:4]}", "")
                df_raw.iat[header_r, pcnl_cols['nx_nldt']] = "NX Năng lực đặc thù"
            if pcnl_cols['nx_pc'] == -1: 
                pcnl_cols['nx_pc'] = len(df_raw.columns)
                df_raw.insert(pcnl_cols['nx_pc'], f"NX_PC_{uuid.uuid4().hex[:4]}", "")
                df_raw.iat[header_r, pcnl_cols['nx_pc']] = "NX Phẩm chất"

        for i in range(s_row, len(df_raw)):
            ten = str(df_raw.iloc[i, n_col]).strip()
            if ten.lower() not in ['nan', 'none', '']:
                if loai_nx == "PC-NL":
                    row_data = {"Họ và tên": ten}
                    if pcnl_headers:
                        for j, h_name in pcnl_headers:
                            val = str(df_raw.iloc[i, j]).strip().upper()
                            row_data[h_name] = val if val not in ['NAN', 'NONE'] else ""
                    else:
                        m_nlc = str(df_raw.iloc[i, pcnl_cols['muc_nlc']]).strip().upper() if pcnl_cols['muc_nlc'] != -1 else ""
                        m_nldt = str(df_raw.iloc[i, pcnl_cols['muc_nldt']]).strip().upper() if pcnl_cols['muc_nldt'] != -1 else ""
                        m_pc = str(df_raw.iloc[i, pcnl_cols['muc_pc']]).strip().upper() if pcnl_cols['muc_pc'] != -1 else ""
                        row_data["Mức NLC"] = m_nlc if m_nlc not in ['NAN', 'NONE'] else ""
                        row_data["Mức NLĐT"] = m_nldt if m_nldt not in ['NAN', 'NONE'] else ""
                        row_data["Mức PC"] = m_pc if m_pc not in ['NAN', 'NONE'] else ""
                        
                    row_data["NX Năng lực chung"] = ""
                    row_data["NX Năng lực đặc thù"] = ""
                    row_data["NX Phẩm chất"] = ""
                    data_list.append(row_data)
                else:
                    v_diem = str(df_raw.iloc[i, d_col]).strip() if d_col != -1 else ""
                    v_muc = str(df_raw.iloc[i, m_col]).strip().upper() if m_col != -1 else ""
                    if v_diem.upper() in ['NAN', 'NONE']: v_diem = ""
                    if v_muc.upper() in ['NAN', 'NONE']: v_muc = ""
                    # Chuẩn TT27: Điểm số bậc tiểu học là số nguyên đã làm tròn
                    if v_diem:
                        v_diem = lam_tron_diem(v_diem)
                    data_list.append({"Họ và tên": ten, "Điểm": v_diem, "Mức": v_muc, "Nhận xét": ""})
                mapping_indices.append(i)
        
        if not data_list:
            if loai_nx == "PC-NL":
                cols = ["Họ và tên"]
                if pcnl_headers: cols.extend([h for _, h in pcnl_headers])
                else: cols.extend(["Mức NLC", "Mức NLĐT", "Mức PC"])
                cols.extend(["NX Năng lực chung", "NX Năng lực đặc thù", "NX Phẩm chất"])
                df_view = pd.DataFrame(columns=cols)
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
            if pcnl_headers:
                for _, h_name in pcnl_headers:
                    config[h_name] = st.column_config.Column(width="small")
            else:
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
            st.session_state.ket_qua_nlc = []
            st.session_state.ket_qua_nldt = []
            st.session_state.ket_qua_pc = []
            
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
                    "BẮT BUỘC MỞ CÂU: Bằng việc đánh giá KỸ NĂNG THỰC HÀNH/VẬN DỤNG (VD: Thực hiện xuất sắc, Kỹ năng thực hành cần rèn luyện thêm...)",
                    "BẮT BUỘC MỞ CÂU: Bằng sự TỔNG KẾT KẾT QUẢ (VD: Kết quả học tập xuất sắc, Chưa hoàn thành mục tiêu...)",
                    "BẮT BUỘC MỞ CÂU: Bằng việc phân tích THÁI ĐỘ/TƯ DUY (VD: Tư duy nhạy bén, Thái độ học tập thiếu tập trung...)",
                    "BẮT BUỘC MỞ CÂU: Bằng một ĐIỂM NỔI TRỘI HOẶC NỘI DUNG CẦN CỐ GẮNG của môn học (VD: Đọc diễn cảm rất tốt, Kỹ năng tính toán còn chậm...)",
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
                    if pcnl_headers:
                        all_vals = [str(row.get(h_name, "")).strip() for _, h_name in pcnl_headers]
                        if all(v == "" for v in all_vals): is_empty_row = True
                    else:
                        m_nlc = str(row.get("Mức NLC", "")).strip()
                        m_nldt = str(row.get("Mức NLĐT", "")).strip()
                        m_pc = str(row.get("Mức PC", "")).strip()
                        if m_nlc == "" and m_nldt == "" and m_pc == "": is_empty_row = True
                else:
                    d_val = str(row.get("Điểm", "")).strip()
                    m_val = str(row.get("Mức", "")).strip()
                    if d_val == "" and m_val == "": is_empty_row = True

                if is_empty_row:
                    if loai_nx == "PC-NL":
                        df_view.at[idx, "NX Năng lực chung"] = ""
                        df_view.at[idx, "NX Năng lực đặc thù"] = ""
                        df_view.at[idx, "NX Phẩm chất"] = ""
                        df_raw.iat[int(real_idx), int(pcnl_cols['nx_nlc'])] = ""
                        df_raw.iat[int(real_idx), int(pcnl_cols['nx_nldt'])] = ""
                        df_raw.iat[int(real_idx), int(pcnl_cols['nx_pc'])] = ""
                        st.session_state.ket_qua_nhan_xet.append("")
                        st.session_state.ket_qua_nlc.append("")
                        st.session_state.ket_qua_nldt.append("")
                        st.session_state.ket_qua_pc.append("")
                    else:
                        df_view.at[idx, "Nhận xét"] = ""
                        df_raw.iat[int(real_idx), int(c_col)] = ""
                        st.session_state.ket_qua_nhan_xet.append("")
                else:
                    if loai_nx == "PC-NL":
                        if pcnl_headers:
                            nlc_vals = []
                            nldt_vals = []
                            pc_vals = []
                            all_evals = []
                            for _, h_name in pcnl_headers:
                                val = str(row.get(h_name, "")).upper().strip()
                                if not val or val in ['NAN', 'NONE']: continue
                                all_evals.append(val)
                                h_low = h_name.lower()
                                if any(w in h_low for w in ["chung", "nlc", "tự phục vụ", "tự quản", "tự học", "hợp tác", "giao tiếp", "giải quyết", "sáng tạo"]):
                                    nlc_vals.append(val)
                                elif any(w in h_low for w in ["đặc thù", "nldt", "nlđt", "ngôn ngữ", "tính toán", "thẩm mĩ", "thể chất", "khoa học"]):
                                    nldt_vals.append(val)
                                elif any(w in h_low for w in ["phẩm chất", "pc", "yêu nước", "nhân ái", "chăm", "trung thực", "trách nhiệm", "kỷ luật", "kỉ luật", "yêu thương", "tự tin"]):
                                    pc_vals.append(val)
                            
                            overall = calc_overall_mdd(all_evals) if all_evals else "Đ"
                            mdd_nlc = calc_overall_mdd(nlc_vals) if nlc_vals else (get_mdd(str(row.get("Mức NLC", ""))) if "Mức NLC" in row and row["Mức NLC"] else overall)
                            mdd_nldt = calc_overall_mdd(nldt_vals) if nldt_vals else (get_mdd(str(row.get("Mức NLĐT", ""))) if "Mức NLĐT" in row and row["Mức NLĐT"] else overall)
                            mdd_pc = calc_overall_mdd(pc_vals) if pc_vals else (get_mdd(str(row.get("Mức PC", ""))) if "Mức PC" in row and row["Mức PC"] else overall)
                        else:
                            mdd_nlc = get_mdd(m_nlc)
                            mdd_nldt = get_mdd(m_nldt)
                            mdd_pc = get_mdd(m_pc)
                        
                        if api_key:
                            prompt = f"Mã:{salt}. Đóng vai giáo viên tiểu học viết học bạ chuẩn Thông tư 27. Viết 3 nhận xét ngắn gọn, riêng biệt: 1. Năng lực chung (Mức {mdd_nlc}: Tốt/Đạt/Cần cố gắng), 2. Năng lực đặc thù (Mức {mdd_nldt}: Tốt/Đạt/Cần cố gắng), 3. Phẩm chất (Mức {mdd_pc}: Tốt/Đạt/Cần cố gắng). PHONG CÁCH: {style_prompt}. BẮT BUỘC TRẢ VỀ THEO ĐỊNH DẠNG: [Nhận xét 1] | [Nhận xét 2] | [Nhận xét 3]. TUYỆT ĐỐI KHÔNG DÙNG TỪ 'Em', 'Về năng lực', 'Về phẩm chất' ở đầu câu. TUYỆT ĐỐI CẤM dùng các từ: 'giỏi', 'khá', 'trung bình', 'yếu', 'kém'. Luôn dùng ngôn ngữ chuẩn TT27: Tốt, Đạt, Cần cố gắng, tích cực, chủ động, hoàn thành, cần rèn luyện thêm. {lenh_cam_cam_xuc}"
                            try:
                                res = model.generate_content(prompt); text = res.text.strip()
                                parts = text.split('|')
                                nx_nlc = parts[0].strip() if len(parts) > 0 else ""
                                nx_nldt = parts[1].strip() if len(parts) > 1 else ""
                                nx_pc = parts[2].strip() if len(parts) > 2 else ""
                            except:
                                nx_nlc, nx_nldt, nx_pc = sinh_nhan_xet_pcnl_offline(mdd_nlc, mdd_nldt, mdd_pc, student_idx=idx)
                        else:
                            nx_nlc, nx_nldt, nx_pc = sinh_nhan_xet_pcnl_offline(mdd_nlc, mdd_nldt, mdd_pc, student_idx=idx)
                        
                        df_view.at[idx, "NX Năng lực chung"] = nx_nlc
                        df_view.at[idx, "NX Năng lực đặc thù"] = nx_nldt
                        df_view.at[idx, "NX Phẩm chất"] = nx_pc
                        
                        df_raw.iat[int(real_idx), int(pcnl_cols['nx_nlc'])] = nx_nlc
                        df_raw.iat[int(real_idx), int(pcnl_cols['nx_nldt'])] = nx_nldt
                        df_raw.iat[int(real_idx), int(pcnl_cols['nx_pc'])] = nx_pc
                        st.session_state.ket_qua_nhan_xet.append(f"{nx_nlc} | {nx_nldt} | {nx_pc}")
                        st.session_state.ket_qua_nlc.append(nx_nlc)
                        st.session_state.ket_qua_nldt.append(nx_nldt)
                        st.session_state.ket_qua_pc.append(nx_pc)
                        
                    else:
                        mdd = "H"
                        if d_val.replace('.', '', 1).isdigit():
                            diem_so = int(math.floor(float(d_val) + 0.5))
                            diem_so = max(1, min(10, diem_so))
                            d_val = str(diem_so)
                            # Chuẩn TT27 môn học: Điểm 9-10 là T (Hoàn thành tốt), Điểm 5-8 là H (Hoàn thành), Dưới 5 là C (Chưa hoàn thành)
                            if diem_so >= 9: mdd = "T"
                            elif diem_so >= 5: mdd = "H"
                            else: mdd = "C"
                        elif m_val.replace('.', '', 1).isdigit():
                            diem_so = int(math.floor(float(m_val) + 0.5))
                            diem_so = max(1, min(10, diem_so))
                            m_val = str(diem_so)
                            if diem_so >= 9: mdd = "T"
                            elif diem_so >= 5: mdd = "H"
                            else: mdd = "C"
                        else:
                            chk_val = m_val if m_val != "" else d_val
                            mdd = get_mdd(chk_val, is_pcnl=False)

                        mach_kt_list = lay_mach_kien_thuc(mon, khoi, thoi_diem)
                        focus_kt = random.choice(mach_kt_list)

                        if api_key:
                            try:
                                k_q = f"Điểm: {d_val} " if d_val else ""
                                k_q += f"Mức: {m_val}" if m_val else ""
                                tuan_info = TUAN_THEO_THOI_DIEM.get(thoi_diem, "trong kì học")
                                prompt = f"Mã:{salt}. Đóng vai giáo viên tiểu học. Viết 1 nhận xét học bạ môn {mon} lớp {khoi.split(' ')[1]} vào {thoi_diem} ({tuan_info}) theo chuẩn bộ sách Kết nối tri thức với cuộc sống.\nKết quả: {k_q.strip()} (Mức đánh giá: {mdd}).\nMẠCH KIẾN THỨC BẮT BUỘC ĐÃ HỌC ({thoi_diem} - {tuan_info}): '{focus_kt}'.\nNGUYÊN TẮC QUAN TRỌNG:\n1. BÁM SÁT THỜI ĐIỂM {thoi_diem} ({tuan_info}): Chỉ được nhận xét trong phạm vi kiến thức, bài học '{focus_kt}' mà học sinh đã học ở {tuan_info}. TUYỆT ĐỐI KHÔNG nhận xét kiến thức của các tuần khác hoặc học kì khác.\n2. TRÁNH NHẬN XÉT CHUNG CHUNG HOANG MANG: Nhận xét cụ thể, nêu rõ học sinh nắm bắt và thực hành bài học '{focus_kt}' như thế nào.\n3. PHONG CÁCH: {style_prompt}.\n4. {lenh_xung_ho}\n5. {lenh_cam_cam_xuc}\n6. {lenh_mon_dac_thu}\n7. Nếu <5 hoặc C bắt buộc bắt đầu 'Chưa hoàn thành...' hoặc nêu rõ điểm yếu cần khắc phục ở nội dung này.\n8. {lenh_do_dai}\n9. {lenh_chong_lap}\nQUY TẮC BẮT BUỘC THEO THÔNG TƯ 27: Ở tiểu học chỉ có 3 mức đánh giá môn học là Hoàn thành tốt (T), Hoàn thành (H), Chưa hoàn thành (C). TUYỆT ĐỐI CẤM SỬ DỤNG các từ xếp loại học lực: 'giỏi', 'khá', 'trung bình', 'yếu', 'kém'. Diễn đạt mạch lạc, chuẩn mực sư phạm theo đúng Thông tư 27."
                                res = model.generate_content(prompt); nx_text = res.text.strip()
                            except: nx_text = ""
                        
                        if not nx_text:
                            nx_text = sinh_nhan_xet_offline("Môn học", mdd, focus_kt, style_key, xung_ho, bat_xung_ho, mon, thoi_diem)

                        df_view.at[idx, "Nhận xét"] = nx_text
                        df_raw.iat[int(real_idx), int(c_col)] = nx_text
                        st.session_state.ket_qua_nhan_xet.append(nx_text)
                
                tab_place.dataframe(df_view, use_container_width=True, height=450, column_config=config)
                bar.progress((idx + 1) / len(df_view))
                status.text(f"✔ Đang hoàn thiện: {ten_hs}")
                time.sleep(1.0 if api_key else 0.01)

            st.balloons()
            status.success(f"✅ Hoàn thành xuất sắc bộ học bạ!")
            
            if st.session_state.ket_qua_nhan_xet:
                if loai_nx == "PC-NL":
                    st.markdown("### 📋 KẾT QUẢ COPY NHANH THEO CỘT (DÁN VÀO EXCEL / SMAS / CSDL)")
                    st.info("💡 **HƯỚNG DẪN DÁN:** Chọn Tab cột cần dán bên dưới, click chuột vào khung, ấn **Ctrl+A** rồi **Ctrl+C**. Sau đó trên Excel/SMAS, click chuột 1 lần vào ô đầu tiên của cột đó và ấn **Ctrl+V** để dán hàng loạt!")
                    tab_nlc, tab_nldt, tab_pc, tab_all = st.tabs([
                        "1️⃣ Cột Năng lực chung", 
                        "2️⃣ Cột Năng lực đặc thù", 
                        "3️⃣ Cột Phẩm chất", 
                        "📑 Cả 3 cột (Dạng gộp |)"
                    ])
                    with tab_nlc:
                        st.text_area("📋 Nhận xét NĂNG LỰC CHUNG (Ctrl+A rồi Ctrl+C):", value="\n".join(st.session_state.ket_qua_nlc), height=300)
                    with tab_nldt:
                        st.text_area("📋 Nhận xét NĂNG LỰC ĐẶC THÙ (Ctrl+A rồi Ctrl+C):", value="\n".join(st.session_state.ket_qua_nldt), height=300)
                    with tab_pc:
                        st.text_area("📋 Nhận xét PHẨM CHẤT (Ctrl+A rồi Ctrl+C):", value="\n".join(st.session_state.ket_qua_pc), height=300)
                    with tab_all:
                        st.text_area("📋 Dạng gộp [NLC | NLĐT | PC]:", value="\n".join(st.session_state.ket_qua_nhan_xet), height=300)
                else:
                    st.markdown("### 📋 KẾT QUẢ COPY NHANH (DÁN TRỰC TIẾP VÀO EXCEL)")
                    copy_text = "\n".join(st.session_state.ket_qua_nhan_xet)
                    st.text_area("Bấm chuột vào khung dưới đây, ấn Ctrl+A để chọn tất cả, rồi ấn Ctrl+C để Copy:", value=copy_text, height=350)
                    st.warning("🚨 **LỖI DÁN 1 DÒNG DÀI NGOẰNG VÀ CÁCH KHẮC PHỤC:**\nNguyên nhân là do thầy/cô đã click đúp (nhấn chuột 2 lần) vào ô Excel khiến con trỏ nhấp nháy bên trong ô.\n\n👉 **CÁCH LÀM ĐÚNG:** Chỉ **CLICK CHUỘT 1 LẦN DUY NHẤT** vào ô đầu tiên (sao cho ô đó hiện viền màu xanh, TUYỆT ĐỐI KHÔNG có con trỏ nháy nháy bên trong). Sau đó ấn **Ctrl + V**, Excel sẽ tự động rải đều mỗi em 1 dòng!")

            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as writer:
                df_raw.to_excel(writer, index=False, header=False)
            st.download_button("📥 Tải file kết quả dự phòng", data=out.getvalue(), file_name=f"SDGHS_ThinhDam.xlsx")