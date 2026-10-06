Write-Host "Starting NetScope Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload`""

Write-Host "Starting NetScope Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command `"cd frontend; npm run dev`""

Write-Host "NetScope is starting! Check the new windows for progress."
