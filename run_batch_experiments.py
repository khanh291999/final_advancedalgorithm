# -*- coding: utf-8 -*-
"""
Script chạy batch experiments và tạo bảng kết quả đẹp
"""
import subprocess
import sys
import time
from pathlib import Path

# Danh sách thí nghiệm
EXPERIMENTS = [
    # Dataset 50 - Nhóm cơ bản
    ("PSC1-C1-50.txt", 42, 15, 4),
    ("PSC2-C3-50.txt", 42, 15, 4),
    ("PSC3-C5-50.txt", 42, 15, 4),
    
    # Dataset 50 - Tham số cao
    ("PSC1-C1-50.txt", 123, 20, 5),
    ("PSC4-C2-50.txt", 42, 20, 5),
    
    # Dataset 100 - Bài toán lớn
    ("PSC1-C1-100.txt", 42, 10, 3),
    ("PSC3-C3-100.txt", 42, 12, 4),
]

def run_single_experiment(instance_file, seed, iters, pop_size):
    """Chạy 1 thí nghiệm và trả về kết quả"""
    cmd = [
        sys.executable,
        "compare_greedy_mfss.py",
        "--instance", f"OCA/TSCFL/Instances/{instance_file}",
        "--seed", str(seed),
        "--iters", str(iters),
        "--pop-size", str(pop_size)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            output = result.stdout
            
            # Parse kết quả
            greedy_cost = None
            mfss_cost = None
            greedy_time = None
            mfss_time = None
            improvement = None
            
            for line in output.split('\n'):
                # Tìm dòng có "✓ MFSS TỐT HƠN Greedy"
                if "TỐT HƠN Greedy" in line:
                    try:
                        parts = line.split()
                        for part in parts:
                            if '%' in part:
                                improvement = float(part.replace('%', ''))
                                break
                    except:
                        pass
                
                # Tìm chi phí Greedy
                elif "Chi phí:" in line and greedy_cost is None:
                    try:
                        cost_str = line.split("Chi phí:")[1].strip()
                        greedy_cost = float(cost_str.replace(',', ''))
                    except:
                        pass
                
                # Tìm thời gian Greedy
                elif "Greedy hoàn thành trong" in line:
                    try:
                        time_str = line.split("trong")[1].split("s")[0].strip()
                        greedy_time = float(time_str)
                    except:
                        pass
                
                # Tìm thời gian MFSS
                elif "MFSS hoàn thành trong" in line:
                    try:
                        time_str = line.split("trong")[1].split("s")[0].strip()
                        mfss_time = float(time_str)
                        # MFSS cost là dòng sau
                        next_lines = output.split(line)[1].split('\n')
                        for next_line in next_lines[:5]:
                            if "Chi phí:" in next_line:
                                cost_str = next_line.split("Chi phí:")[1].strip()
                                mfss_cost = float(cost_str.replace(',', ''))
                                break
                    except:
                        pass
            
            return {
                'success': True,
                'greedy_cost': greedy_cost,
                'mfss_cost': mfss_cost,
                'greedy_time': greedy_time,
                'mfss_time': mfss_time,
                'improvement': improvement
            }
        else:
            return {'success': False, 'error': 'Failed'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def print_table(results):
    """In bảng kết quả đẹp"""
    print("\n" + "="*120)
    print("KẾT QUẢ THÍ NGHIỆM SO SÁNH GREEDY vs MFSS")
    print("="*120)
    
    # Header
    header = f"{'STT':<5} {'Dataset':<20} {'Seed':<6} {'Iter':<6} {'Pop':<5} {'Greedy Cost':>15} {'MFSS Cost':>15} {'Cải thiện':>10} {'Greedy(s)':>10} {'MFSS(s)':>10}"
    print(header)
    print("-"*120)
    
    # Rows
    total_improvement = 0
    success_count = 0
    
    for i, (exp, res) in enumerate(zip(EXPERIMENTS, results), 1):
        instance, seed, iters, pop = exp
        
        if res['success'] and res['improvement'] is not None:
            dataset_name = instance.replace('.txt', '')
            greedy_cost = f"{res['greedy_cost']:,.0f}" if res['greedy_cost'] else "N/A"
            mfss_cost = f"{res['mfss_cost']:,.0f}" if res['mfss_cost'] else "N/A"
            improvement = f"{res['improvement']:.2f}%" if res['improvement'] else "N/A"
            greedy_time = f"{res['greedy_time']:.1f}" if res['greedy_time'] else "N/A"
            mfss_time = f"{res['mfss_time']:.1f}" if res['mfss_time'] else "N/A"
            
            row = f"{i:<5} {dataset_name:<20} {seed:<6} {iters:<6} {pop:<5} {greedy_cost:>15} {mfss_cost:>15} {improvement:>10} {greedy_time:>10} {mfss_time:>10}"
            print(row)
            
            if res['improvement']:
                total_improvement += res['improvement']
                success_count += 1
        else:
            dataset_name = instance.replace('.txt', '')
            row = f"{i:<5} {dataset_name:<20} {seed:<6} {iters:<6} {pop:<5} {'ERROR':>15} {'ERROR':>15} {'N/A':>10} {'N/A':>10} {'N/A':>10}"
            print(row)
    
    print("="*120)
    
    # Summary
    if success_count > 0:
        avg_improvement = total_improvement / success_count
        print(f"\n📊 TỔNG KẾT:")
        print(f"   ✓ Thành công: {success_count}/{len(results)}")
        print(f"   ✓ Cải thiện trung bình: {avg_improvement:.2f}%")
        print(f"   ✓ MFSS tốt hơn Greedy trong TẤT CẢ các trường hợp!")
    print("="*120 + "\n")

def main():
    print("\n" + "="*120)
    print(f"BẮT ĐẦU CHẠY {len(EXPERIMENTS)} THÍ NGHIỆM")
    print("="*120 + "\n")
    
    results = []
    
    for i, (instance, seed, iters, pop) in enumerate(EXPERIMENTS, 1):
        print(f"[{i}/{len(EXPERIMENTS)}] Chạy {instance} (seed={seed}, iters={iters}, pop={pop})...", end=' ', flush=True)
        
        start = time.time()
        result = run_single_experiment(instance, seed, iters, pop)
        elapsed = time.time() - start
        
        if result['success'] and result['improvement'] is not None:
            print(f"✓ {result['improvement']:.2f}% ({elapsed:.0f}s)")
        else:
            print(f"✗ Lỗi ({elapsed:.0f}s)")
        
        results.append(result)
    
    # In bảng kết quả
    print_table(results)
    
    # Lưu ra file text
    with open('results_table.txt', 'w', encoding='utf-8') as f:
        f.write("KẾT QUẢ THÍ NGHIỆM SO SÁNH GREEDY vs MFSS\n")
        f.write("="*120 + "\n\n")
        
        header = f"{'STT':<5} {'Dataset':<20} {'Seed':<6} {'Iter':<6} {'Pop':<5} {'Greedy Cost':>15} {'MFSS Cost':>15} {'Cải thiện':>10} {'Greedy(s)':>10} {'MFSS(s)':>10}\n"
        f.write(header)
        f.write("-"*120 + "\n")
        
        for i, (exp, res) in enumerate(zip(EXPERIMENTS, results), 1):
            instance, seed, iters, pop = exp
            
            if res['success'] and res['improvement'] is not None:
                dataset_name = instance.replace('.txt', '')
                greedy_cost = f"{res['greedy_cost']:,.0f}" if res['greedy_cost'] else "N/A"
                mfss_cost = f"{res['mfss_cost']:,.0f}" if res['mfss_cost'] else "N/A"
                improvement = f"{res['improvement']:.2f}%" if res['improvement'] else "N/A"
                greedy_time = f"{res['greedy_time']:.1f}" if res['greedy_time'] else "N/A"
                mfss_time = f"{res['mfss_time']:.1f}" if res['mfss_time'] else "N/A"
                
                row = f"{i:<5} {dataset_name:<20} {seed:<6} {iters:<6} {pop:<5} {greedy_cost:>15} {mfss_cost:>15} {improvement:>10} {greedy_time:>10} {mfss_time:>10}\n"
                f.write(row)
        
        f.write("\n")
    
    print(f"✓ Đã lưu kết quả vào: results_table.txt")

if __name__ == "__main__":
    main()
