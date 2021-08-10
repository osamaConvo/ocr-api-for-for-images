import boto3
from trp import Document

# Amazon Textract client
textract = boto3.client('textract')

def text_extraction_images(binary_data):
    # Call Amazon Textract    
    response = textract.analyze_document(Document={'Bytes': binary_data},FeatureTypes=["FORMS","TABLES"])

    # print(response)
    doc = Document(response)

    # for item in response["Blocks"]:
    #     if item["BlockType"] == "LINE":
    #         print ('\033[94m' +  item["Text"] + '\033[0m')
      
    # for page in doc.pages:
    #     # Print fields
    #     print("Fields:")
    #     for field in page.form.fields:
    #         print("Key: {}, Value: {}".format(field.key, field.value))

    #     # Get field by key
    #     print("\nGet Field by Key:")
    #     key = "Phone Number:"
    #     field = page.form.getFieldByKey(key)
    #     if(field):
    #         print("Key: {}, Value: {}".format(field.key, field.value))

    #     # Search fields by key
    #     print("\nSearch Fields:")
    #     key = "address"
    #     fields = page.form.searchFieldsByKey(key)
    #     for field in fields:
    #         print("Key: {}, Value: {}".format(field.key, field.value))

    # for page in doc.pages:
    #     for table in page.tables:
    #         for r, row in enumerate(table.rows):
    #             for c, cell in enumerate(row.cells):
    #                 print("Table[{}][{}] = {}".format(r, c, cell.text))


    if 'AXIS CONTAINER SERVICES (PRIVATE) LIMITED' in str(response) or 'Axis Container Services (Pvt) Ltd.' in str(response):
        if 'EMPTY IN / OUT' in str(response):
            return axis_empty_formation(doc)
        else:
            return axis_lolo_formation(doc)
    elif 'DEX INTERNATIONAL CONTAINER TERMINAL' in str(response):
        if 'EMPTY IN / OUT' in str(response):
            dex_empty_formation(doc)
            return "Format Not Available"
        else:
            return dex_lolo_formation(doc)
    elif 'Pak Pacific Container Terminal (PVT) Ltd.' in str(response):
        if 'DELIVER EMPTY CONTAINERS' in str(response):
            return ppct_empty_formation(doc)
        else:
            return ppct_lolo_formation(doc)
    elif 'QASIM INTERNATIONAL CONTAINER TERMINAL PAKISTAN LIMITED' in str(response):
        if 'Received Export Container' in str(response):
            return qasim_int_formation(doc)
        else:
            return "Format Not Available"
    elif 'Hutchison Ports Pakistan' in str(response):
        if 'Receive Export Container' in str(response):
            return hutchisonport_lolo_formation(doc)
        else:
            hutchisonport_empty_formation(doc)
            return "Format Not Available"
    else:
        return "Not Supported"

def axis_empty_formation(data):
    final_format = {}
    final_format['Company'] = 'Axis Container Service (PVT) LTD'
    final_format['Type'] = 'Empty'
    for page in data.pages:
        for field in page.form.fields:
            final_format[str(field.key)] = str(field.value)
            # print("Key: {}, Value: {}".format(field.key, field.value))
        for table in page.tables:
            for r, row in enumerate(table.rows):
                for c, cell in enumerate(row.cells):
                    if c % 2 == 0 and cell.text.strip() not in final_format.keys():
                        final_format[cell.text.strip()] = row.cells[c+1].text.strip()
                # print("Table[{}][{}] = {}".format(r, c, cell.text))
    return final_format

def axis_lolo_formation(data):
    final_format = {}
    final_format['Company'] = 'Axis Container Service (PVT) LTD'
    final_format['Type'] = 'lolo'
    keys = ["Receipt No","Date","Shift","Received with thanks from ","the sum of Rupees"]
    for page in data.pages:
        for key in keys:
            fields = page.form.searchFieldsByKey(key)
            for field in fields:
                final_format[str(field.key).strip()] = str(field.value).strip()
        for table in page.tables:
            for r, row in enumerate(table.rows):
                for c, cell in enumerate(row.cells):
                    if r == 0 and cell.text.strip() not in final_format.keys():
                        if cell.text.strip() == 'Signature & Stamp' or cell.text.strip() == 'Thanks for your Business' or cell.text == '':
                            print('pass')
                        else:
                            final_format[cell.text.strip()] = table.rows[1].cells[c].text.strip()
    return final_format

