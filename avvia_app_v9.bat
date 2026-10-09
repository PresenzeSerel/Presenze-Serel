@echo off
echo ========================================================
echo   SEREL S.R.L. - Avvio Applicazione Presenze v9
echo ========================================================
echo.
echo Controllo ed installazione moduli richiesti...
py -m pip install streamlit pandas openpyxl
echo.
echo Avvio dell'applicazione Web...
py -m streamlit run app_presenze_v9.py
pause
