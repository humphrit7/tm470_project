"""
Generates queries to separate the main locations database out into many smaller ones based on
longitude.
Also generates some python code to select from the database based on the longitude provided
"""

MIN_LONG = -7.10
MAX_LONG = -2.95
queries = []
cases = []
counter = 1
upper_r = int(MAX_LONG*1000-MIN_LONG*1000)
print(upper_r)

for i in range(0, upper_r, 50):

    wee = round(MIN_LONG+round(i/1000, 2), 2)
    poo = round(wee + 0.05, 2)
    print(i, poo, wee)
    query = f"create table locations{counter} " \
            f"as " \
            f"select * " \
            f"from locations " \
            f"where longitude <= {poo} " \
            f"and longitude > {wee};\n\n"
    queries.append(query)
    codey = (f"elif longitude <= {poo} and longitude > {wee}:\n"
             f"\ttables.add('locations{counter}')\n")
    cases.append(codey)
    counter += 1

with open("queries.txt", 'w') as q:
    q.writelines(queries)

with open("cases.txt", 'w') as c:
    c.writelines(cases)






