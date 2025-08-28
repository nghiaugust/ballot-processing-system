# Ballot Processing System
This is the source code for a system that applies deep learning and transformer models for ballot counting and processing
## Installation

### 1. Python Environment

The system requires Python 3.8 or higher.

### 2. Installing Dependencies

```bash
# Install PyTorch (adjust the command based on your CUDA version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install core libraries
pip install transformers ultralytics opencv-python pillow numpy

# Install supplementary libraries
pip install matplotlib seaborn pandas scikit-learn
```

### 3. Verifying Installation

```bash
python -c "import torch; print('PyTorch version:', torch.__version__)"
python -c "import transformers; print('Transformers version:', transformers.__version__)"
python -c "import ultralytics; print('Ultralytics version:', ultralytics.__version__)"
```

## Running the System

### 1. Processing with TrOCR + YOLO 

```bash
# Process all ballots in the ballot/data1 and ballot/data2 directories
python -m processors.trocr_yolo

# Process a specific directory
python -m processors.trocr_yolo --input ballot/data1

# Process multiple directories
python -m processors.trocr_yolo --input ballot/data1,ballot/data2

# Process a single image file
python -m processors.trocr_yolo --single ballot/data1/ballot_1.jpg

# Specify a custom output directory
python -m processors.trocr_yolo --output results/my_results
```

### 2. Processing with TrOCR Only

```bash
# Process all ballots
python -m processors.only_trocr

# Process a specific directory
python -m processors.only_trocr --input ballot/data1

# Process a single image file
python -m processors.only_trocr --single ballot/data1/ballot_1.jpg
```

### 3. Command-Line Arguments

#### trocr_yolo.py

- `--input`: Directory or comma-separated list of directories containing ballot images.
- `--output`: Directory to save the results.
- `--weights`: Path to the YOLO weights file (default: models/best.pt).
- `--single`: Path to a single image file to process.

#### only_trocr.py

- `--input`: Directory or comma-separated list of directories containing ballot images.
- `--output`: Directory to save the results.
- `--single`: Path to a single image file to process.

## Evaluation

### 1. Calculate CER/WER

```bash
python evaluation/cer_wer.py
```

### 2. Calculate Precision/Recall

```bash
python evaluation/precision_recall.py
```

### 3. Calculate Vote Tally Statistics

```bash
python evaluation/ti_le_phieu.py
```

## Output

### Results Directory Structure

```
results/
├── ket_qua_trocr_yolo/          # Results from TrOCR + YOLO
│   ├── ket_qua_data1/           # Results for the data1 set
│   │   ├── ballot_1_result.json # Detailed results for each ballot
│   └── ket_qua_data2/           # Results for the data2 set
└── ket_qua_only_trocr/          # Results from TrOCR only
```

### Evaluation Metrics

The system employs several standard metrics to evaluate model performance:

- **CER (Character Error Rate)**: Measures the number of character errors (insertions, deletions, substitutions) relative to the total number of characters in the ground truth. A lower CER indicates better performance.
- **WER (Word Error Rate)**: Similar to CER but calculated at the word level. A lower WER is better.
- **Accuracy (full name)**: The proportion of correctly predicted full names out of the total number of name samples.
- **Precision**: The ratio of correctly predicted positive observations to the total predicted positive observations. It measures the accuracy of positive predictions.
- **Recall**: The ratio of correctly predicted positive observations to all observations in the actual class. It measures the model's ability to find all relevant cases.
- **F1-score**: The harmonic mean of Precision and Recall, providing a single score that balances both metrics.
- **Accuracy (X mark)**:The proportion of correctly detected "X" marks out of the total number of "X" mark samples.