# tscflp_core.py
"""File lõi dùng chung cho cả Greedy và MFSS.

- Định nghĩa cấu trúc dữ liệu cho bài toán TSCFLP
- Cài đặt hàm solve_full_mip() dùng PuLP để giải MILP
- Hàm load_instance_from_file() để đọc dataset từ file
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import pulp as pl


# =====================================================================
# 1. ĐỊNH NGHĨA INSTANCE BÀI TOÁN & CẤU TRÚC LƯU LỜI GIẢI
# =====================================================================

@dataclass
class TSCFLPInstance:
    """
    Mô tả 1 instance của bài toán Two-Stage Capacitated Facility Location Problem (TSCFLP)

    Tầng 1: primary facilities (nhà máy)       i in I
    Tầng 2: secondary facilities (kho)         j in J
    Khách hàng                                 k in K

    Mục tiêu: mở một số nhà máy + kho, và quyết định luồng hàng w(i,j), z(j,k)
               sao cho tổng:
                    - chi phí mở nhà máy
                    - chi phí mở kho
                    - chi phí vận chuyển i->j
                    - chi phí vận chuyển j->k
               là nhỏ nhất, đồng thời thỏa:
                    - capacity của nhà máy, kho
                    - thỏa mãn demand khách hàng
    """
    # primary facilities (nhà máy)
    f: List[float]     # fixed cost mở tại i
    U: List[float]     # capacity (công suất tối đa) tại i

    # secondary facilities (kho)
    g: List[float]     # fixed cost mở tại j
    V: List[float]     # capacity tại j

    # customers
    D: List[float]     # nhu cầu của khách hàng k

    # transport costs
    c: List[List[float]]  # chi phí đơn vị i -> j
    d: List[List[float]]  # chi phí đơn vị j -> k

    def __post_init__(self):
        """
        Sau khi khởi tạo, tạo luôn các tập chỉ số I, J, K
        để dùng cho vòng lặp cho tiện.
        """
        self.I = list(range(len(self.f)))   # index nhà máy
        self.J = list(range(len(self.g)))   # index kho
        self.K = list(range(len(self.D)))   # index khách hàng


@dataclass
class Solution:
    """
    Lưu lời giải ở mức "facility mở hay không" + cost.
    (Phần luồng chi tiết w(i,j), z(j,k) không lưu lại ở đây
     vì mục đích chính là so sánh cost và pattern mở/đóng.)
    """
    cost: float
    open_I: List[int]   # 0/1 cho từng nhà máy i
    open_J: List[int]   # 0/1 cho từng kho j


# =====================================================================
# 2. HÀM GIẢI MILP ĐẦY ĐỦ CHO TSCFLP (DÙNG CHUNG CHO GREEDY + MFSS)
# =====================================================================

def solve_full_mip(inst: TSCFLPInstance,
                   time_limit: Optional[float] = None,
                   fixed: Optional[Dict[str, Dict[int, int]]] = None,
                   verbose: bool = True
                   ) -> Solution:
    """
    Giải đầy đủ mô hình MILP của TSCFLP bằng PuLP (CBC).

    Parameters
    ----------
    inst : TSCFLPInstance
        Instance của bài toán.
    time_limit : float, optional
        Giới hạn thời gian cho solver (giây). Nếu None thì không giới hạn.
    fixed : dict, optional
        Nếu muốn "cố định" một số biến x_i, y_j (dùng trong MFSS),
        truyền vào dạng:
            {
              'I': {i: 0 hoặc 1, ...},
              'J': {j: 0 hoặc 1, ...}
            }
    verbose : bool, optional
        In log từ solver hay không (default: True)

    Returns
    -------
    Solution
        Cost tối ưu (hoặc tốt nhất trong time limit) và pattern mở/đóng facility.
    """
    # ===== BƯỚC 1: Lấy dữ liệu từ instance =====
    I, J, K = inst.I, inst.J, inst.K  # Tập chỉ số plants, depots, customers
    f, g, U, V, D = inst.f, inst.g, inst.U, inst.V, inst.D  # Chi phí, capacity, demand
    c, d = inst.c, inst.d  # Ma trận chi phí vận chuyển

    # ===== BƯỚC 2: Tạo model MILP =====
    prob = pl.LpProblem("TSCFLP", pl.LpMinimize)  # Bài toán tối thiểu hóa chi phí

    # ===== BƯỚC 3: Định nghĩa biến quyết định =====
    # x[i]: Biến nhị phân - 1 nếu mở nhà máy i, 0 nếu không
    x = pl.LpVariable.dicts("x", I, lowBound=0, upBound=1, cat="Binary")
    
    # y[j]: Biến nhị phân - 1 nếu mở kho j, 0 nếu không
    y = pl.LpVariable.dicts("y", J, lowBound=0, upBound=1, cat="Binary")

    # w[i,j]: Biến liên tục - lượng hàng vận chuyển từ nhà máy i đến kho j
    w = pl.LpVariable.dicts("w", (I, J), lowBound=0, cat="Continuous")
    
    # z[j,k]: Biến liên tục - lượng hàng vận chuyển từ kho j đến khách hàng k
    z = pl.LpVariable.dicts("z", (J, K), lowBound=0, cat="Continuous")

    # ===== BƯỚC 4: Định nghĩa hàm mục tiêu (Objective Function) =====
    # Tối thiểu hóa tổng chi phí = chi phí mở facility + chi phí vận chuyển
    prob += (
        pl.lpSum(f[i] * x[i] for i in I) +                     # Tổng chi phí mở nhà máy
        pl.lpSum(g[j] * y[j] for j in J) +                     # Tổng chi phí mở kho
        pl.lpSum(c[i][j] * w[i][j] for i in I for j in J) +    # Tổng chi phí vận chuyển plant->depot
        pl.lpSum(d[j][k] * z[j][k] for j in J for k in K)      # Tổng chi phí vận chuyển depot->customer
    )

    # ===== BƯỚC 5: Thêm các ràng buộc (Constraints) =====
    
    # Ràng buộc 1: Capacity của nhà máy
    # Tổng hàng xuất từ nhà máy i không vượt quá capacity U[i] (chỉ khi mở x[i]=1)
    for i in I:
        prob += pl.lpSum(w[i][j] for j in J) <= U[i] * x[i]

    # Ràng buộc 2: Capacity của kho
    # Tổng hàng qua kho j không vượt quá capacity V[j] (chỉ khi mở y[j]=1)
    for j in J:
        prob += pl.lpSum(z[j][k] for k in K) <= V[j] * y[j]

    # Ràng buộc 3: Bảo toàn luồng tại kho
    # Hàng vào kho j (từ plants) = Hàng ra kho j (đến customers)
    # Đảm bảo không tồn kho, không mất hàng
    for j in J:
        prob += pl.lpSum(w[i][j] for i in I) == pl.lpSum(z[j][k] for k in K)

    # Ràng buộc 4: Thỏa mãn nhu cầu khách hàng
    # Tổng hàng nhận được của khách k phải đúng bằng nhu cầu D[k]
    for k in K:
        prob += pl.lpSum(z[j][k] for j in J) == D[k]

    # ===== BƯỚC 6: Fixed-set constraints (dùng cho MFSS) =====
    # Trong MFSS, ta cố định một số facility đã chọn, chỉ cho một số facility tự do
    # Điều này giúp thu hẹp không gian tìm kiếm, giải nhanh hơn
    if fixed is not None:
        # Cố định các plant: x[i] = 0 hoặc 1
        for i, val in fixed.get('I', {}).items():
            prob += x[i] == int(val)
        # Cố định các depot: y[j] = 0 hoặc 1
        for j, val in fixed.get('J', {}).items():
            prob += y[j] == int(val)

    # ===== BƯỚC 7: Chọn solver và giải bài toán =====
    # Sử dụng CBC solver (mặc định của PuLP, miễn phí, mã nguồn mở)
    # msg=False: không in log chi tiết của solver
    # timeLimit: giới hạn thời gian giải (giây)
    solver = pl.PULP_CBC_CMD(msg=False, timeLimit=time_limit)
    
    if verbose:
        print("  → Đang giải MILP...", end='', flush=True)
    
    try:
        # Giải bài toán MILP
        prob.solve(solver)
        
        if verbose:
            print(" ✓")  # In dấu tick khi giải xong
        
        # ===== BƯỚC 8: Lấy kết quả =====
        # Lấy giá trị hàm mục tiêu (tổng chi phí)
        cost = pl.value(prob.objective)
        if cost is None:  # Nếu không giải được
            cost = float('inf')
        
        # Lấy pattern facility mở/đóng từ biến x[i] và y[j]
        # round() để chuyển từ số thực (0.0/1.0) sang số nguyên (0/1)
        open_I = [int(round(x[i].value())) if x[i].value() is not None else 0 for i in I]
        open_J = [int(round(y[j].value())) if y[j].value() is not None else 0 for j in J]
        
        # Trả về Solution object chứa chi phí và pattern
        return Solution(cost=cost, open_I=open_I, open_J=open_J)
        
    except Exception as e:
        # Xử lý lỗi: in thông báo và trả về nghiệm không khả thi
        print(f"Solver error: {e}")
        return Solution(cost=float('inf'), open_I=[0]*len(I), open_J=[0]*len(J))


# =====================================================================
# 3. ĐỌC DỮ LIỆU TỪ FILE DATASET
# =====================================================================

def load_instance_from_file(filepath: str) -> TSCFLPInstance:
    """
    Đọc instance TSCFLP từ file dataset theo format chuẩn.
    
    Format file:
    - Dòng 1: I J K (số plants, depots, customers)
    - I dòng tiếp: chi phí mở plant (f)
    - J dòng tiếp: chi phí mở depot (g)
    - I dòng tiếp: capacity plant (U)
    - J dòng tiếp: capacity depot + tọa độ x (V x)
    - K dòng tiếp: demand customer + tọa độ x (D x)
    
    Lưu ý:
    - Ma trận chi phí c[i][j] và d[j][k] được tính từ khoảng cách Euclidean
    - Capacity được tự động scale để đảm bảo bài toán khả thi
    """
    import math
    import random
    
    # ===== BƯỚC 1: Đọc file và phân tích cấu trúc =====
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]  # Bỏ dòng trống
    
    idx = 0  # Con trỏ theo dõi vị trí đọc
    
    # Đọc dòng đầu tiên: số lượng plants, depots, customers
    I_size, J_size, K_size = map(int, lines[idx].split())
    idx += 1
    
    # ===== BƯỚC 2: Đọc chi phí mở facility =====
    # I dòng tiếp theo: chi phí mở từng plant
    f = [float(lines[idx + i]) for i in range(I_size)]
    idx += I_size
    
    # J dòng tiếp theo: chi phí mở từng depot
    g = [float(lines[idx + j]) for j in range(J_size)]
    idx += J_size
    
    # ===== BƯỚC 3: Đọc capacity và tọa độ =====
    # I dòng tiếp: capacity của từng plant (số nguyên hoặc thực)
    U_raw = [float(lines[idx + i]) for i in range(I_size)]
    idx += I_size
    
    # J dòng tiếp: capacity + tọa độ của depot (format: "V x")
    V_raw = []       # Capacity kho
    depot_x = []     # Tọa độ x của kho (dùng để tính chi phí vận chuyển)
    for j in range(J_size):
        parts = list(map(float, lines[idx + j].split()))
        V_raw.append(parts[0])                           # Capacity
        depot_x.append(parts[1] if len(parts) > 1 else 0)  # Tọa độ (nếu có)
    idx += J_size
    
    # K dòng tiếp: demand + tọa độ của customer (format: "D x")
    D = []           # Nhu cầu khách hàng
    customer_x = []  # Tọa độ x của khách hàng
    for k in range(K_size):
        parts = list(map(float, lines[idx + k].split()))
        D.append(parts[0])                               # Demand
        customer_x.append(parts[1] if len(parts) > 1 else 0)  # Tọa độ (nếu có)
    idx += K_size
    
    # ===== BƯỚC 4: Auto-scaling capacity để đảm bảo khả thi =====
    # Vấn đề: Dataset gốc có thể có capacity < demand → bài toán infeasible
    # Giải pháp: Tự động scale capacity lên để đủ phục vụ demand
    
    total_demand = sum(D)      # Tổng nhu cầu cần phục vụ
    total_U_raw = sum(U_raw)   # Tổng capacity plant gốc
    total_V_raw = sum(V_raw)   # Tổng capacity depot gốc
    
    # Scale factor cho plant: đảm bảo tổng capacity ≥ 110% tổng demand
    # 10% buffer để tránh trường hợp biên
    u_scale = max(1.0, (total_demand / total_U_raw) * 1.1)
    U = [u * u_scale for u in U_raw]  # Apply scale factor
    
    # Scale factor cho depot: tương tự cho throughput capacity
    v_scale = max(1.0, (total_demand / total_V_raw) * 1.1)
    V = [v * v_scale for v in V_raw]
    
    # In thông báo scale factor (để user biết capacity đã được điều chỉnh)
    print(f"  → Scale factors: U×{u_scale:.1f}, V×{v_scale:.1f} (đảm bảo feasible)")
    
    # ===== BƯỚC 5: Tạo tọa độ cho plants và tính ma trận chi phí =====
    # Plants không có tọa độ trong file → sinh ngẫu nhiên trong khoảng
    random.seed(42)  # Fixed seed để kết quả lặp lại được
    min_x = min(min(depot_x), min(customer_x))
    max_x = max(max(depot_x), max(customer_x))
    plant_x = [random.uniform(min_x, max_x) for _ in range(I_size)]
    
    # Tính ma trận chi phí c[i][j]: khoảng cách từ plant i đến depot j
    # Giả định: chi phí tỷ lệ thuận với khoảng cách Euclidean
    c = []
    for i in range(I_size):
        row = []
        for j in range(J_size):
            dist = abs(plant_x[i] - depot_x[j])  # Khoảng cách 1D
            row.append(dist)  # Chi phí = khoảng cách
        c.append(row)
    
    # Tính ma trận chi phí d[j][k]: khoảng cách từ depot j đến customer k
    d = []
    for j in range(J_size):
        row = []
        for k in range(K_size):
            dist = abs(depot_x[j] - customer_x[k])  # Khoảng cách 1D
            row.append(dist)  # Chi phí = khoảng cách
        d.append(row)
    
    # ===== BƯỚC 6: Tạo và trả về TSCFLPInstance =====
    return TSCFLPInstance(f=f, U=U, g=g, V=V, D=D, c=c, d=d)
