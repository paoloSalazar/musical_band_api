# PDF Documents Plan — Musical Band / Event Services

> FastAPI + Jinja2 + WeasyPrint + React + TypeScript

---

## 1. Dependencies

### Backend (Python)
```bash
pip install fastapi weasyprint jinja2 uvicorn
```

> **WeasyPrint** requires platform-specific system libraries:
>
> **Ubuntu/Debian:**
> ```bash
> apt-get install libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0
> ```
>
> **Windows:**
> ```powershell
> # Install GTK+ runtime from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
> # Or use chocolatey:
> choco install gtk
> ```
>
> **macOS:**
> ```bash
> brew install pango libffi
> ```

### Frontend (Node)
```bash
# No additional dependencies required for PDF download
# Frontend only uses fetch() and triggers blob download
```

---

## 2. File Structure

```
musical_band_api/
├── main.py
├── web/
│   ├── receipts.py    # Receipt PDF endpoint
│   └── contracts.py   # Contract PDF endpoint
├── services/
│   ├── receipt_service.py
│   └── contract_service.py
├── utils/
│   └── number_to_words.py
├── templates/
│   ├── receipt.html
│   └── contract.html
└── data/
    ├── event.py           # Event data access
    ├── event_payment.py   # Payment data access
    ├── user.py            # User data access
    └── user_detail.py     # User detail data access (CI, etc.)
```

---

## 3. Shared Utilities

### `utils/number_to_words.py`
Converts numeric amounts to Spanish text (Bolivian Spanish format).

```python
def number_to_words_es(amount: float) -> str:
    """
    Convert a numeric amount to Spanish literal representation.
    Example: 1523.50 -> "Un mil quinientos veintitrés 50/100 Bolivianos"
    """
```

---

## 4. Payment Receipt (Recibo)

### Design
Mimics the standard Bolivian receipt (RECIBO) format:
- Blue header with "RECIBO" title and date grid (CITY / DAY / MONTH / YEAR)
- Amount fields in Bs. and $us.
- Receipt number in red
- Fields: Received from, Amount in words, For the concept of
- Total row: Paid / Balance / Total
- Signatures: PROVIDED BY / RECEIVED BY
- Page size: A6 landscape (148mm × 105mm)

### Template Context Variables
| Variable | Source | Description |
|----------|--------|-------------|
| `number` | Receipt ID | Sequential receipt number |
| `date.city` | Static | "Cochabamba" |
| `date.day/month/year` | `date.today()` | Current date |
| `amount_bs` | Event.price | Total in Bolivianos |
| `amount_usd` | Optional | Total in USD (if applicable) |
| `received_from` | User.name + lastname | Client full name |
| `amount_in_words` | `number_to_words_es()` | Amount in Spanish words |
| `concept` | Event.name | Event description |
| `partial_payment` | EventPayment.amount | Amount already paid |
| `balance` | EventPayment.pending | Remaining balance |
| `total` | Event.price | Full event price |

### Data Sources
- **Event**: `data.event.get_one(event_id)`
- **User**: `data.user.get_one_by_id(event.user_id)`
- **Payments**: `data.event_payment.get_payments_by_event(event_id)`
- **User Details**: `data.user_detail.get_by_user_id(user_id)` (filter for `detail_type="ci"`)

---

## 5. Service Contract

### Required Data Fields
| Field | Source | Description |
|-------|--------|-------------|
| `client_name` | User.name + lastname | Full client name |
| `client_id` | UserDetail (type="ci") | Cédula de Identidad number |
| `client_phone` | User.phone_number | Contact phone |
| `company_name` | Static or configurable | Band/Company name |
| `contract_date` | `date.today()` | Generated automatically |
| `event_name` | Event.name | Event title |
| `event_location` | Event.place | Event venue |
| `event_date` | Event.start_datetime | Event date |
| `event_start_time` | Event.start_datetime | Start time |
| `event_end_time` | Event.end_datetime | End time |
| `total_amount` | Event.price | Total in Bs. |
| `deposit_percent` | Configurable | Advance percentage (30-50%) |

### Contract Template Context
| Variable | Source | Description |
|----------|--------|-------------|
| `client_name` | User | Full name |
| `client_id` | UserDetail | CI number |
| `client_phone` | User | Phone number |
| `company_name` | Config | Provider name |
| `contract_date.day/month/month_name/year` | `date.today()` | Contract date |
| `event.name` | Event | Event name |
| `event.location` | Event.place | Event venue |
| `event.date` | Event.start_datetime | Formatted date |
| `event.start_time` | Event.start_datetime | Start time |
| `event.end_time` | Event.end_datetime | End time |
| `payment.total` | Event.price | Total amount |
| `payment.total_in_words` | `number_to_words_es()` | Total in words |
| `payment.deposit_percent` | Parameter | Advance % |
| `payment.deposit` | Calculated | Advance amount |
| `payment.balance` | Calculated | Remaining amount |

### Data Sources
- **Event**: `data.event.get_one(event_id)`
- **User**: `data.user.get_one_by_id(event.user_id)`
- **User Details**: `data.user_detail.get_by_user_id(user_id)` (filter for `detail_type="ci"`)

---

## 6. FastAPI Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/receipts/{event_id}/pdf` | Download receipt for event |
| `POST` | `/api/contracts/{event_id}/pdf` | Generate contract with body data |

### Endpoint Details

#### GET `/api/receipts/{event_id}/pdf`
Generates payment receipt PDF for an event.

```python
# Query event with user and payments
# Calculate totals from EventPayment records
# Render receipt.html template
# Return PDF as attachment
```

#### POST `/api/contracts/{event_id}/pdf`
Generates service contract PDF for an event.

```python
# Request body:
{
    "client_id": "12345678",
    "deposit_percent": 30,
    "company_name": "Musical Band Name"
}
# Query event with user
# Render contract.html template
# Return PDF as attachment
```

---

## 7. Frontend React Components

### `hooks/useDownloadPdf.ts`
Generic hook for PDF downloads.

```typescript
export function useDownloadPdf() {
  const download = async (
    url: string,
    filename: string,
    options?: RequestInit
  ): Promise<void> => { ... }
  return { download }
}
```

### `components/ReceiptDownloadButton.tsx`
Downloads receipt for a specific event.

### `components/ContractDownloadButton.tsx`
Generates and downloads contract for a specific event.

---

## 8. Implementation Notes

1. **Receipt Generation**: Sum all payments for event, show paid/balance breakdown
2. **Contract Generation**: Use event price as total, calculate advance/saldo
3. **Templates**: Store in `templates/` directory, rendered via Jinja2
4. **Number to Words**: Spanish Bolivian format (e.g., "1,500.00" -> "Un mil quinientos 00/100")
5. **Authentication**: Both endpoints require valid JWT token