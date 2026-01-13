# Google Sheets Structure

Kronox uses a single Google Sheets file as the source of truth.

## Design rules
- One file per user
- No cross-file calculations
- No IMPORTRANGE dependencies
- All calculations stay inside the same file

## Responsibilities
- Registro: raw daily inputs
- Nominas: monthly aggregation and comparison
- Python/AI: data input only

Sheets calculate.
Automation moves data.
AI interprets intent.
