#!/bin/bash
# wrapper script for cron job
# runs instagram analytics sync to notion

cd /Users/athenahernandez/Documents/code-with-coco/content-manager
/opt/homebrew/bin/python3 sync_to_notion.py
