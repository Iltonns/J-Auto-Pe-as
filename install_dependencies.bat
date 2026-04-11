@echo off
REM Script para instalar dependências no Windows
REM Execute este arquivo clicando 2 vezes ou no terminal:
REM   install_dependencies.bat

echo.
echo ============================================================
echo  Instalando dependencias - FG Auto Pecas
echo ============================================================
echo.

REM Ativar o ambiente virtual
call .venv\Scripts\activate.bat

REM Instalar os pacotes essenciais
echo Instalando Flask...
python -m pip install Flask --quiet

echo Instalando werkzeug...
python -m pip install werkzeug --quiet

echo Instalando psycopg2-binary...
python -m pip install psycopg2-binary --quiet

echo Instalando python-dotenv...
python -m pip install python-dotenv --quiet

echo Instalando pytz...
python -m pip install pytz --quiet

echo.
echo ============================================================
echo  Instalacao concluida!
echo ============================================================
echo.
pause
