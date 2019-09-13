import csv
import argparse
import clingo
import os
import webbrowser
from distutils.dir_util import copy_tree, remove_tree

# HTML templates configuration
REPORT_TEMPLATE_DIR_PATH = "./reportTemplate/"
REPORT_RESOURCES_DIRNAME = ".resources/"
REPORT_DIR_NAME = "htmlReports/"
INDEX_PAGE_TEMPLATE_FILENAME = "index_template.html"
INDEX_LIST_ELEMENT_TEMPLATE_FILENAME = "index_list_element_template.html"
HTML_REPORT_TEMPLATE_FILENAME = "report_template.html"
POINTS_TEMPLATE_FILENAME = "points_template.js"
RECTANGLE_TEMPLATE_FILENAME = "rectangle_template.js"

 # Experimental Fix to decimal numbers, probably have to deal with them dynamically
FACTOR = 100

points = None 
csv_features = None
links_to_reports_html = None

def print_global():
    print(points)
    print(csv_features)

def init_directory():
        # Creates destination directory
    try:
        os.mkdir(REPORT_DIR_NAME)
    except FileExistsError:
        remove_tree(REPORT_DIR_NAME)
        os.mkdir(REPORT_DIR_NAME)

    # Copy reports dependencies
    copy_tree(REPORT_TEMPLATE_DIR_PATH + REPORT_RESOURCES_DIRNAME, REPORT_DIR_NAME + REPORT_RESOURCES_DIRNAME)

def build_index():
    # Build index page
    index_page = index_template.replace("#link_list_items#", links_to_reports_html)

    # Write report index page
    index_page_file = open(REPORT_DIR_NAME + "index.html", "w+")
    index_page_file.write(index_page)
    index_page_file.close()    

    print("\nFinished. Reports were generated in '" + REPORT_DIR_NAME + "'. Opening index.html in the default browser...")
    webbrowser.open_new(REPORT_DIR_NAME + "index.html")
    print()

def build_html_report(clingo_solution):
    """Generates the html reports using tokens and templates

    'points' must be a dictionary indexed by target class names and each value 
    must be a list of points. 
    Example -> {'Iris-setosa' : [[1,2],[2,3]], 'Iris-versicolor': [[3,2],[4,5]]}

    This function supposes that clingo solutions contain 'rectval',
    'overlapcount' and 'outliercount' facts.
    """

    # Load the templates
    report_base_template  = open(REPORT_TEMPLATE_DIR_PATH + HTML_REPORT_TEMPLATE_FILENAME, 'r').read()
    points_template       = open(REPORT_TEMPLATE_DIR_PATH + POINTS_TEMPLATE_FILENAME, 'r').read()
    rectangle_template    = open(REPORT_TEMPLATE_DIR_PATH + RECTANGLE_TEMPLATE_FILENAME, 'r').read()


    # Generate one report for each solution
    sol_n = 1
    index_page_data = {}
    index_page_data[sol_n] = {}
    
    # Get clusters data and solution stats from solution
    clusters = {}
    params = []
    for sym in clingo_solution.symbols(shown=True):
        if sym.name == "minrectval":
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
            index_page_data[sol_n]['overlapping'] = overlapping
        elif sym.name == "outliercount":
            outliercount = str(sym.arguments[0])
            index_page_data[sol_n]['outliercount'] = outliercount
        elif sym.name == "selattr":
            params += [str(sym.arguments[0])]
    
    param1_index = csv_features.index(params[0][1:-1])
    param2_index = csv_features.index(params[1][1:-1])

    x_axis_index = min(param1_index, param2_index)
    y_axis_index = max(param1_index, param2_index)

    x_axis_parameter_name = csv_features[x_axis_index]
    y_axis_parameter_name = csv_features[y_axis_index]


    # Generate points data from points_template
    points_data = ""
    for class_name, values in points.items():
        filtered_values = [[v[x_axis_index], v[y_axis_index]] for v in values]
        points_data += points_template.replace("#className#", class_name).replace("#data#", str(filtered_values))

    # Generate clusters_data
    chart_data = ""
    for cluster, limits in clusters.items():
        cluster_data = rectangle_template.replace("#name#", cluster)
        cluster_data = cluster_data.replace("#x_low_limit#", limits['low'][x_axis_parameter_name])
        cluster_data = cluster_data.replace("#x_high_limit#", limits['high'][x_axis_parameter_name])
        cluster_data = cluster_data.replace("#y_low_limit#", limits['low'][y_axis_parameter_name])
        cluster_data = cluster_data.replace("#y_high_limit#", limits['high'][y_axis_parameter_name])

        chart_data += cluster_data

    chart_data = points_data + chart_data

    # Build report
    report = report_base_template.replace("#report_id#", str(sol_n)). \
        replace("#class_names#", str(list(points.keys()))). \
        replace("#chart_data#", chart_data). \
        replace("#overlapping#", overlapping). \
        replace("#outliercount#", outliercount). \
        replace("#x_axis_name#", x_axis_parameter_name). \
        replace("#y_axis_name#", y_axis_parameter_name)

    # Write report file for actual solution
    report_file = open(REPORT_DIR_NAME + str(sol_n) + "_report.html", 'w+')
    report_file.write(report)
    report_file.close()

    # Load index page templates
    index_template = open(REPORT_TEMPLATE_DIR_PATH + INDEX_PAGE_TEMPLATE_FILENAME, 'r').read()
    index_list_element_template = open(REPORT_TEMPLATE_DIR_PATH + INDEX_LIST_ELEMENT_TEMPLATE_FILENAME, 'r').read()

    # Generate links to reports (html code)

    global links_to_reports_html
    links_to_reports_html = ""
    for report_id, report_data in index_page_data.items():
        links_to_reports_html += index_list_element_template.replace("#report_file_path#", str(report_id) + "_report.html"). \
            replace("#report_id#", str(report_id)). \
            replace("#overlapping#", str(report_data['overlapping'])). \
            replace("#outliercount#", str(report_data['outliercount'])). \
            replace("#x_axis_name#", x_axis_parameter_name). \
            replace("#y_axis_name#", y_axis_parameter_name)


