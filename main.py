import csv
import json
import xmltodict
import xml.etree.ElementTree as ET
from decimal import *
import xlrd
import logging
from dateutil.parser import *


logging.basicConfig(filename="SupportBank.log", filemode="w", level=logging.DEBUG)
logging.info("Code started")

OWED = {}
FILES = []


def validateDate(date, row, file, fuzzy=False):
    try:
        parse(date, fuzzy=fuzzy)
        return True
    except ValueError:
        logging.info(f"Incorrect formatting of {date} in Date column of row {row} in input {file}")
        logging.info(f"Row {row} in input {file} has been skipped")
        print(f"Incorrect formatting of {date} in Date column of row {row} in input {file}")
        print(f"Row {row} in input {file} has been skipped")
        return False


def validateAmount(amount, row, file):
    try:
        Decimal(amount)
        return True
    except InvalidOperation:
        logging.info(f"Incorrect formatting of {amount} in Amount column of row {row} in input {file}")
        logging.info(f"Row {row} in input {file} has been skipped")
        print(f"Incorrect formatting of {amount} in Amount column of row {row} in input {file}")
        print(f"Row {row} in input {file} has been skipped")
        return False


def validateUniqueTransactions(transactionList):
    if transactionList in FILES:
        return True
    else:
        return False


def mergeDicts(dict1, dict2):
    for key, value in dict2.items():
        if dict2[key] in dict1.keys():
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = value

    return dict1


def getValuesAtDeepestLayer(my_dict):
    sub_vals = []
    actual_vals = []
    for val in my_dict.values():
        try:
            sub_vals += getValuesAtDeepestLayer(val)
        except AttributeError:
            actual_vals += [val]

    return sub_vals + actual_vals


def convertOleToDateTime(ole):
    ole = int(ole) - 2
    datetime_date = xlrd.xldate_as_datetime(ole, 0)
    date_object = datetime_date.date()
    string_date = date_object.strftime("%d-%m-%Y")
    return string_date


