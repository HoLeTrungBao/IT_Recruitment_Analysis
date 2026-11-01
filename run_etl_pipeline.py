"""
=============================================================
  ETL Pipeline Điều phối - Dự án IT Recruitment Analysis
=============================================================
  Chạy toàn bộ luồng ETL từ dữ liệu thô đến Data Warehouse.
  
  Cách sử dụng:
    python run_etl_pipeline.py               # Chạy toàn bộ pipeline
    python run_etl_pipeline.py --step extract    # Chỉ chạy bước Extract
    python run_etl_pipeline.py --step transform  # Chỉ chạy bước Transform
    python run_etl_pipeline.py --step load       # Chỉ chạy bước Load

  Thiết kế lũy đẳng (Idempotent):
    Bạn có thể chạy script này bao nhiêu lần tùy thích,
    dữ liệu trong Data Warehouse LUÔN LUÔN chính xác,
    KHÔNG BAO GIỜ bị trùng lặp hay đè sai.
=============================================================
"""
import os
import sys
import time
import argparse

# Thêm thư mục gốc của dự án vào sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from src.extract import extract_all
from src.transform import transform_all
from src.load import load_to_warehouse

# Các đường dẫn thư mục
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
WAREHOUSE_DIR = os.path.join(BASE_DIR, "data", "warehouse")


def run_extract():
    """Bước 1: Trích xuất dữ liệu thô."""
    print("=" * 60)
    print("[BƯỚC 1/3] EXTRACT - Trích xuất dữ liệu từ các tệp thô")
    print("=" * 60)
    raw_dfs = extract_all(RAW_DIR)
    return raw_dfs


def run_transform(raw_dfs):
    """Bước 2: Biến đổi và làm sạch dữ liệu."""
    print()
    print("=" * 60)
    print("[BƯỚC 2/3] TRANSFORM - Làm sạch, chuẩn hóa & hợp nhất")
    print("=" * 60)
    df_clean = transform_all(raw_dfs)
    return df_clean


def run_load(df_clean):
    """Bước 3: Nạp dữ liệu vào Data Warehouse (Star Schema)."""
    print()
    print("=" * 60)
    print("[BƯỚC 3/3] LOAD - Nạp vào Data Warehouse (Star Schema)")
    print("=" * 60)
    tables = load_to_warehouse(df_clean, WAREHOUSE_DIR)
    return tables


def main():
    parser = argparse.ArgumentParser(
        description="ETL Pipeline - IT Recruitment Analysis"
    )
    parser.add_argument(
        "--step",
        choices=["extract", "transform", "load"],
        default=None,
        help="Chạy riêng một bước cụ thể. Mặc định: chạy toàn bộ pipeline.",
    )
    args = parser.parse_args()

    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║    ETL PIPELINE - IT RECRUITMENT DATA ANALYSIS          ║")
    print("║    Dự án Phân tích Dữ liệu Tuyển dụng IT Việt Nam      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    start_time = time.time()

    if args.step == "extract":
        run_extract()
    elif args.step == "transform":
        raw_dfs = run_extract()
        run_transform(raw_dfs)
    elif args.step == "load":
        raw_dfs = run_extract()
        df_clean = run_transform(raw_dfs)
        run_load(df_clean)
    else:
        # Chạy toàn bộ pipeline E -> T -> L
        raw_dfs = run_extract()
        df_clean = run_transform(raw_dfs)
        tables = run_load(df_clean)

    elapsed = time.time() - start_time

    print()
    print("=" * 60)
    print(f"  PIPELINE HOÀN TẤT THÀNH CÔNG TRONG {elapsed:.1f} GIÂY!")
    print()
    print(f"  Data Warehouse: {WAREHOUSE_DIR}")
    print(f"  SQLite DB:      {os.path.join(WAREHOUSE_DIR, 'it_recruitment_dwh.db')}")
    print()
    print("  Bước tiếp theo: Mở Power BI -> Get Data -> Text/CSV")
    print(f"  Trỏ vào thư mục: {WAREHOUSE_DIR}")
    print("  Sau đó bấm Refresh để cập nhật Dashboard.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
