import csv
import json
from decimal import *
import logging
from dateutil.parser import *

logging.basicConfig(filename="SupportBank.log", filemode="w", level=logging.DEBUG)
logging.info("Code started")


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


def mergeDicts(dict1, dict2):
    for key, value in dict2.items():
        dict1[key] = dict1[key] + dict2[key]

    return dict1


def csvToDict(file):
    BalanceDict = {}
    rowCounter = 0
    with open(file, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            date = row["Date"]
            debt = row["Amount"]
            if validateAmount(debt, rowCounter, file) and validateDate(date, rowCounter, file):
                debtDecimal = Decimal(debt)

                if row["From"] not in BalanceDict.keys():
                    BalanceDict[row["From"]] = 0
                if row["To"] not in BalanceDict.keys():
                    BalanceDict[row["To"]] = 0

                fromAccountChange = Decimal(BalanceDict[row["From"]])
                fromAccountChange -= debtDecimal
                BalanceDict[row["From"]] = fromAccountChange

                ToAccountChange = Decimal(BalanceDict[row["To"]])
                ToAccountChange += debtDecimal
                BalanceDict[row["To"]] = ToAccountChange
            rowCounter += 1
    return BalanceDict


def jsonToDict(file):
    f = open(file)
    jsonDict = json.load(f)

    BalanceDict = {}
    rowCounter = 0
    for row in jsonDict:
        date = row["date"]
        debt = str(row["amount"])
        if validateAmount(debt, rowCounter, file) and validateDate(date, rowCounter, file):
            debtDecimal = Decimal(debt)

            if row["fromAccount"] not in BalanceDict.keys():
                BalanceDict[row["fromAccount"]] = 0
            if row["toAccount"] not in BalanceDict.keys():
                BalanceDict[row["toAccount"]] = 0

            fromAccountChange = Decimal(BalanceDict[row["fromAccount"]])
            fromAccountChange -= debtDecimal
            BalanceDict[row["fromAccount"]] = fromAccountChange

            ToAccountChange = Decimal(BalanceDict[row["toAccount"]])
            ToAccountChange += debtDecimal
            BalanceDict[row["toAccount"]] = ToAccountChange
        rowCounter += 1
    for k, v in BalanceDict.items():
        print(k, v)


def listAll():
    firstCSV = csvToDict("Transactions2014.csv")
    print("\nFirst CSV \n")

    for k, v in firstCSV.items():
        print(k, v)

    secondCSV = csvToDict("DodgyTransactions2015.csv")
    print("\nSecond CSV \n")

    for k, v in secondCSV.items():
        print(k, v)

    merged = mergeDicts(firstCSV, secondCSV)
    print("\nMerged \n")

    for k, v in merged.items():
        print(k, v)


def listAccount(inputName):
    with open("Transactions2014.csv", mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            if row["From"] == inputName or row["To"] == inputName:
                print(row["Date"], row["Narrative"])


# def main():
#     response = input("Welcome \n"
#                      "Please enter one of the following commands: \n"
#                      "List All \n"
#                      "List [Account])")
#
#     if response.lower() == "list all":
#         listAll()
#     elif:
#         response

# listAll()
jsonToDict("Transactions2013.json")
