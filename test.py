import pickle


class human():
    name:str = None
    rost:int = None

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

    def who_am_i(self):
        print(self.name, self.rost)

    


def hui(a:int, b:int) -> int:
    sum:int = a+b
    return sum
    pass

class controlled_execution:
    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b

        pass

    def __enter__(self):
        return sum([self.a,self.b])

    def __exit__(self, type, value, traceback):
        print("vot i vse")



def make_humans_to_file(file):
    serega = human("Egorkin", 180)
    vasyan = human("Klyazmin", 190)
    romych = human("Rysin", 280)
        
    with open(file, "wb") as file:
        pickle.dump({
            'a':serega,
            'b':vasyan,
            'c':romych
        }, file)

def get_humans_from_file(file):
    someone:human = None

    with open(file, "rb") as file:
        data = pickle.load(file)
        someone = data["b"]

    someone.who_am_i()

    return someone




def main():
    
    print("wdwwdw")

    pass


if __name__ == "__main__":
    main()
    pass