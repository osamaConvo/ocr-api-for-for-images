import boto3
import time
from trp import Document


def startJob(s3BucketName, objectName):
    response = None
    client = boto3.client('textract')
    response = client.start_document_analysis(
    DocumentLocation={
        'S3Object': {
            'Bucket': s3BucketName,
            'Name': objectName
        }
    },FeatureTypes=["FORMS","TABLES"])

    return response["JobId"]

def isJobComplete(jobId):
    time.sleep(5)
    client = boto3.client('textract')
    response = client.get_document_analysis(JobId=jobId)
    status = response["JobStatus"]
    print("Job status: {}".format(status))

    while(status == "IN_PROGRESS"):
        time.sleep(5)
        response = client.get_document_analysis(JobId=jobId)
        status = response["JobStatus"]
        print("Job status: {}".format(status))

    return status

def getJobResults(jobId):

    pages = []

    time.sleep(5)

    client = boto3.client('textract')
    response = client.get_document_analysis(JobId=jobId)
    
    pages.append(response)
    print("Resultset page recieved: {}".format(len(pages)))
    nextToken = None
    if('NextToken' in response):
        nextToken = response['NextToken']

    while(nextToken):
        time.sleep(5)

        response = client.get_document_analysis(JobId=jobId, NextToken=nextToken)

        pages.append(response)
        print("Resultset page recieved: {}".format(len(pages)))
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']

    return pages

def getResults():
    # Document
    s3BucketName = "container-slip-textract"
    documentName = "cma_cgm.pdf"

    jobId = startJob(s3BucketName, documentName)
    print("Started job with id: {}".format(jobId))
    if(isJobComplete(jobId)):
        response = getJobResults(jobId)

    #print(response)

    # Print detected text
    for resultPage in response:
        for item in resultPage["Blocks"]:
            if item["BlockType"] == "LINE":
                print ('\033[94m' +  item["Text"] + '\033[0m')


    doc = Document(response)

    print(doc)

    for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                print ('\033[94m' +  item["Text"] + '\033[0m')
        
    for page in doc.pages:
        # Print fields
        print("Fields:")
        for field in page.form.fields:
            print("Key: {}, Value: {}".format(field.key, field.value))

        # Get field by key
        print("\nGet Field by Key:")
        key = "Phone Number:"
        field = page.form.getFieldByKey(key)
        if(field):
            print("Key: {}, Value: {}".format(field.key, field.value))

        # Search fields by key
        print("\nSearch Fields:")
        key = "address"
        fields = page.form.searchFieldsByKey(key)
        for field in fields:
            print("Key: {}, Value: {}".format(field.key, field.value))

    for page in doc.pages:
        for table in page.tables:
            for r, row in enumerate(table.rows):
                for c, cell in enumerate(row.cells):
                    print("Table[{}][{}] = {}".format(r, c, cell.text))

