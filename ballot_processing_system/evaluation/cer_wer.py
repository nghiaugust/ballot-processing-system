import json
import os
import re

# =============================
# 1. Chuẩn bị Ground Truth (danh sách tên chính xác)
# =============================
GROUND_TRUTH = [
    "OLIVER JOHNSON",
    "SOPHIA MILLER",
    "JAMES ROBINSON",
    "EMILY HARRIS",
    "BENJAMIN SCOTT",
    "CHARLOTTE WALKER",
    "WILLIAM TURNER",
    "AMELIA COOPER",
    "DANIEL PARKER",
    "GRACE MITCHELL"
]

# =============================
# 2. Hàm chuẩn hoá chuỗi
# =============================
def normalize_text(s: str) -> str:
    """Chuẩn hoá chuỗi: bỏ khoảng trắng dư, viết hoa toàn bộ"""
    if s is None:
        return ""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)  # gộp nhiều khoảng trắng thành 1
    return s.upper()

# =============================
# 3. Tính edit distance + đếm S, D, I
# =============================
def edit_ops_counts(ref_tokens, hyp_tokens):
    """
    Tính số lỗi Substitution (S), Deletion (D), Insertion (I)
    ref_tokens: danh sách ký tự hoặc từ chuẩn
    hyp_tokens: danh sách ký tự hoặc từ nhận dạng
    """
    m, n = len(ref_tokens), len(hyp_tokens)
    dp = [[0]*(n+1) for _ in range(m+1)]

    for i in range(1, m+1):
        dp[i][0] = i
    for j in range(1, n+1):
        dp[0][j] = j

    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if ref_tokens[i-1] == hyp_tokens[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # deletion
                dp[i][j-1] + 1,      # insertion
                dp[i-1][j-1] + cost  # substitution hoặc match
            )

    i, j = m, n
    S = D = I = 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + (0 if ref_tokens[i-1] == hyp_tokens[j-1] else 1):
            if ref_tokens[i-1] != hyp_tokens[j-1]:
                S += 1
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
            D += 1
            i -= 1
        else:
            I += 1
            j -= 1
    return S, D, I, m

# =============================
# 4. Hàm tính CER và WER
# =============================
def calc_cer(ref, hyp):
    ref_n, hyp_n = normalize_text(ref), normalize_text(hyp)
    S, D, I, N = edit_ops_counts(list(ref_n), list(hyp_n))
    return S, D, I, N

def calc_wer(ref, hyp):
    ref_n, hyp_n = normalize_text(ref), normalize_text(hyp)
    S, D, I, N = edit_ops_counts(ref_n.split(), hyp_n.split())
    return S, D, I, N

# =============================
# 5. Đọc dữ liệu JSON và tính toán
# =============================
# Đường dẫn đến các thư mục chứa kết quả
data1_dir = "results/ket_qua_trocr_yolo/ket_qua_data1"
data2_dir = "results/ket_qua_trocr_yolo/ket_qua_data2"
# data1_dir = "results/ket_qua_only_trocr/ket_qua_data1"
# data2_dir = "results/ket_qua_only_trocr/ket_qua_data2"


# Lấy tất cả file JSON từ cả hai thư mục
json_paths = []
for directory in [data1_dir, data2_dir]:
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith("_result.json"):
                json_paths.append(os.path.join(directory, filename))

print(f"Tìm thấy {len(json_paths)} file JSON để xử lý")

# Biến tổng hợp
char_S = char_D = char_I = char_N = 0
word_S = word_D = word_I = word_N = 0
total_seq = 0
correct_seq = 0

for path in json_paths:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"Đang xử lý: {os.path.basename(path)}")
        
        data_sorted = sorted(data, key=lambda x: x.get("stt", 0))

        for entry in data_sorted:
            stt = entry.get("stt")
            hyp = entry.get("chi_tiet", {}).get("ho_ten_ocr", "")

            if isinstance(stt, int) and 1 <= stt <= len(GROUND_TRUTH):
                ref = GROUND_TRUTH[stt-1]
            else:
                ref = ""

            # CER
            S, D, I, N = calc_cer(ref, hyp)
            char_S += S; char_D += D; char_I += I; char_N += N

            # WER
            S, D, I, N = calc_wer(ref, hyp)
            word_S += S; word_D += D; word_I += I; word_N += N

            # Exact Match Accuracy (toàn chuỗi)
            if normalize_text(ref) == normalize_text(hyp):
                correct_seq += 1
            total_seq += 1
    
    except FileNotFoundError:
        print(f"Không tìm thấy file: {path}")
    except json.JSONDecodeError:
        print(f"Lỗi đọc JSON: {path}")
    except Exception as e:
        print(f"Lỗi xử lý file {path}: {e}")

# =============================
# 6. In kết quả tổng hợp
# =============================
CER = (char_S + char_D + char_I) / char_N if char_N > 0 else 0
WER = (word_S + word_D + word_I) / word_N if word_N > 0 else 0
ACC_SEQ = correct_seq / total_seq if total_seq > 0 else 0

print("\n" + "="*50)
print("KẾT QUẢ ĐÁNH GIÁ")
print("="*50)
print(f"Số file JSON đã xử lý: {len(json_paths)}")
print(f"Tổng số sequence: {total_seq}")
print(f"Số sequence chính xác: {correct_seq}")
print("-" * 50)
print(f"CER = {CER:.4f} ({CER*100:.2f}%)")
print(f"WER = {WER:.4f} ({WER*100:.2f}%)")
print(f"Accuracy (toàn chuỗi) = {ACC_SEQ:.4f} ({ACC_SEQ*100:.2f}%)")
print("-" * 50)
print(f"Chi tiết lỗi ký tự - S: {char_S}, D: {char_D}, I: {char_I}, Total chars: {char_N}")
print(f"Chi tiết lỗi từ - S: {word_S}, D: {word_D}, I: {word_I}, Total words: {word_N}")
print("="*50)
