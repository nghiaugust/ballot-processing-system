# Hệ Thống Xử Lý Phiếu Bầu

## Cài đặt thư viện cần thiết

### 1. Python Environment

Hệ thống yêu cầu Python 3.8 trở lên.

### 2. Cài đặt dependencies

```bash
# Cài đặt PyTorch (thay đổi theo CUDA version của bạn)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Cài đặt các thư viện chính
pip install transformers ultralytics opencv-python pillow numpy

# Cài đặt thêm các thư viện hỗ trợ
pip install matplotlib seaborn pandas scikit-learn
```

### 3. Kiểm tra cài đặt

```bash
python -c "import torch; print('PyTorch version:', torch.__version__)"
python -c "import transformers; print('Transformers version:', transformers.__version__)"
python -c "import ultralytics; print('Ultralytics version:', ultralytics.__version__)"
```

## Chạy hệ thống

### 1. Xử lý với TrOCR + YOLO 

```bash
# Xử lý tất cả phiếu bầu trong ballot/data1 và ballot/data2
python -m processors.trocr_yolo

# Xử lý một thư mục cụ thể
python -m processors.trocr_yolo --input ballot/data1

# Xử lý nhiều thư mục
python -m processors.trocr_yolo --input ballot/data1,ballot/data2

# Xử lý một ảnh cụ thể
python -m processors.trocr_yolo --single ballot/data1/ballot_1.jpg

# Chỉ định thư mục output
python -m processors.trocr_yolo --output results/my_results
```

### 2. Xử lý với TrOCR only

```bash
# Xử lý tất cả phiếu bầu
python -m processors.only_trocr

# Xử lý một thư mục cụ thể
python -m processors.only_trocr --input ballot/data1

# Xử lý một ảnh cụ thể
python -m processors.only_trocr --single ballot/data1/ballot_1.jpg
```

### 3. Tham số dòng lệnh

#### trocr_yolo.py

- `--input`: Thư mục hoặc danh sách thư mục chứa ảnh phiếu bầu
- `--output`: Thư mục lưu kết quả
- `--weights`: Đường dẫn đến file weights YOLO (mặc định: models/best.pt)
- `--single`: Xử lý một ảnh cụ thể

#### only_trocr.py

- `--input`: Thư mục hoặc danh sách thư mục chứa ảnh phiếu bầu
- `--output`: Thư mục lưu kết quả
- `--single`: Xử lý một ảnh cụ thể

## Đánh giá kết quả

### 1. Tính CER/WER

```bash
python evaluation/cer_wer.py
```

### 2. Tính Precision/Recall

```bash
python evaluation/precision_recall.py
```

### 3. Thống kê tỷ lệ phiếu

```bash
python evaluation/ti_le_phieu.py
```

## Kết quả đầu ra

### Cấu trúc thư mục results

```
results/
├── ket_qua_trocr_yolo/           # Kết quả TrOCR + YOLO
│   ├── ket_qua_data1/           # Kết quả data1
│   │   ├── ballot_1_result.json # Kết quả chi tiết từng phiếu
│   ├── ket_qua_data2/           # Kết quả data2
└── ket_qua_only_trocr/          # Kết quả chỉ TrOCR
```