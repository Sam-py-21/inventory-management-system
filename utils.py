def get_int(msg):
    while True:
        try:
            value = int(input(msg))
            return value
        except ValueError:
            print("❌ Please enter a valid integer!")


def get_float(msg):
    while True:
        try:
            value = float(input(msg))
            return value
        except ValueError:
            print("❌ Please enter a valid number!")


def get_non_empty_string(msg):
    while True:
        value = input(msg).strip()
        if value:
            return value
        print("❌ Input cannot be empty!")

def get_positive_int(msg):
    while True:
        try:
            value = int(input(msg))
            if value > 0:
                return value
            print("❌ Must be greater than 0!")
        except ValueError:
            print("❌ Please enter a valid integer!")
