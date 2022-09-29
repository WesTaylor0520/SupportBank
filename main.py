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
        return False


def validateAmount(amount, row, file):
    try:
        Decimal(amount)
        return True
    except InvalidOperation:
        logging.info(f"Incorrect formatting of {amount} in Amount column of row {row} in input {file}")
        logging.info(f"Row {row} in input {file} has been skipped")
        return False


def transactionsListDuplication(transactionList):
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
    print("\n")
    for k, v in OWED.items():
        print(k, v)
    print("\n")


def listAccount(inputName):
    for transaction in FILES:
        if ".csv" in transaction:
            with open(transaction, mode="r") as csv_file:
                csv_reader = csv.DictReader(csv_file)

                for row in csv_reader:
                    if row["From"] == inputName or row["To"] == inputName:
                        print(row["Date"], row["Narrative"])
        elif ".json" in transaction:
            f = open(transaction)
            jsonDict = json.load(f)

            for row in jsonDict:
                if row["fromAccount"] == inputName or row["toAccount"] == inputName:
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
                if nameFrom == inputName or nameTo == inputName:
                    print(convertOleToDateTime(data["@Date"]), data["Description"])

    print("\n")


def main():
    end = False
    while not end:
        response = input("Welcome \n"
                         "Please enter one of the following commands: \n"
                         "1. List All \n"
                         "2. List Account \n"
                         "3. Import File \n"
                         "4. Delete Database \n"
                         "5. Quit \n")

        if response == "1":
            listAll()

        elif response == "2":
            account = input("Please enter the name of the account: ")
            listAccount(account)

        elif response == "3":
            fileName = input("Please enter the name of your file \n")
            fileType = input("Please select a file type:\n"
                             "1. CSV\n"
                             "2. JSON\n"
                             "3. XML\n")

            if fileType == "1":
                completeFileName = fileName + ".csv"
                if transactionsListDuplication(completeFileName):
                    print("Transaction document already exists in system\n"
                          "Document not added to Database\n")
                else:
                    FILES.append(completeFileName)
                    newDict = csvToDict(completeFileName)
                    mergeDicts(OWED, newDict)
                    print("File added to database\n")
            elif fileType == "2":
                completeFileName = fileName + ".json"
                if transactionsListDuplication(completeFileName):
                    print("Transaction document already exists in system\n"
                          "Document not added to Database\n")
                else:
                    FILES.append(completeFileName)
                    newDict = jsonToDict(completeFileName)
                    mergeDicts(OWED, newDict)
                    print("File added to database\n")
            elif fileType == "3":
                completeFileName = fileName + ".xml"
                if transactionsListDuplication(completeFileName):
                    print("Transaction document already exists in system\n"
                          "Document not added to Database\n")
                else:
                    FILES.append(completeFileName)
                    newDict = xmlToDict(completeFileName)
                    mergeDicts(OWED, newDict)
                    print("File added to database\n")

            else:
                print("Sorry your chosen file cannot be found")

        elif response == "4":
            pass

        elif response == "5":
            end = True

        else:
            print("Sorry that is not a valid input, Please try again\n")


if __name__ == "__main__":
    main()
