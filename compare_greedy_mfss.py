# compare_greedy_mfss.py
# -*- coding: utf-8 -*-
"""
Script so sánh hiệu quả giữa Greedy và MFSS trên dataset thật.
"""

import sys
import io
import argparse
import time
import random
import numpy as np
from tscflp_core import load_instance_from_file
from greedy_tscflp import greedy_tscflp
from mfss_tscflp import mfss

# Fix encoding cho Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='So sánh Greedy vs MFSS trên TSCFLP')
    parser.add_argument('--instance', type=str, required=True,
                        help='Đường dẫn đến file instance (VD: OCA/TSCFL/Instances/PSC1-C1-50.txt)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed (default: 42)')
    parser.add_argument('--iters', type=int, default=50,
                        help='Số iterations cho MFSS (default: 50)')
    parser.add_argument('--pop-size', type=int, default=5,
                        help='Kích thước population cho MFSS (default: 5)')
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    np.random.seed(args.seed)
    
    print("="*70)
    print(f"Đang load instance từ: {args.instance}")
    
    try:
        inst = load_instance_from_file(args.instance)
        I_size = len(inst.f)
        J_size = len(inst.g)
        K_size = len(inst.D)
        total_demand = sum(inst.D)
        
        print(f"I={I_size} plants, J={J_size} depots, K={K_size} customers – |D|={int(total_demand)} tổng demand")
        print("="*70)
    except Exception as e:
        print(f"Lỗi khi load instance: {e}")
        return
    
    # ========== 1. Chạy GREEDY ==========
    print("\n[1] Xây dựng nghiệm bằng GREEDY (rcl_size=1)...")
    start_time = time.time()
    
    try:
        sol_greedy = greedy_tscflp(inst, rcl_size=1)
        greedy_time = time.time() - start_time
        
        print(f"  ✓ Greedy hoàn thành trong {greedy_time:.2f}s")
        print(f"  - Chi phí: {sol_greedy.cost:,.2f}")
        print(f"  - Số plant mở: {sum(sol_greedy.open_I)}/{I_size}")
        print(f"  - Số depot mở: {sum(sol_greedy.open_J)}/{J_size}")
    except Exception as e:
        print(f"  ✗ Greedy thất bại: {e}")
        sol_greedy = None
        greedy_time = 0
    
    # ========== 2. Chạy MFSS ==========
    print(f"\n[2] Chạy MFSS (pop_size={args.pop_size}, iterations={args.iters})...")
    start_time = time.time()
    
    try:
        sol_mfss = mfss(
            inst,
            Npop=args.pop_size,
            max_iter=args.iters,
            tinit=30.0
        )
        mfss_time = time.time() - start_time
        
        print(f"  ✓ MFSS hoàn thành trong {mfss_time:.2f}s")
        print(f"  - Chi phí: {sol_mfss.cost:,.2f}")
        print(f"  - Số plant mở: {sum(sol_mfss.open_I)}/{I_size}")
        print(f"  - Số depot mở: {sum(sol_mfss.open_J)}/{J_size}")
    except Exception as e:
        print(f"  ✗ MFSS thất bại: {e}")
        sol_mfss = None
        mfss_time = 0
    
    # ========== 3. SO SÁNH KẾT QUẢ ==========
    print("\n" + "="*70)
    print("KẾT QUẢ SO SÁNH")
    print("="*70)
    
    if sol_greedy and sol_mfss:
        improvement = ((sol_greedy.cost - sol_mfss.cost) / sol_greedy.cost) * 100
        
        print(f"\n{'Phương pháp':<15} {'Chi phí':>20} {'Thời gian':>15} {'Cải thiện':>15}")
        print("-"*70)
        print(f"{'Greedy':<15} {sol_greedy.cost:>20,.2f} {greedy_time:>14.2f}s {'-':>15}")
        print(f"{'MFSS':<15} {sol_mfss.cost:>20,.2f} {mfss_time:>14.2f}s {improvement:>14.2f}%")
        print("-"*70)
        
        if improvement > 0:
            print(f"\n✓ MFSS TỐT HƠN Greedy {improvement:.2f}%")
            print(f"  Tiết kiệm được: {sol_greedy.cost - sol_mfss.cost:,.2f}")
        elif improvement < 0:
            print(f"\n✗ MFSS KÉMHƠN Greedy {abs(improvement):.2f}%")
        else:
            print(f"\n= Hai phương pháp cho kết quả tương đương")
    elif sol_greedy:
        print(f"\nChỉ có Greedy thành công với chi phí: {sol_greedy.cost:,.2f}")
    elif sol_mfss:
        print(f"\nChỉ có MFSS thành công với chi phí: {sol_mfss.cost:,.2f}")
    else:
        print("\nCả hai phương pháp đều thất bại!")
    
    print("="*70)


if __name__ == "__main__":
    main()
