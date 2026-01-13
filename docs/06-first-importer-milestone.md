# First Automation Milestone: importer_queue.py

## Summary
The first automated data input into Kronox has been successfully implemented.

A Python script (`importer_queue.py`) is now able to write structured data
directly into the Google Sheets engine, respecting the defined data contract.

This marks the transition from a fully manual system to an automated pipeline.

---

## What works
- Python can authenticate against Google Sheets
- Data is written into the correct sheet (`Registro` / `Nominas`)
- Column formats are respected (dates, time, decimals)
- No calculated cells are overwritten

---

## What this script does NOT do
- It does not calculate payroll
- It does not interpret natural language
- It does not validate business logic

Its only responsibility is:
**move validated data into the calculation engine**

---

## Current input strategy
- Inputs are provided in a structured format (manual / queued)
- Each input maps 1:1 to the data contract
- Errors stop execution instead of silently failing

---

## Why this matters
This milestone proves that:
- The data model is stable
- The Google Sheets engine can be automated safely
- Future layers (AI, WhatsApp) can be added without changing calculations

This is the foundation of the Kronox automation pipeline.
