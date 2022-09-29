import csv
from decimal import *
import logging

logging.basicConfig(filename="SupportBank.log", filemode="w", level=logging.DEBUG)
logging.info("Code started")


def addToBalanceDict(file):
    BalanceDict = {}
    with open(file, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row["From"] not in BalanceDict.keys():
                BalanceDict[row["From"]] = 0
            if row["To"] not in BalanceDict.keys():
                BalanceDict[row["To"]] = 0

            debt = Decimal(row["Amount"])

            fromAccountChange = Decimal(BalanceDict[row["From"]])
            fromAccountChange -= debt
            BalanceDict[row["From"]] = fromAccountChange

            ToAccountChange = Decimal(BalanceDict[row["To"]])
            ToAccountChange += debt
            BalanceDict[row["To"]] = ToAccountChange
    return BalanceDict


def listAll():
    try:
        firstCSV = addToBalanceDict("Transactions2014.txt")
        logging.info("firstCSV Created")
    except InvalidOperation:
        logging.info("firstCSV failed to be created")

    try:
        secondCSV = addToBalanceDict("DodgyTransactions2015.txt")
    except InvalidOperation:
        logging.info("secondCSV failed to be created")

    for k, v in firstCSV.items():
        print(k, v)

    for k, v in secondCSV.items():
        print(k, v)


def listAccount(inputName):
    with open("Transactions2014.txt", mode="r") as csv_file:
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
