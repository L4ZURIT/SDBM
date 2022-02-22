

class human():
    name:str
    rost:int
    def __init__(self, name, rost) -> None:
        self.name = name
        self.rost = rost
        pass
    def poop(self):
        print("Я пукнул")


def hui(a:int, b:int) -> int:
    sum:int = a+b
    return sum
    pass



def main():
    cadet:human = human("oleg", 145)
    cadet.poop()
    print(cadet.name, cadet.rost)
    pass


if __name__ == "__main__":
    main()
    pass