def dex_empty_formation(data):
    pass

def dex_lolo_formation(data):
    final_format = {}
    keys = ["Receipt No","Date","Shift","Received with thanks from ","Ref#","Line","PO #","Vessel","Voyage","Cost Center","the sum of Rupees"]
    for page in data.pages:
        for key in keys:
            fields = page.form.searchFieldsByKey(key)
            for field in fields:
                final_format[str(field.key).strip().replace(":","")] = str(field.value).strip()
        for table in page.tables:
            for r, row in enumerate(table.rows):
                for c, cell in enumerate(row.cells):
                    if r == 0 and cell.text.strip() not in final_format.keys():
                        final_format[cell.text.strip().replace(":","")] = table.rows[1].cells[c].text.strip().replace(" ","")
    return final_format

def ppct_empty_formation(data):
    final_format = {}
    keys = ["Issue Date","EIR No.","Divry Date","Line Name","Container #","Size","Condition","Voyage","Shipper","Transportor","Truck No.","Booking No","POL","Remarks"]
    for page in data.pages:
        
        for key in keys:
            fields = page.form.searchFieldsByKey(key)
            for field in fields:
                final_format[str(field.key).strip()] = str(field.value).strip()
        
        for idx, line in enumerate(page.lines):
            print(idx, line.text)
            if line.text.strip() == 'Shift':
                if page.lines[idx+1].text.strip() != 'Remarks':
                    final_format[line.text.strip()] = page.lines[idx+1].text.strip()
                    print(final_format)

        for table in page.tables:
            for r, row in enumerate(table.rows):
                for c, cell in enumerate(row.cells):
                    if c % 2 == 0 and cell.text.strip() not in final_format.keys() and cell.text.strip() != '':
                        final_format[cell.text.strip()] = row.cells[c+1].text.strip()
    
    return final_format

def ppct_lolo_formation(data):
    final_format = {}
    for page in data.pages:
        for idx, line in enumerate(page.lines):
            print(idx, line.text)
            if 'RECEIPT #' in line.text.strip() and 'DT' in line.text.strip():
                receipt_lst = line.text.split()
                receipt_key = ''.join(receipt_lst[:2])
                receipt_value = receipt_lst[2]
                
                final_format[receipt_key] = receipt_value

                date_key = receipt_lst[3]
                date_value = receipt_lst[4]
                final_format[date_key] = date_value

                ro_num_key = receipt_lst[5]
                if len(receipt_lst) > 6:
                    ro_num_value = receipt_lst[6]
                else:
                    ro_num_value = 'None'
                final_format[ro_num_key] = ro_num_value
            
            if 'CONTAINER #' in line.text.strip():
                if page.lines[idx+1].text.strip() != 'Received with thanks':
                    final_format[line.text.strip()] = page.lines[idx+1].text.strip()
            
            if 'DESCRIPTION:' in line.text.strip():
                final_format[str(line.text.split(':')[0])] =  line.text.strip().split(':')[1]
            
            if 'HD' in line.text.strip():
                if page.lines[idx+1].text.strip() != "Customer's Copy":
                    final_format[line.text.strip()] =  page.lines[idx+1].text.strip()
    print(final_format)
    return final_format

def hutchisonport_empty_formation(data):
    pass

