import argparse
import string
import csv
from random import randint

AXIS = 50
MINSIZE = 5
MAXSIZE = 40

def feature_name(alpha_id):
    alpha = string.ascii_lowercase
    feature_str = ""
    if alpha_id // 26 > 0:
        feature_str += alpha[((alpha_id)//26)-1]
    feature_str += alpha[(alpha_id)%26]
    return feature_str

def main():
    parser = argparse.ArgumentParser(description='Rectangular dataset generator')
    parser.add_argument('outfile', type=str, help="Output CSV Filename")
    parser.add_argument('rectN', type=int, help="Number of rectangles")
    parser.add_argument('featureN', type=int, help="Number of features")
    parser.add_argument('pointsPerRectangle', type=float, help="Point density")

    args = parser.parse_args()

    feats = [feature_name(featID) for featID in range(args.featureN)]
    csvfile = open("./input/generated/" + args.outfile, 'w', newline='')
    csvwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(feats + ["cluster"])

    rectangles = {}
    # Create the N rectangles with M features each
    for rectID in range(args.rectN):
        rectangles[rectID] = {}
        rectangles[rectID]["features"] = {}
        #rectangles[rectID]["volume"] = 1
        for featName in feats:
            size = randint(MINSIZE, MAXSIZE+1)
            start = randint(0, AXIS-size)
            rectangles[rectID]["features"][featName] = (start, start+size)
            #rectangles[rectID]["volume"] = rectangles[rectID]["volume"] * size
    

    # Fill rectangles with points up to density
    for rectID, rectVals in rectangles.items():
        # Keeping volume for density option
        #rectVolume = rectVals["volume"]
        rectPointCount = 0
        while (rectPointCount < args.pointsPerRectangle):
            point = []
            for featName, (l,h) in rectVals["features"].items():
                point += [randint(l,h+1)]
            csvwriter.writerow(point + ["c" + str(rectID)])
            rectPointCount += 1


        
            
        


            
        
        
if __name__ == "__main__":
    main()



    