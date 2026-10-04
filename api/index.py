# -*- coding: utf-8 -*-
"""
Vercel Serverless Function WSGI Entrypoint
"""

import os
import sys

# 프로젝트 루트 디렉터리를 sys.path에 추가하여 app 및 database 모듈을 임포트할 수 있도록 설정
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from app import app

# Vercel이 'app' 객체를 WSGI 앱으로 인식합니다.
if __name__ == "__main__":
    app.run()
