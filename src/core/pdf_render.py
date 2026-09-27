import os
import subprocess
from openpyxl import load_workbook
from openpyxl.styles import Border, Side, Alignment, Font


def render_one_student(excel_template: str, data: dict, output_folder: str) -> str:
    """
    Рендерит один PDF. Возвращает путь к готовому PDF.

    :param excel_template: путь к шаблону xlsx
    :param data: словарь с данными студента
    :param output_folder: папка для сохранения PDF

    :return: путь к готовому PDF
    """

    code = data["code"]
    surname_name = data["surname_name"]

    # Загрузка шаблона
    wb = load_workbook(excel_template)
    try:
        ws = wb["Протокол"]
        fill_template(ws, data)

        # Сохранение временного xlsx
        tmp_xlsx = os.path.abspath(f"{code} {surname_name}.xlsx")
        wb.save(tmp_xlsx)
    finally:
        wb.close()

    # Конвертация в PDF
    pdf_path = os.path.abspath(
        os.path.join(output_folder, f"{code} {surname_name}.pdf")
    )
    convert_to_pdf(tmp_xlsx, pdf_path)

    # Удаление временного xlsx
    try:
        os.remove(tmp_xlsx)
    except OSError:
        pass

    return pdf_path


def fill_template(ws, data: dict) -> None:
    """
    Заполняет лист 'Протокол'. Все данные берутся из dict.

    :param ws: Экземпляр WorkBook
    :param data: Словарь с информацией

    return: None
    """

    thin_border = Border(bottom=Side(border_style="thin", color="000000"))

    for row_num in range(1, 60):
        ws.row_dimensions[row_num].height = 15

    ws.row_dimensions[14].height = 35
    ws.row_dimensions[17].height = 35
    ws.row_dimensions[19].height = 35

    set_cell(ws, "A1",
              "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ\n"
              "Федеральное государственное бюджетное образовательное "
              "учреждение высшего образования\n"
              "«Тамбовский государственный технический университет»",
             h_align="center", v_align="center", wrap=True, size=12)
    ws.row_dimensions[1].height = 42

    set_cell(ws, "A8", "ПРОТОКОЛ №___________",
             h_align="center", v_align="center", size=14, bold=True)
    ws.row_dimensions[8].height = 20

    set_cell(ws, "A10", "от  «___»__________________20___г.",
             h_align="center", v_align="center", size=12)
    ws.row_dimensions[10].height = 15

    set_cell(ws, "I5", "___________Д.Ю. Муромцев",
             h_align="left", v_align="center", size=12)
    ws.row_dimensions[5].height = 15

    set_cell(ws, "I6", "«___»______________20___г.",
             h_align="left", v_align="center", size=12)
    ws.row_dimensions[6].height = 15

    set_cell(ws, ws.cell(row=29, column=3), data["surname_datelnyi_p"],
             h_align="center", italic=True, border=thin_border)
    set_cell(ws, ws.cell(row=39, column=4), data["surname_name_p"],
             h_align="center", italic=True, border=thin_border)
    set_cell(ws, "J39", "", h_align="left", border=thin_border)

    set_cell(ws, ws.cell(row=26, column=4), data["discipline"],
             wrap=True, v_align="bottom", italic=True, border=thin_border)
    ws.row_dimensions[26].height = 30

    set_cell(ws, ws.cell(row=23, column=1), data["direction"],
             wrap=True, v_align="bottom", italic=True, border=thin_border)
    ws.row_dimensions[23].height = 30

    set_cell(ws, ws.cell(row=14, column=1), data["comm1_text"],
             wrap=True, v_align="bottom", italic=True, border=thin_border)
    set_cell(ws, ws.cell(row=42, column=9), data["comm1_fio"],
             h_align="center", v_align="center", border=thin_border)

    set_cell(ws, ws.cell(row=17, column=1), data["comm2_text"],
             wrap=True, v_align="bottom", italic=True, border=thin_border)
    set_cell(ws, ws.cell(row=45, column=9), data["comm2_fio"],
             h_align="center", v_align="center", border=thin_border)

    set_cell(ws, ws.cell(row=19, column=1), data["comm3_text"],
             wrap=True, v_align="bottom", italic=True, border=thin_border)
    set_cell(ws, ws.cell(row=47, column=9), data["comm3_fio"],
             h_align="center", v_align="center", border=thin_border)

    if len(data["surname_name_p"]) > 35:
        ws.cell(row=39, column=4).font = Font(name="Times New Roman", size=8, italic=True)
    else:
        ws.cell(row=39, column=4).font = Font(name="Times New Roman", size=12, italic=True)

    ws.row_dimensions[2].height = 20
    ws.row_dimensions[7].height = 5
    ws.row_dimensions[21].height = 5
    ws.row_dimensions[25].height = 5
    ws.row_dimensions[28].height = 5
    ws.row_dimensions[44].height = 10
    for r in (33, 34, 35, 36, 37):
        ws.row_dimensions[r].height = 18


def set_cell(ws, cell_ref, value, *, h_align="left", v_align="center",
             wrap=False, size=12, italic=False, bold=False, border=None) -> None:
    """

    :param ws:
    :param cell_ref:
    :param value:
    :param h_align:
    :param v_align:
    :param wrap:
    :param size:
    :param italic:
    :param bold:
    :param border:

    :return:
    """


    cell = ws[cell_ref] if isinstance(cell_ref, str) else cell_ref
    cell.value = value
    cell.alignment = Alignment(horizontal=h_align, vertical=v_align, wrap_text=wrap)
    cell.font = Font(name="Times New Roman", size=size, italic=italic, bold=bold)
    if border is not None:
        cell.border = border


def convert_to_pdf(excel_path: str, pdf_path: str) -> None:
    """
    Конвертирует Excel → PDF через cscript + VBS.

    :param excel_path:
    :param pdf_path:

    :return: None
    """

    vba_script = f'''
        Dim xlApp
        Dim xlBook
        Set xlApp = CreateObject("Excel.Application")
        xlApp.Visible = False
        Set xlBook = xlApp.Workbooks.Open("{excel_path}")
        xlBook.Sheets(1).ExportAsFixedFormat 0, "{pdf_path}"
        xlBook.Close False
        xlApp.Quit
        Set xlBook = Nothing
        Set xlApp = Nothing
    '''

    vbs_file = os.path.abspath(f"temp_convert_{os.getpid()}.vbs")
    with open(vbs_file, "w", encoding="windows-1251") as f:
        f.write(vba_script)

    try:
        result = subprocess.run(
            ["cscript", "//Nologo", vbs_file],
            shell=False, timeout=60, check=False,
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"cscript error (rc={result.returncode}): {result.stdout} | {result.stderr}"
            )
    finally:
        try:
            os.remove(vbs_file)
        except OSError:
            pass
