import csv
import sys
import re

class CryptoDeque:
    def __init__(self):
        self.orders = []
        self.price = 0
        self.profits = 0

    def isEmpty(self):
        return self.orders == []

    def addFront(self, order): #enqueue
        self.price = float(order[1])
        self.orders.append(order)

    def addRear(self, order): #use when splitting between orders
        self.orders.insert(0, order) #replace partial order
        self.profits -= float(order[0]) * (self.price - float(order[1])) #decrease profits to account for returning partial order

    def removeFront(self): #not going to use this
        return self.orders.pop()

    def removeRear(self, sellPrice): #dequeue
        self.price = sellPrice
        a = self.orders.pop(0)
        self.profits += float(a[0]) * (self.price - float(a[1]))
        return a

    def size(self):
        return len(self.orders)


def processOrder(token, order):
    q = assets[token] #this is the dequeue
    orderQuantity = float(order[0])
    orderPrice = float(order[1])
    if orderQuantity > 0:
        q.addFront(order) #purchase
        quantity[token] += orderQuantity
    else: #sell
        batch = q.removeRear(orderPrice) #sell all of the asset bought at the oldest price
        batchQuantity = float(batch[0])
        batchPrice = float(batch[1])
        quantity[token] -= min(abs(orderQuantity), batchQuantity)
        if abs(orderQuantity) > batchQuantity: #need to split this sell order across multiple buy orders
            return processOrder(token, (orderQuantity + batchQuantity, orderPrice)) #process the remainder
        elif abs(orderQuantity) < batchQuantity: #smaller than a single buy order
            q.addRear((batchQuantity - abs(orderQuantity), batchPrice)) #place residual order at the front of the queue


def catchErrors(line):
    try:
        date = line[0]
        asset = line[1]
        price = float(line[2])
        amount = float(line[3])
        assert price >=0,"Assets cannot have negative prices" #tested
        if amount < 0:
            assert asset in quantity.keys(),"detected sale before purchase (short selling is not supported)" #tested
            assert abs(amount) <= quantity[asset],"sell amount exceeds supply" #tested
    except ValueError as err:
        print("incompatible datatypes: must be Date, String, Float, Float")#tested

file = open(sys.argv[1])
reader = csv.reader(file)
assets = {}
quantity = {}
value = {}
portfolioValue = 0
grossProfit = 0
for line in reader:
    if line[0] != "DATE":
        catchErrors(line)
        if line[1] not in assets.keys():
            assets[line[1]] = CryptoDeque()
            quantity[line[1]] = 0
        theOrder = (line[3], line[2])
        processOrder(line[1], theOrder)


print("Portfolio (" + str(len(assets.keys())) + " assets)")
#print ("assets")
for asset in assets.keys():
    value[asset] = quantity[asset] * assets[asset].price
    portfolioValue += value[asset]
    print(asset + ": " + str(quantity[asset]) + " $" + str(value[asset]))
print("Total portfolio value: $" + str(portfolioValue))
print("Portfolio P&L (" + str(len(assets.keys())) + " assets) :")
for asset in assets:
    grossProfit += assets[asset].profits
    print(asset + ": $" + str(assets[asset].profits))
print("Total P&L: $" + str(grossProfit))
