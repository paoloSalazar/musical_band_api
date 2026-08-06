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
├── static/
│   └── watermark.png    # Watermark image for PDF documents
├── web/
│   ├── receipts.py      # Receipt PDF endpoint (GET /api/receipts/{event_id}/pdf)
│   └── contracts.py     # Contract PDF endpoint (GET /api/contracts/{event_id}/pdf)
├── utils/
│   ├── number_to_words.py
│   └── image_utils.py   # Base64 image conversion utility
├── templates/
│   ├── receipt.html     # A6 landscape format (148mm × 105mm)
│   └── contract.html    # A4 format
└── data/
    ├── event.py           # Event data access
    ├── event_payment.py   # Payment data access
    ├── user.py            # User data access
    ├── user_detail.py     # User detail data access (CI, etc.)
    ├── receipt_service.py # Receipt data retrieval
    └── contract_service.py # Contract data retrieval
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
| `client_name` | Event.user.name + lastname | Full client name |
| `client_id` | Event.user.ci | Cédula de Identidad number (from user's CI field) |
| `client_phone` | Event.user.phone_number | Contact phone |
| `company_name` | `GROUP_NAME` env variable | Band/Company name (from environment) |
| `contract_date` | `date.today()` | Generated automatically |
| `event_name` | Event.name | Event title |
| `event_location` | Event.place | Event venue |
| `event_duration` | Calculated from Event | "6 Horas" for all-day, or calculated hours |
| `total_amount` | Event.price | Total in Bs. |
| `deposit_percent` | Default: 30 | Advance percentage |

### Contract Template Context
| Variable | Source | Description |
|----------|--------|-------------|
| `client_name` | Event.user | Full name |
| `client_id` | Event.user.ci | CI number |
| `client_phone` | Event.user | Phone number |
| `company_name` | `GROUP_NAME` env var | Provider name |
| `contract_date.day/month/month_name/year` | `date.today()` | Contract date |
| `event.name` | Event | Event name |
| `event.location` | Event.place | Event venue |
| `event.duration` | Calculated | "6 Horas" or N hours |
| `event_date.day/month/month_name/year` | Event.start_datetime | Event date |
| `payment.total` | Event.price | Total amount |
| `payment.total_in_words` | `number_to_words_es()` | Total in words |
| `payment.deposit_percent` | Default 30 | Advance % |
| `payment.deposit` | Calculated | Advance amount |
| `payment.balance` | Calculated | Remaining amount |

### Data Sources
- **Event**: `data.event.get_one(event_id)`
- **User**: `data.user.get_one_by_id(event.user_id)`
- **User Details**: `data.user_detail.get_by_user_id(user_id)` (filter for `detail_type="ci"`)

### API Endpoint Change
**From:** `POST /api/contracts/{event_id}/pdf` with JSON body
**To:** `GET /api/contracts/{event_id}/pdf` (no body required)

### Template Variables Added
| Variable | Purpose |
|----------|---------|
| `event_date.day` | Day of event |
| `event_date.month` | Month number (1-12) |
| `event_date.month_name` | Month name in Spanish |
| `event_date.year` | Year (e.g., 2026) |

---

## 6. FastAPI Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/receipts/{event_id}/pdf` | Download receipt for event |
| `GET` | `/api/contracts/{event_id}/pdf` | Generate contract for event |

### Permissions

Both PDF endpoints require authentication via JWT token. Additionally:
- **Event owners** (users who created the event) can generate invoices and contracts
- **Admins** can generate invoices and contracts for any event
- Other authenticated users are denied access

### Endpoint Details

#### GET `/api/receipts/{event_id}/pdf`
Generates payment receipt PDF for an event.

```python
# Query event with user and payments
# Calculate totals from EventPayment records
# Render receipt.html template
# Return PDF as attachment
```

#### GET `/api/contracts/{event_id}/pdf`
Generates service contract PDF for an event.

```python
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
6. **Authorization**: Event owners and admins only can generate PDFs
7. **Company Name**: Retrieved from `GROUP_NAME` environment variable
8. **Client CI**: Retrieved from user's CI field (user_detail table)
9. **Event Duration**: Calculated from event dates (6 hours for all-day events, otherwise computed)

---

## 9. Test-Driven Development Approach

### 9.1 Test File Structure
```
tests/
├── unit/
│   ├── models/
│   │   └── test_event.py, test_user.py, test_event_payment.py
│   ├── schemas/
│   │   └── test_event.py, test_user.py
│   ├── data/
│   │   └── test_event.py, test_user.py, test_event_payment.py
│   └── services/
│       └── test_event.py, test_user.py, test_event_payment.py
├── integration/
│   └── test_event_payment_api.py  # API endpoint tests
└── conftest.py
```

### 9.2 Test Cases (TDD - Write First)

**Unit Tests - `tests/unit/models/test_event.py`**
```python
def test_event_has_price_field():
    """Test that Event model has price field"""
    event = Event(name="Test", place="Venue", ...)
    assert hasattr(event, 'price')
```

**Data Layer Tests - `tests/unit/data/test_event.py`**
```python
def test_get_one_with_payments(db_session):
    """Test retrieving event with payments"""
    ...

def test_get_payments_by_event(db_session):
    """Test getting payments for an event"""
    ...
```

**Service Layer Tests - `tests/unit/services/test_event_payment.py`**
```python
def test_get_event_payment_summary():
    """Test payment summary calculation"""
    ...
```

**Integration Tests - `tests/integration/test_event_payment_api.py`**
```python
def test_get_receipt_pdf():
    """Test GET /api/receipts/{event_id}/pdf endpoint"""
    response = client.get("/api/receipts/1/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

def test_get_contract_pdf():
    """Test GET /api/contracts/{event_id}/pdf endpoint"""
    response = client.get("/api/contracts/1/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

def test_receipt_pdf_permission_denied():
    """Test that non-owners cannot generate receipts"""
    # Login as user who doesn't own the event
    # Try to generate receipt
    response = client.get("/api/receipts/1/pdf")
    assert response.status_code == 403

def test_contract_pdf_permission_denied():
    """Test that non-owners cannot generate contracts"""
    response = client.get("/api/contracts/1/pdf")
    assert response.status_code == 403
```

### 9.3 Implementation Order (TDD)

1. **Write failing tests first**
   - Unit tests for templates context builders
   - Integration tests for PDF endpoints (including permission tests)

2. **Implement changes**
   - Create `data/receipt_service.py` and `data/contract_service.py`
   - Create `templates/receipt.html` and `templates/contract.html`
   - Create `utils/number_to_words.py`
   - Create `web/receipts.py` with `GET /api/receipts/{event_id}/pdf`
   - Create `web/contracts.py` with `GET /api/contracts/{event_id}/pdf`
   - Update `data/contract_service.py` to include company_name, deposit_percent, event_duration
   - Add permission checks in endpoints (event owner/admin only)

3. **Run tests and verify**
   - All tests should pass after implementation

4. **Update main.py**
   - Include new routers

5. **Update endpoints.rest**
   - Add PDF endpoint documentation

---

## 10. Test Commands

```bash
# Run all tests
pytest tests/ -v

# Run PDF-related tests
pytest tests/unit/services/test_event_payment.py tests/integration/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 11. Git Commit Structure

Each commit should be self-contained and focused:

1. **Commit: `feat(pdf): add number_to_words utility`**
   - Add `utils/number_to_words.py`
   - Convert numeric amounts to Spanish text (Bolivian format)

2. **Commit: `feat(pdf): add data access layer for receipts and contracts`**
   - Add `data/receipt_service.py`
   - Add `data/contract_service.py`
   - Functions to retrieve event, user, and payment data

3. **Commit: `feat(pdf): add PDF templates`**
   - Add `templates/receipt.html` (A6 landscape format)
   - Add `templates/contract.html` (A4 format)

4. **Commit: `feat(pdf): add receipt PDF endpoint`**
   - Add `web/receipts.py` with `GET /api/receipts/{event_id}/pdf`
   - Include permission checks (event owner/admin)

5. **Commit: `feat(pdf): add contract PDF endpoint`**
   - Add `web/contracts.py` with `GET /api/contracts/{event_id}/pdf`
   - Include permission checks (event owner/admin)

6. **Commit: `feat(pdf): register PDF routes in main.py`**
   - Include new routers in FastAPI app

7. **Commit: `test(pdf): add unit tests for PDF utilities`**
   - Test number_to_words conversion

8. **Commit: `test(pdf): add integration tests for PDF endpoints`**
   - Test successful PDF generation
   - Test permission denial (403)
   - Test not found scenarios (404)

9. **Commit: `feat(pdf): add watermark support`**
   - Create `static/watermark.png`
   - Add `utils/image_utils.py` for base64 conversion
   - Update `web/receipts.py` and `web/contracts.py` with watermark context
   - Update templates with watermark CSS and img tag

---

## 12. Water Marker Addition

### Implementation Approach
Watermarks are implemented as image overlays on PDF documents using CSS with WeasyPrint. The watermark image is converted to base64 and passed to the template context.

### Watermark Image Location
- **Path**: `static/watermark.png`
- **Purpose**: Semi-transparent logo/text overlay on all PDF pages

### Utility Function: Image to Base64

```python
# utils/image_utils.py
import base64
from pathlib import Path

def image_to_base64(image_path: str) -> str:
    """Convert a local image file to a base64 data URI."""
    path = Path(image_path)
    mime_types = {".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml"}
    mime = mime_types.get(path.suffix.lower(), "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"
```

### Endpoint Integration

```python
# web/receipts.py
from utils.image_utils import image_to_base64

@router.get("/{event_id}/pdf")
async def download_receipt_pdf(event_id: int):
    ...
    context = build_receipt_context(receipt_data)
    
    # Add watermark image to context
    context["watermark_image"] = image_to_base64("static/watermark.png")
    
    html_string = templates.get_template("receipt.html").render(**context)
    pdf_bytes = HTML(string=html_string).write_pdf()
    ...
```

### CSS Watermark Styling

```css
.watermark {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-30deg);
  opacity: 0.08;
  width: 70mm;
  z-index: -1;
}
```

### Template Implementation

```html
<style>
  .watermark {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    opacity: 0.08;
    width: 70mm;
    z-index: -1;
  }
</style>

<body>
  <img class="watermark" src="{{ watermark_image }}" alt="">
  <!-- rest of receipt content -->
</body>
```

### Contract Endpoint Integration

```python
# web/contracts.py
from utils.image_utils import image_to_base64

@router.get("/{event_id}/pdf")
async def download_contract_pdf(event_id: int):
    ...
    context = build_contract_context(contract_data)
    
    # Add watermark image to context
    context["watermark_image"] = image_to_base64("static/watermark.png")
    
    html_string = templates.get_template("contract.html").render(**context)
    pdf_bytes = HTML(string=html_string).write_pdf()
    ...
```

### Contract Template Implementation

```html
<style>
  .watermark {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    opacity: 0.08;
    width: 100mm;
    z-index: -1;
  }
</style>

<body>
  <img class="watermark" src="{{ watermark_image }}" alt="">
  <!-- rest of contract content -->
</body>
```

---