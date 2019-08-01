import csv
import argparse
import clingo

def solve(asp_program, asp_facts, clingo_args):
    c = clingo.Control(clingo_args)
    if asp_program != "":
        c.load("./asp/"+asp_program+".lp")
    for facts in asp_facts:
        c.add("base", [], facts)
    c.ground([("base", [])])
    ret = []
    with c.solve(yield_=True) as handle:
        for m in handle:
            ret += [m.symbols(shown=True)]
    return ret

def solve_optimal(asp_program, asp_facts, clingo_args):
    c = clingo.Control(clingo_args + ["--opt-mode=optN"])
    if asp_program != "":
        c.load("./asp/"+asp_program+".lp")
    for facts in asp_facts:
        c.add("base", [], facts)
    c.ground([("base", [])])
    ret = []
    with c.solve(yield_=True) as handle:
        for m in handle:
            if (m.optimality_proven):
                ret += [m.symbols(shown=True)]
    return ret

def main():
    parser = argparse.ArgumentParser(description='Experimental ASP clustering tool')
    parser.add_argument('file', type=str, help="CSV File")
    parser.add_argument('target', nargs='?', type=str, help="Target Classification Field if any")
    args = parser.parse_args()

    # Experimental Fix to decimal numbers, probably have to deal with them dynamically
    factor = 10

    with open(args.file) as csvfile:
        asp_facts = ""
        if args.target:
            asp_facts += "target('{0}').\n".format(args.target)
        datareader = csv.DictReader(csvfile)
        for att in datareader.fieldnames:
            asp_facts += "attribute('{0}'). ".format(att)
        asp_facts += "\n"
        for i,row in enumerate(datareader):
            for j,(k,v) in enumerate(row.items()):
                if k != args.target:
                    asp_facts += "value({0},'{1}',{2:d}). ".format(i,k,int(float(v)*factor))
                if k == args.target:
                    asp_facts += "cluster({0}, '{1}'). ".format(i,v.replace('-','_').lower())
            asp_facts += "\n"

    print(asp_facts)
    
    # # Ad hoc selected parameters for iris dataset
    # selected_parameters = "selattr('petal_width'). selattr('sepal_width')."

    # # Use -c selectcount=N to specify the number of dimensions of each rectangle

    # # Specify the number of rectangles by changing the nrect value
    # solutions = solve('rectangles_strict', [asp_facts, selected_parameters], ['-c nrect=2'])

    # # Alternative method with optimization and such, Work In Progress
    # #solutions = solve_optimal('rectangles', [asp_facts, selected_parameters], ['-c nrect=2'])

    # for sol in solutions:
    #     for sym in sol:
    #         if sym.name == "rectval":
    #             args = sym.arguments 
    #             #print("RECT {0} : {1} ({2}, {3})".format(args[0], args[1], args[2], args[3]))



if __name__ == "__main__":
    main()
