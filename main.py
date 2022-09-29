import csv
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


def addToBalanceDict(file):
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


def listAll():
    firstCSV = addToBalanceDict("Transactions2014.csv")
    print("\nFirst CSV \n")

    for k, v in firstCSV.items():
        print(k, v)

    secondCSV = addToBalanceDict("DodgyTransactions2015.csv")
    print("\nSecond CSV \n")

    for k, v in secondCSV.items():
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

listAll()
