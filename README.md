# TSCFLP - Two-Stage Capacitated Facility Location Problem

> **Cài đặt 2 thuật toán giải bài toán TSCFLP: Greedy và MFSS**

---

## 📋 Mục lục

1. [Giới thiệu](#-giới-thiệu)
2. [Cài đặt nhanh](#-cài-đặt-nhanh)
3. [Cách chạy code](#-cách-chạy-code)
4. [Chi tiết thuật toán](#-chi-tiết-thuật-toán)
5. [Giải thích code](#-giải-thích-code)
6. [Dataset và Format](#-dataset-và-format)
7. [Kết quả thí nghiệm](#-kết-quả-thí-nghiệm)
8. [Tùy chỉnh](#-tùy-chỉnh)
9. [Xử lý lỗi](#-xử-lý-lỗi)
10. [Tips & Best Practices](#-tips--best-practices)

---

## 📚 Giới thiệu

### Bài toán TSCFLP

Bài toán **Two-Stage Capacitated Facility Location Problem (TSCFLP)** là bài toán tối ưu hóa chuỗi cung ứng với 3 tầng:

- **Tầng 1 (Primary)**: Nhà máy sản xuất (plants) - tập I
- **Tầng 2 (Secondary)**: Kho trung chuyển (depots) - tập J  
- **Tầng 3**: Khách hàng (customers) - tập K

**Mục tiêu**: Chọn nhà máy và kho nào mở, phân phối hàng sao cho:
- ✅ Thỏa mãn nhu cầu khách hàng
- ✅ Không vượt quá công suất nhà máy và kho
- ✅ **Tổng chi phí nhỏ nhất** (chi phí mở + chi phí vận chuyển)

### Thuật toán được cài đặt

1. **Algorithm 1: Greedy** - Thuật toán tham lam xây dựng nghiệm nhanh (~1-10s)
2. **Algorithm 2: MFSS** - Matheuristic Fixed Set Search cải thiện nghiệm (~20-150s)

**Kết quả**: MFSS cho nghiệm tốt hơn Greedy **0.5-1.2%** nhưng chậm hơn ~20 lần.

---

## 🚀 Cài đặt nhanh

### Bước 1: Tạo môi trường ảo Python

```powershell
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
.\venv\Scripts\Activate.ps1
```

### Bước 2: Cài đặt thư viện

```powershell
pip install numpy pulp
```

**Thư viện sử dụng:**
- `numpy`: Xử lý ma trận, tính toán
- `pulp`: Giải bài toán MILP (Mixed Integer Linear Programming) với solver CBC

### Bước 3: Kiểm tra cài đặt

```powershell
python -c "import numpy, pulp; print('OK')"
```

---

## 🎯 Cách chạy code

### Option 1: Chạy riêng Greedy (Nhanh - 1-10s)

```powershell
.\venv\Scripts\python.exe greedy_tscflp.py
```

**Output mẫu:**
```
======================================================================
CHẠY GREEDY (Algorithm 1) TRÊN DATASET THẬT
======================================================================

→ Đang load instance: OCA/TSCFL/Instances/PSC1-C1-50.txt
  → Scale factors: U×24.0, V×1.4 (đảm bảo feasible)
  I=50 plants, J=100 depots, K=200 customers
  Tổng demand: 16388

→ Chạy Greedy (rcl_size=1 - pure greedy)...

======================================================================
KẾT QUẢ
======================================================================
Chi phí: 329,483,633.72
Thời gian: 1.59s
Số plant mở: 45/50
Số depot mở: 95/100
======================================================================
```

### Option 2: Chạy riêng MFSS (Chậm - 20-150s, chất lượng cao hơn)

```powershell
.\venv\Scripts\python.exe mfss_tscflp.py
```

**Output mẫu:**
```
======================================================================
CHẠY MFSS (Algorithm 2) TRÊN DATASET THẬT
======================================================================

→ Đang load instance: OCA/TSCFL/Instances/PSC1-C1-50.txt
  I=50 plants, J=100 depots, K=200 customers

→ Chạy MFSS (pop_size=3, iterations=10)...
  → Tạo 3 nghiệm ban đầu... ✓
  → Bắt đầu 10 vòng lặp tối ưu hóa...
    [Vòng 1/10] ✓ Cải thiện 0.30%
    [Vòng 2/10] -
    ...

======================================================================
KẾT QUẢ
======================================================================
Chi phí: 328,493,374.19
Thời gian: 19.42s
Số plant mở: 46/50
Số depot mở: 95/100
======================================================================
```

### Option 3: So sánh 2 thuật toán

```powershell
.\venv\Scripts\python.exe compare_greedy_mfss.py --instance OCA/TSCFL/Instances/PSC1-C1-50.txt --seed 42 --iters 15 --pop-size 4
```

**Tham số:**
- `--instance`: Đường dẫn file dataset
- `--seed`: Random seed (để lặp lại kết quả)
- `--iters`: Số vòng lặp MFSS
- `--pop-size`: Kích thước population của MFSS

**Output mẫu:**
```
======================================================================
KẾT QUẢ SO SÁNH
======================================================================

Phương pháp                  Chi phí       Thời gian       Cải thiện
----------------------------------------------------------------------
Greedy                329,483,633.72           1.53s               -
MFSS                  326,983,108.72          29.49s           0.76%
----------------------------------------------------------------------

✓ MFSS TỐT HƠN Greedy 0.76%
  Tiết kiệm được: 2,500,525.00
======================================================================
```

### Option 4: Chạy batch experiments (Khuyến nghị) ⭐

```powershell
.\venv\Scripts\python.exe run_batch_experiments.py
```

Script này sẽ:
- Chạy 7 thí nghiệm đại diện (5 dataset size 50 + 2 dataset size 100)
- So sánh Greedy vs MFSS trên mỗi dataset
- Tạo bảng kết quả tổng hợp
- Lưu kết quả vào file `results_table.txt`

---

## 📖 Chi tiết thuật toán

### Algorithm 1: Greedy (Tham lam)

#### Ý tưởng
```
while (còn demand chưa phục vụ):
    1. Chọn plant tốt nhất theo heuristic h_p(i)
    2. Với plant đã chọn:
       while (còn hàng từ plant cần phân phối):
           a. Chọn depot tốt nhất theo h_s(i,j)
           b. Với depot đã chọn:
              while (còn hàng từ depot cần phân phối):
                  i. Chọn customer gần nhất theo h_c(j,k)
                  ii. Phân phối hàng

Giải lại MILP với fixed-set → Tối ưu luồng
```

#### Heuristic functions

**h_p(i) - Chọn plant:**
```python
hp = f[i] / U[i] + avg(c[i,j])
```
- **Ý nghĩa:** Chi phí mở / capacity + chi phí trung bình đến depots
- **Ưu tiên:** Plant có chi phí mở thấp, capacity lớn, gần depots

**h_s(i,j) - Chọn depot:**
```python
hs = c[i,j] + g[j] / V[j] + avg(d[j,k])
```
- **Ý nghĩa:** Chi phí từ plant + (chi phí mở / capacity) + chi phí đến customers
- **Ưu tiên:** Depot gần plant, chi phí mở thấp, capacity lớn, gần customers

**h_c(j,k) - Chọn customer:**
```python
hc = d[j,k]
```
- **Ý nghĩa:** Chi phí vận chuyển depot → customer
- **Ưu tiên:** Customer gần depot nhất

#### Ưu điểm & Nhược điểm

**Ưu điểm:**
- ⚡ Rất nhanh (~1-10s)
- Cho nghiệm khả thi tốt
- Đơn giản, dễ hiểu

**Nhược điểm:**
- Chất lượng nghiệm không tối ưu
- Phụ thuộc thứ tự chọn facility

---

### Algorithm 2: MFSS (Matheuristic Fixed Set Search)

#### Ý tưởng

```
1. Tạo population ban đầu:
   - Chạy Greedy nhiều lần với RCL (randomization)
   - Lưu Npop nghiệm khác nhau

2. Lặp max_iter vòng:
   a. Chọn n_best nghiệm tốt nhất
   b. Với mỗi nghiệm:
      - Sinh ngẫu nhiên subset facilities để "free" (tự do)
      - Cố định các facility còn lại (fixed-set)
      - Giải MILP subproblem (nhỏ hơn → nhanh hơn)
      - Nếu tốt hơn → thay thế vào population
   c. Adaptive: nếu không cải thiện sau 5 vòng → tăng time_limit

3. Trả về nghiệm tốt nhất
```

#### Các tham số quan trọng

| Tham số | Ý nghĩa | Trade-off | Khuyến nghị |
|---------|---------|-----------|-------------|
| `Npop` | Kích thước population | ↑ = đa dạng, chậm hơn | 3-5 (size 50), 3-4 (size 100) |
| `n_best` | Số nghiệm tốt nhất xét | - | ≈ Npop/2 đến 2×Npop/3 |
| `Sizemax` | Facilities "free" tối đa | ↑ = tốt hơn, CHẬM NHIỀU | 5-10 (size 50), 3-5 (size 100) |
| `tinit` | Time limit subproblem (s) | Adaptive, tự tăng | 1.0-2.0s |
| `max_iter` | Số vòng lặp | ↑ = tốt hơn, chậm tuyến tính | 10-20 |

#### Fixed-set Subproblem

**Ví dụ:** 150 facilities → chỉ cho 5 facility tự do
```python
fixed = {
    'I': {0: 1, 1: 0, 2: 1, ...},  # Cố định 145 plants
    'J': {0: 1, 1: 1, 2: 0, ...}   # Cố định 95 depots
}
# → Chỉ tối ưu 5 facilities → Giải nhanh hơn NHIỀU
```

#### Ưu điểm & Nhược điểm

**Ưu điểm:**
- 🎯 Chất lượng nghiệm cao hơn (0.5-1.2% tốt hơn Greedy)
- Kết hợp ưu điểm heuristic + MILP
- Adaptive time limit

**Nhược điểm:**
- ⏱️ Chậm hơn (~20-150s)
- Nhiều tham số cần điều chỉnh

---

## 🔧 Giải thích code

### Kiến trúc tổng quan

```
tscflp_core.py         → Module lõi (data structures + MILP solver)
      ↑
      ├── greedy_tscflp.py      → Algorithm 1: Greedy
      ├── mfss_tscflp.py        → Algorithm 2: MFSS
      ├── compare_greedy_mfss.py → So sánh 2 thuật toán
      └── run_batch_experiments.py → Batch experiments
```

### File 1: `tscflp_core.py` (Module lõi)

#### Class `TSCFLPInstance`
```python
@dataclass
class TSCFLPInstance:
    f: List[float]     # Chi phí mở plants
    U: List[float]     # Capacity plants
    g: List[float]     # Chi phí mở depots
    V: List[float]     # Capacity depots
    D: List[float]     # Demand customers
    c: List[List[float]]  # Chi phí vận chuyển plant → depot
    d: List[List[float]]  # Chi phí vận chuyển depot → customer
```

#### Function `solve_full_mip()`

Giải bài toán MILP với các bước:

1. **Lấy dữ liệu** từ instance
2. **Tạo model** MILP
3. **Định nghĩa biến quyết định:**
   - `x[i]`: Binary - 1 nếu mở plant i
   - `y[j]`: Binary - 1 nếu mở depot j
   - `w[i,j]`: Continuous - lượng hàng plant i → depot j
   - `z[j,k]`: Continuous - lượng hàng depot j → customer k

4. **Hàm mục tiêu:**
   ```
   Minimize: Σ f[i]×x[i] + Σ g[j]×y[j] + Σ c[i,j]×w[i,j] + Σ d[j,k]×z[j,k]
   ```

5. **Ràng buộc:**
   - Capacity plant: `Σ w[i,j] ≤ U[i] × x[i]`
   - Capacity depot: `Σ z[j,k] ≤ V[j] × y[j]`
   - Bảo toàn luồng: `Σ w[i,j] = Σ z[j,k]` (tại depot j)
   - Thỏa demand: `Σ z[j,k] = D[k]` (của customer k)

6. **Fixed-set** (cho MFSS)
7. **Giải** với CBC solver
8. **Trả về** kết quả

#### Function `load_instance_from_file()`

Đọc dataset với các bước:

1. **Đọc file** và parse dữ liệu
2. **Đọc chi phí** mở facility (f, g)
3. **Đọc capacity** và tọa độ (U, V, D)
4. **Auto-scaling capacity:**
   ```python
   u_scale = max(1.0, (total_demand / total_U_raw) * 1.1)  # +10% buffer
   U = [u * u_scale for u in U_raw]
   ```
   → Đảm bảo `Σ U ≥ 1.1 × Σ D` để bài toán khả thi

5. **Tính ma trận chi phí** từ khoảng cách Euclidean
6. **Tạo TSCFLPInstance**

---

## 📊 Dataset và Format

### Cấu trúc thư mục

```
OCA/TSCFL/Instances/
├── PSC1-C1-50.txt   (50 plants, 100 depots, 200 customers)
├── PSC1-C1-100.txt  (100 plants, 200 depots, 400 customers)
├── PSC2-C3-50.txt
└── ... (50 files total)
```

### Format tên file: `PSCx-Cy-size.txt`
- `x` (1-5): Nhóm problem set
- `y` (1-5): Configuration type
- `size`: 50 hoặc 100

### Cấu trúc file dataset

```
50 100 200          # Dòng 1: I J K (số plants, depots, customers)
1000                # I dòng: chi phí mở plant
1200
...
500                 # J dòng: chi phí mở depot
600
...
10                  # I dòng: capacity plant
12
...
8 150.5             # J dòng: capacity depot + tọa độ x
7 200.3
...
2 100.0             # K dòng: demand customer + tọa độ x
3 150.0
...
```

**Lưu ý:** 
- Ma trận chi phí `c[i][j]` và `d[j][k]` được tính tự động từ khoảng cách Euclidean
- Capacity được tự động scale để đảm bảo bài toán khả thi

---

## 📈 Kết quả thí nghiệm

### Bảng kết quả 7 thí nghiệm mẫu

| # | Dataset | Size | Seed | Iter | Pop | Greedy Cost | MFSS Cost | Cải thiện | Time Greedy | Time MFSS |
|---|---------|------|------|------|-----|-------------|-----------|-----------|-------------|-----------|
| 1 | PSC1-C1 | 50 | 42 | 15 | 4 | 329.5M | 327.0M | **0.76%** | 1.6s | 29.2s |
| 2 | PSC2-C3 | 50 | 42 | 15 | 4 | 4,163.7M | 4,156.8M | **0.17%** | 1.5s | 31.6s |
| 3 | PSC3-C5 | 50 | 42 | 15 | 4 | 3,033.8M | 3,021.0M | **0.42%** | 1.5s | 28.0s |
| 4 | PSC1-C1 | 50 | 123 | 20 | 5 | 329.5M | 325.5M | **1.22%** | 1.6s | 39.0s |
| 5 | PSC4-C2 | 50 | 42 | 20 | 5 | 650.9M | 647.1M | **0.60%** | 1.7s | 40.5s |
| 6 | PSC1-C1 | 100 | 42 | 10 | 3 | 657.0M | 649.4M | **1.15%** | 6.9s | 86.7s |
| 7 | PSC3-C3 | 100 | 42 | 12 | 4 | 8,292.8M | 8,285.6M | **0.09%** | 10.6s | 148.7s |

### Phân tích

**✅ Kết luận:**
- MFSS **luôn tốt hơn** Greedy trong tất cả 7 thí nghiệm
- Cải thiện trung bình: **0.63%**
- Trade-off: MFSS chậm hơn ~20x nhưng cho nghiệm tốt hơn
- Dataset lớn hơn → thời gian tăng đáng kể (cả 2 thuật toán)

**🎯 Best result:** PSC1-C1-50 (seed=123) - MFSS tốt hơn **1.22%**

---

## 🔧 Tùy chỉnh

### Thay đổi dataset trong file riêng lẻ

Sửa biến `filepath` trong `greedy_tscflp.py` hoặc `mfss_tscflp.py`:

```python
filepath = "OCA/TSCFL/Instances/PSC2-C3-50.txt"  # Đổi file ở đây
```

### Thay đổi tham số MFSS

Sửa trong `mfss_tscflp.py` (hàm main):

```python
sol = mfss(inst, 
           Npop=5,         # Tăng population size → chất lượng tốt hơn, chậm hơn
           n_best=3,       # Số nghiệm tốt nhất giữ lại
           Sizemax=10,     # Số facility tự do trong subproblem → càng lớn càng chậm
           tinit=2.0,      # Time limit ban đầu cho subproblem (giây)
           max_iter=20)    # Số vòng lặp → nhiều hơn = tốt hơn nhưng chậm hơn
```

### Thay đổi tham số Greedy

```python
sol = greedy_tscflp(inst, rcl_size=3)  # rcl_size > 1 → randomization
```
- `rcl_size = 1`: Pure greedy (luôn chọn tốt nhất)
- `rcl_size > 1`: Semi-greedy (chọn ngẫu nhiên trong top rcl_size)

### Thêm dataset vào batch experiments

Sửa trong `run_batch_experiments.py`:

```python
experiments = [
    # (file, seed, iterations, pop_size)
    ("OCA/TSCFL/Instances/PSC1-C1-50.txt", 42, 15, 4),
    ("OCA/TSCFL/Instances/PSC5-C4-50.txt", 42, 20, 5),  # Thêm dòng này
    # ...
]
```

---

## 🐛 Xử lý lỗi

### Lỗi: `ModuleNotFoundError: No module named 'pulp'`

**Nguyên nhân:** Chưa cài đặt thư viện hoặc chưa activate venv.

**Giải pháp:**
```powershell
.\venv\Scripts\Activate.ps1
pip install pulp numpy
```

### Lỗi: `UnicodeEncodeError` (console Windows)

**Nguyên nhân:** Console Windows không hỗ trợ UTF-8 mặc định.

**Giải pháp:** Đã được fix sẵn trong code với:
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

### Lỗi: `FileNotFoundError` (không tìm thấy dataset)

**Nguyên nhân:** Đường dẫn file sai hoặc file không tồn tại.

**Giải pháp:** Kiểm tra đường dẫn:
```powershell
# Từ thư mục gốc project
dir OCA\TSCFL\Instances\
```

### Bài toán infeasible (capacity < demand)

**Nguyên nhân:** Dataset gốc có tổng capacity < tổng demand.

**Giải pháp:** Đã được fix tự động bằng auto-scaling:
```python
# Code tự động scale capacity lên 110% tổng demand
u_scale = max(1.0, (total_demand / total_U_raw) * 1.1)
```

### Solver chạy quá lâu / treo

**Nguyên nhân:** Tham số MFSS quá lớn hoặc dataset quá lớn.

**Giải pháp:**
- Giảm `max_iter` (vd: 10 → 5)
- Giảm `Npop` (vd: 5 → 3)
- Giảm `Sizemax` (vd: 10 → 5)
- Giảm `tinit` (vd: 2.0 → 1.0)

---

## 💡 Tips & Best Practices

### Khi nào dùng Greedy?
- ✅ Cần kết quả nhanh
- ✅ Dataset nhỏ/vừa (< 100 facilities)
- ✅ Chấp nhận nghiệm "đủ tốt"
- ✅ Tạo nghiệm khởi tạo cho MFSS

### Khi nào dùng MFSS?
- ✅ Cần nghiệm chất lượng cao
- ✅ Có thời gian chờ (vài phút)
- ✅ So sánh benchmark
- ✅ Báo cáo nghiên cứu

### Tối ưu hiệu năng

**Để chạy nhanh hơn:**
1. Giảm `max_iter`: Chạy nhanh hơn, giảm chất lượng ít
2. Giảm `Npop`: Giảm đa dạng nhưng nhanh hơn nhiều
3. Giảm `Sizemax`: Subproblem nhỏ hơn → nhanh hơn
4. Giảm `tinit`: Solver dừng sớm hơn

**Để chất lượng tốt hơn:**
1. Tăng `max_iter`: Nhiều vòng lặp hơn
2. Tăng `Npop`: Đa dạng hơn
3. Tăng `Sizemax`: Không gian tìm kiếm lớn hơn
4. Tăng `tinit`: Solver có thời gian tìm nghiệm tốt hơn

### Debug

**Xem log chi tiết solver:**

Sửa trong `tscflp_core.py`:
```python
solver = pl.PULP_CBC_CMD(msg=True, timeLimit=time_limit)  # msg=True
```

**Kiểm tra capacity:**

Sau khi load instance:
```python
print(f"Total capacity: {sum(inst.U) + sum(inst.V)}")
print(f"Total demand: {sum(inst.D)}")
```

**Trace Greedy:**

Thêm print trong vòng lặp:
```python
print(f"Selected plant {i_star}, remaining demand: {total_demand}")
```

### Chiến lược chọn dataset cho báo cáo

**Dataset Size 50** (Nhỏ - Chạy nhanh ~20-40s):
- PSC1-C1-50: Baseline chuẩn
- PSC2-C3-50: Phân bố capacity đồng đều
- PSC3-C5-50: Fixed cost cao
- PSC4-C2-50: Demand phân bố đặc biệt

**Dataset Size 100** (Lớn - Test scalability ~60-150s):
- PSC1-C1-100: So sánh với size 50
- PSC3-C3-100: Challenging case

**Tham số đề xuất:**
- Size 50: `--iters 15-20 --pop-size 4-5`
- Size 100: `--iters 10-12 --pop-size 3-4`

---

## 📚 Tham khảo

**Paper gốc:** Fernandes et al. (2014) - "A matheuristic for the Two-Stage Capacitated Facility Location Problem"

**Thuật toán:**
- Algorithm 1: Greedy construction heuristic
- Algorithm 2: MFSS (Matheuristic Fixed Set Search)

**Dataset:** OCA - Operations Research Competition Archive

---

## 📂 Cấu trúc Project

```
codefinalwithdataset/
│
├── README.md                   # File này - Tài liệu đầy đủ
│
├── tscflp_core.py              # Module lõi: MILP solver + data structures
├── greedy_tscflp.py            # Algorithm 1: Greedy
├── mfss_tscflp.py              # Algorithm 2: MFSS
├── compare_greedy_mfss.py      # So sánh 2 thuật toán
├── run_batch_experiments.py    # Chạy batch experiments
│
├── OCA/TSCFL/Instances/        # 50 dataset files
│   ├── PSC1-C1-50.txt
│   ├── PSC1-C1-100.txt
│   └── ...
│
├── results_table.txt           # Kết quả thí nghiệm (tự động tạo)
└── venv/                       # Virtual environment
```

---

## 👥 Tác giả

Dự án cài đặt thuật toán TSCFLP cho môn **Giải thuật nâng cao - UTE**

---

## 📝 License

Dự án dùng cho mục đích học tập và nghiên cứu.

---

## 🎓 Độ phức tạp

### Greedy
- **Time:** O(I × J + J × K) ≈ O(n²)
- **Space:** O(I + J + K) ≈ O(n)

### MFSS
- **Time per iteration:** O(2^Sizemax × MILP_time)
- **Total time:** O(max_iter × Npop × MILP_time)
- **Space:** O(Npop × n)

---

## ❓ FAQ

**Q1: Tôi chưa biết gì về TSCFLP, nên bắt đầu từ đâu?**

A: Đọc phần [Giới thiệu](#-giới-thiệu) và [Chi tiết thuật toán](#-chi-tiết-thuật-toán).

**Q2: Làm sao chạy code nhanh nhất?**

A: Chạy `run_batch_experiments.py` để test nhiều dataset cùng lúc.

**Q3: Code bị lỗi, làm sao debug?**

A: Xem phần [Xử lý lỗi](#-xử-lý-lỗi).

**Q4: Làm sao cải thiện kết quả MFSS?**

A: Xem phần [Tùy chỉnh](#-tùy-chỉnh) và [Tips & Best Practices](#-tips--best-practices).

**Q5: Dataset nào nên chọn cho báo cáo?**

A: Xem "Chiến lược chọn dataset" trong phần [Tips](#-tips--best-practices).

---

**🎉 Chúc bạn thành công với dự án TSCFLP!**

**💬 Lưu ý:** Tất cả code đều có comment chi tiết bằng tiếng Việt. Đọc comment trong code để hiểu rõ hơn!
