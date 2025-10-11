import xml.etree.ElementTree as xml
import random
from random import randrange
from datetime import datetime
from datetime import timedelta

Max_Objects = 7500000
Max_Options = 7500000
Max_Step_1 = 100000
Max_Step_2 = 50000

SPARQL_path = "C:/Blazegraph/1"
Model_path_node1 = "Linear_model/1/"
Model_path_node2 = "Linear_model/2/"


def createXML(filename):
    """
    Создаем XML файл.
    """
#Open SPARQL file
    spql1 = open(Model_path_node1 + "sparql_script.spql", "wt")
    spql2 = open(Model_path_node2 + "sparql_script.spql", "wt")

# Add header
    header = str("<?xml version='1.0' encoding='UTF-8'?>\n<rdf:RDF\nxmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'\nxmlns:vCard='http://www.w3.org/2001/vcard-rdf/3.0#'\nxmlns:my='http://127.0.0.1/bg/ont/test1#'\n>")

    f1 = open(Model_path_node1 + filename + "_static.nq", "wt")
    f2 = open(Model_path_node2 + filename + "_static.nq", "wt")
    f1.write(header)
    f2.write(header)

# Model 1 hierarchy definition
# Add Core definitions
    f1.write("\n<!--Model 1 Core definitions-->\n<rdf:Description rdf:about='http://127.0.0.1/Core_1/'>\n<my:has_id>Core_1</my:has_id>\n</rdf:Description>")
    f2.write(
        "\n<!--Model 1 Core definitions-->\n<rdf:Description rdf:about='http://127.0.0.1/Core_1/'>\n<my:has_id>Core_1</my:has_id>\n</rdf:Description>")

    # Model 2 hierarchy definition
# Add Core definitions
    f1.write("\n<!--Model 2 Core definitions-->\n<rdf:Description rdf:about='http://127.0.0.1/Core_2/'>\n<my:has_id>Core_2</my:has_id>\n</rdf:Description>")
    f1.write("\n</rdf:RDF>\n")
    f1.close()
    f2.write(
        "\n<!--Model 2 Core definitions-->\n<rdf:Description rdf:about='http://127.0.0.1/Core_2/'>\n<my:has_id>Core_2</my:has_id>\n</rdf:Description>")
    f2.write("\n</rdf:RDF>\n")
    f2.close()
    spql1.write("\nLOAD <file:///" + str(SPARQL_path) + "/" + filename + "_static.nq>;\n")
    spql2.write("\nLOAD <file:///" + str(SPARQL_path) + "/" + filename + "_static.nq>;\n")

# Add Object  definitions Node 1
    FileNum = 0
    i = 1
    k = 1
    while i <= Max_Objects/2:
        FileNum = FileNum + 1
        f1 = open(Model_path_node1 + filename + "_object_" + str(FileNum) + "_.nq", "at")
        f1.write(header)
        f1.write("\n<!--Objects definitions-->\n")
        while k <= Max_Step_1:
            body = str("<rdf:Description rdf:about='http://127.0.0.1/Object_") + str(i) + str("/'>\n<my:has_id>Object_") + str(i) + str("</my:has_id>\n<my:has_parent_id>Core_1</my:has_parent_id>\n</rdf:Description>\n")
            f1.write(body)
            i = i + 1
            k = k + 1
        f1.write("\n</rdf:RDF>\n")
        f1.close()
        spql1.write("\nLOAD <file:///" + str(SPARQL_path) + "/" + filename + "_object_" + str(FileNum) + "_.nq>;\n")
        k = 1

    # Add Object  definitions Node 2
    FileNum = 0
    i = int(Max_Objects / 2 + 1)
    k = 1
    while i <= Max_Objects:
        FileNum = FileNum + 1
        f2 = open(Model_path_node2 + filename + "_object_" + str(FileNum) + "_.nq", "at")
        f2.write(header)
        f2.write("\n<!--Objects definitions-->\n")
        while k <= Max_Step_1:
            body = str("<rdf:Description rdf:about='http://127.0.0.1/Object_") + str(i) + str(
                    "/'>\n<my:has_id>Object_") + str(i) + str(
                    "</my:has_id>\n<my:has_parent_id>Core_1</my:has_parent_id>\n</rdf:Description>\n")
            f2.write(body)
            i = i + 1
            k = k + 1
        f2.write("\n</rdf:RDF>\n")
        f2.close()
        spql2.write("\nLOAD <file:///" + str(SPARQL_path) + "/" + filename + "_object_" + str(FileNum) + "_.nq>;\n")
        k = 1



