# Data Model (Contract)

This document defines the strict data contract used by Kronox.
Any automation (Python or AI) must comply with this contract.

---

## Sheet: Registro (daily inputs)

| Column | Name          | Type   | Format         | Description |
|------|---------------|--------|----------------|-------------|
| A    | diaTurno      | Date   | DD/MM/YYYY     | Day of work |
| B    | claveHoraria  | String | Free text      | Schedule key |
| C    | extrasAntes   | Time   | HH:MM          | Extra time before shift |
| D    | extrasDespues | Time   | HH:MM          | Extra time after shift |

Notes:
- Time values must be real time cells, not text
- Empty values are allowed

---

## Sheet: Nominas

### A) Fixed data (first interaction)

| Field | Type | Format |
|-----|------|--------|
| Apellidos, Nombre | String | `SURNAME1 SURNAME2, NAME` |
| C.J | Decimal | e.g. `0.75` |
| Fecha antiguedad | Date | DD/MM/YYYY |

---

### B) Dynamic data (per payslip)

| Field | Type | Format |
|-----|------|--------|
| Año | Number | YYYY |
| Mes | String | YYYY-MM (MonthKey) |
| C.J | Decimal | Optional override |
| Plus Supervisor | Boolean | TRUE / FALSE |
| Plus Conductor | Boolean | TRUE / FALSE |

---

### C) Payslip real values (EUR)

All values are decimals in EUR.

- Salario Base
- Paga extra
- Plus festivo
- Plus domingo
- Plus nocturno
- Plus transporte
- Manutenciones
- Horas complementarias
- Plus fijo T.P
- Plus Supervisor
- Plus Conductor
- IRPF_IMPORTE
- COT REGIMEN GEN
- COT DESEMPL y FP
- COT MEI

---

### D) Payment

| Field | Type | Format |
|-----|------|--------|
| IRPF_PCT | Decimal | e.g. `0.11` for 11% |
