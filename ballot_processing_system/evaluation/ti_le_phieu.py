import json
import os
import glob
import re

# =============================
# 1. Ground Truth (danh sách tên chính xác)
# =============================
GROUND_TRUTH_NAMES = [
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
# 3. Đọc file labels cho X
# =============================
def load_x_labels():
    """Đọc file nhãn cho các ô đánh dấu X"""
    x_labels = {}
    
    # Đọc labels cho data1 và data2
    label_files = [
        ('data1', 'lable_ballot/lable_ballot_data1.json'),
        ('data2', 'lable_ballot/lable_ballot_data2.json')
    ]
    
    for dataset_name, filename in label_files:
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    labels = json.load(f)
                x_labels[dataset_name] = labels
                print(f"✅ Đọc thành công labels cho {dataset_name}: {len(labels)} ballots")
            except Exception as e:
                print(f"❌ Lỗi đọc file {filename}: {e}")
        else:
            print(f"⚠️ Không tìm thấy file {filename}")
    
    return x_labels

# =============================
# 4. Kiểm tra xem ballot có nhãn không
# =============================
def has_ballot_labels(ballot_name, x_ground_truth):
    """
    Kiểm tra xem ballot có nhãn X không
    
    Args:
        ballot_name: Tên file ballot
        x_ground_truth: Ground truth cho dấu X
    
    Returns:
        bool: True nếu có nhãn, False nếu không
    """
    return ballot_name in x_ground_truth and len(x_ground_truth[ballot_name]) > 0

# =============================
# 5. Kiểm tra từng dòng trong phiếu
# =============================
def check_ballot_lines(ballot_result, x_ground_truth, ballot_name):
    """
    Kiểm tra từng dòng trong phiếu (dòng đúng = cả họ tên và dấu X đều đúng)
    
    Args:
        ballot_result: Kết quả từ file JSON
        x_ground_truth: Ground truth cho dấu X
        ballot_name: Tên file ballot
    
    Returns:
        dict: Thông tin chi tiết về số dòng đúng
    """
    # Kiểm tra xem có nhãn X cho ballot này không
    if not has_ballot_labels(ballot_name, x_ground_truth):
        return None  # Trả về None để báo hiệu không thể xử lý
    
    total_lines = len(ballot_result)
    correct_lines = 0
    
    line_details = []
    
    for entry in ballot_result:
        stt = entry.get("stt", 0)
        
        name_correct = False
        x_correct = False
        
        # Kiểm tra họ tên
        predicted_name = entry.get("chi_tiet", {}).get("ho_ten_ocr", "")
        if 1 <= stt <= len(GROUND_TRUTH_NAMES):
            true_name = GROUND_TRUTH_NAMES[stt - 1]
            name_correct = normalize_text(predicted_name) == normalize_text(true_name)
        
        # Kiểm tra dấu X
        if stt - 1 < len(x_ground_truth[ballot_name]):
            gt_entry = x_ground_truth[ballot_name][stt - 1]
            
            pred_yes = entry.get("dong_y", False)
            pred_no = entry.get("khong_dong_y", False)
            
            true_yes = gt_entry.get("dong_y", 0) == 1
            true_no = gt_entry.get("khong_dong_y", 0) == 1
            
            # Kiểm tra cả đồng ý và không đồng ý
            x_correct = (pred_yes == true_yes) and (pred_no == true_no)
        
        # Dòng đúng = cả họ tên và dấu X đều đúng
        line_correct = name_correct and x_correct
        
        if line_correct:
            correct_lines += 1
        
        line_details.append({
            'stt': stt,
            'name_correct': name_correct,
            'x_correct': x_correct,
            'line_correct': line_correct,
            'predicted_name': predicted_name,
            'true_name': GROUND_TRUTH_NAMES[stt - 1] if 1 <= stt <= len(GROUND_TRUTH_NAMES) else "N/A"
        })
    
    return {
        'ballot_name': ballot_name,
        'total_lines': total_lines,
        'correct_lines': correct_lines,
        'line_accuracy': correct_lines / total_lines if total_lines > 0 else 0,
        'line_details': line_details
    }

# =============================
# 6. Xử lý một dataset
# =============================
def process_dataset(result_dir, x_labels, dataset_name):
    """Xử lý một dataset và trả về thống kê theo dòng"""
    
    print(f"\n🔍 Xử lý dataset: {dataset_name}")
    print(f"   📂 Thư mục: {result_dir}")
    
    if not os.path.exists(result_dir):
        print(f"   ❌ Không tìm thấy thư mục: {result_dir}")
        return None
    
    # Lấy tất cả file kết quả
    pattern = os.path.join(result_dir, "*_result.json")
    result_files = glob.glob(pattern)
    
    if not result_files:
        print(f"   ⚠️ Không tìm thấy file kết quả nào")
        return None
    
    print(f"   📄 Tìm thấy {len(result_files)} file kết quả")
    
    # Lấy ground truth cho X
    x_ground_truth = x_labels.get(dataset_name.lower(), {})
    
    if not x_ground_truth:
        print(f"   ❌ Không có nhãn X cho dataset {dataset_name}")
        return None
    
    total_lines = 0
    correct_lines = 0
    ballot_results = []
    skipped_ballots = []  # Danh sách ballot bị bỏ qua
    
    for file_path in result_files:
        ballot_name = os.path.basename(file_path).replace("_result.json", "")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                ballot_result = json.load(f)
        except Exception as e:
            print(f"   ❌ Lỗi đọc file {file_path}: {e}")
            continue
        
        # Kiểm tra xem có nhãn cho ballot này không
        if not has_ballot_labels(ballot_name, x_ground_truth):
            skipped_ballots.append(ballot_name)
            print(f"   ⚠️ Bỏ qua {ballot_name}: Không có nhãn X")
            continue
        
        # Kiểm tra từng dòng trong phiếu này
        ballot_check = check_ballot_lines(ballot_result, x_ground_truth, ballot_name)
        
        if ballot_check is None:
            # Không nên xảy ra vì đã kiểm tra trước đó, nhưng để chắc chắn
            skipped_ballots.append(ballot_name)
            continue
        
        ballot_results.append(ballot_check)
        
        total_lines += ballot_check['total_lines']
        correct_lines += ballot_check['correct_lines']
        
        print(f"   📋 {ballot_name}: {ballot_check['correct_lines']}/{ballot_check['total_lines']} dòng đúng ({ballot_check['line_accuracy']*100:.1f}%)")
    
    line_accuracy = correct_lines / total_lines if total_lines > 0 else 0
    
    # Thông báo về ballot bị bỏ qua
    if skipped_ballots:
        print(f"   ⚠️ Đã bỏ qua {len(skipped_ballots)} ballot không có nhãn: {', '.join(skipped_ballots[:5])}{'...' if len(skipped_ballots) > 5 else ''}")
    
    result = {
        'dataset_name': dataset_name,
        'total_lines': total_lines,
        'correct_lines': correct_lines,
        'line_accuracy': line_accuracy,
        'ballot_results': ballot_results,
        'total_ballots': len(ballot_results),
        'skipped_ballots': skipped_ballots,
        'total_found_files': len(result_files)
    }
    
    print(f"   📊 Kết quả: {correct_lines}/{total_lines} dòng đúng = {line_accuracy:.4f} ({line_accuracy*100:.2f}%) từ {len(ballot_results)}/{len(result_files)} ballot")
    
    return result

# =============================
# 6. Hàm chính
# =============================
def main():
    """Tính tỉ lệ dòng đúng (cả họ tên và dấu X đều đúng trên 1 dòng)"""
    
    print("🎯 TÍNH TỈ LỆ DÒNG ĐÚNG (CẢ HỌ TÊN VÀ DẤU X TRÊN 1 DÒNG)")
    print("="*60)
    
    # Đọc labels cho dấu X
    x_labels = load_x_labels()
    
    # Danh sách datasets cần xử lý
    datasets = [
        {
            'name': 'Data1',
            'result_dir': 'results/ket_qua_trocr_yolo/ket_qua_data1'
            # 'result_dir': "results/ket_qua_only_trocr/ket_qua_data1"
        },
        {
            'name': 'Data2',
            'result_dir': 'results/ket_qua_trocr_yolo/ket_qua_data2'
            # 'result_dir': "results/ket_qua_only_trocr/ket_qua_data2"
        }
    ]
    
    all_results = []
    total_correct_lines = 0
    total_lines = 0
    
    # Xử lý từng dataset
    for dataset in datasets:
        result = process_dataset(
            dataset['result_dir'], 
            x_labels, 
            dataset['name']
        )
        
        if result:
            all_results.append(result)
            total_correct_lines += result['correct_lines']
            total_lines += result['total_lines']
    
    # Tính tổng kết
    overall_line_accuracy = total_correct_lines / total_lines if total_lines > 0 else 0
    
    # In kết quả tổng hợp
    print(f"\n{'='*60}")
    print(f"📊 KẾT QUẢ TỔNG HỢP (THEO DÒNG)")
    print(f"{'='*60}")
    
    for result in all_results:
        print(f"{result['dataset_name']:8}: {result['correct_lines']:4}/{result['total_lines']:4} dòng = {result['line_accuracy']:.4f} ({result['line_accuracy']*100:5.2f}%)")
    
    print(f"{'─'*60}")
    print(f"{'TỔNG':8}: {total_correct_lines:4}/{total_lines:4} dòng = {overall_line_accuracy:.4f} ({overall_line_accuracy*100:5.2f}%)")
    print(f"{'='*60}")
    
    # Phân tích chi tiết lỗi theo dòng
    print(f"\n📋 PHÂN TÍCH CHI TIẾT LỖI THEO DÒNG:")
    print(f"{'─'*60}")
    
    name_only_errors = 0
    x_only_errors = 0
    both_errors = 0
    total_error_lines = 0
    
    for result in all_results:
        for ballot in result['ballot_results']:
            for line in ballot['line_details']:
                if not line['line_correct']:
                    total_error_lines += 1
                    
                    has_name_error = not line['name_correct']
                    has_x_error = not line['x_correct']
                    
                    if has_name_error and has_x_error:
                        both_errors += 1
                    elif has_name_error:
                        name_only_errors += 1
                    elif has_x_error:
                        x_only_errors += 1
    
    if total_error_lines > 0:
        print(f"Chỉ lỗi họ tên:     {name_only_errors:4} dòng ({name_only_errors/total_error_lines*100:5.2f}%)")
        print(f"Chỉ lỗi dấu X:      {x_only_errors:4} dòng ({x_only_errors/total_error_lines*100:5.2f}%)")
        print(f"Lỗi cả hai:         {both_errors:4} dòng ({both_errors/total_error_lines*100:5.2f}%)")
        print(f"Tổng dòng lỗi:      {total_error_lines:4} dòng")
    
    # Thống kê theo ballot
    total_ballots = sum(result['total_ballots'] for result in all_results)
    total_found_files = sum(result['total_found_files'] for result in all_results)
    total_skipped = sum(len(result['skipped_ballots']) for result in all_results)
    
    print(f"\n📈 THỐNG KÊ TỔNG QUAN:")
    print(f"{'─'*60}")
    print(f"Tổng file result:   {total_found_files:4} file")
    print(f"Ballot có nhãn:     {total_ballots:4} ballot")
    print(f"Ballot bỏ qua:      {total_skipped:4} ballot (không có nhãn)")
    print(f"Tổng số dòng:       {total_lines:4} dòng")
    print(f"Dòng đúng:          {total_correct_lines:4} dòng")
    print(f"Dòng sai:           {total_lines - total_correct_lines:4} dòng")
    print(f"Trung bình:         {total_lines/total_ballots:.1f} dòng/phiếu" if total_ballots > 0 else "Trung bình:         0.0 dòng/phiếu")
    
    # Hiển thị danh sách ballot bị bỏ qua nếu có
    if total_skipped > 0:
        print(f"\n⚠️ DANH SÁCH BALLOT BỊ BỎ QUA (KHÔNG CÓ NHÃN):")
        print(f"{'─'*60}")
        for result in all_results:
            if result['skipped_ballots']:
                print(f"{result['dataset_name']:8}: {len(result['skipped_ballots'])} ballot - {', '.join(result['skipped_ballots'][:3])}{'...' if len(result['skipped_ballots']) > 3 else ''}")
    
    print(f"\n✅ Hoàn thành phân tích tỉ lệ dòng đúng!")

if __name__ == "__main__":
    main()