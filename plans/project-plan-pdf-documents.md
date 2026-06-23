# Plan de Documentos PDF — Grupo Musical / Servicios de Eventos
> FastAPI + Jinja2 + WeasyPrint + React + TypeScript

---

## Índice

1. [Dependencias](#1-dependencias)
2. [Estructura de archivos](#2-estructura-de-archivos)
3. [Utilidades compartidas](#3-utilidades-compartidas)
4. [Recibo de pago](#4-recibo-de-pago)
5. [Contrato de prestación de servicios](#5-contrato-de-prestación-de-servicios)
6. [Endpoints FastAPI](#6-endpoints-fastapi)
7. [Frontend React](#7-frontend-react)

---

## 1. Dependencias

### Backend (Python)
```bash
pip install fastapi weasyprint jinja2 uvicorn
```

> **WeasyPrint** requiere librerías del sistema. En Ubuntu/Debian:
> ```bash
> apt-get install libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0
> ```

### Frontend (Node)
```bash
# No se requieren dependencias adicionales para la descarga de PDFs
# El frontend solo hace fetch() y dispara la descarga del blob
```

---

## 2. Estructura de archivos

```
project/
├── main.py
├── routers/
│   ├── receipts.py
│   └── contracts.py
├── services/
│   ├── receipt_service.py
│   └── contract_service.py
├── utils/
│   └── number_to_words.py
└── templates/
    ├── receipt.html
    └── contract.html
```

---

## 3. Utilidades compartidas

### `utils/number_to_words.py`
Convierte un monto numérico a su representación literal en español boliviano.

```python
def number_to_words_es(amount: float) -> str:
    """
    Convert a numeric amount to its Spanish literal representation.
    Example: 1523.50 -> "Un mil quinientos veintitrés 50/100 Bolivianos"
    """
    units = [
        "", "uno", "dos", "tres", "cuatro", "cinco",
        "seis", "siete", "ocho", "nueve", "diez",
        "once", "doce", "trece", "catorce", "quince",
        "dieciséis", "diecisiete", "dieciocho", "diecinueve",
    ]
    tens = [
        "", "", "veinte", "treinta", "cuarenta",
        "cincuenta", "sesenta", "setenta", "ochenta", "noventa",
    ]
    hundreds = [
        "", "cien", "doscientos", "trescientos", "cuatrocientos",
        "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos",
    ]

    def convert_below_1000(n: int) -> str:
        if n == 0:
            return ""
        if n < 20:
            return units[n]
        if n < 30:
            return "veinte" if n == 20 else "veinti" + units[n - 20]
        if n < 100:
            d, u = divmod(n, 10)
            return tens[d] if u == 0 else f"{tens[d]} y {units[u]}"
        if n == 100:
            return "cien"
        c, remainder = divmod(n, 100)
        return hundreds[c] + (f" {convert_below_1000(remainder)}" if remainder else "")

    def convert(n: int) -> str:
        if n == 0:
            return "cero"
        if n < 1_000:
            return convert_below_1000(n)
        if n < 1_000_000:
            thousands, remainder = divmod(n, 1_000)
            prefix = "mil" if thousands == 1 else f"{convert_below_1000(thousands)} mil"
            return prefix + (f" {convert_below_1000(remainder)}" if remainder else "")
        if n < 1_000_000_000:
            millions, remainder = divmod(n, 1_000_000)
            prefix = "un millón" if millions == 1 else f"{convert_below_1000(millions)} millones"
            return prefix + (f" {convert(remainder)}" if remainder else "")
        return str(n)

    integer_part = int(amount)
    cents = round((amount - integer_part) * 100)
    words = convert(integer_part).capitalize()
    return f"{words} {cents:02d}/100 Bolivianos"
```

---

## 4. Recibo de pago

### Diseño
Replica el talonario boliviano estándar (RECIBO) con:
- Encabezado azul con título "RECIBO" y grilla de fecha (LUGAR / DÍA / MES / AÑO)
- Celdas de monto en Bs. y $us.
- Número de recibo en rojo
- Campos: Recibí de, La suma de, Por concepto de
- Fila de totales: A cuenta / Saldo / Total
- Firmas: ENTREGUÉ CONFORME / RECIBÍ CONFORME
- Tamaño de página: A6 apaisado (148mm × 105mm)

### `templates/receipt.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <style>
    @page {
      size: 148mm 105mm;
      margin: 8mm;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: Arial, sans-serif;
      font-size: 10px;
      color: #1a1a1a;
      border: 2px solid #1a4fa0;
      border-radius: 4px;
      padding: 10px 12px;
      height: 100%;
    }

    .top-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
    }

    .receipt-box {
      border: 2px solid #1a4fa0;
      border-radius: 3px;
      padding: 4px 6px;
      min-width: 170px;
    }

    .receipt-title {
      background: #1a4fa0;
      color: white;
      font-size: 18px;
      font-weight: 900;
      letter-spacing: 4px;
      text-align: center;
      padding: 1px 4px;
      border-radius: 2px;
      margin-bottom: 4px;
    }

    .date-grid {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr;
      border: 1px solid #1a4fa0;
      font-size: 8px;
      color: #1a4fa0;
      text-align: center;
    }

    .date-grid .header-cell {
      border-bottom: 1px solid #1a4fa0;
      padding: 1px 2px;
    }

    .date-grid .header-cell:not(:last-child),
    .date-grid .value-cell:not(:last-child) {
      border-right: 1px solid #1a4fa0;
    }

    .date-grid .value-cell {
      padding: 3px 2px;
      font-size: 9px;
      color: #1a1a1a;
    }

    .amount-box { text-align: right; }

    .amount-labels {
      font-size: 10px;
      color: #1a4fa0;
      margin-bottom: 3px;
      display: flex;
      gap: 4px;
      justify-content: flex-end;
    }

    .amount-label { min-width: 52px; text-align: center; }

    .amount-cells { display: flex; gap: 6px; justify-content: flex-end; }

    .amount-cell {
      border: 1.5px solid #1a4fa0;
      width: 60px;
      height: 22px;
      border-radius: 2px;
      font-size: 11px;
      font-weight: bold;
      color: #1a1a1a;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      padding-right: 4px;
    }

    .receipt-number {
      color: #e53935;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 3px;
      margin-top: 5px;
    }

    .field { margin-bottom: 5px; }

    .field label {
      color: #1a4fa0;
      font-size: 9px;
      display: block;
    }

    .field .line {
      border-bottom: 1px solid #888;
      padding-bottom: 1px;
      min-height: 13px;
      font-size: 10px;
    }

    .currency-label {
      font-size: 9px;
      color: #1a4fa0;
      margin-bottom: 5px;
    }

    .totals-row {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
    }

    .totals-row .col { flex: 1; }

    .signatures {
      display: flex;
      justify-content: space-between;
      margin-top: 8px;
    }

    .signature { width: 44%; text-align: center; }

    .signature .signature-line {
      border-bottom: 1px solid #555;
      margin-bottom: 3px;
    }

    .signature .signature-label {
      font-size: 8px;
      color: #1a4fa0;
    }
  </style>
</head>
<body>

  <div class="top-row">
    <!-- Receipt title + date grid -->
    <div class="receipt-box">
      <div class="receipt-title">RECIBO</div>
      <div class="date-grid">
        <div class="header-cell">LUGAR</div>
        <div class="header-cell">DÍA</div>
        <div class="header-cell">MES</div>
        <div class="header-cell">AÑO</div>
        <div class="value-cell">{{ date.city }}</div>
        <div class="value-cell">{{ date.day }}</div>
        <div class="value-cell">{{ date.month }}</div>
        <div class="value-cell">{{ date.year }}</div>
      </div>
    </div>

    <!-- Amount boxes + receipt number -->
    <div class="amount-box">
      <div class="amount-labels">
        <span class="amount-label">Bs.</span>
        <span class="amount-label">$us.</span>
      </div>
      <div class="amount-cells">
        <div class="amount-cell">{{ "%.2f"|format(amount_bs) if amount_bs else "" }}</div>
        <div class="amount-cell">{{ "%.2f"|format(amount_usd) if amount_usd else "" }}</div>
      </div>
      <div class="receipt-number">{{ "%07d"|format(number) }}</div>
    </div>
  </div>

  <div class="field">
    <label>Recibí de:</label>
    <div class="line">{{ received_from }}</div>
  </div>

  <div class="field">
    <label>La suma de:</label>
    <div class="line">{{ amount_in_words }}</div>
  </div>

  <div class="field">
    <label>Por concepto de:</label>
    <div class="line">{{ concept }}</div>
    {% if concept_extra %}
    <div class="line" style="margin-top:3px;">{{ concept_extra }}</div>
    {% endif %}
  </div>

  <div class="currency-label">Bolivianos/Dólares</div>

  <div class="totals-row">
    <div class="col field">
      <label>A cuenta:</label>
      <div class="line">{{ "%.2f"|format(partial_payment) if partial_payment else "" }}</div>
    </div>
    <div class="col field">
      <label>Saldo:</label>
      <div class="line">{{ "%.2f"|format(balance) if balance else "" }}</div>
    </div>
    <div class="col field">
      <label>Total:</label>
      <div class="line">{{ "%.2f"|format(total) }}</div>
    </div>
  </div>

  <div class="signatures">
    <div class="signature">
      <div class="signature-line"></div>
      <div class="signature-label">C.I. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ENTREGUÉ CONFORME</div>
    </div>
    <div class="signature">
      <div class="signature-line"></div>
      <div class="signature-label">C.I. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; RECIBÍ CONFORME</div>
    </div>
  </div>

</body>
</html>
```

### `routers/receipts.py`

```python
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from weasyprint import HTML
from datetime import date

from services.receipt_service import get_receipt
from utils.number_to_words import number_to_words_es
from auth.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/receipts", tags=["receipts"])
templates = Jinja2Templates(directory="templates")


def _build_receipt_context(receipt_id: int, receipt: dict) -> dict:
    """Build the template context dict from a receipt record."""
    today = date.today()
    total = receipt["amount_bs"]

    return {
        "number":          receipt_id,
        "date": {
            "city":  "Cochabamba",
            "day":   today.day,
            "month": today.month,
            "year":  today.year,
        },
        "amount_bs":       total,
        "amount_usd":      receipt.get("amount_usd"),
        "received_from":   receipt["client_name"],
        "amount_in_words": number_to_words_es(total),
        "concept":         receipt["concept"],
        "concept_extra":   receipt.get("concept_extra"),
        "partial_payment": receipt.get("partial_payment"),
        "balance":         receipt.get("balance"),
        "total":           total,
    }


@router.get("/{receipt_id}/pdf")
async def download_receipt_pdf(
    receipt_id: int,
    current_user: User = Depends(get_current_user)
):
    """Generate and return a receipt PDF for the given receipt ID.
    
    Permission: Event owner or admin only.
    """
    receipt = get_receipt(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Check permissions - owner or admin
    if receipt.get("event_user_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    context = _build_receipt_context(receipt_id, receipt)
    html_string = templates.get_template("receipt.html").render(**context)
    pdf_bytes = HTML(string=html_string, base_url=".").write_pdf()

    return Response(
        content    = pdf_bytes,
        media_type = "application/pdf",
        headers    = {
            "Content-Disposition": f'attachment; filename="receipt-{receipt_id:07d}.pdf"'
        },
    )
```

---

## 5. Contrato de prestación de servicios

### Datos requeridos
| Campo | Descripción |
|---|---|
| `client_name` | Nombre completo del contratante |
| `client_id` | Número de Cédula de Identidad |
| `client_phone` | Teléfono de contacto |
| `company_name` | Nombre del grupo / empresa |
| `contract_date` | Fecha de firma (generada automáticamente) |
| `event_name` | Nombre del evento |
| `event_location` | Lugar del evento |
| `event_date` | Fecha del evento |
| `event_start_time` | Hora de inicio |
| `event_end_time` | Hora de finalización |
| `total_amount` | Monto total en Bs. |
| `deposit_percent` | Porcentaje de anticipo (30% a 50%) |

### Texto completo del contrato

```
CONTRATO DE PRESTACIÓN DE SERVICIOS ARTÍSTICOS Y MUSICALES

En la ciudad de Cochabamba, Bolivia, a los [DÍA] días del mes de [MES] de [AÑO]

PARTES CONTRATANTES

EL CONTRATANTE:
[NOMBRE COMPLETO], con Cédula de Identidad N° [CI], con domicilio en la ciudad de
Cochabamba, con número de teléfono [TELÉFONO], a quien en adelante se denominará
"EL CONTRATANTE".

EL PRESTADOR DE SERVICIOS:
[NOMBRE EMPRESA/GRUPO MUSICAL], legalmente constituida y con domicilio en la ciudad
de Cochabamba, Bolivia, a quien en adelante se denominará "EL PRESTADOR".

CLÁUSULAS

PRIMERA — OBJETO DEL CONTRATO
El presente contrato tiene por objeto la prestación de servicios artísticos y musicales
por parte de EL PRESTADOR en favor de EL CONTRATANTE, para el evento denominado
"[NOMBRE DEL EVENTO]", a realizarse en [LUGAR DEL EVENTO], el día [FECHA DEL EVENTO].

SEGUNDA — DESCRIPCIÓN DEL SERVICIO
EL PRESTADOR se compromete a brindar los siguientes servicios:
- Presentación musical en vivo durante el evento.
- Equipos de sonido e iluminación según los requerimientos acordados.
- Personal artístico y técnico necesario para la correcta ejecución del espectáculo.
- Puntualidad en la hora de inicio según lo acordado entre las partes.

TERCERA — DURACIÓN DEL SERVICIO
EL PRESTADOR brindará sus servicios durante la jornada establecida para el evento,
desde las [HORA INICIO] hasta las [HORA FIN], pudiendo prorrogarse de mutuo acuerdo
y con el pago adicional correspondiente.

CUARTA — PRECIO Y FORMA DE PAGO
Las partes acuerdan una retribución económica de Bs. [MONTO] ([MONTO EN LETRAS]
Bolivianos), pagaderos de la siguiente forma:

- Anticipo a la firma del presente contrato ([PORCENTAJE]% del total acordado):
  Bs. [ANTICIPO].
- Saldo restante a cancelarse al inicio del evento: Bs. [SALDO].

El pago podrá realizarse mediante cualquiera de las siguientes modalidades,
a elección de EL CONTRATANTE:
1. Efectivo, entregado directamente al representante de EL PRESTADOR.
2. Transferencia bancaria, a la cuenta indicada por EL PRESTADOR al momento del pago.
3. Código QR, mediante las plataformas de pago móvil habilitadas por EL PRESTADOR.

En todos los casos, EL PRESTADOR emitirá el recibo correspondiente como constancia
del pago recibido.

QUINTA — OBLIGACIONES DEL PRESTADOR
EL PRESTADOR se obliga a:
1. Presentarse puntualmente en el lugar y hora acordados.
2. Contar con el personal artístico y técnico completo para el desarrollo del evento.
3. Garantizar el buen funcionamiento de equipos de sonido e iluminación.
4. Mantener una conducta profesional durante toda la prestación del servicio.
5. Notificar a EL CONTRATANTE con mínimo 72 horas de anticipación ante cualquier
   eventualidad que pueda afectar la prestación.

SEXTA — OBLIGACIONES DEL CONTRATANTE
EL CONTRATANTE se obliga a:
1. Realizar los pagos en los plazos y montos establecidos en la Cláusula Cuarta.
2. Garantizar las condiciones mínimas para la prestación del servicio: espacio
   adecuado, acceso al lugar, alimentación del personal técnico y artístico.
3. Suministrar energía eléctrica suficiente en el lugar del evento.
4. Informar a EL PRESTADOR sobre cualquier restricción o condición especial
   del lugar del evento.

SÉPTIMA — CANCELACIÓN Y PENALIDADES
- Si EL CONTRATANTE cancela el evento con menos de 15 días de anticipación,
  el anticipo pagado no será reembolsable.
- Si EL CONTRATANTE cancela con más de 15 días de anticipación, se devolverá
  el 50% del anticipo.
- Si EL PRESTADOR cancela el servicio sin causa justificada, deberá devolver
  el doble del anticipo recibido como penalidad.

OCTAVA — FUERZA MAYOR
Ninguna de las partes será responsable por el incumplimiento del presente contrato
cuando dicho incumplimiento sea causado por eventos de fuerza mayor o caso fortuito
debidamente comprobados, tales como desastres naturales, disposiciones gubernamentales
o situaciones de emergencia nacional. En tal caso, las partes acordarán de buena fe
una nueva fecha para la prestación del servicio.

NOVENA — RESOLUCIÓN DE CONTROVERSIAS
Cualquier controversia derivada del presente contrato será resuelta en primera
instancia mediante acuerdo directo entre las partes. En caso de no llegar a un
acuerdo, las partes se someterán a la jurisdicción y competencia de los Juzgados
de la ciudad de Cochabamba, de conformidad con la legislación boliviana vigente,
en particular la Ley N° 439 — Código Procesal Civil y el Código Civil boliviano.

DÉCIMA — DISPOSICIONES GENERALES
El presente contrato se rige por las leyes de la República de Bolivia. Cualquier
modificación al mismo deberá constar por escrito y ser firmada por ambas partes.
El presente contrato se extiende en dos ejemplares de igual valor, quedando uno
en poder de cada parte.

FIRMAS

En señal de conformidad con todas las cláusulas del presente contrato, las partes
firman en la ciudad de Cochabamba, a los [DÍA] días del mes de [MES] de [AÑO].

EL CONTRATANTE                          EL PRESTADOR

_______________________                 _______________________
[NOMBRE COMPLETO]                       [NOMBRE EMPRESA]
C.I.: [CI]                              Representante Legal
Tel.: [TELÉFONO]
```

### `templates/contract.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <style>
    @page {
      size: A4;
      margin: 2.5cm 2cm;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: Arial, sans-serif;
      font-size: 11px;
      color: #1a1a1a;
      line-height: 1.6;
    }

    /* ── Header ── */
    .contract-header {
      text-align: center;
      border-bottom: 2px solid #1a4fa0;
      padding-bottom: 12px;
      margin-bottom: 20px;
    }

    .contract-header h1 {
      font-size: 14px;
      font-weight: 700;
      color: #1a4fa0;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 4px;
    }

    .contract-header .subtitle {
      font-size: 10px;
      color: #555;
    }

    /* ── Section titles ── */
    .section-title {
      font-size: 11px;
      font-weight: 700;
      color: #1a4fa0;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid #ccd6e8;
      padding-bottom: 3px;
      margin: 16px 0 8px;
    }

    /* ── Parties ── */
    .party-block {
      background: #f4f7fc;
      border-left: 3px solid #1a4fa0;
      padding: 8px 12px;
      margin-bottom: 10px;
      border-radius: 0 3px 3px 0;
    }

    .party-block .party-role {
      font-weight: 700;
      color: #1a4fa0;
      font-size: 10px;
      text-transform: uppercase;
      margin-bottom: 3px;
    }

    /* ── Clauses ── */
    .clause {
      margin-bottom: 12px;
    }

    .clause .clause-title {
      font-weight: 700;
      font-size: 11px;
      margin-bottom: 4px;
    }

    .clause ol, .clause ul {
      padding-left: 20px;
      margin-top: 4px;
    }

    .clause li {
      margin-bottom: 3px;
    }

    /* ── Payment highlight ── */
    .payment-box {
      border: 1px solid #1a4fa0;
      border-radius: 3px;
      padding: 8px 12px;
      margin: 8px 0;
    }

    .payment-box .amount-main {
      font-size: 13px;
      font-weight: 700;
      color: #1a4fa0;
    }

    .payment-row {
      display: flex;
      justify-content: space-between;
      padding: 3px 0;
      border-bottom: 1px solid #e8edf5;
      font-size: 10px;
    }

    .payment-row:last-child { border-bottom: none; }
    .payment-row .label { color: #555; }
    .payment-row .value { font-weight: 700; }

    /* ── Signatures ── */
    .signatures-section {
      margin-top: 40px;
      display: flex;
      justify-content: space-between;
    }

    .signature-block {
      width: 44%;
      text-align: center;
    }

    .signature-line {
      border-bottom: 1px solid #555;
      margin-bottom: 6px;
      height: 40px;
    }

    .signature-name { font-weight: 700; font-size: 10px; }
    .signature-detail { font-size: 9px; color: #555; margin-top: 2px; }

    /* ── Footer ── */
    .page-footer {
      position: running(footer);
      font-size: 8px;
      color: #999;
      text-align: center;
      border-top: 1px solid #e0e0e0;
      padding-top: 4px;
    }

    @page { @bottom-center { content: element(footer); } }
  </style>
</head>
<body>

  <div class="contract-header">
    <h1>Contrato de Prestación de Servicios Artísticos y Musicales</h1>
    <div class="subtitle">
      Ciudad de Cochabamba, Bolivia — {{ contract_date.day }} de {{ contract_date.month_name }} de {{ contract_date.year }}
    </div>
  </div>

  <!-- PARTIES -->
  <div class="section-title">Partes Contratantes</div>

  <div class="party-block">
    <div class="party-role">El Contratante</div>
    <strong>{{ client_name }}</strong>, con Cédula de Identidad N° <strong>{{ client_id }}</strong>,
    con domicilio en la ciudad de Cochabamba, con número de teléfono <strong>{{ client_phone }}</strong>,
    a quien en adelante se denominará <strong>"EL CONTRATANTE"</strong>.
  </div>

  <div class="party-block">
    <div class="party-role">El Prestador de Servicios</div>
    <strong>{{ company_name }}</strong>, legalmente constituida y con domicilio en la ciudad de
    Cochabamba, Bolivia, a quien en adelante se denominará <strong>"EL PRESTADOR"</strong>.
  </div>

  <!-- CLAUSES -->
  <div class="section-title">Cláusulas</div>

  <div class="clause">
    <div class="clause-title">Primera — Objeto del Contrato</div>
    El presente contrato tiene por objeto la prestación de servicios artísticos y musicales
    por parte de EL PRESTADOR en favor de EL CONTRATANTE, para el evento denominado
    <strong>"{{ event.name }}"</strong>, a realizarse en <strong>{{ event.location }}</strong>,
    el día <strong>{{ event.date }}</strong>.
  </div>

  <div class="clause">
    <div class="clause-title">Segunda — Descripción del Servicio</div>
    EL PRESTADOR se compromete a brindar los siguientes servicios:
    <ul>
      <li>Presentación musical en vivo durante el evento.</li>
      <li>Equipos de sonido e iluminación según los requerimientos acordados.</li>
      <li>Personal artístico y técnico necesario para la correcta ejecución del espectáculo.</li>
      <li>Puntualidad en la hora de inicio según lo acordado entre las partes.</li>
    </ul>
  </div>

  <div class="clause">
    <div class="clause-title">Tercera — Duración del Servicio</div>
    EL PRESTADOR brindará sus servicios durante la jornada establecida para el evento,
    desde las <strong>{{ event.start_time }}</strong> hasta las <strong>{{ event.end_time }}</strong>,
    pudiendo prorrogarse de mutuo acuerdo y con el pago adicional correspondiente.
  </div>

  <div class="clause">
    <div class="clause-title">Cuarta — Precio y Forma de Pago</div>
    Las partes acuerdan una retribución económica de:

    <div class="payment-box">
      <div class="amount-main">Bs. {{ "%.2f"|format(payment.total) }}</div>
      <div style="font-size:10px; color:#555; margin-bottom:8px;">
        {{ payment.total_in_words }}
      </div>
      <div class="payment-row">
        <span class="label">Anticipo ({{ payment.deposit_percent }}%) — a la firma del contrato</span>
        <span class="value">Bs. {{ "%.2f"|format(payment.deposit) }}</span>
      </div>
      <div class="payment-row">
        <span class="label">Saldo restante — al inicio del evento</span>
        <span class="value">Bs. {{ "%.2f"|format(payment.balance) }}</span>
      </div>
    </div>

    El pago podrá realizarse mediante cualquiera de las siguientes modalidades,
    a elección de EL CONTRATANTE:
    <ol>
      <li><strong>Efectivo</strong>, entregado directamente al representante de EL PRESTADOR.</li>
      <li><strong>Transferencia bancaria</strong>, a la cuenta indicada por EL PRESTADOR al momento del pago.</li>
      <li><strong>Código QR</strong>, mediante las plataformas de pago móvil habilitadas por EL PRESTADOR.</li>
    </ol>
    En todos los casos, EL PRESTADOR emitirá el recibo correspondiente como constancia del pago recibido.
  </div>

  <div class="clause">
    <div class="clause-title">Quinta — Obligaciones del Prestador</div>
    EL PRESTADOR se obliga a:
    <ol>
      <li>Presentarse puntualmente en el lugar y hora acordados.</li>
      <li>Contar con el personal artístico y técnico completo para el desarrollo del evento.</li>
      <li>Garantizar el buen funcionamiento de equipos de sonido e iluminación.</li>
      <li>Mantener una conducta profesional durante toda la prestación del servicio.</li>
      <li>Notificar a EL CONTRATANTE con mínimo 72 horas de anticipación ante cualquier eventualidad que pueda afectar la prestación.</li>
    </ol>
  </div>

  <div class="clause">
    <div class="clause-title">Sexta — Obligaciones del Contratante</div>
    EL CONTRATANTE se obliga a:
    <ol>
      <li>Realizar los pagos en los plazos y montos establecidos en la Cláusula Cuarta.</li>
      <li>Garantizar las condiciones mínimas para la prestación del servicio: espacio adecuado, acceso al lugar, alimentación del personal técnico y artístico.</li>
      <li>Suministrar energía eléctrica suficiente en el lugar del evento.</li>
      <li>Informar a EL PRESTADOR sobre cualquier restricción o condición especial del lugar del evento.</li>
    </ol>
  </div>

  <div class="clause">
    <div class="clause-title">Séptima — Cancelación y Penalidades</div>
    <ul>
      <li>Si EL CONTRATANTE cancela el evento con <strong>menos de 15 días de anticipación</strong>, el anticipo pagado no será reembolsable.</li>
      <li>Si EL CONTRATANTE cancela con <strong>más de 15 días de anticipación</strong>, se devolverá el 50% del anticipo.</li>
      <li>Si EL PRESTADOR cancela el servicio sin causa justificada, deberá devolver el doble del anticipo recibido como penalidad.</li>
    </ul>
  </div>

  <div class="clause">
    <div class="clause-title">Octava — Fuerza Mayor</div>
    Ninguna de las partes será responsable por el incumplimiento del presente contrato cuando
    dicho incumplimiento sea causado por eventos de fuerza mayor o caso fortuito debidamente
    comprobados, tales como desastres naturales, disposiciones gubernamentales o situaciones
    de emergencia nacional. En tal caso, las partes acordarán de buena fe una nueva fecha
    para la prestación del servicio.
  </div>

  <div class="clause">
    <div class="clause-title">Novena — Resolución de Controversias</div>
    Cualquier controversia derivada del presente contrato será resuelta en primera instancia
    mediante acuerdo directo entre las partes. En caso de no llegar a un acuerdo, las partes
    se someterán a la jurisdicción y competencia de los Juzgados de la ciudad de Cochabamba,
    de conformidad con la legislación boliviana vigente, en particular la
    <strong>Ley N° 439 — Código Procesal Civil</strong> y el <strong>Código Civil boliviano</strong>.
  </div>

  <div class="clause">
    <div class="clause-title">Décima — Disposiciones Generales</div>
    El presente contrato se rige por las leyes de la República de Bolivia. Cualquier
    modificación al mismo deberá constar por escrito y ser firmada por ambas partes.
    El presente contrato se extiende en dos ejemplares de igual valor, quedando uno
    en poder de cada parte.
  </div>

  <!-- SIGNATURES -->
  <div class="signatures-section">
    <div class="signature-block">
      <div class="signature-line"></div>
      <div class="signature-name">{{ client_name }}</div>
      <div class="signature-detail">C.I.: {{ client_id }}</div>
      <div class="signature-detail">Tel.: {{ client_phone }}</div>
      <div class="signature-detail" style="margin-top:4px; font-weight:700;">EL CONTRATANTE</div>
    </div>
    <div class="signature-block">
      <div class="signature-line"></div>
      <div class="signature-name">{{ company_name }}</div>
      <div class="signature-detail">Representante Legal</div>
      <div class="signature-detail" style="margin-top:4px; font-weight:700;">EL PRESTADOR</div>
    </div>
  </div>

  <div class="page-footer">
    {{ company_name }} — Cochabamba, Bolivia — Documento generado el {{ contract_date.day }}/{{ contract_date.month }}/{{ contract_date.year }}
  </div>

</body>
</html>
```

### `routers/contracts.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from weasyprint import HTML
from datetime import date

from utils.number_to_words import number_to_words_es
from auth.auth import get_current_user
from models.user import User
from services.event import get_event

router = APIRouter(prefix="/contracts", tags=["contracts"])
templates = Jinja2Templates(directory="templates")

MONTH_NAMES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


class EventData(BaseModel):
    name: str
    location: str
    date: str           # e.g. "28 de junio de 2026"
    start_time: str     # e.g. "20:00"
    end_time: str       # e.g. "02:00"


class ContractRequest(BaseModel):
    client_name: str
    client_id: str           # Cédula de Identidad
    client_phone: str
    company_name: str
    event: EventData
    total_amount: float
    deposit_percent: int     # 30 to 50


def _build_contract_context(contract_id: int, data: ContractRequest) -> dict:
    """Build the Jinja2 template context from a contract request."""
    today = date.today()

    # Calculate deposit and balance
    deposit = round(data.total_amount * data.deposit_percent / 100, 2)
    balance = round(data.total_amount - deposit, 2)

    return {
        "contract_id":   contract_id,
        "client_name":   data.client_name,
        "client_id":     data.client_id,
        "client_phone":  data.client_phone,
        "company_name":  data.company_name,
        "contract_date": {
            "day":        today.day,
            "month":      today.month,
            "month_name": MONTH_NAMES_ES[today.month],
            "year":       today.year,
        },
        "event": {
            "name":       data.event.name,
            "location":   data.event.location,
            "date":       data.event.date,
            "start_time": data.event.start_time,
            "end_time":   data.event.end_time,
        },
        "payment": {
            "total":           data.total_amount,
            "total_in_words":  number_to_words_es(data.total_amount),
            "deposit_percent": data.deposit_percent,
            "deposit":         deposit,
            "balance":         balance,
        },
    }


@router.post("/{contract_id}/pdf")
async def download_contract_pdf(
    contract_id: int,
    data: ContractRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate and return a service contract PDF.
    
    Permission: Event owner or admin only.
    """
    # Verify event ownership
    event = get_event(data.event.id if hasattr(data.event, 'id') else None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    context = _build_contract_context(contract_id, data)
    html_string = templates.get_template("contract.html").render(**context)
    pdf_bytes = HTML(string=html_string, base_url=".").write_pdf()

    return Response(
        content    = pdf_bytes,
        media_type = "application/pdf",
        headers    = {
            "Content-Disposition": f'attachment; filename="contract-{contract_id:06d}.pdf"'
        },
    )
```

---

## 6. Endpoints FastAPI — Resumen

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/receipts/{id}/pdf` | Descarga el recibo N° `id` en PDF |
| `POST` | `/contracts/{id}/pdf` | Genera el contrato con los datos del body |

### Permisos

Ambos endpoints requieren autenticación mediante token JWT. Además:
- **Propietarios del evento** (usuarios que crearon el evento) pueden generar recibos y contratos
- **Administradores** pueden generar recibos y contratos para cualquier evento
- Otros usuarios autenticados reciben acceso denegado (403)

---

## 7. Frontend React

### `hooks/useDownloadPdf.ts`
Hook genérico reutilizable para ambos documentos.

```typescript
export function useDownloadPdf() {
  const download = async (
    url: string,
    filename: string,
    options?: RequestInit
  ): Promise<void> => {
    const response = await fetch(url, options);

    if (!response.ok) {
      throw new Error(`Failed to generate PDF: ${response.statusText}`);
    }

    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);

    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = filename;
    anchor.click();

    URL.revokeObjectURL(objectUrl);
  };

  return { download };
}
```

### `components/ReceiptDownloadButton.tsx`

```typescript
import { useState } from "react";
import { useDownloadPdf } from "../hooks/useDownloadPdf";

interface Props {
  receiptId: number;
}

export function ReceiptDownloadButton({ receiptId }: Props) {
  const { download } = useDownloadPdf();
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      await download(
        `/api/receipts/${receiptId}/pdf`,
        `recibo-${String(receiptId).padStart(7, "0")}.pdf`
      );
    } catch {
      alert("No se pudo generar el recibo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleClick} disabled={loading}>
      {loading ? "Generando..." : "⬇ Descargar Recibo"}
    </button>
  );
}
```

### `components/ContractDownloadButton.tsx`

```typescript
import { useState } from "react";
import { useDownloadPdf } from "../hooks/useDownloadPdf";

interface ContractData {
  client_name: string;
  client_id: string;
  client_phone: string;
  company_name: string;
  event: {
    name: string;
    location: string;
    date: string;
    start_time: string;
    end_time: string;
  };
  total_amount: number;
  deposit_percent: number; // 30 to 50
}

interface Props {
  contractId: number;
  data: ContractData;
}

export function ContractDownloadButton({ contractId, data }: Props) {
  const { download } = useDownloadPdf();
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      await download(
        `/api/contracts/${contractId}/pdf`,
        `contrato-${String(contractId).padStart(6, "0")}.pdf`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        }
      );
    } catch {
      alert("No se pudo generar el contrato.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleClick} disabled={loading}>
      {loading ? "Generando..." : "⬇ Descargar Contrato"}
    </button>
  );
}
```

---

## 10. Comandos de prueba

```bash
# Ejecutar todas las pruebas
pytest tests/ -v

# Ejecutar pruebas relacionadas con PDF
pytest tests/unit/services/test_event_payment.py tests/integration/ -v

# Ejecutar con cobertura
pytest tests/ --cov=. --cov-report=html
```

---

## 11. Estructura de commits recomendada

Cada commit debe ser autónomo y enfocado:

1. **Commit: `feat(pdf): add number_to_words utility`**
   - Agregar `utils/number_to_words.py`
   - Convertir montos numéricos a texto en español (formato boliviano)

2. **Commit: `feat(pdf): add data access layer for receipts and contracts`**
   - Agregar `data/receipt_service.py`
   - Agregar `data/contract_service.py`
   - Funciones para obtener datos de eventos, usuarios y pagos

3. **Commit: `feat(pdf): add PDF templates`**
   - Agregar `templates/receipt.html` (formato A6 horizontal)
   - Agregar `templates/contract.html` (formato A4)

4. **Commit: `feat(pdf): add receipt PDF endpoint`**
   - Agregar `web/receipts.py` con `GET /api/receipts/{event_id}/pdf`
   - Incluir verificación de permisos (propietario/admin)

5. **Commit: `feat(pdf): add contract PDF endpoint`**
   - Agregar `web/contracts.py` con `POST /api/contracts/{event_id}/pdf`
   - Incluir verificación de permisos (propietario/admin)

6. **Commit: `feat(pdf): register PDF routes in main.py`**
   - Incluir nuevos routers en la aplicación FastAPI

7. **Commit: `test(pdf): add unit tests for PDF services`**
   - Probar funciones de contexto de plantillas
   - Probar conversión number_to_words

8. **Commit: `test(pdf): add integration tests for PDF endpoints`**
- Probar generación exitosa de PDF
    - Probar denegación de permisos (403)
    - Probar escenarios no encontrados (404)