def hutchisonport_lolo_formation(data):
    final_format = {}
    keys = ['LINE OPERATOR','DATE/TIME','CONTAINER','CONTAINER TYPE','SHIPPER',
    'VESSEL','VOYAGE','LOAD PORT','STATUS','GROSS WEIGHT',
    'SAFE WEIGHT','Shipper VGM','COMMODITY','HAZARD CODE','ORIGIN',
    'DESTINATION','TRUCKING COMPANY','TRUCK ID','AGENT','LINE SLAL''LINE SEAL','OTHER SEAL']
    check_func = lambda value : value if value != '' else 'None'
    
    for page in data.pages:
        for key in keys:
            fields = page.form.searchFieldsByKey(key)
            for field in fields:
                final_format[str(field.key).strip().replace(":","")] = str(field.value).strip()
        for table in page.tables:
            # print(table)
            for r, row in enumerate(table.rows):
                print(row)
                for c, cell in enumerate(row.cells):
                    print(cell,c)
                    if 'TRANSACTION' in cell.text.strip():
                        # print(cell.text.strip().split(':'))
                        value = cell.text.strip().split(':')[1]
                        final_format[cell.text.strip().split(':')[0]] = check_func(value)
                    if 'SET TEMP' in cell.text.strip():
                        # print(cell.text.strip().split(':'))
                        value = cell.text.strip().split(':')[1]
                        final_format[cell.text.strip().split(':')[0]] = check_func(value)
                    if 'LINE SEAL' in cell.text.strip()  or 'LINE SLAL' in cell.text.strip():
                        if 'LINE SLAL' in cell.text.strip():
                            # print(row.cells[1].text.strip())
                            value = row.cells[1].text.strip()
                            final_format['LINE SEAL'] = check_func(value)
                        else:
                            print(row.cells[1].text.strip().split(':'))
                            value = row.cells[1].text.strip().split(':')[1]
                            final_format['LINE SEAL'] = check_func(value)
                    if 'BUNDLE SON ID' in cell.text.strip():
                        # print(cell.text.strip().split(':'))
                        value = cell.text.strip().split(':')[1]
                        final_format[cell.text.strip().split(':')[0]] = check_func(value)
                    # if 'CUSTOMS SEAL' in cell.text.strip():
                    #     # print(cell.text.strip().split(':'))
                    #     value = cell.text.strip().split(':')[1]
                    #     final_format[cell.text.strip().split(':')[0]] = check_func(value)
                    # if 'SECURITY SEAL' in cell.text.strip():
                    #     # print(cell.text.strip().split(':'))
                    #     value = cell.text.strip().split(':')[1]
                    #     final_format[cell.text.strip().split(':')[0]] = check_func(value)
                    # if 'OTHER SEAL' in cell.text.strip():
                    #     # print(cell.text.strip().split(':'))
                    #     value = cell.text.strip().split(':')[1]
                    #     final_format[cell.text.strip().split(':')[0]] = check_func(value)
                    # print("Table[{}][{}] = {}".format(r, c, cell.text))
    # print(final_format)
    return final_format

def qasim_int_formation(data):
    final_format = {}
    keys = ['COMPANY','SEAL NUMBER','FORWARDER','CONTAINER','DATE/TIME','COMMODITY','VESSEL/VOYAGE','SAFE WEIGHT','ORIGIN/DESTINATION','REGISTRATION','GROSS WEIGHT','GROUP ID'
    'EMPTY RETURN DEPOT','PORT OF LOADING','CONTAINER TYPE','STATUS/HAZARD','CONSIGN/SHIPPER','Damages & Notes']
    check_func = lambda value : value if value != '' else 'None'
    
    for page in data.pages:
        for key in keys:
            fields = page.form.searchFieldsByKey(key)
            for field in fields:
                final_format[str(field.key).strip().replace(":","")] = str(field.value).strip()
        for table in page.tables:
            for r, row in enumerate(table.rows):
                for c, cell in enumerate(row.cells):
                    if 'LINE OPERATOR' in cell.text.strip():
                        # print(cell.text.strip().split(':'))
                        value = ''.strip().join(cell.text.strip().split(':')[1:])
                        final_format[cell.text.strip().split(':')[0]] = check_func(value)
                    if 'EMPERATURE' in cell.text.strip()  or 'TEMPERATURE' in cell.text.strip():
                        print(cell.text.strip().split(':'))
                        value = cell.text.strip().split(':')[1]
                        final_format['TEMPERATURE'] = check_func(value)
                    # print("Table[{}][{}] = {}".format(r, c, cell.text))
    # print(final_format)
    return final_format