def print_build_model(m):
    print(str(m))
    build_html_report(m)


def solve(asp_program, asp_facts, clingo_args):
    c = clingo.Control(clingo_args)
    if asp_program != "":
        c.load("./asp/"+asp_program+".lp")
    for facts in asp_facts:
        c.add("base", [], facts)
    c.ground([("base", [])])
    ret = []
    with c.solve(on_model=print_build_model, yield_=True) as handle:
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
    with c.solve(on_model=print_build_model, yield_=True) as handle:
        for m in handle:
            if (m.optimality_proven):
                ret += [m.symbols(shown=True)]
    return ret

def main():
    # Handling command line arguments
    parser = argparse.ArgumentParser(description='Experimental ASP clustering tool')
    parser.add_argument('file', type=str, help="CSV File")
    parser.add_argument('target', nargs='?', type=str, help="Target Classification Field if any")
    parser.add_argument('-f', '--features', type=int, default=2, help="Number of features used")
    parser.add_argument('-s', '--selfeatures', type=str, nargs='*', help="Selected features by name")
    parser.add_argument('-n', '--nrect', type=int, default=2, help="Number of clusters")
    parser.add_argument('-c', '--solcount', type=int, default=10, help="Number of reported optimal solutions")
    parser.add_argument('-r', '--report', action='store_true', default=False)

    args = parser.parse_args()

    # Ad hoc selected parameters for iris dataset
    if args.selfeatures:
        selected_parameters = args.selfeatures
    else:
        selected_parameters = []

    feature_count = max(len(selected_parameters), args.features)

    if feature_count != 2 and args.report:
        raise SystemExit('Error: When reporting, only 2 features are supported')
    if feature_count < 2:
        raise SystemExit('Error: Must use more than 2 features for clustering')



    global csv_features
    global points
    # Csv data to ASP facts & points
    with open(args.file) as csvfile:
        asp_facts = ""
        points = {}
        if args.target:
            asp_facts += "target('{0}').\n".format(args.target)
        datareader = csv.DictReader(csvfile)

        csv_features = list(datareader.fieldnames)
        for att in datareader.fieldnames:
            asp_facts += "attribute('{0}'). ".format(att)
        asp_facts += "\n"
        for i,row in enumerate(datareader):
            point = []
            for j,(k,v) in enumerate(row.items()):
                if k == args.target:
                    asp_facts += "cluster({0}, '{1}'). ".format(i,v.replace('-','_').lower())
                    if v not in points:
                        points[v] = []
                    points[v].append(point)
                else:
                    asp_facts += "value({0},'{1}',{2:d}). ".format(i,k,int(float(v)*FACTOR))
                    point.append(v)
            asp_facts += "\n"
    
    # selected parameters facts for asp
    asp_selected_parameters = ""
    for parameter in selected_parameters:
        asp_selected_parameters += "selattr('" + parameter + "')."

    # Use -c selectcount=N to specify the number of dimensions of each rectangle
    # Specify the number of rectangles by changing the nrect value
    options = [args.solcount]
    options += ['-c nrect=' + str(args.nrect)]
    options += ['-c selectcount=' + str(feature_count)]

    init_directory()

    solutions = solve_optimal('rectangles_strict', [asp_facts, asp_selected_parameters], options)

    build_index()


if __name__ == "__main__":
    main()
