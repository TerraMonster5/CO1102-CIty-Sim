from __future__ import annotations
import random
from copy import copy

class City:
    def __init__(self, pop: int, growth: int, casualties: int) -> None:
        self.__pop = pop
        self.__growth = growth
        self.__casualties = casualties
        self.__entering = 0
        self.__leaving = 0
    
    def updateOne(self) -> None:
        self.__pop = int(self.__pop * 1+self.__growth/100)
    
    def updateTwo(self) -> None:
        if random.randint(1, 10) == 1:
            self.__pop -= self.__casualties
    
    def calcBiggerCity(self, cities: list[City]) -> None:
        newcities = copy(cities)
        if self in newcities:
            newcities.remove(self)
        for _ in range(self.__pop):
            if random.randint(0, 1):
                continue

            newCity = random.choice(cities)
            if random.randint(1, self.__pop+newCity.getPop()) > self.__pop:
                newCity.addEntering(1)
                self.__leaving += 1
    
    def updateThree(self) -> None:
        self.__pop -= self.__leaving
        self.__pop += self.__entering
        self.__leaving = 0
        self.__entering = 0
    
    def addEntering(self, new: int) -> None:
        self.__entering += new

    def getPop(self) -> int:
        return self.__pop

cities = [City(987500, 7, 12), City(1000000, 4, 11)]

for x in range(30):
    print(x, end=" ")
    cities[0].updateOne()
    cities[1].updateOne()
    cities[0].updateTwo()
    cities[1].updateTwo()
    cities[0].calcBiggerCity(cities)
    cities[1].calcBiggerCity(cities)
    cities[0].updateThree()
    cities[1].updateThree()
    print(cities[0].getPop(), cities[1].getPop())