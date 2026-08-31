#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Keepalive Foresight - Script de Inicializacao da API FastAPI Cloud
Inicia o servidor uvicorn na porta 8000 escutando em todas as interfaces (0.0.0.0)
"""

import sys
import os
import uvicorn
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

if __name__ == "__main__":
    print("\n=======================================================")
    print("   ⚡ KEEPALIVE FORESIGHT - BACKEND CLOUD FASTAPI")
    print("   API de Telemetria & Motor Dead Man's Switch")
    print("=======================================================\n")
    print("🚀 Servidor ouvindo em: http://0.0.0.0:8000")
    print("📖 Documentacao Swagger: http://localhost:8000/docs")
    print("🔍 Endpoint da Sonda: http://<SEU_IP_LOCAL>:8000/api/v1/telemetry\n")
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, app_dir=str(BACKEND_DIR))
