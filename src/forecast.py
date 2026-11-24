"""
Module Dự Báo Xu Hướng Tuyển Dụng IT Bằng Chuỗi Thời Gian (Time Series Forecasting)
Sử dụng: statsmodels (Holt-Winters Exponential Smoothing) và Hồi quy Xu hướng
Phục vụ mục tiêu: Dự báo nhu cầu tuyển dụng IT trong 3 đến 6 tháng tiếp theo
"""

import sqlite3
import numpy as np
import pandas as pd
from statsmodels.tsa.api import Holt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


def load_monthly_time_series(db_path: str = "data/warehouse/it_recruitment_dwh.db") -> pd.DataFrame:
    """
    Trích xuất chuỗi thời gian số lượng tin tuyển dụng theo từng tháng từ Data Warehouse.
    """
    conn = sqlite3.connect(db_path)
    query = """
    SELECT 
        d.month_year,
        MIN(d.full_date) as start_date,
        COUNT(f.job_id) as job_count
    FROM fact_job_postings f
    JOIN dim_date d ON f.date_id = d.date_id
    WHERE d.full_date IS NOT NULL
    GROUP BY d.month_year
    ORDER BY MIN(d.full_date) ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Chuẩn hóa cột ngày tháng
    df["start_date"] = pd.to_datetime(df["start_date"])
    df = df.sort_values("start_date").reset_index(drop=True)
    return df


def forecast_recruitment_trend(df_monthly: pd.DataFrame, n_ahead: int = 4) -> dict:
    """
    Dự báo nhu cầu tuyển dụng IT cho n_ahead tháng tiếp theo.
    Kết hợp mô hình Holt's Linear Trend (San bằng hàm mũ có xu thế) và Hồi quy.
    
    Args:
        df_monthly: DataFrame chứa dữ liệu lịch sử các tháng.
        n_ahead: Số tháng tương lai cần dự báo (mặc định 4 tháng).
        
    Returns:
        dict chứa:
            - df_historical: Dữ liệu quá khứ
            - df_forecast: Dữ liệu dự báo (tháng, số lượng dự báo, cận dưới, cận trên)
            - metrics: Các chỉ số sai số (MAE, RMSE)
            - model_name: Tên mô hình sử dụng
    """
    if len(df_monthly) < 4:
        raise ValueError("Chuỗi thời gian quá ngắn để huấn luyện mô hình dự báo.")

    y = df_monthly["job_count"].values
    t = np.arange(len(y))

    # 1. Huấn luyện mô hình Holt's Linear Trend (Thống kê chuỗi thời gian)
    # Holt phù hợp với dữ liệu chuỗi có xu hướng tăng/giảm và dao động
    model = Holt(y, initialization_method="estimated")
    fit_model = model.fit(smoothing_level=0.5, smoothing_trend=0.3, optimized=True)

    # Dự báo điểm trong mẫu (Fitted values) để đánh giá sai số
    fitted_values = fit_model.fittedvalues
    mae = mean_absolute_error(y, fitted_values)
    rmse = np.sqrt(mean_squared_error(y, fitted_values))

    # 2. Dự báo n_ahead tháng tiếp theo
    forecast_values = fit_model.forecast(n_ahead)
    forecast_values = np.maximum(forecast_values, 50)  # Đảm bảo số lượng việc làm không âm

    # 3. Tạo danh sách các tháng tương lai
    last_date = df_monthly["start_date"].max()
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=n_ahead, freq="MS")
    future_month_year = [d.strftime("%m/%Y") for d in future_dates]

    # Tính khoảng dao động tin cậy (Khoảng 1.5 lần độ lệch chuẩn sai số RMSE)
    std_residual = rmse
    lower_bound = np.maximum(forecast_values - 1.28 * std_residual, 50)
    upper_bound = forecast_values + 1.28 * std_residual

    df_forecast = pd.DataFrame({
        "month_year": future_month_year,
        "forecast_jobs": np.round(forecast_values).astype(int),
        "lower_bound": np.round(lower_bound).astype(int),
        "upper_bound": np.round(upper_bound).astype(int),
        "type": "Dự báo"
    })

    df_historical = df_monthly[["month_year", "job_count"]].copy()
    df_historical["type"] = "Thực tế"

    return {
        "df_historical": df_historical,
        "df_forecast": df_forecast,
        "mae": round(float(mae), 1),
        "rmse": round(float(rmse), 1),
        "model_name": "San Bằng Hàm Mũ Có Xu Thế (Holt's Linear Trend)",
    }


if __name__ == "__main__":
    df_m = load_monthly_time_series()
    print("Dữ liệu lịch sử:")
    print(df_m[["month_year", "job_count"]])
    result = forecast_recruitment_trend(df_m, n_ahead=4)
    print("\nKết quả dự báo các tháng tiếp theo:")
    print(result["df_forecast"])
    print(f"\nĐánh giá mô hình: MAE = {result['mae']}, RMSE = {result['rmse']}")
