"""
Script truy vấn nhanh dữ liệu trực tiếp từ Data Warehouse (SQLite)
Phục vụ Demo trực tiếp trong buổi báo cáo.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'warehouse', 'it_recruitment_dwh.db')

def run_queries():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 65)
    print(" 🎯 TRUY VẤN 1: TỔNG QUAN NGUỒN DỮ LIỆU TRONG DATA WAREHOUSE")
    print("=" * 65)
    cursor.execute("""
        SELECT source, COUNT(*) 
        FROM fact_job_postings 
        GROUP BY source 
        ORDER BY COUNT(*) DESC;
    """)
    for src, cnt in cursor.fetchall():
        print(f"  • Nguồn {src:<16}: {cnt:>5} tin sạch")

    print("\n" + "=" * 65)
    print(" 🎯 TRUY VẤN 2: TOP 5 KỸ NĂNG CÔNG NGHỆ ĐƯỢC SĂN ĐÓN NHẤT")
    print("=" * 65)
    query2 = """
    SELECT 
        ds.skill_name AS [Kỹ năng],
        COUNT(*) AS [Số tin tuyển dụng]
    FROM fact_job_skills fjs
    JOIN dim_skill ds ON fjs.skill_id = ds.skill_id
    GROUP BY ds.skill_name
    ORDER BY [Số tin tuyển dụng] DESC
    LIMIT 5;
    """
    cursor.execute(query2)
    rows2 = cursor.fetchall()
    
    print(f"{'Hạng':<6} | {'Kỹ năng công nghệ':<22} | {'Số tin tuyển dụng':<18}")
    print("-" * 55)
    for idx, (skill, cnt) in enumerate(rows2, 1):
        print(f"#{idx:<5} | {skill:<22} | {cnt:>8} tin")

    print("\n" + "=" * 65)
    print(" 📈 TRUY VẤN 3: XU HƯỚNG NHU CẦU TOP 3 KỸ NĂNG THEO THỜI GIAN")
    print("=" * 65)
    query3 = """
    SELECT 
        dd.month_year AS [Thời gian],
        ds.skill_name AS [Kỹ năng],
        COUNT(*) AS [Số lượt yêu cầu]
    FROM fact_job_skills fjs
    JOIN dim_skill ds ON fjs.skill_id = ds.skill_id
    JOIN dim_date dd ON fjs.date_id = dd.date_id
    WHERE ds.skill_name IN ('JavaScript', 'Java', 'Python')
    GROUP BY dd.month_year, ds.skill_name
    ORDER BY dd.month_year, [Số lượt yêu cầu] DESC
    LIMIT 12;
    """
    cursor.execute(query3)
    rows3 = cursor.fetchall()
    
    print(f"{'Thời gian':<12} | {'Kỹ năng':<15} | {'Nhu cầu tuyển dụng':<18}")
    print("-" * 55)
    current_month = None
    for month, skill, cnt in rows3:
        if current_month != month:
            if current_month is not None:
                print("-" * 55)
            current_month = month
        print(f"{month:<12} | {skill:<15} | {cnt:>8} tin")

    print("=" * 65)
    conn.close()

if __name__ == '__main__':
    run_queries()
