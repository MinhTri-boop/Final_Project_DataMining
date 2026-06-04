<#
.SYNOPSIS
Script khởi động toàn bộ môi trường từ đầu (End-to-End) dành cho Frontend Developer.

.DESCRIPTION
Script này sẽ thực hiện tự động các bước sau:
1. Chạy ETL Pipeline để làm sạch data và đưa vào PostgreSQL.
2. Thêm cột 'id' vào bảng Iceberg Cube để Java Backend map thành công.
3. Chạy thuật toán Machine Learning (Huấn luyện mô hình XGBoost/Random Forest).
4. Khởi động ML Service (Python FastAPI) ở một cửa sổ mới (Port 8000).
5. Biên dịch và Khởi động Core API (Java Spring Boot) ở một cửa sổ mới (Port 8080).
#>

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "🚀 GLOBAL SECURITY & RISK INTELLIGENCE - SETUP SCRIPT" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Chạy ETL Pipeline
Write-Host "[1/5] Running ETL Pipeline..." -ForegroundColor Yellow
python etl/run_etl_pipeline.py --input "data/raw/globalterrorismdb_0718dist.csv" --eda_outdir "data/processed/outputs_t01" --min_sup 20
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error running ETL!" -ForegroundColor Red
    exit 1
}
Write-Host "ETL Complete." -ForegroundColor Green
Write-Host ""

# 2. Thêm cột ID vào Database cho Backend Java
Write-Host "[2/5] Configuring Database..." -ForegroundColor Yellow
$pythonSqlScript = @"
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST','localhost'), 
        database=os.getenv('DB_NAME','gtd_dw'), 
        user=os.getenv('DB_USER','postgres'), 
        password=os.getenv('DB_PASSWORD','postgres')
    )
    cur = conn.cursor()
    cur.execute('ALTER TABLE iceberg_cube ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY;')
    conn.commit()
    cur.close()
    conn.close()
    print('Added ID column successfully!')
except Exception as e:
    print(f'Error adding ID column: {e}')
"@
python -c $pythonSqlScript
Write-Host "Database configuration complete." -ForegroundColor Green
Write-Host ""

# 3. Chạy Data Mining & Machine Learning
Write-Host "[3/5] Running ML & Data Mining..." -ForegroundColor Yellow
python ml/03_data_mining.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error running ML!" -ForegroundColor Red
    exit 1
}
Write-Host "ML Complete." -ForegroundColor Green
Write-Host ""

# 4. Khởi động ML Service (Python)
Write-Host "[4/5] Starting ML Service..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/c title ML Service & .\.venv\Scripts\activate & python -m uvicorn ml_service.main:app --host 127.0.0.1 --port 8000 --reload & pause"
Write-Host "ML Service started." -ForegroundColor Green
Write-Host ""

# 5. Khởi động Spring Boot Backend (Java)
Write-Host "[5/5] Starting Core API..." -ForegroundColor Yellow

# Load .env file into Environment Variables for Java
if (Test-Path ".env") {
    foreach($line in Get-Content .env) {
        if($line -match '^\s*#') { continue }
        if($line -match '^\s*(.+?)\s*=\s*(.*)') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
}

Set-Location -Path "backend/core-api"
$java21 = "C:\Program Files\Eclipse Adoptium\jdk-21.0.7.6-hotspot"
$mvnCmd = "F:\apache-maven-3.9.16-bin\apache-maven-3.9.16\bin\mvn.cmd"
Start-Process "cmd.exe" -ArgumentList "/c `"title Core API (Java Spring Boot) & set DB_PASSWORD=$env:DB_PASSWORD& set JAVA_HOME=$java21& set PATH=$java21\bin;%PATH%& `"$mvnCmd`" spring-boot:run & pause`""
Set-Location -Path "../.."
Write-Host "Core API started." -ForegroundColor Green
Write-Host ""

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "🎉 ENVIRONMENT IS READY!" -ForegroundColor Cyan
Write-Host "- ML Service is running at: http://localhost:8000" -ForegroundColor White
Write-Host "- Core API is running at:   http://localhost:8080" -ForegroundColor White
Write-Host "You can start coding the Frontend and calling APIs!" -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor Cyan
