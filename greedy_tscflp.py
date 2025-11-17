# greedy_tscflp.py
"""
Cài đặt Algorithm 1: Greedy Algorithm for the TSCFLP.

- Sinh 1 lời giải khả thi bằng cách:
  + chọn dần các primary (nhà máy) theo heuristic h_p(i, S)
  + với mỗi primary, chọn các secondary (kho) theo h_s(i, j, S)
  + với mỗi secondary, gán cho các khách có chi phí d_jk nhỏ nhất
- Sau khi đã chọn tập facility, gọi lại MILP để tối ưu luồng (SolveMinCostFlow)
"""

import random
from typing import List, Tuple
import numpy as np

from tscflp_core import TSCFLPInstance, Solution, solve_full_mip


def greedy_tscflp(inst: TSCFLPInstance, rcl_size: int = 1) -> Solution:
    """
    Cài đặt gần sát Algorithm 1 trong paper.

    Parameters
    ----------
    inst : TSCFLPInstance
        Instance bài toán.
    rcl_size : int
        - Nếu rcl_size = 1  -> thuần greedy (luôn chọn ứng viên tốt nhất).
        - Nếu rcl_size > 1  -> dùng RCL (Restricted Candidate List):
                              chọn ngẫu nhiên trong top rcl_size ứng viên tốt nhất.
                              Dùng khi cần randomization để sinh nhiều lời giải khác nhau
                              (ví dụ dùng cho population khởi tạo của MFSS).

    Returns
    -------
    Solution
        Lời giải (pattern facility mở + cost) sau khi giải lại MILP để tối ưu luồng.
    """
    # ===== KHỞI TẠO DỮ LIỆU =====
    I, J, K = inst.I, inst.J, inst.K  # Tập chỉ số facilities và customers
    f, g, U0, V0, D0 = inst.f, inst.g, inst.U, inst.V, inst.D  # Chi phí, capacity, demand gốc
    c, d = inst.c, inst.d  # Ma trận chi phí vận chuyển

    # Copy capacity/demand vì trong thuật toán sẽ giảm dần khi phân phối hàng
    U = U0.copy()   # Capacity còn lại của từng plant
    V = V0.copy()   # Capacity còn lại của từng depot  
    D = D0.copy()   # Demand còn lại của từng customer

    total_demand = sum(D)  # Tổng demand cần phục vụ

    # Tập facility đã được chọn mở
    selected_I = set()  # Plants đã mở
    selected_J = set()  # Depots đã mở

    # Tập khách hàng chưa được phục vụ đầy đủ
    unmet_customers = set(k for k in K if D[k] > 0)

    def choose_with_rcl(scores: List[Tuple[int, float]], rcl_sz: int):
        """
        Chọn facility từ RCL (Restricted Candidate List).
        
        Args:
            scores: Danh sách (index, heuristic_value) của các ứng viên
            rcl_sz: Kích thước RCL (số ứng viên tốt nhất xét)
        
        Returns:
            index của facility được chọn
            
        Cách hoạt động:
        - Sắp xếp ứng viên theo heuristic (tăng dần = tốt hơn)
        - Lấy top rcl_sz ứng viên tốt nhất
        - Chọn ngẫu nhiên 1 trong số đó
        
        Lưu ý: rcl_sz=1 → pure greedy (luôn chọn tốt nhất)
        """
        scores = sorted(scores, key=lambda x: x[1])  # Sắp xếp tăng dần
        rcl = scores[:max(1, min(rcl_sz, len(scores)))]  # Lấy top rcl_sz
        return random.choice(rcl)[0]  # Chọn ngẫu nhiên

    # ===== VÒNG LẶP CHÍNH: Xây dựng nghiệm dần =====
    # Lặp cho đến khi phục vụ hết demand
    while total_demand > 1e-6:
        
        # ===== BƯỚC 1: Chọn plant (primary facility) =====
        # Chỉ xét plants còn capacity
        cand_I = [i for i in I if U[i] > 1e-6]
        if not cand_I:
            raise RuntimeError("Không đủ capacity primary để đáp ứng demand")

        # Depots còn capacity (dùng để tính heuristic)
        J_available = [j for j in J if V[j] > 1e-6]

        # Tính heuristic h_p(i, S) cho từng plant
        scores_i = []
        for i in cand_I:
            # h_p(i) = (chi phí mở / capacity) + (trung bình chi phí đến depots)
            # → Ưu tiên plant có: chi phí mở thấp, capacity lớn, gần depots
            avg_c = np.mean([c[i][j] for j in J_available]) if J_available else 0.0
            hp = f[i] / (U0[i] + 1e-9) + avg_c  # +1e-9 tránh chia 0
            scores_i.append((i, hp))

        # Chọn plant theo RCL
        i_star = choose_with_rcl(scores_i, rcl_size)
        selected_I.add(i_star)  # Đánh dấu plant đã được mở

        # Lượng hàng plant i_star cung cấp = min(demand còn lại, capacity còn lại)
        U_used = min(total_demand, U[i_star])
        U[i_star] -= U_used          # Giảm capacity còn lại
        remaining_from_i = U_used    # Lượng hàng từ i_star cần phân phối đến depots
        total_demand -= U_used       # Giảm tổng demand còn lại

        # ===== BƯỚC 2: Chọn depots (secondary facilities) để nhận hàng từ plant =====
        # Lặp cho đến khi phân phối hết remaining_from_i
        while remaining_from_i > 1e-6:
            # Chỉ xét depots còn capacity
            cand_J = [j for j in J if V[j] > 1e-6]
            if not cand_J:
                raise RuntimeError("Không đủ capacity secondary để nhận hàng")

            # Tính heuristic h_s(i,j,S) cho từng depot
            scores_j = []
            for j in cand_J:
                # h_s(i,j) = (chi phí i→j) + (chi phí mở / capacity) + (trung bình chi phí đến customers)
                # → Ưu tiên depot: gần plant, chi phí mở thấp, capacity lớn, gần customers
                avg_d = np.mean([d[j][k] for k in unmet_customers]) if unmet_customers else 0.0
                hs = c[i_star][j] + g[j] / (V0[j] + 1e-9) + avg_d
                scores_j.append((j, hs))

            # Chọn depot theo RCL
            j_star = choose_with_rcl(scores_j, rcl_size)
            selected_J.add(j_star)  # Đánh dấu depot đã được mở

            # Lượng hàng chuyển từ i_star đến j_star
            V_used = min(remaining_from_i, V[j_star])
            V[j_star] -= V_used         # Giảm capacity depot còn lại
            remaining_from_i -= V_used  # Giảm lượng hàng cần phân phối

            remaining_from_j = V_used  # Lượng hàng depot j_star cần phân phối cho customers

            # ===== BƯỚC 3: Gán hàng từ depot cho customers =====
            # Lặp cho đến khi phân phối hết remaining_from_j
            while remaining_from_j > 1e-6:
                # Chỉ xét customers còn demand
                cand_K = [k for k in unmet_customers if D[k] > 1e-6]
                if not cand_K:
                    break  # Không còn customer nào cần phục vụ

                # Heuristic h_c(j,k) = d[j][k] (chi phí vận chuyển depot → customer)
                # → Ưu tiên customer gần depot nhất
                scores_k = [(k, d[j_star][k]) for k in cand_K]
                k_star = choose_with_rcl(scores_k, rcl_size)

                # Lượng hàng giao cho customer k_star
                amount = min(remaining_from_j, D[k_star])
                D[k_star] -= amount           # Giảm demand còn lại
                remaining_from_j -= amount    # Giảm hàng cần phân phối

                # Nếu customer đã được phục vụ đủ → xóa khỏi danh sách
                if D[k_star] <= 1e-6 and k_star in unmet_customers:
                    unmet_customers.remove(k_star)

    # ===== BƯỚC CUỐI: Giải lại MILP để tối ưu luồng =====
    # Greedy đã chọn xong tập facility mở/đóng
    # Giờ cố định pattern này, giải MILP để tìm luồng phân phối tối ưu
    # → Đảm bảo nghiệm cuối cùng khả thi và có chi phí chính xác
    fixed = {
        'I': {i: (1 if i in selected_I else 0) for i in I},  # Cố định plants
        'J': {j: (1 if j in selected_J else 0) for j in J},  # Cố định depots
    }
    
    # Gọi solver MILP với fixed-set constraints
    sol = solve_full_mip(inst, fixed=fixed, verbose=False)
    return sol


