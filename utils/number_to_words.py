def number_to_words_es(amount: float) -> str:
    """
    Convert a numeric amount to Spanish literal representation.
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