def csvToDict(file):
    dictNameAndBalance = {}
    rowCounter = 0
    with open(file, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            date = row["Date"]
            debt = row["Amount"]
            if validateAmount(debt, rowCounter, file) and validateDate(date, rowCounter, file):
                debtDecimal = Decimal(debt)

                if row["From"] not in dictNameAndBalance.keys():
                    dictNameAndBalance[row["From"]] = 0
                if row["To"] not in dictNameAndBalance.keys():
                    dictNameAndBalance[row["To"]] = 0

                fromAccountChange = Decimal(dictNameAndBalance[row["From"]])
                fromAccountChange -= debtDecimal
                dictNameAndBalance[row["From"]] = fromAccountChange

                ToAccountChange = Decimal(dictNameAndBalance[row["To"]])
                ToAccountChange += debtDecimal
                dictNameAndBalance[row["To"]] = ToAccountChange
            rowCounter += 1
    return dictNameAndBalance


def jsonToDict(file):
    f = open(file)
    jsonDict = json.load(f)

    dictNameAndBalance = {}
    rowCounter = 0
    for row in jsonDict:
        date = row["date"]
        debt = str(row["amount"])
        if validateAmount(debt, rowCounter, file) and validateDate(date, rowCounter, file):
            debtDecimal = Decimal(debt)

            if row["fromAccount"] not in dictNameAndBalance.keys():
                dictNameAndBalance[row["fromAccount"]] = 0
            if row["toAccount"] not in dictNameAndBalance.keys():
                dictNameAndBalance[row["toAccount"]] = 0

            fromAccountChange = Decimal(dictNameAndBalance[row["fromAccount"]])
            fromAccountChange -= debtDecimal
            dictNameAndBalance[row["fromAccount"]] = fromAccountChange

            ToAccountChange = Decimal(dictNameAndBalance[row["toAccount"]])
            ToAccountChange += debtDecimal
            dictNameAndBalance[row["toAccount"]] = ToAccountChange
        rowCounter += 1
    return dictNameAndBalance


def xmlToDict(file):
    tree = ET.parse(file)
    xml_data = tree.getroot()
    xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')

    data_dict = dict(xmltodict.parse(xmlstr))

    listDeepestLayer = getValuesAtDeepestLayer(data_dict)
    lenOfTransactions = len(listDeepestLayer[0])

    rowCounter = 0
    dictNameAndBalance = {}
    for i in range(lenOfTransactions):
        data = data_dict["TransactionList"]["SupportTransaction"][i]
        date = convertOleToDateTime(data["@Date"])
        debt = str(data["Value"])

        if validateAmount(debt, rowCounter, file) and validateDate(date, rowCounter, file):
            debtDecimal = Decimal(debt)

            if data["Parties"]["From"] not in dictNameAndBalance.keys():
                dictNameAndBalance[data["Parties"]["From"]] = 0
            if data["Parties"]["To"] not in dictNameAndBalance.keys():
                dictNameAndBalance[data["Parties"]["To"]] = 0

            fromAccountChange = Decimal(dictNameAndBalance[data["Parties"]["From"]])
            fromAccountChange -= debtDecimal
            dictNameAndBalance[data["Parties"]["From"]] = fromAccountChange

            ToAccountChange = Decimal(dictNameAndBalance[data["Parties"]["To"]])
            ToAccountChange += debtDecimal
            dictNameAndBalance[data["Parties"]["To"]] = ToAccountChange
        rowCounter += 1
    return dictNameAndBalance


def listAll():
    if not OWED.items():
        print("No Accounts found")
    for k, v in OWED.items():
        print(k, v)
    print("\n")


def listAccount(inputName):
    account = inputName[6:-1]
    for transaction in FILES:
        if ".csv" in transaction:
            with open(transaction, mode="r") as csv_file:
                csv_reader = csv.DictReader(csv_file)

                for row in csv_reader:
                    if row["From"] == account or row["To"] == account:
                        print(row["Date"], row["Narrative"])
        elif ".json" in transaction:
            f = open(transaction)
            jsonDict = json.load(f)

            for row in jsonDict:
                if row["fromAccount"] == account or row["toAccount"] == account:
                    print(row["date"], row["narrative"])
        elif ".xml" in transaction:
            tree = ET.parse(transaction)
            xml_data = tree.getroot()
            xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')

            data_dict = dict(xmltodict.parse(xmlstr))

            listDeepestLayer = getValuesAtDeepestLayer(data_dict)
            lenOfTransactions = len(listDeepestLayer[0])

            for i in range(lenOfTransactions):
                data = data_dict["TransactionList"]["SupportTransaction"][i]
                nameFrom = data["Parties"]["From"]
                nameTo = data["Parties"]["To"]
                if nameFrom == account or nameTo == account:
                    print(convertOleToDateTime(data["@Date"]), data["Description"])

    print("\n")


def importFile(response):
    fileName = response[13:-1]

    if ".csv" in fileName:
        if validateUniqueTransactions(fileName):
            print("Transaction document already exists in system\n"
                  "Document not added to Database\n")
        else:
            FILES.append(fileName)
            newDict = csvToDict(fileName)
            mergeDicts(OWED, newDict)
            print("File added to database\n")
    elif ".json" in fileName:
        if validateUniqueTransactions(fileName):
            print("Transaction document already exists in system\n"
                  "Document not added to Database\n")
        else:
            FILES.append(fileName)
            newDict = jsonToDict(fileName)
            mergeDicts(OWED, newDict)
            print("File added to database\n")
    elif ".xml" in fileName:
        if validateUniqueTransactions(fileName):
            print("Transaction document already exists in system\n"
                  "Document not added to Database\n")
        else:
            FILES.append(fileName)
            newDict = xmlToDict(fileName)
            mergeDicts(OWED, newDict)
            print("File added to database\n")


def exportFile():
    with open("file.txt", "w") as f:
        for key, value in OWED.items():
            f.write('%s:%s\n' % (key, value))


def main():
    end = False
    while not end:
        response = input("Welcome \n"
                         "Please enter one of the following commands: \n"
                         "List All \n"
                         "List [Account] \n"
                         "Import File [filename] \n"
                         "Export File [filename] \n"
                         "Quit \n")

        if response == "List All":
            listAll()

        elif "List [" in response:
            listAccount(response)

        elif "Import File [" in response:
            importFile(response)

        elif "Export File [" in response:
            importFile(response)
            exportFile()

        elif response == "Quit":
            end = True

        else:
            print("Sorry that is not a valid input, Please try again\n")


if __name__ == "__main__":
    main()
