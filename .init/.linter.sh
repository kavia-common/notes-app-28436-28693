#!/bin/bash
cd /home/kavia/workspace/code-generation/notes-app-28436-28693/BackendAPIContainer
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

