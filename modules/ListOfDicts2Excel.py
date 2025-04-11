from openpyxl import Workbook

def write_to_excel(results, output_file):
    workbook = Workbook()

    for result in results:
        if result is None:
            continue
        else:
            # If sheet named 'Data' does not exist, create it
            if 'Data' not in workbook:
                worksheet = workbook.create_sheet(title='Data')
                worksheet.append([key for key in result])

            # Insert the row of values that need to be inserted (action happens whether header row was created or not
            if result is not None:
                worksheet = workbook['Data']
                worksheet.append(list(result.values()))

    # format the resulting spreadsheet
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2) * 1.0
        worksheet.column_dimensions[column_letter].width = adjusted_width

    # Freeze top rows
    worksheet.freeze_panes = 'A2'
    workbook.remove(workbook['Sheet'])
    workbook.save(output_file)