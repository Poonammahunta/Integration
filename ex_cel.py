from openpyxl.reader.excel import load_workbook
wb = load_workbook("C:\\Users\\sanjeeb das\\Desktop\\offline_report.xlsx")
sheet = wb.get_sheet_by_name('Sheet1')

print sheet['A1'].value