if __name__ == "__main__":
    import sys
    import io
    import time
    
    # Fix UTF-8 encoding cho console Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    from tscflp_core import load_instance_from_file
    
    print("=" * 70)
    print("CHẠY GREEDY (Algorithm 1) TRÊN DATASET THẬT")
    print("=" * 70)
    
    # Load instance từ file
    filepath = "OCA/TSCFL/Instances/PSC1-C1-50.txt"
    print(f"\n→ Đang load instance: {filepath}")
    inst = load_instance_from_file(filepath)
    print(f"  I={len(inst.I)} plants, J={len(inst.J)} depots, K={len(inst.K)} customers")
    print(f"  Tổng demand: {sum(inst.D):.0f}")
    
    # Chạy Greedy
    print("\n→ Chạy Greedy (rcl_size=1 - pure greedy)...")
    start_time = time.time()
    sol = greedy_tscflp(inst, rcl_size=1)
    elapsed = time.time() - start_time
    
    # Hiển thị kết quả
    print("\n" + "=" * 70)
    print("KẾT QUẢ")
    print("=" * 70)
    print(f"Chi phí: {sol.cost:,.2f}")
    print(f"Thời gian: {elapsed:.2f}s")
    print(f"Số plant mở: {sum(sol.open_I)}/{len(inst.I)}")
    print(f"Số depot mở: {sum(sol.open_J)}/{len(inst.J)}")
    print("=" * 70)
