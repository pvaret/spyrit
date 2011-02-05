@echo off

REM Make sure that your Python installation is on the path, and that
REM pyinstaller is in your home!

python -O "%HOMEPATH%\pyinstaller\Configure.py"
python "%HOMEPATH%\pyinstaller\Makespec.py" --onefile --windowed --icon=..\..\resources\spyrit-icon.ico ..\..\spyrit.py
python -O "%HOMEPATH%\pyinstaller\Build.py" spyrit.spec
