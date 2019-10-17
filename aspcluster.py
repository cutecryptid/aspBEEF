import csv
import argparse
import os
import tempfile
import json
from subprocess import PIPE, Popen
from sys import argv
from datetime import datetime
import ntpath
import webbrowser
from distutils.dir_util import copy_tree, remove_tree

# HTML templates configuration
REPORT_TEMPLATE_DIR_PATH = "./reportTemplate/"
REPORT_RESOURCES_DIRNAME = ".resources/"
REPORT_DIR_NAME = "htmlReports/"
INDEX_PAGE_TEMPLATE_FILENAME = "index_template.html"
INDEX_LIST_ELEMENT_TEMPLATE_FILENAME = "index_list_element_template.html"
HOME_INDEX_PAGE_TEMPLATE_FILENAME = "home_index_template.html"
HOME_INDEX_LIST_ELEMENT_TEMPLATE_FILENAME = "home_index_list_element_template.html"
HTML_REPORT_TEMPLATE_FILENAME = "report_template.html"
POINTS_TEMPLATE_FILENAME = "points_template.js"
RECTANGLE_TEMPLATE_FILENAME = "rectangle_template.js"

 # Experimental Fix to decimal numbers, probably have to deal with them dynamically
FACTOR = 100

# Global variables
points = None 
csv_features = None
index_page_data = {}
sol_n = 0
selected_attributes = None

dataset_name = None
moment = None

def init_directories():
    # Creates reports directory if not exists
    if not os.path.exists(REPORT_DIR_NAME):
        os.mkdir(REPORT_DIR_NAME)

    # Copy reports dependencies
    if not os.path.exists(REPORT_DIR_NAME + REPORT_RESOURCES_DIRNAME):
        copy_tree(REPORT_TEMPLATE_DIR_PATH + REPORT_RESOURCES_DIRNAME, REPORT_DIR_NAME + REPORT_RESOURCES_DIRNAME)

    # Dataset directory
    if not os.path.exists(REPORT_DIR_NAME + dataset_name):
        os.mkdir(REPORT_DIR_NAME + dataset_name)

    # Execution instance directory
    if not os.path.exists(REPORT_DIR_NAME + dataset_name + '/' + moment):
        os.mkdir(REPORT_DIR_NAME + dataset_name + '/' + moment)

def store_command(command):
    with open(REPORT_DIR_NAME + dataset_name + '/' + moment + '/command', 'w') as f:
        f.write(command)

def build_report_index():
    # Load index page templates
    index_template = open(REPORT_TEMPLATE_DIR_PATH + INDEX_PAGE_TEMPLATE_FILENAME, 'r').read()
    index_list_element_template = open(REPORT_TEMPLATE_DIR_PATH + INDEX_LIST_ELEMENT_TEMPLATE_FILENAME, 'r').read()

    # Generate links to reports (html code)
    trace_links_to_reports_html = ""
    optimal_links_to_reports_html = ""
    for report_id, report_data in index_page_data.items():
        tmp_html = index_list_element_template.replace("#report_file_path#", str(report_id) + "_report.html"). \
            replace("#report_id#", str(report_id)). \
            replace("#overlapping#", str(report_data['overlapping'])). \
            replace("#outliercount#", str(report_data['outliercount'])). \
            replace("#impurecount#", str(report_data['impurity'])). \
            replace("#selattr#", selected_attributes)
        if report_data["optimum"]:
            optimal_links_to_reports_html += tmp_html
        else:
            trace_links_to_reports_html += tmp_html

    # Build index page
    index_page = index_template.replace("#trace_link_list_items#", trace_links_to_reports_html). \
        replace("#optimal_link_list_items#", optimal_links_to_reports_html)

    # Write report index page
    index_page_file = open(REPORT_DIR_NAME + dataset_name + '/' + moment + '/' + "index.html", "w+")
    index_page_file.write(index_page)
    index_page_file.close()

