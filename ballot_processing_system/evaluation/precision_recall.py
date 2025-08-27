import json
import os
import glob

def calculate_overall_metrics(result_dir, labels, dataset_name):
    """
    Tính Precision và Recall cho một dataset
    
    Args:
        result_dir: Thư mục chứa file kết quả (_result.json)
        labels: Dict chứa nhãn gốc
        dataset_name: Tên dataset (để debug)
    """
    TP, FP, FN, TN = 0, 0, 0, 0
    processed_files = 0

    # Lấy tất cả file *_result.json trong thư mục
    pattern = os.path.join(result_dir, "*_result.json")
    result_files = glob.glob(pattern)
    
    print(f"\n🔍 Xử lý {dataset_name}:")
    print(f"   - Thư mục: {result_dir}")
    print(f"   - Tìm thấy {len(result_files)} file kết quả")

    for file_path in result_files:
        ballot_name = os.path.basename(file_path).replace("_result.json", "")
        
        # Kiểm tra có nhãn không
        if ballot_name not in labels:
            print(f"   ⚠️ Không tìm thấy nhãn cho {ballot_name}")
            continue
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                result = json.load(f)
        except Exception as e:
            print(f"   ❌ Lỗi đọc file {file_path}: {e}")
            continue

        ground_truth = labels[ballot_name]
        processed_files += 1

        for res in result:
            stt = res["stt"]
            
            # Kiểm tra index hợp lệ
            if stt - 1 >= len(ground_truth):
                continue
                
            gt = ground_truth[stt - 1]  # vì index bắt đầu từ 0

            # Prediction (cả đồng ý và không đồng ý)
            pred_yes = res["dong_y"]
            pred_no = res["khong_dong_y"]

            # Ground truth (cả đồng ý và không đồng ý)
            true_yes = gt["dong_y"] == 1
            true_no = gt["khong_dong_y"] == 1

            # Tính toán cho cả đồng ý và không đồng ý
            # Đồng ý
            if pred_yes and true_yes:
                TP += 1
            elif pred_yes and not true_yes:
                FP += 1
            elif not pred_yes and true_yes:
                FN += 1
            elif not pred_yes and not true_yes:
                TN += 1
                
            # Không đồng ý
            if pred_no and true_no:
                TP += 1
            elif pred_no and not true_no:
                FP += 1
            elif not pred_no and true_no:
                FN += 1
            elif not pred_no and not true_no:
                TN += 1

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) > 0 else 0
    
    print(f"   ✅ Đã xử lý {processed_files} file")
    print(f"   📊 TP={TP}, FP={FP}, FN={FN}, TN={TN}")
    print(f"   📈 Precision={precision:.4f}, Recall={recall:.4f}, F1={f1:.4f}, Accuracy={accuracy:.4f}")
    
    return precision, recall, f1, accuracy, TP, FP, FN, TN

def main():
    """
    Tính 4 giá trị trung bình: X_Precision, X_Recall, X_F1, X_Accuracy
    """
    print("🚀 TÍNH TOÁN 4 GIÁ TRỊ X_PRECISION, X_RECALL, X_F1, X_ACCURACY")
    
    # Cấu hình datasets
    datasets = [
        {
            'name': 'Data1',
            'label_file': 'lable_ballot/lable_ballot_data1.json',
            'result_dir': 'results/ket_qua_trocr_yolo/ket_qua_data1'
            # 'result_dir': "results/ket_qua_only_trocr/ket_qua_data1"
        },
        {
            'name': 'Data2', 
            'label_file': 'lable_ballot/lable_ballot_data2.json',
            'result_dir': 'results/ket_qua_trocr_yolo/ket_qua_data2'
            # 'result_dir': "results/ket_qua_only_trocr/ket_qua_data2"
        }
    ]
    
    total_tp, total_fp, total_fn, total_tn = 0, 0, 0, 0
    
    for dataset in datasets:
        name = dataset['name']
        label_file = dataset['label_file']
        result_dir = dataset['result_dir']
        
        # Kiểm tra file nhãn
        if not os.path.exists(label_file):
            print(f"❌ Không tìm thấy file nhãn: {label_file}")
            continue
            
        # Kiểm tra thư mục kết quả
        if not os.path.exists(result_dir):
            print(f"❌ Không tìm thấy thư mục kết quả: {result_dir}")
            continue
        
        # Đọc file nhãn
        try:
            with open(label_file, "r", encoding="utf-8") as f:
                labels = json.load(f)
            print(f"📖 Đọc thành công file nhãn {label_file}")
        except Exception as e:
            print(f"❌ Lỗi đọc file nhãn {label_file}: {e}")
            continue
        
        # Tính metrics cho dataset này
        precision, recall, f1, accuracy, tp, fp, fn, tn = calculate_overall_metrics(result_dir, labels, name)
        
        # Cộng dồn cho tổng
        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_tn += tn
    
    # Tính 4 giá trị trung bình tổng hợp
    if total_tp + total_fp + total_fn + total_tn > 0:
        x_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        x_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        x_f1 = 2 * x_precision * x_recall / (x_precision + x_recall) if (x_precision + x_recall) > 0 else 0
        x_accuracy = (total_tp + total_tn) / (total_tp + total_tn + total_fp + total_fn)
        
        print(f"\n{'='*50}")
        print(f"📊 KẾT QUẢ 4 GIÁ TRỊ TRUNG BÌNH:")
        print(f"{'='*50}")
        print(f"X_Precision: {x_precision:.4f}")
        print(f"X_Recall:    {x_recall:.4f}")
        print(f"X_F1:        {x_f1:.4f}")
        print(f"X_Accuracy:  {x_accuracy:.4f}")
        print(f"{'='*50}")
    
    else:
        print("❌ Không có dữ liệu để tính toán")

if __name__ == "__main__":
    main()
