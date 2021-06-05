"""
Script to simplify placement of participants in a choice-based progressive programming unit
for summer camp

Inputs: participants.csv (Name, Age, Cabin, Choice1, Choice2, Choice3)
        programs.csv (Name, Age Start, Age End, Capacity)

Output: placement.csv

run as:
    python3 place_students.py {participants_file} {programs_file} {out_file}

Further work:
    ~implement negotiation on Participant class to bump high-satisfaction participants
    to lower choice to make room for unplaceable participants.
    ~implement argument safety checks
    ~web ui via webassembly?
"""

import csv
from pprint import pprint
from collections import OrderedDict
import random
import sys

class Program:
    def __init__(self, **kwargs):
        self.name = kwargs['Program Name']
        self.age_start = int(kwargs['Age Start'])
        self.age_end = int(kwargs['Age End'])
        self.capacity = kwargs['Capacity']
        self.participants = []

    def __repr__(self):
        return self.name

class Participant:
    def __init__(self, **kwargs):
        #print(kwargs['Name'])
        self.name = kwargs['Name']
        self.age = int(kwargs['Age'])
        self.cabin = kwargs['Cabin']
        self.choices = [kwargs[k] for k in ['Choice1', 'Choice2', 'Choice3','Choice4']]
        self.satisfaction = len(self.choices) + 1
        self.program = None

    def claim_next_best(self):
        for i, choice in enumerate(self.choices):
            try:
                prog = programs[choice]
            except:
                break
            if self.age < prog.age_start:
                #print(self.name, "Too young for", prog.name)
                continue
            if self.age > prog.age_end:
                #print(self.name, "Too old for", prog.name)
                continue
            if len(prog.participants) < int(prog.capacity):
                prog.participants.append(self)
                self.program = prog
                #print(self.name, " placed in ", prog.name)
                self.satisfaction -= i
                return prog
            else:
                pass
                #print(prog.name, "doesn't have room for", self.name)
        if self.program is None:
            #print("{} in {} doesn't have a good fit".format(self.name, self.cabin))
            self.satisfaction -= (len(self.choices) + 1)

    def reset(self):
        self.satisfaction = len(self.choices) + 1
        self.program = None

    def __repr__(self):
        return "{}: {}".format(self.name, self.cabin)
    


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit()
         
    programs = dict()
    participants = dict()
    print(sys.argv)
    with open(sys.argv[1]) as csvpart:
        part_reader = csv.DictReader(csvpart)
        for row in part_reader:
            participants[row['Name']] = Participant(**row)

    with open(sys.argv[2]) as csvprog:
        prog_reader = csv.DictReader(csvprog)
        for row in prog_reader:
            programs[row['Program Name']] = Program(**row)

    max_average_satisfaction = 0
    max_satisfaction_participants = None

    random_participants = [v for v in participants.values()]
    for i in range(10000):
        print(i)
        random.shuffle(random_participants)
        
        for program in programs.values():
            program.participants = []

        for participant in random_participants:
            participant.reset()
            participant.claim_next_best()

        satisfactions = [p.satisfaction for p in random_participants]
        avg_satisfaction = sum(satisfactions)/len(satisfactions)
        print("Average satisfaction:", avg_satisfaction)
        if avg_satisfaction > max_average_satisfaction:
            max_satisfaction_participants = random_participants
            

    with open(sys.argv[3], 'w') as csvout:
        part_writer = csv.DictWriter(csvout,
                                    fieldnames = ['Name', 'Cabin', 'Age', 'Program','Satisfaction','Choices'])
        part_writer.writeheader()
        for p in max_satisfaction_participants:
            rowdict = {k: getattr(p,k.lower()) for k in part_writer.fieldnames}
            part_writer.writerow(rowdict)
