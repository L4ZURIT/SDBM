

class human():
    name:str
    rost:int

    @staticmethod
    def strike(text):
        result = ''
        for c in text:
            result = result + c + '\u0336'
        return result

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
    print(cadet.strike("goggog"))
    pass


if __name__ == "__main__":
    main()
    pass