import csv


class Thing():
    name = "lamp"
    colour = "black"


thing1 = Thing()
thing2 = Thing(name="laptop")

# thing1.name = "mouse"
# tester = thing2.name
tester = Thing()
thing3 = Thing()

print(thing1.name)
print(thing2.name)
print(thing3.name)
print(tester)

Thing.name = "speaker"

print("After changing the class variable value:")
print(thing1.name)
print(thing2.name)
print(thing3.name)
print(tester.name)

# with open("questions/flashcards_english_deck1.csv") as csv_file:
#     csv_reader = csv.DictReader(csv_file, delimiter=",")
#     for i in range(3):
#         myOrDict = next(csv_reader)
#         print(next(iter(myOrDict)))
#         myDict = dict(myOrDict)
#         print(myDict)
#         mykeys = iter(myOrDict.keys())
#         # print(next(mykeys))
#         # print(next(mykeys))
#         # print(next(mykeys))
#         # print(next(myDict))
#         # for k, v in myDict.items():
#         #     print(k, ":", v)
