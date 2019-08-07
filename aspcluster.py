import csv
import argparse
import clingo
import os
from distutils.dir_util import copy_tree, remove_tree

# HTML templates constants
REPORT_TEMPLATE_DIR = "./reportTemplate/"  # Path of the html report templates
REPORT_DIR_NAME = "htmlReports/"
HTML_REPORT_TEMPLATE_FILENAME = "report_template.html"
CLASS_POINTS_TEMPLATE_FILENAME = "class_points_template.js"
RECTANGLE_TEMPLATE_FILENAME = "rectangle_template.js"

FACTOR = 10  # Experimental Fix to decimal numbers, probably have to deal with them dynamically


"""
    Generate an html report for each solution using the templates from REPORT_TEMPLATE_DIR
"""
def build_reports(solutions, points, x_axis_parameter, y_axis_parameter):
    # Creates destination directory
    try:
        os.mkdir(REPORT_DIR_NAME)
    except FileExistsError:
        remove_tree(REPORT_DIR_NAME)
        os.mkdir(REPORT_DIR_NAME)

    # Copy report dependencies
    copy_tree(REPORT_TEMPLATE_DIR + ".resources/", REPORT_DIR_NAME + ".resources/")

    # Load the templates
    report_base_template  = open(REPORT_TEMPLATE_DIR + HTML_REPORT_TEMPLATE_FILENAME, 'r').read()
    class_points_template = open(REPORT_TEMPLATE_DIR + CLASS_POINTS_TEMPLATE_FILENAME, 'r').read()
    rectangle_template    = open(REPORT_TEMPLATE_DIR + RECTANGLE_TEMPLATE_FILENAME, 'r').read()

    # Process base template
    report_base_template = report_base_template.replace("#class_names#", str(list(points.keys())))

    # Generate points data
    points_data = ""
    for class_name, values in points.items():
        points_data += class_points_template.replace("#className#", class_name).replace("#data#", str(values))

    # Generate each report
    sol_n = 1
    for sol in solutions:
        print("\rGenerating html reports: " + str(sol_n) + "/" + str(len(solutions)), end='')  # Update progress
        
        # Get clusters and stats from solution
        clusters = {}
        for sym in sol:
            if sym.name == "rectval":
                args = sym.arguments  # 0: rectangle id | 1: parameter | 2: low limit | 3: high limit 
                cluster_name = 'cluster' + str(args[0])
                if cluster_name not in clusters:
                    clusters[cluster_name] = {}
                    clusters[cluster_name]['low']  = {}
                    clusters[cluster_name]['high'] = {}
                clusters[cluster_name]['low'][str(args[1]).replace("'", '')] = str(args[2].number/FACTOR)
                clusters[cluster_name]['high'][str(args[1]).replace("'", '')] = str(args[3].number/FACTOR)
            elif sym.name == "overlapcount":
                overlapping = str(sym.arguments[0])
            elif sym.name == "outliercount":
                outliercount = str(sym.arguments[0])

        # Generate clusters_data
        clusters_data = ""
        for cluster, limits in clusters.items():
            cluster_data = rectangle_template.replace("#name#", cluster)
            cluster_data = cluster_data.replace("#x_low_limit#", limits['low'][x_axis_parameter])
            cluster_data = cluster_data.replace("#x_high_limit#", limits['high'][x_axis_parameter])
            cluster_data = cluster_data.replace("#y_low_limit#", limits['low'][y_axis_parameter])
            cluster_data = cluster_data.replace("#y_high_limit#", limits['high'][y_axis_parameter])

            clusters_data += cluster_data

        # Build report
        report = report_base_template.replace("#chart_data#", clusters_data + points_data). \
            replace("#overlapping#", overlapping). \
            replace("#outliercount#", outliercount). \
            replace("#x_axis_name#", x_axis_parameter). \
            replace("#y_axis_name#", y_axis_parameter)

        # Generate report for actual solution
        report_file = open(REPORT_DIR_NAME + str(sol_n) + "_report.html", 'w+')
        report_file.write(report)
        report_file.close()

        sol_n += 1

    print("\nFinished. Reports were generated in '" + REPORT_DIR_NAME + "'")

def print_model(m):
    print(str(m))

def solve(asp_program, asp_facts, clingo_args):
    c = clingo.Control(clingo_args)
    if asp_program != "":
        c.load("./asp/"+asp_program+".lp")
    for facts in asp_facts:
        c.add("base", [], facts)
    c.ground([("base", [])])
    ret = []
    with c.solve(on_model=print_model, yield_=True) as handle:
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
    with c.solve(on_model=print_model, yield_=True) as handle:
        for m in handle:
            if (m.optimality_proven):
                ret += [m.symbols(shown=True)]
    return ret

def main():
    # Handling arguments
    parser = argparse.ArgumentParser(description='Experimental ASP clustering tool')
    parser.add_argument('file', type=str, help="CSV File")
    parser.add_argument('target', nargs='?', type=str, help="Target Classification Field if any")
    #TODO: report option
    args = parser.parse_args()

    # Ad hoc selected parameters for iris dataset
    selected_parameters = ['sepal_width', 'petal_width']

    # Csv data to ASP facts & points
    with open(args.file) as csvfile:
        asp_facts = ""
        points = {}
        if args.target:
            asp_facts += "target('{0}').\n".format(args.target)
        datareader = csv.DictReader(csvfile)
        for att in datareader.fieldnames:
            asp_facts += "attribute('{0}'). ".format(att)
        asp_facts += "\n"
        for i,row in enumerate(datareader):
            value = []
            for j,(k,v) in enumerate(row.items()):
                if k in selected_parameters:
                    asp_facts += "value({0},'{1}',{2:d}). ".format(i,k,int(float(v)*FACTOR))
                    value.append(v)
                if k == args.target:
                    asp_facts += "cluster({0}, '{1}'). ".format(i,v.replace('-','_').lower())
                    if v not in points:
                        points[v] = []
                    points[v].append(value)
            asp_facts += "\n"
    
    # selected parameters facts for asp
    asp_selected_parameters = ""
    for parameter in selected_parameters:
        asp_selected_parameters += "selattr('" + parameter + "')."

    # Use -c selectcount=N to specify the number of dimensions of each rectangle

    # Specify the number of rectangles by changing the nrect value
    solutions = solve('rectangles', [asp_facts, asp_selected_parameters], ['-c nrect=2'])

    # Alternative method with optimization and such, Work In Progress
    #solutions = solve_optimal('rectangles', [asp_facts, selected_parameters], ['-c nrect=2'])

    # Generate an html report for each solution
    build_reports(solutions, points, selected_parameters[0], selected_parameters[1])

if __name__ == "__main__":
    main()