# Add Options  definitions Node 1
    FileNum = 0
    i = 1
    k = 1
    while i <= int(Max_Options / 2):
        FileNum = FileNum + 1
        f1 = open(Model_path_node1 + filename + "_option_" + str(FileNum) + "_.nq", "at")
        f1.write(header)
        f1.write("\n<!--Options definitions-->\n")
        while k <= Max_Step_1:
            body = str("<rdf:Description rdf:about='http://127.0.0.1/Option_") + str(i) + str(
                "/'>\n<my:has_id>Option_") + str(i) + str("</my:has_id>\n<my:has_parent_id>Core_2</my:has_parent_id>\n</rdf:Description>\n")
            f1.write(body)
            i = i + 1
            k = k + 1
            if i >= Max_Options: break
        f1.write("\n</rdf:RDF>\n")
        f1.close()
        spql1.write("\nLOAD <file:///" + str(SPARQL_path) + "/" + filename + "_option_" + str(FileNum) + "_.nq>;\n")
        k = 1

    # Add Options  definitions Node 1
    FileNum = 0
    i = int(Max_Options / 2 + 1)
    k = 1
    while i <= Max_Options:
        FileNum = FileNum + 1
        f2 = open(Model_path_node2 + filename + "_option_" + str(FileNum) + "_.nq", "at")
        f2.write(header)
        f2.write("\n<!--Options definitions-->\n")
        while k <= Max_Step_1:
            body = str("<rdf:Description rdf:about='http://127.0.0.1/Option_") + str(i) + str(
                    "/'>\n<my:has_id>Option_") + str(i) + str(
                    "</my:has_id>\n<my:has_parent_id>Core_2</my:has_parent_id>\n</rdf:Description>\n")
            f2.write(body)
            i = i + 1
            k = k + 1
            if i >= Max_Options: break
        f2.write("\n</rdf:RDF>\n")
        f2.close()
        spql2.write("\nLOAD <file:///" + str(SPARQL_path) + "/" + filename + "_option_" + str(FileNum) + "_.nq>;\n")
        k = 1



# Add Object-option links links Type-1  definitions Node 1
    FileNum = 0
    i = 1
    k = 1
    while i <= int(Max_Objects / 2):
        FileNum = FileNum + 1
        f1 = open(Model_path_node1 + filename + "_links_1_" + str(FileNum) + "_.nq", "at")
        f1.write(header)
        f1.write("\n<!--Add Object-option links Type-Linear-->\n")
        while k <= Max_Step_1:
            body = str("<rdf:Description rdf:about='http://127.0.0.1/Object_") + str(i) + str(
                "/'>\n<my:has_option_id>Option_") + str(random.randint(1, int(Max_Objects / 2))) + str("</my:has_option_id>\n</rdf:Description>\n")
            f1.write(body)
            i = i + 1
            k = k + 1
        f1.write("\n</rdf:RDF>\n")
        f1.close()
        spql1.write("\nLOAD <file:///" + str(SPARQL_path) + "/" + filename + "_links_1_" + str(FileNum) + "_.nq>;\n")
        k = 1

    # Add Object-option links links Type-1  definitions Node 2
    FileNum = 0
    i = int(Max_Objects / 2 + 1)
    k = 1
    while i <= Max_Objects:
        FileNum = FileNum + 1
        f2 = open(Model_path_node2 + filename + "_links_1_" + str(FileNum) + "_.nq", "at")
        f2.write(header)
        f2.write("\n<!--Add Object-option links Type-Linear-->\n")
        while k <= Max_Step_1:
            body = str("<rdf:Description rdf:about='http://127.0.0.1/Object_") + str(i) + str(
                    "/'>\n<my:has_option_id>Option_") + str(random.randint(int(Max_Options / 2 + 1), Max_Options)) + str(
                    "</my:has_option_id>\n</rdf:Description>\n")
            f2.write(body)
            i = i + 1
            k = k + 1
        f2.write("\n</rdf:RDF>\n")
        f2.close()
        spql2.write("\nLOAD <file:///" + str(SPARQL_path) + "/" + filename + "_links_1_" + str(FileNum) + "_.nq>;\n")
        k = 1



    spql1.close()
    spql2.close()

if __name__ == "__main__":
    createXML("KG_telecom")
