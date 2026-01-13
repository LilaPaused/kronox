# Vision

Kronox exists to solve a very specific problem:

Shift workers often do not know if their payslip is correct.

Schedules change, extra hours are fragmented, and payslips are hard to interpret.
Most existing tools are either too complex or designed for companies, not workers.

Kronox follows three principles:

1. The calculation engine must be transparent and debuggable
2. Users should not be forced to learn new interfaces
3. Automation must never introduce silent errors

Google Sheets is used as the calculation engine because:
- it is transparent
- formulas can be audited
- errors are visible and fixable

Automation layers are added only after the logic is proven to work manually.
