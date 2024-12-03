from __future__ import annotations
import random
import tkinter as tk
from tkinter import ttk
from functools import partial
from threading import Thread
from time import sleep
from copy import deepcopy

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
        newcities = deepcopy(cities)
        if self in newcities:
            newcities.remove(self)
        self.__leaving = 0
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
    
    def addEntering(self, new: int) -> None:
        self.__entering += new

    def getPop(self) -> int:
        return self.__pop

class CitiesList(tk.LabelFrame):
    def __init__(self, master, max: int=10, cnf: dict={}, **kwargs):
        kwargs = cnf or kwargs

        self.__max = max

        self.__label = ttk.Label(master, text="Cities")

        super().__init__(master, labelwidget=self.__label, width=111, height=max*21+42, **kwargs)

        self.grid_propagate(False)
        self.columnconfigure(0, minsize=33)
        self.columnconfigure(1, minsize=62)

        ttk.Label(self, text="Index", anchor="center").grid(row=0, column=0)
        ttk.Label(self, text="Population").grid(row=0, column=1)

        self.__textVars: list[tk.StringVar] = []
        self.__cities: list[City] = []
        self.__buttonRef: dict[int, int] = dict()
        self.__records = [[] for _ in range(max)]
        self.__free = 0
        self.__count = 0

        self.__cancelIcon = tk.PhotoImage(file="close.png").subsample(4, 4)
    
    def addCity(self, pop: int, growth: int, casualties: int) -> None:
        if self.__free >= self.__max:
            return
        
        self.__textVars.append(tk.StringVar())

        self.__textVars[self.__free].set(str(pop))
        
        self.__cities.append(City(pop, growth, casualties))
        
        self.__records[self.__free].append(ttk.Label(self, text=self.__count))

        self.__records[self.__free].append(ttk.Entry(self, width=9, textvariable=self.__textVars[self.__free]))
        self.__records[self.__free][1].state(["readonly"])

        self.__records[self.__free].append(tk.Button(self,
                                                     image=self.__cancelIcon,
                                                     relief="flat",
                                                     overrelief="flat",
                                                     bd=0,
                                                     width=10,
                                                     command=partial(self.__removeCity, self.__count)))
        
        for col in range(3):
            self.__records[self.__free][col].grid(row=self.__free+1, column=col)
        
        self.__buttonRef[self.__count] = self.__free
        
        self.__free += 1
        self.__count += 1
    
    def __removeCity(self, index) -> None:
        row = self.__buttonRef[index]

        for wgt in self.__records[row]:
            wgt.destroy()

        self.__textVars.pop(row)
        self.__cities.pop(row)
        self.__records.pop(row)
        self.__records.append([])

        self.__buttonRef.pop(index)

        for i, n in enumerate(self.__buttonRef.keys()):
            self.__buttonRef[n] = i
        
        for r in self.__records:
            for wgt in r:
                wgt.grid_forget()
        
        for r, lst in enumerate(self.__records):
            for c, wgt in enumerate(lst):
                wgt.grid(row=r+1, column=c)
        
        self.__free -= 1
    
    def updateStringVar(self, index):
        self.__textVars[index].set(str(self.__cities[index].getPop()))
    
    def getCities(self) -> list[City]:
        return self.__cities

class Main(tk.Tk):
    def __init__(self, cnf: dict={}, **kwargs):
        kwargs = cnf or kwargs
        super().__init__(**kwargs)

        self.resizable(False, False)
        self.title("City Simulation")

        self.__citiesList = CitiesList(self)
        self.__citiesList.grid(row=0, column=2, rowspan=10, padx="2p", pady="2p", ipadx="1p", ipady="1p")

        heading = ttk.Label(self, text="New City:")
        heading.grid(row=0, column=0, columnspan=2)

        ttk.Label(self, text="Population:").grid(row=1, column=0)
        self.__enterPop = ttk.Entry(self, width=9)
        self.__enterPop.grid(row=1, column=1)

        ttk.Label(self, text="Growth:").grid(row=2, column=0)
        self.__enterGrowth = ttk.Entry(self, width=9)
        self.__enterGrowth.grid(row=2, column=1)

        ttk.Label(self, text="Casualties:").grid(row=3, column=0)
        self.__enterCasualties = ttk.Entry(self, width=9)
        self.__enterCasualties.grid(row=3, column=1)

        self.__addButton = ttk.Button(self, text="Add City", command=self.__addCity)
        self.__addButton.grid(row=4, column=0, columnspan=2)

        redText = ttk.Style()
        redText.configure("red.TLabel", foreground="red")
        self.__error = ttk.Label(self, text="Invalid Field(s)!")
        self.__error.configure(style="red.TLabel")

        self.rowconfigure(5, minsize=self.__error.winfo_reqheight())

        ttk.Label(self, text="Years:").grid(row=6, column=0)
        self.__enterYears = ttk.Entry(self, width=9)
        self.__enterYears.grid(row=6, column=1)

        self.__simButton = ttk.Button(self, text="Run Sim", command=self.__runSim)
        self.__simButton.grid(row=7, column=0, columnspan=2)
    
    def __addCity(self) -> None:
        pop = int(self.__enterPop.get())
        growth = int(self.__enterGrowth.get())
        casualties = int(self.__enterCasualties.get())

        self.__citiesList.addCity(pop, growth, casualties)
    
    def __runSim(self) -> None:
        self.__addButton.state(["disabled"])
        self.__simButton.state(["disabled"])

        self.__simThread = Thread(target=self.__simulation, daemon=True)
        self.__simThread.start()
    
    def __simulation(self) -> None:
        years = int(self.__enterYears.get())

        cities = self.__citiesList.getCities()

        for j in range(years):
            for city in cities:
                city.updateOne()
            for city in cities:
                city.updateTwo()
            for city in cities:
                city.calcBiggerCity(cities)
            for i, city in enumerate(cities):
                city.updateThree()
                self.__citiesList.updateStringVar(i)
        
        self.__addButton.state(["!disabled"])
        self.__simButton.state(["!disabled"])

if __name__ == "__main__":
    root = Main()
    root.mainloop()