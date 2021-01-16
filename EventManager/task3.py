contacts = {}

while True:
    print("Enter the valid option:\n1)Create a new contact\n2)Search a contact by name\n3)Exit")
    opt = int(input())
    if opt == 1:
        cname = input("Enter name of the contact:")
        try:
            cno = int(input("Enter contact number:"))
        except ValueError:
            print("Please enter valid contact number.")
            continue
        if len(str(cno)) < 9 or len(str(cno)) > 11:
            print("Please enter valid contact number. The contact number should have length between 9 to 11 characters.")
            continue
        if cname in contacts:
            contacts[cname].add(cno)
        else:
            contacts[cname] = {cno}
        print("Successfully saved")
    elif opt == 2:
        flag = 0
        query = input("Enter search query:")
        for all_keys in contacts:
            if all_keys.find(query) == -1:
                continue
            else:
                flag = 1
                print(all_keys)
        if flag == 0:
            print("No such contact found.")
            continue
        namequery = input("Enter the name whose contact you want to access:")
        try:
            for all_nos in contacts[namequery]:
                print(all_nos)
        except KeyError:
            print("The contact with given name doesn't exist in the search list.")
            continue
    elif opt == 3:
        exit()
    else:
        print("Please enter valid option.")
        continue