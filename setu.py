from bs4 import BeautifulSoup
import numpy as np
import pickle
import pandas as pd
from copy import deepcopy

def gen_database(filename, save_filename):
    with open(filename, "r") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, "lxml")

    database = {}
    for article in soup.find_all("article"):
        if int(article.find("div", attrs={"class": "CrossCategoryBlockRow TableContainer"}).find("tbody").find("tr").find("td").text) <= 1:
            continue
        N = int(article.find("div", attrs={"class": "CrossCategoryBlockRow TableContainer"}).find("tbody").find("tr").find("td").text)
        if N <= 1:
            continue

        entry = {}
        entry["N"] = N
        code = article.find("table").find_all("tr")[3].text
        unit_code = code.split("_")[0]
        entry["code"] = code
        entry["unit_code"] = unit_code
        scores = []
        for divs in article.find_all("div", attrs={"class": "FrequencyBlock_HalfMain"}):

            q_title = divs.find("div", attrs={"class": "FrequencyQuestionTitle"}).text
            tables = divs.find_all("table")
            score = tables[1].tbody.find_all("tr")[1].find("td").text
            try:
                score = float(score)
                scores.append(score)
            except Exception:
                print("score could not be converted: {}, {}".format(code, score))

        entry["scores"] = np.array(scores)
        database[code] = entry

        with open(save_filename, "wb") as f:
            pickle.dump(database, f, pickle.HIGHEST_PROTOCOL)

    return database

def load_database(filename):
    with open(filename, "rb") as f:
        database = pickle.load(f)
    return database


#gen_database("2020_S2_SETU.html", "setudb_2020_S2.pkl")
database = load_database("setudb_2020_S2.pkl")
#database = load_database("setudb.pkl")
database2 = load_database("setudb.pkl")

array = list(database.values()) + list(database2.values())
#array = list(database.values())
newarray = []

science_prefix = {"MTH", "ASP", "BCH", "BIO", "BMH", "BTH", "CHM", "DEV", "EAE", "ENS", "ENV",
                                      "FST", "GEN", "HUP", "IBL", "IMM", "MBS", "MCB", "MIC", "MIS", "MSC", "PHA",
                                      "PHS", "PHY", "SCI", "STA", "PSY"}
eng_prefix = {"CHE", "CIV", "ECE", "ENE", "ENG", "MAE", "MEC", "MTE", "RSE", "TRC"}

def no_malaysia_or_online(entry): return ("CAMPUS" in entry["code"] and "CLAYTON" in entry["code"])
def malaysia(entry): return ("MALAYSIA" in entry["code"])

def filter1(db):
    # level 1 2 3 4 5 science units
    array = db
    newarray = []
    for entry in array:
        if entry["unit_code"][1:4] in science_prefix and entry["unit_code"][4] in ["1", "2", "3", "4", "5"] and not malaysia(entry):
            newarray.append([entry["code"], np.mean(entry["scores"][:]), entry["N"]])
    return newarray

def filter1N(db):
    # level 1 2 3 4 5 science units
    array = db
    newarray = []
    for entry in array:
        if entry["unit_code"][1:4] in science_prefix and entry["unit_code"][4] in ["1", "2", "3", "4", "5"] and not malaysia(entry) and entry["N"]>=10:
            newarray.append([entry["code"], np.mean(entry["scores"][:]), entry["N"]])
    return newarray

def filter_math(db):
    # level 1 2 3 4 5 science units
    array = db
    newarray = []
    for entry in array:
        if entry["unit_code"][1:4] in ["MTH",] and entry["unit_code"][4] in ["1", "2", "3", "4", "5"] and not malaysia(entry):
            newarray.append([entry["code"], np.mean(entry["scores"][:]), entry["N"]])
    return newarray

def filter_fit(db):
    # level 1 2 3 4 5 science units
    array = db
    newarray = []
    for entry in array:
        if entry["unit_code"][1:4] in ["FIT", "MTH"] and entry["unit_code"][4] in [ "2", "3"] and no_malaysia_or_online(entry):
            newarray.append([entry["code"], np.mean(entry["scores"][:]), entry["N"]])
    return newarray


def satisfaction(db):
    array = db
    newarray = []
    for entry in array:
        newarray.append([entry["code"], entry["scores"][7], entry["N"]])
    return newarray

def nofilter(db):
    array = db
    newarray = []
    for entry in array:
        newarray.append([entry["code"], np.mean(entry["scores"][:]), entry["N"]])
    return newarray

def csv_dump(db):
    db = deepcopy(db)
    for i in range(len(db)):
        for j in range(8):
            db[i]["Item " + str(j+1)] = db[i]["scores"][j]
    df = pd.DataFrame(db)
    df = df.drop(["scores",], axis=1)
    df.to_csv("2020_S1_SETU.csv")

#csv_dump(array)

array = filter_fit(array)
array.sort(key= lambda x: x[1], reverse=True)

#print(array[:10])
#print(array[-10:])
#print("Unit | Average Rating | N")
print("Rank | Unit | Average Rating | N")
print("----------------------")
for i, element in enumerate(array):
    #print("{:8} | {:4.2f} | {}".format(element[0].split("_")[0], element[1], element[2]))
    #print("{:8} | {:4.2f} | {}".format(element[0].split("_")[0] + "_" + element[0].split("_")[4][:2], element[1], element[2]))
    print("{:4} | {:8} | {:4.2f} | {}".format(i+1, element[0].split("_")[0] + "_" + element[0].split("_")[4][:2], element[1],
                                       element[2]))


#for article in soup.find_all("article")
#    for
