@echo off
echo ============================================================
echo SMART PARK - LOCALHOST DEPLOYMENT
echo ============================================================
echo.
echo Project Location: %CD%
echo.
echo Steps to run the application:
echo 1. Make sure you're in the project directory
echo 2. Run the Django development server
echo 3. Open your browser to http://localhost:8000/
echo.
echo Running Django system check...
python manage.py check
echo.
if %ERRORLEVEL% EQU 0 (
    echo System check passed!
    echo.
    echo Running all tests...
    python manage.py test parking
    echo.
    if %ERRORLEVEL% EQU 0 (
        echo All tests passed!
        echo.
        echo Starting Django development server...
        echo Press Ctrl+C to stop the server
        echo.
        python manage.py runserver
    ) else (
        echo Tests failed. Please fix the issues before running the server.
    )
) else (
    echo System check failed. Please fix the issues before running the server.
)