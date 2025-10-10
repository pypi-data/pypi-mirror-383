# print("This is Python Code for Operations on Strings to find Vowels, Consonants, Spaces, Digits and Special Characters")
# print("==============================================")
def charFun(st):
    counts = {"vowels" : 0, "cons" : 0, "space":0, "digits":0, "sc":0}
    for i in st:
        if i.isalpha():
            if i in "aeiouAEIOU":
                counts["vowels"] = counts["vowels"]+1
            else:
                counts["cons"] = counts["cons"]+1
        elif i.isspace():
            counts["space"] = counts["space"]+1
        elif i.isdigit():
            counts["digits"] = counts["digits"]+1
        else:
            counts["sc"] = counts["sc"]+1
    print("Vowels: ", counts["vowels"])
    print("Consonants: ", counts["cons"])
    print("Spaces: ", counts["space"])
    print("Digits: ", counts["digits"])
    print("Special Characters: ", counts["sc"])
# print("This is Completed Python Code for Operations on Strings to find Vowels, Consonants, Spaces, Digits and Special Characters")
# print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")