#!/bin/bash
set -e

python -m alembic upgrade head
uvicorn main:app --reload
