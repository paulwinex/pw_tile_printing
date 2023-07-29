import cups


def print_image(path: str, printer_name: str) -> int:
    """
    Send image to printer

    :param path:
    :param printer_name:
    """
    conn = cups.Connection()
    printers = conn.getPrinters()
    if printer_name not in printers:
        raise (f"Error: Printer '{printer_name}' not found.")
    print_job = conn.printFile(printer_name, str(path), "Image Print", {})
    return print_job


def get_printers() -> tuple:
    """
    Get printer name list
    """
    conn = cups.Connection()
    printers = conn.getPrinters()
    return tuple(printers.keys())