def update_home_page():
    # Load home page templates
    home_template = open(REPORT_TEMPLATE_DIR_PATH + HOME_INDEX_PAGE_TEMPLATE_FILENAME, 'r').read()
    home_list_element_template = open(REPORT_TEMPLATE_DIR_PATH + HOME_INDEX_LIST_ELEMENT_TEMPLATE_FILENAME, 'r').read()

    # Build home page
    links = ""
    dirs = [x[0] for x in os.walk(REPORT_DIR_NAME + dataset_name)]
    for d in sorted(dirs[1:]):
        command = open(REPORT_DIR_NAME + dataset_name + "/" + ntpath.basename(d) + '/command', 'r').read()
        links += home_list_element_template.replace('#timestamp#', ntpath.basename(d)). \
            replace('#command#', command)

    # Build index page
    home_page = home_template.replace("#link_list_items#", links). \
            replace('#dataset_name#', dataset_name)

    # Write home page file
    index_page_file = open(REPORT_DIR_NAME + dataset_name + '/' + "index.html", "w+")
    index_page_file.write(home_page)
    index_page_file.close()

    print("\nFinished. New reports were generated in '" + REPORT_DIR_NAME + '/' + dataset_name + '/' + moment + "/'. Opening home page in the default browser...")
    webbrowser.open_new(REPORT_DIR_NAME + dataset_name + "/index.html")
    print()

def build_asprin(sol_data):
    """Generates the html reports using tokens and templates"""

    # Load the templates
    report_base_template  = open(REPORT_TEMPLATE_DIR_PATH + HTML_REPORT_TEMPLATE_FILENAME, 'r').read()
    points_template       = open(REPORT_TEMPLATE_DIR_PATH + POINTS_TEMPLATE_FILENAME, 'r').read()
    rectangle_template    = open(REPORT_TEMPLATE_DIR_PATH + RECTANGLE_TEMPLATE_FILENAME, 'r').read()


    sol_n = sol_data["solnum"]
    global index_page_data
    index_page_data[sol_n] = {}

    if "optimum" in sol_data.keys():
        index_page_data[sol_n]["optimum"] = True
    else:
        index_page_data[sol_n]["optimum"] = False
    
    # Get clusters data and solution stats from solution
    clusters = {}
    params = []
    for rect in sol_data["atoms"]["minrectval"]:
        cluster_name = 'cluster' + str(rect[0])
        if cluster_name not in clusters:
            clusters[cluster_name] = {}
            clusters[cluster_name]['low']  = {}
            clusters[cluster_name]['high'] = {}
        clusters[cluster_name]['low'][str(rect[1]).replace("\"", '')] = str(rect[2]/FACTOR)
        clusters[cluster_name]['high'][str(rect[1]).replace("\"", '')] = str(rect[3]/FACTOR)
    
    for attr in sol_data["atoms"]["selattr"]:
        params += [attr[0]]

    overlapping = str(sol_data["atoms"]["overlapcount"][0][0])
    index_page_data[sol_n]['overlapping'] = overlapping

    outliers = str(sol_data["atoms"]["outliercount"][0][0])
    index_page_data[sol_n]['outliercount'] = outliers

    impurity = str(sol_data["atoms"]["impurecount"][0][0])
    index_page_data[sol_n]['impurity'] = impurity
    
    param_index = [csv_features.index(x) for x in params]
    param_index = sorted(param_index)
    param_index_names = [csv_features[x] for x in param_index]

    # TODO: Work with lists instead of named x/y params to allow for multidimensional visualization
    x_axis_parameter_name = param_index_names[0]
    y_axis_parameter_name = param_index_names[1]

    global selected_attributes
    selected_attributes = "/".join(param_index_names)

    # Generate points data from points_template
    points_data = ""
    for class_name, values in points.items():
        filtered_values = [[v[param_index[0]], v[param_index[1]]] for v in values]
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
        replace("#outliercount#", outliers). \
        replace("#impurecount#", impurity). \
        replace("#x_axis_name#", x_axis_parameter_name). \
        replace("#y_axis_name#", y_axis_parameter_name)

    # Write report file for actual solution
    report_file = open(REPORT_DIR_NAME + dataset_name + '/' + moment + '/' + str(sol_n) + "_report.html", 'w+')
    report_file.write(report)
    report_file.close()

def build_rules(sol_data):
    clusters = {k:v for (k,v) in sol_data['atoms']['rectcluster']}
    rev_clusters = {}
    for k,v in clusters.items():
        rev_clusters[v] = rev_clusters.get(v, []) + [k]

    rectvals = {}
    for rect in sol_data['atoms']['minrectval']:
        cluster = rect[0]
        attr = rect[1]
        vals = tuple(rect[2:])
        if cluster not in rectvals.keys():
            rectvals.update({ cluster: { attr: vals }})
        else:
            rectvals[cluster].update( { attr:vals } )   

    clustervals = {}
    for k,v in rev_clusters.items():
        clustervals.update({ k: [rectvals[cl] for cl in v]})
  
    return clustervals

def rules_to_text(rule_dict):
    rulestr = ""
    for k,v in rule_dict.items():
        rulestr += "Rule(s) for Class {0}\n".format(k)
        for idx,rect in enumerate(v):
            rulestr += "  Rule #{0}\n".format(idx)
            for attr,val in rect.items():
                rulestr += "    {a} is between {l} and {h}\n".format(
                    a = attr, l = val[0], h = val[1]
                )
    return rulestr
    

def solve_asprin(asp_program, asp_facts, clingo_args, report=False):
    program = ''
    with open("./asp/"+asp_program+".lp", 'r') as f:
        program = f.read()
    for fact in asp_facts:
        program += fact + " \n"
    
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(program.encode())
        temp_file.flush()
        process = Popen(["asprin", temp_file.name] + clingo_args, stdout=PIPE, stderr=PIPE)
        parser = Popen(["./asparser/asparser"], stdin=process.stdout, stdout=PIPE, stderr=PIPE)
        while True:
            line = parser.stdout.readline().rstrip()
            if not line:
                break
            parsed_line = line.decode('utf-8)')
            sol_data = json.loads(parsed_line)
            print("FOUND SOLUTION #{0} ({1} / {2} / {3})".format(sol_data["solnum"],
                sol_data["atoms"]["overlapcount"][0][0], sol_data["atoms"]["impurecount"][0][0],
                sol_data["atoms"]["outliercount"][0][0]))
            if "optimum" in sol_data.keys():
                rules = build_rules(sol_data)
                print(rules_to_text(rules))
            if report:
                build_asprin(sol_data)
            
            
def main():
    os.environ["PYTHONUNBUFFERED"] = "TRUE"

    # Handling command line arguments
    parser = argparse.ArgumentParser(description='Experimental ASP clustering tool')
    parser.add_argument('file', type=str, help="CSV File")
    parser.add_argument('target', nargs='?', type=str, help="Target Classification Field if any")
    parser.add_argument('-f', '--features', type=int, default=2, help="Number of features used")
    parser.add_argument('-s', '--selfeatures', type=str, nargs='*', help="Selected features by name")
    parser.add_argument('-n', '--nrect', type=int, default=2, help="Number of clusters")
    parser.add_argument('-c', '--solcount', type=int, default=1, help="Number of reported optimal solutions")
    parser.add_argument('-r', '--report', action='store_true', default=False)
    parser.add_argument('-m', '--mode', choices=['weak', 'heuristic'])

    args = parser.parse_args()

    # Setting up some global variables for report generation
    global dataset_name
    dataset_name = ntpath.basename(args.file)
    
    global moment
    timestamp = datetime.now()
    moment = timestamp.strftime("%Y_%m_%d-%H:%M:%S")

    command = " ".join(argv[2:])

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
    options = [str(args.solcount)]
    options += ['-c','nrect=' + str(args.nrect)]
    options += ['-c','selectcount=' + str(feature_count)]
    if args.mode is not None:
        options += ['--approximation='+ str(args.mode) ]

    if args.report:
        init_directories()
        store_command(command)

    solve_asprin('rectangles_asprin', [asp_facts, asp_selected_parameters], options, report=args.report)

    if args.report:
        build_report_index()
        # TODO: Update Home Page with each solution
        update_home_page()
    
    os.environ["PYTHONUNBUFFERED"] = "FALSE"

if __name__ == "__main__":
    main()
