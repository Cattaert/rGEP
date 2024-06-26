"""
Created by:     Bryce Chung (neuRowsATL)
Last Modified:  May 20, 2016 (version 3)
Description: This class opens and saves AnimatLab models from .aproj files.
Modified August 23 2017 Daniel Cattaert
    ActualizeAproj now include StartTime and EndTime of externalStimuli
modified November 09, 2017 (D. Cattaert):
    class AnimatLabSimFile has been completed to include motor elements
    for getElementByType("MotorPosition") and getElementByType("MotorVelocity")
    These facilities are used in "optimization.py" in affichMotor() function
modified November 29, 2018 (D. Cattaert):
    Informations are now printed depending on the verbose level

Translated in Python 3.8 Jan 2023 (D. Cattaert)
modified February 01, 2024 (D. Cattaert):
    Bug fixed in lookupAppend4() method for synapsesFR to make it compatible
    with python3.8.
"""

# Import dependencies
import os
import glob
import numpy as np
from FoldersArm import FolderOrg

import xml.etree.ElementTree as elementTree

global verbose
verbose = 0

# # ===== ===== ===== ===== =====
# # ===== ===== ===== ===== =====


class AnimatLabModelError(Exception):
    """
    This class manages errors thrown by the AnimatLabModel class.
    Right now, this class does nothing other than print an error message.
    Last updated:   December 28, 2015
    Modified by:    Bryce Chung
    """
    def __init__(self, value):
        """
        __init__(value)
        Set the value of the error message.
        """
        self.value = value

    def __str__(self):
        """
        __str__()
        Returns the error message.
        """
        return repr(self.value)


# # ===== ===== ===== ===== =====
# # ===== ===== ===== ===== =====


class AnimatLabModel(object):
    """
    AnimatLabModel(folder='', asimFile='')
    API class that uploads, saves, and manages an AnimatLab simulation file.
    Using this class, you can load a simulation file and view its parameters,
    change its parameters, or use it to generate and save a new simulation file
    with different parameters.

    folder          Specifies folder for AnimatLab project files
    asimFile        Specifies .asim file for AnimatLab model

    get_aproj()                Get .aproj file path string
    get_asim()                 Get .asim file path string
    get_xmlRoot()              Get root XML element from parsed .asim file
    set_aproj(filePath)        Set path string for .aproj file
    set_asim(filePath)         Set path string for .asim file
    getElementByType(elType)   Get element(s) by AnimatLab type
    getElementByName(elName)   Get element(s) by AnimatLab name
    getElementByID(elID)       Get element by AnimatLab ID
    """
    def __init__(self, folder='', asimFile=''):
        """
        __init__(folder='', asimFile='')
        Initializes an AnimatLabModel class object.

        folder      Specifies full folder path for AnimatLab project files
        asimFile    Specifies full .asim file path for AnimatLab model

        If no folder is specified, the object will default to the current
        working directory.

        If no asimFile is specified, the object will search for an .asim file
        in the model folder with the character string, "_Standalone". If no
        file exists as "*_Standalone.asim" then the object will look for any
        file with the .asim extension.

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """

        # # Set root folder for AnimatLab model resource files
        if folder == '':
            self.projectFolder = os.getcwd()
        else:
            self.projectFolder = folder

        try:
            # # Check for AnimatLab project file
            aprojFile = glob.glob(os.path.join(self.projectFolder, '*.aproj'))
            if len(aprojFile) == 0:
                error = "No AnimatLab project file exists with extension " \
                        "*.aproj in folder:  %s" +\
                        "  Check AnimatLab project folder for consistency."
                raise AnimatLabModelError(error % self.projectFolder)
            elif len(aprojFile) > 1:
                error = "Multiple AnimatLab aproj files exist with extension" \
                        " *.aproj in folder: %s" +\
                        "  Check AnimatLab project folder for consistency."
                raise AnimatLabModelError(error % self.projectFolder)

            self.aprojFile = aprojFile[0]
            aprojFile = os.path.split(self.aprojFile)[-1]
            projectFileName = os.path.splitext(aprojFile)[0]
            self.aprojFile = os.path.join(self.projectFolder, aprojFile)

            if asimFile != '':
                # # Check to see if AnimatLab asimfile exists if specified
                if os.path.isfile(os.path.join(self.projectFolder, asimFile)):
                    self.asimFile = os.path.join(self.projectFolder, asimFile)
                else:
                    error = "Specified AnimatLab simulation file does not " \
                            "exist: %s"
                    raise AnimatLabModelError(error % os.path.join(
                                                self.projectFolder, asimFile))
            else:
                # # Try to find default AnimatLab simulation files...
                if os.path.isfile(
                    os.path.join(self.projectFolder,
                                 projectFileName+'_Standalone.asim')):
                    self.asimFile = os.path.join(
                        self.projectFolder, projectFileName+'_Standalone.asim')
                elif len(glob.glob(os.path.join(
                                    self.projectFolder, '*.asim'))) == 1:
                    self.asimFile = os.path.join(self.projectFolder, '*.asim')
                elif len(glob.glob(os.path.join(
                                    self.projectFolder, '*.asim'))) == 0:
                    error = "No standalone simulation file exists with " \
                            "extension *.asim in folder: %s" \
                            "  Generate a standalone simulation file from " \
                            "the AnimatLab GUI"
                    txt = error % self.projectFolder
                    raise AnimatLabModelError(txt)
                else:
                    error = "Multiple simulation files exist with extension "\
                            "*.asim in folder %s" +\
                            "  Delete duplicates and leave one file or "\
                            "initiate AnimatLabModel object with ASIM file "\
                            "specified"
                    raise AnimatLabModelError(error)

        except AnimatLabModelError as e:
            print("Error initializing AnimatLab model object:\n\n %s" % e.value)
            raise

        if verbose > 0:
            print("\nUsing AnimatLab Project File:\n%s" % self.aprojFile)
            print("\nUsing AnimatLab Simulation File:\n%s" % self.asimFile)

        # Set up lookup table for asim model elements
        self.tree = elementTree.parse(self.asimFile)
        root = self.tree.getroot()

        lookupType = []
        lookupID = []
        lookupName = []
        lookupElement = []

        def lookupAppend(el, elType):
            lookupType.append(elType)
            lookupID.append(el.find("ID").text)
            lookupName.append(el.find("Name").text)
            lookupElement.append(el)

        def lookupAppend2(el, elType):
            lookupType.append(elType)
            lookupID.append(el.find("ID").text)
            s = (el.find("SourceID").text)
            t = (el.find("TargetID").text)
            sm = np.array(lookupElement, dtype=object
                          )[np.where(np.array(lookupID) == s)[0]]
            if len(sm) == 1:
                sname = sm[0].find("Name").text
            tm = np.array(lookupElement, dtype=object
                          )[np.where(np.array(lookupID) == t)[0]]
            if len(tm) == 1:
                tname = tm[0].find("Name").text
            # lookupName.append(s + "*" + t)
            lookupName.append(sname + "*" + tname)
            lookupElement.append(el)

        def lookupAppend3(el, elType):
            lookupType.append(elType)
            lookupID.append(el.find("ID").text)
            lookupName.append(el.find("ColumnName").text)
            lookupElement.append(el)

        def lookupAppend4(el, elType, NeuID):
            lookupType.append(elType)
            lookupID.append(el.find("ID").text)
            s = (el.find("FromID").text)
            t = NeuID
            sm = np.array(lookupElement, dtype=object
                          )[np.where(np.array(lookupID) == s)[0]]
            if len(sm) == 1:
                sname = sm[0].find("Name").text
            tm = np.array(lookupElement, dtype=object
                          )[np.where(np.array(lookupID) == t)[0]]
            if len(tm) == 1:
                tname = tm[0].find("Name").text
            # lookupName.append(s + "*" + t)
            lookupName.append(sname + "*" + tname)
            lookupElement.append(el)

        ######################################################################
        """
        modified August 30, 2017 (D. Cattaert) to handle Joints parameters
        """
        def analyzeChilbodies(rb, level):
            txt = ""
            rbfound = 0
            chrblist = []
            for n in range(level):
                txt += "\t"
            # print txt, level, rb, rb.find("Name").text
            el = rb.find("Joint")
            if el is not None:
                print(txt + el.find("Name").text)
                lookupAppend(el, "Joint")
            elt = rb.find("ChildBodies")
            if elt is not None:
                rbfound = 1
                chrblist = list(elt)
            # if rbfound == 0:
            #     print txt + "No childbodies"
            # if rbfound == 1:
            #     print txt + "childbodies found",
            #     print txt, level, chrblist
            return [rbfound, chrblist]

        print("\nREADING .asim elements...")

        """
        modified August 30, 2017 (D. Cattaert) to handle Joints parameters
        """
        level = 0
        rbfound = 0
        subfound = 0
        childRbNb = 0
        nbsub = 1  # the firt list of rigid bodies
        subchrblist = []
        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for rigidbodyelmt in list(organism.find("RigidBody")):
                # print(rigidbodyelmt)
                if list(rigidbodyelmt) != []:
                    # print(list(rigidbodyelmt))
                    subfound = 1
                    rbeltlist = list(rigidbodyelmt)
                    subchrblist.append(rbeltlist)
                    childRbNb = 0
                    # number of child RigidBodies

                    while subfound:
                        for ch in range(nbsub):
                            childRbNb = 0
                            subfound = 0  # flag to indicate a child rb exists
                            # first looks for all childbodies from same parent
                            for rb in subchrblist[level+ch]:
                                [rbfound, chrblist] = analyzeChilbodies(rb,
                                                                        level)
                                if rbfound:
                                    childRbNb += 1
                                    subfound = 1
                                    # each time childbodies are found, the list
                                    # is added to the subchrblist
                                    subchrblist.append(chrblist)
                                nbsub = childRbNb
                                # ... continues the analysis of the parent
                            if subfound:    # once the parent has been scaned,
                                level += 1  # and childbodies found, each child
                                # becomes parent: the process starts again
        ######################################################################

        for el in list(root.find("ExternalStimuli")):
            if el.find("Type").text == "MotorPosition":
                lookupAppend(el, "MotorPosition")

        for el in list(root.find("ExternalStimuli")):
            if el.find("Type").text == "MotorVelocity":
                lookupAppend(el, "MotorVelocity")

        for el in list(root.find("ExternalStimuli")):
            if el.find("Type").text == "Current":
                lookupAppend(el, "ExternalStimuli")

        # path = "Environment/Organisms/Organism/NervousSystem/NeuralModules"
        # modules = root.find(path).getchildren()
        # for module in modules:
        """
        # modified by Daniel Cattaert May 2016
        in order to allow this module to work when a second organism is added
        the three lines above have been replaced in the three next lines
        """

        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for ns in list(organism.find("NervousSystem")):
                if list(ns) == []:
                    print("No NeuralModule")
                elif list(ns) != []:
                    # print(list(ns))
                    for mod in ns:
                        if mod.find("ModuleName").text == 'IntegrateFireSim':
                            for el in list(mod.find("Neurons")):
                                lookupAppend(el, "Neurons")
                        elif mod.find("ModuleName").text == 'PhysicsModule':
                            for el in list(mod.find("Adapters")):
                                lookupAppend(el, "Adapters")

        # path = "Environment/Organisms/Organism/NervousSystem/NeuralModules" \
        #        + "/NeuralModule/Synapses/SpikingSynapses"
        # modules = root.find(path).getchildren()
        # for el in modules:
        #    lookupAppend(el, "SpikingSynapses")

        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for ns in list(organism.find("NervousSystem")):
                if list(ns) == []:
                    print("No NeuralModule")
                elif list(ns) != []:
                    # print list(ns)
                    for mod in ns:
                        if mod.find("ModuleName").text == 'IntegrateFireSim':
                            for syn in list(mod.find("Synapses")):
                                # print syn
                                for el in syn:
                                    lookupAppend(el, "Synapses")

        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for ns in list(organism.find("NervousSystem")):
                if list(ns) == []:
                    print("No NeuralModule")
                elif list(ns) != []:
                    # print(list(ns))
                    for mod in ns:
                        if mod.find("ModuleName").text == 'IntegrateFireSim':
                            for el in list(mod.find("Connexions")):
                                lookupAppend2(el, "Connexions")

        for el in list(root.find("DataCharts")):
            lookupAppend(el, "Chart")

        """
        path = "DataCharts/DataChart/DataColumns"
        modules = list(root.find(path))
        for el in modules:
            lookupAppend3(el, "ChartcolName")
        """
        ch = 0
        for module in list(root.find("DataCharts")):
            print(module.find("Name").text)
            for el in list(module.find("DataColumns")):
                typ = "ChartCol" + str(ch)
                lookupAppend3(el, typ)
            ch += 1

        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for ns in list(organism.find("NervousSystem")):
                if list(ns) == []:
                    print("No NeuralModule")
                elif list(ns) != []:
                    # print list(ns)
                    for module in ns:
                        if module.find("ModuleName").text == 'FiringRateSim':
                            for el in list(module.find("Neurons")):
                                lookupAppend(el, "NeuronsFR")

        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for ns in list(organism.find("NervousSystem")):
                if list(ns) == []:
                    print("No NeuralModule")
                elif list(ns) != []:
                    # print list(ns)
                    for module in ns:
                        if module.find("ModuleName").text == 'FiringRateSim':
                            for el in list(module.find("Neurons")):
                                NeurID = el.find("ID").text
                                for syn in list(el.find("Synapses")):
                                    lookupAppend4(syn, "SynapsesFR", NeurID)

        self.lookup = {}
        self.lookup["Type"] = lookupType
        self.lookup["ID"] = lookupID
        self.lookup["Name"] = lookupName
        self.lookup["Element"] = lookupElement
        #

        # ===============================================
        # Set up lookup table for aproj model elements
        # ===============================================
        self.aprojtree = elementTree.parse(self.aprojFile)
        aprojroot = self.aprojtree.getroot()

        aprojlookupType = []
        aprojlookupID = []
        aprojlookupName = []
        aprojlookupElement = []

        def aprojlookupAppend(el, elType):
            aprojlookupType.append(elType)
            aprojlookupID.append(el.find("ID").text)
            aprojlookupName.append(el.find("Name").text)
            aprojlookupElement.append(el)

        def aprojlookupAppendNode(el, elType):
            aprojlookupType.append(elType)
            aprojlookupID.append(el.find("ID").text)
            aprojlookupName.append(el.find("Text").text)
            aprojlookupElement.append(el)

        def aprojlookupAppend2(el, elType):
            aprojlookupType.append(elType)
            aprojlookupID.append(el.find("ID").text)
            s = (el.find("OriginID").text)
            t = (el.find("DestinationID").text)
            sm = np.array(aprojlookupElement, dtype=object
                          )[np.where(np.array(aprojlookupID) == s)[0]]
            if len(sm) == 1:
                sname = sm[0].find("Text").text
            tm = np.array(aprojlookupElement, dtype=object
                          )[np.where(np.array(aprojlookupID) == t)[0]]
            if len(tm) == 1:
                tname = tm[0].find("Text").text
            aprojlookupName.append(sname + "*" + tname)
            # print sname + "*" + tname,
            aprojlookupElement.append(el)

        def aprojlookupAppend3(el, elType):
            aprojlookupType.append(elType)
            aprojlookupID.append(el.find("ID").text)
            aprojlookupName.append(el.find("ColumnName").text)
            aprojlookupElement.append(el)

        def aprojlookupAppend4(el, elType):
            aprojlookupType.append(elType)
            aprojlookupID.append(el.find("ID").text)
            s = (el.find("OriginID").text)
            t = (el.find("DestinationID").text)
            sm = np.array(aprojlookupElement, dtype=object
                          )[np.where(np.array(aprojlookupID) == s)[0]]
            if len(sm) == 1:
                sname = sm[0].find("Text").text
            tm = np.array(aprojlookupElement, dtype=object
                          )[np.where(np.array(aprojlookupID) == t)[0]]
            if len(tm) == 1:
                tname = tm[0].find("Text").text
            aprojlookupName.append(sname + "*" + tname)
            # print sname + "*" + tname,
            aprojlookupElement.append(el)

        print("\nREADING .aproj elements...")
        # print "Stimuli"
        path = "Simulation/Stimuli"
        for el in list(aprojroot.find(path)):
            # print el.find("Name").text,
            aprojlookupAppend(el, "Stimulus")
        # print

        # print "Neurons"
        path = "Simulation/Environment/Organisms"
        organisms = list(aprojroot.find(path))
        for organism in organisms:
            ns = organism.find("NervousSystem/Node")
            if ns is None:
                print("No Neuron")
            elif ns is not None:
                nodes = ns.find("Nodes")
                # print nodes, list(nodes)
                for el in list(nodes):
                    cn = el.find("ClassName").text
                    if cn.split('.')[0] == "IntegrateFireGUI":
                        # print el.find("Text").text,
                        aprojlookupAppendNode(el, "Neurons")

        # print

        # print "Adapters"
        path = "Simulation/Environment/Organisms"
        organisms = list(aprojroot.find(path))
        for organism in organisms:
            ns = organism.find("NervousSystem/Node")
            if ns is None:
                print("No Neuron")
            elif ns is not None:
                nodes = ns.find("Nodes")
                # print nodes, list(nodes)
                for el in list(nodes):
                    cn = el.find("ClassName").text
                    if cn.split('.')[-1] == "NodeToPhysicalAdapter":
                        # print el.find("Text").text,
                        aprojlookupAppendNode(el, "Adapters")
                    elif cn.split('.')[-1] == "PhysicalToNodeAdapter":
                        # print el.find("Text").text,
                        aprojlookupAppendNode(el, "Adapters")
        # print

        # print "Symapses types"
        path = "Simulation/Environment/Organisms"
        organisms = list(aprojroot.find(path))
        for organism in organisms:
            ns = organism.find("NervousSystem/NeuralModules")
            if list(ns) == []:
                print("No NeuralModule")
            elif list(ns) != []:
                for node in ns:
                    syty = node.find("SynapseTypes")
                    if syty is not None:
                        # print syty
                        li = list(syty)
                        for el in li:
                            # print el.find("Name").text,
                            aprojlookupAppend(el, "Synapses")
        # print

        # print "Connexions (Links)"
        path = "Simulation/Environment/Organisms"
        organisms = list(aprojroot.find(path))
        for organism in organisms:
            ns = organism.find("NervousSystem/Node")
            if ns is None:
                print("No Neuron")
            elif ns is not None:
                links = ns.find("Links")
                for el in list(links):
                    cn = el.find("ClassName").text
                    if cn.split('.')[0] == "IntegrateFireGUI":
                        aprojlookupAppend2(el, "Connexions")
        # print

        # print "NeuronsFR"
        path = "Simulation/Environment/Organisms"
        organisms = list(aprojroot.find(path))
        for organism in organisms:
            ns = organism.find("NervousSystem/Node")
            if ns is None:
                print("No Neuron")
            elif ns is not None:
                nodes = ns.find("Nodes")
                for el in list(nodes):
                    cn = el.find("ClassName").text
                    if cn.split('.')[0] == "FiringRateGUI":
                        # print el.find("Text").text,
                        aprojlookupAppendNode(el, "NeuronsFR")
        # print()

        # print("ConnexionsFR (Links)")
        path = "Simulation/Environment/Organisms"
        organisms = list(aprojroot.find(path))
        for organism in organisms:
            ns = organism.find("NervousSystem/Node")
            if list(ns) == []:
                print("No Neuron")
            elif list(ns) != []:
                for el in list(ns.find('Links')):
                    # print el
                    cn = el.find("ClassName").text
                    # print cn
                    if cn.split('.')[-1] == "Normal":
                        aprojlookupAppend4(el, "SynapsesFR")

        self.aprojlookup = {}
        self.aprojlookup["Type"] = aprojlookupType
        self.aprojlookup["ID"] = aprojlookupID
        self.aprojlookup["Name"] = aprojlookupName
        self.aprojlookup["Element"] = aprojlookupElement

    # GET functions
    def get_aproj(self):
        """
        get_aproj()
        Returns a character string of the .aproj file.

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """
        return self.aprojFile

    def get_asim(self):
        """
        get_asim()
        Returns a character string of the .asim file.

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """
        return self.asimFile

    def get_xml(self):
        """
        get_xml()
        Returns an XML root element for the XML tree.

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """
        try:
            return self.tree.getroot()
        except:
            raise KeyError("XML tree element not initiated")

    # SET functions
    def set_aproj(self, filePath):
        """
        set_aproj(filePath)
        Sets the full file path string for the .aproj file.

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """
        self.aprojFile = filePath

    def set_asim(self, filePath):
        """
        set_asim(filePath)
        Sets the full file path string for the .asim file.

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """
        if os.path.isfile(filePath):
            self.asimFile = filePath
            self.tree = elementTree.parse(self.asimFile)
            root = self.tree.getroot()
        else:
            warning = "No ASIM file specified for AnimatLab Model object."
            raise AnimatLabModelError(warning)

    def getElementByType(self, elType):
        """
        getElementByType(elType)
        Returns an array of XML elements with the type, elType

        elType          Options: "Neurons", "ExternalStimuli", "Adapters"

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
        return np.array(self.lookup["Element"], dtype=object
                        )[np.where(np.array(self.lookup["Type"]) == elType)[0]]

    def getElementByType2(self, elType):
        """
        getElementByType(elType)
        Returns an array of XML elements with the type, elType

        elType          Options: "Neurons", "ExternalStimuli", "Adapters"

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
        return np.array(self.lookup["Element"], dtype=object
                        )[np.where(np.array(self.lookup["Type"]) == elType)[0]]

    def getElementByName(self, elName):
        """
        getElementByName(elName)
        Returns an XML element with the specified name, elName

        elName          AnimatLab name of the desired element

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
        matches = np.array(self.lookup["Element"], dtype=object
                           )[np.where(np.array(self.lookup["Name"]
                                               ) == elName)[0]]
        if len(matches) > 1:
            warning = "WARNING: More than one element with name found!!\n\n \
                        %i instance(s) with name %s"
            print(warning % (len(matches), elName))
            return matches
        elif len(matches) == 1:
            return matches[0]
        else:
            warning = "WARNING: No matches found for elements with name:\n%s"
            print(warning % elName)
            return None

    def getElementByID(self, elID):
        """
        getElementByID(elID)
        Returns an XML element by the AnimatLab ID

        elID            Specifies the AnimatLab ID of the desired element

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
        matches = np.array(self.lookup["Element"], dtype=object
                           )[np.where(np.array(self.lookup["ID"]) == elID)[0]]
        if len(matches) > 1:
            warning = "WARNING: More than one element with ID found!!\n\n \
                        %i instance(s) with ID %s"
            print(warning % (len(matches, elID)))
            return matches
        elif len(matches) == 1:
            return matches[0]
        else:
            print("WARNING: No matches found for elements with ID:\n%s" % elID)
            return None

    def saveXML(self, fileName='', overwrite=False, affiche=True):
        """
        saveXML(fileName='', overwrite=False)
        Saves the current AnimatLabModel object as a .asim file
        with the path name, fileName.

        fileName        Specifies the name of the .asim file.
        overwrite       Boolean flag to overwrite an existing .asim file.

        The default file path is the project folder of
        the AnimatLabModel instantiation.

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
        if overwrite:
            if fileName == '':
                fileName = self.asimFile
            else:
                fileName = os.path.join(os.path.dirname(self.asimFile),
                                        os.path.splitext(fileName)[0]+'.asim')
        else:
            saveDir = os.path.dirname(self.asimFile)
            rootName = os.path.basename(os.path.splitext(self.asimFile)[0])
            oldname = rootName + '*.asim'
            ix = len(glob.glob(os.path.join(saveDir, oldname)))
            newname = rootName + '-%i.asim' % ix
            fileName = os.path.join(saveDir, newname)
        """
        print "----------------------------------"
        print 'asimFile', self.asimFile
        print 'fileName', fileName
        print 'overwrite', overwrite
        if fileName == '':
            if overwrite:
                fileName = self.asimFile
                print('--fileName', fileName)
            else:
                saveDir = os.path.split(self.asimFile)[0]
                rootName = os.path.split(self.asimFile)[-1].split('.')[0]
                oldname = rootName + '*.asim'
                ix = len(glob.glob(os.path.join(saveDir, oldname)))
                newname = rootName + '-%i.asim' % ix
                fileName = os.path.join(saveDir, newname)
                print('saveDir', saveDir)
                print('rootName', rootName)
                print('oldName', oldname)
                print('newName', newname)
                print('fileName', fileName)
        else:
            if overwrite:
                fileName = os.path.join(os.path.split(self.asimFile)[0],
                                        fileName.split('.')[0]+'.asim')
            else:
                saveDir = os.path.split(self.asimFile)[0]
                rootName = os.path.split(self.asimFile)[-1].split('.')[0]
                oldname = rootName + '*.asim'
                ix = len(glob.glob(os.path.join(saveDir, oldname)))
                newname = rootName + '-%i.asim' % ix
                fileName = os.path.join(saveDir, newname)

                ix = len(glob.glob(
                    os.path.join(os.path.split(self.asimFile)[0],
                                 fileName.split('.')[0]+'*.asim')))
                fileName = os.path.join(os.path.split(self.asimFile)[0],
                                        fileName.split('.')[0]+'-%i.asim' % ix)
        """
        if affiche:
            print('Saving file: %s' % fileName)
        self.tree.write(fileName)

    def getElementByNameAproj(self, elName):
        """
        getElementByName(elName)
        Returns an XML element with the specified name, elName
        elName          AnimatLab name of the desired element
        Last updated:   Februaryr 20, 2017
        Modified by:    Daniel Cattaert
        """
        matches = np.array(self.aprojlookup["Element"], dtype=object
                           )[np.where(np.array(self.aprojlookup["Name"]
                                               ) == elName)[0]]
        if len(matches) > 1:
            warning = "WARNING: More than one element with name found!!\n\n \
                        %i instance(s) with name %s"
            print(warning % (len(matches), elName))
            return matches
        elif len(matches) == 1:
            return matches[0]
        else:
            warning = "WARNING: No matches found for elements with name:\n%s"
            print(warning % elName)
            return None

    def changeMeshPath(self, newMeshPath):
        sp = ""

        def changeDir(oldDir, newMeshPath, meshDir):
            newPath = newMeshPath[:newMeshPath.find(meshDir)] + \
                     oldDir[oldDir.find(meshDir):]
            return newPath

        def findmesh(branch, sp):
            for elt in branch:
                print(sp + "elt", elt)
                try:
                    meshpath = elt.find("MeshFile").text
                    print(sp + meshpath)
                    new = changeDir(meshpath, newMeshPath, "MaleSkeleton")
                    elt.find("MeshFile").text = new
                    print(sp + new)
                except:
                    pass
                try:
                    cb = list(elt.find("ChildBodies"))
                    print(sp + "childbodies found")
                    sp = sp + "\t"
                    findmesh(cb, sp)
                except:
                    pass

        # self.tree = elementTree.parse(self.asimFile)
        self.aprojtree = elementTree.parse(self.aprojFile)
        root = self.aprojtree.getroot()
        path = "Simulation/Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            print(organism.find("Name").text)
            findmesh(organism, sp)
        # self.tree = elementTree.parse(self.asimFile)    # return to asimfile
        # root = self.tree.getroot()

    def asimtoaproj(self, el, ptVar, pts, simpar, affiche=0):
        # reads Animatlab Aproj file param value and scale
        va = el.get("Value")
        sc = el.get("Scale")
        ac = el.get("Actual")
        if simpar == "Value":
            txt1 = str(ptVar)
            for k in range(4-int(len(txt1)/8)):
                txt1 += "\t"
            txt2 = "= " + str(va)
            for k in range(2-int(len(txt2)/8)):
                txt2 += "\t"
            if affiche != 0:
                print(txt1 + txt2 + ">>\t" + str(pts[ptVar]))
            # Update the AnimatLab element value
            newValue = pts[ptVar]
            if sc == 'nano':
                newActual = newValue * 1e-09
            elif sc == 'micro':
                newActual = newValue * 1e-06
            elif sc == 'milli':
                newActual = newValue * 1e-03
            elif sc == 'None':
                newActual = newValue
        else:
            txt1 = str(ptVar)
            for k in range(4-int(len(txt1)/8)):
                txt1 += "\t"
            txt2 = "= " + str(ac)
            for k in range(2-int(len(txt2)/8)):
                txt2 += "\t"
            if affiche != 0:
                print(txt1 + txt2 + ">>\t" + str(pts[ptVar]))
            # Update the AnimatLab element value
            newActual = pts[ptVar]
            if sc == 'nano':
                newValue = newActual / 1e-09
            elif sc == 'micro':
                newValue = newActual / 1e-06
            elif sc == 'milli':
                newValue = newActual / 1e-03
            elif sc == 'None':
                newValue = newActual
            el.set("Value", str(newValue))
            el.set("Scale", sc)
            el.set("Actual", str(newActual))

        el.set("Value", str(newValue))
        el.set("Scale", sc)
        el.set("Actual", str(newActual))

    def actualizeAproj(self, obj_simSet, affiche=0):
        for ix, pts in enumerate(obj_simSet.samplePts):
            # print ix, pts
            for ptVar in pts:
                # Find the AnimatLab element by name
                name, param = ptVar.split('.')
                # print name, param
                node = self.getElementByNameAproj(name)
                if param == 'G':
                    # ATTENTION!!! Animatlab simfile indique G = Value
                    el = node.find('SynapticConductance')
                    self.asimtoaproj(el, ptVar, pts, "Value", affiche)
                elif param == 'SynAmp':
                    # ATTENTION!!! Animatlab simfile indique SynAmp = Value
                    el = node.find('MaxSynapticConductance')
                    self.asimtoaproj(el, ptVar, pts, "Value", affiche)
                elif param == 'ThreshV':
                    # ATTENTION!!! Animatlab simfile indique ThreshV = Value
                    el = node.find('PreSynapticThreshold')
                    self.asimtoaproj(el, ptVar, pts, "Value", affiche)
                elif param == "Weight":
                    # ATTENTION!!! Animatlab simfile indique Weight = Actual
                    el = node.find('Weight')
                    self.asimtoaproj(el, ptVar, pts, "Actual", affiche)
                elif param == 'CurrentOn':
                    # ATTENTION!!! Animatlab simfile indique CurrentOn = Actual
                    el = node.find('CurrentOn')
                    self.asimtoaproj(el, ptVar, pts, "Actual", affiche)
                elif param == 'StartTime':
                    el = node.find('StartTime')
                    self.asimtoaproj(el, ptVar, pts, "Actual", affiche)
                elif param == 'EndTime':
                    el = node.find('EndTime')
                    self.asimtoaproj(el, ptVar, pts, "Actual", affiche)

    def actualizeAprojStimState(self, asimtab_stims, affiche=0):
            for extStim in range(len(asimtab_stims)):
                # Find the AnimatLab element by name
                name = asimtab_stims[extStim][0]
                state = asimtab_stims[extStim][5]
                # print(name, state)
                node = self.getElementByNameAproj(name)
                el = node.find('Enabled').text
                node.find('Enabled').text = str(state)
                if affiche != 0:
                    txt1 = str(name)
                    for k in range(3-int(len(txt1)/8)):
                        txt1 += "\t"
                    txt2 = str(el) + " ---> "
                    for k in range(2-int(len(txt2)/8)):
                        txt2 += "\t"
                    print(txt1 + txt2 + str(state))
                    # print name, "\t", el, "--->", "\t", state

    def actualizeAprojMotorState(self, asimtab_motorst, affiche=0):
            for motorSt in range(len(asimtab_motorst)):
                # Find the AnimatLab element by name
                name = asimtab_motorst[motorSt][0]
                state = asimtab_motorst[motorSt][5]
                # print name, state
                node = self.getElementByNameAproj(name)
                el = node.find('Enabled').text
                node.find('Enabled').text = str(state)
                if affiche != 0:
                    txt1 = str(name)
                    for k in range(3-int(len(txt1)/8)):
                        txt1 += "\t"
                    txt2 = str(el) + " ---> "
                    for k in range(2-int(len(txt2)/8)):
                        txt2 += "\t"
                    print(txt1 + txt2 + str(state))
                    # print name, "\t", el, "--->", "\t", state

    def saveXMLaproj(self, fileName='', overwrite=False, affiche=True):
        """
        saveXML(fileName='', overwrite=False)
        Saves the current AnimatLabAproj object as a .aproj file with the
        path name, fileName.split

        fileName        Specifies the name of the .aproj file.
        overwrite       Boolean flag to overwrite an existing .proj file.

        The default file path is the project folder of the AnimatLabAProj
        instantiation.

        Last updated:   September 19, 2017
        Modified by:    Daniel Cattaert
        """
        if fileName == '':
            if overwrite:
                fileNameOK = self.aprojFile
            else:
                saveDir = os.path.split(self.aprojFile)[0]
                saveName = os.path.split(self.aprojFile)[-1]
                rootName = os.path.splitext(saveName)[0]
                oldname = rootName + '*.aproj'
                ix = len(glob.glob(os.path.join(saveDir, oldname)))
                newname = rootName + '-{0:d}.aproj'.format(ix)
                fileNameOK = os.path.join(saveDir, newname)
        else:
            if overwrite:
                saveDir = os.path.split(fileName)[0]
                ficName = os.path.splitext(fileName)[0] + '.aproj'
                fileNameOK = os.path.join(saveDir, ficName)
            else:
                saveDir = os.path.split(fileName)[0]
                ficName = os.path.splitext(fileName)[0] + '*.aproj'
                ix = len(glob.glob(os.path.join(saveDir, ficName)))
                newname = os.path.splitext(fileName)[0] +\
                    '-{0:d}.aproj'.format(ix)
                fileNameOK = os.path.join(saveDir, newname)
        if affiche:
            print('Saving file: {}'.format(fileNameOK))
        self.aprojtree.write(fileNameOK)
        return fileNameOK


class AnimatLabSimFile(object):
    def __init__(self, asimFile=''):
        """
        __init__(asimFile='')
        Initializes an AnimatLabSimFile class object.

        asimFile    Specifies full .asim file path for AnimatLab asim File

        Last updated:   February 20, 2017
        Modified by:    DAniel Cattaert
        """
        # # Set root folder for AnimatLab model resource files
        try:
            if asimFile != '':
                # # Check to see if AnimatLab asimfile exists if specified
                if os.path.isfile(asimFile):
                    self.asimFile = asimFile
                else:
                    error = "Specified AnimatLab simulation file does not " \
                            "exist: %s"
                    raise AnimatLabModelError(error % asimFile)
        except:
            pass

        # Set up lookup table for asim model elements
        self.tree = elementTree.parse(self.asimFile)
        root = self.tree.getroot()

        lookupType = []
        lookupID = []
        lookupName = []
        lookupElement = []

        def lookupAppend(el, elType):
            lookupType.append(elType)
            lookupID.append(el.find("ID").text)
            lookupName.append(el.find("Name").text)
            lookupElement.append(el)

        def lookupAppend2(el, elType):
            lookupType.append(elType)
            lookupID.append(el.find("ID").text)
            s = (el.find("SourceID").text)
            t = (el.find("TargetID").text)
            sm = np.array(lookupElement, dtype=object
                          )[np.where(np.array(lookupID) == s)[0]]
            if len(sm) == 1:
                sname = sm[0].find("Name").text
            tm = np.array(lookupElement, dtype=object
                          )[np.where(np.array(lookupID) == t)[0]]
            if len(tm) == 1:
                tname = tm[0].find("Name").text
            # lookupName.append(s + "*" + t)
            lookupName.append(sname + "*" + tname)
            lookupElement.append(el)

        def lookupAppend3(el, elType):
            lookupType.append(elType)
            lookupID.append(el.find("ID").text)
            lookupName.append(el.find("ColumnName").text)
            lookupElement.append(el)

        def lookupAppend4(el, elType, NeuID):
            lookupType.append(elType)
            lookupID.append(el.find("ID").text)
            s = (el.find("FromID").text)
            t = NeuID
            sm = np.array(lookupElement, dtype=object
                          )[np.where(np.array(lookupID) == s)[0]]
            if len(sm) == 1:
                sname = sm[0].find("Name").text
            tm = np.array(lookupElement, dtype=object
                          )[np.where(np.array(lookupID) == t)[0]]
            if len(tm) == 1:
                tname = tm[0].find("Name").text
            # lookupName.append(s + "*" + t)
            lookupName.append(sname + "*" + tname)
            lookupElement.append(el)

        ######################################################################
        """
        modified August 30, 2017 (D. Cattaert) to handle Joints parameters
        """
        def analyzeChilbodies(rb, level):
            txt = ""
            rbfound = 0
            chrblist = []
            for n in range(level):
                txt += "\t"
            # print txt, level, rb, rb.find("Name").text
            el = rb.find("Joint")
            if el is not None:
                if verbose>2:
                    print(txt + el.find("Name").text)
                lookupAppend(el, "Joint")
            elt = rb.find("ChildBodies")
            if elt is not None:
                rbfound = 1
                chrblist = list(elt)
            # if rbfound == 0:
            #     print txt + "No childbodies"
            # if rbfound == 1:
            #     print txt + "childbodies found",
            #     print txt, level, chrblist
            return [rbfound, chrblist]


        print("\nREADING .asim elements...")

        """
        modified August 30, 2017 (D. Cattaert) to handle Joints parameters
        """
        level = 0
        rbfound = 0
        subfound = 0
        childRbNb = 0
        nbsub = 1  # the firt list of rigid bodies
        subchrblist = []
        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for rigidbodyelmt in list(organism.find("RigidBody")):
                # print rigidbodyelmt
                if list(rigidbodyelmt) != []:
                    # print list(rigidbodyelmt)
                    subfound = 1
                    rbeltlist = list(rigidbodyelmt)
                    subchrblist.append(rbeltlist)
                    childRbNb = 0
                    # number of child RigidBodies

                    while subfound:
                        for ch in range(nbsub):
                            childRbNb = 0
                            subfound = 0  # flag to indicate a child rb exists
                            # first looks for all childbodies from same parent
                            for rb in subchrblist[level+ch]:
                                [rbfound, chrblist] = analyzeChilbodies(rb,
                                                                        level)
                                if rbfound:
                                    childRbNb += 1
                                    subfound = 1
                                    # each time childbodies are found, the list
                                    # is added to the subchrblist
                                    subchrblist.append(chrblist)
                                nbsub = childRbNb
                                # ... continues the analysis of the parent
                            if subfound:    # once the parent has been scaned,
                                level += 1  # and childbodies found, each child
                                # becomes parent: the process starts again
        ######################################################################

        for el in list(root.find("ExternalStimuli")):
            if el.find("Type").text == "MotorPosition":
                lookupAppend(el, "MotorPosition")

        for el in list(root.find("ExternalStimuli")):
            if el.find("Type").text == "MotorVelocity":
                lookupAppend(el, "MotorVelocity")

        for el in list(root.find("ExternalStimuli")):
            if el.find("Type").text == "Current":
                lookupAppend(el, "ExternalStimuli")

        # path = "Environment/Organisms/Organism/NervousSystem/NeuralModules"
        # modules = root.find(path).getchildren()
        # for module in modules:
        """
        # modified by Daniel Cattaert May 2016
        in order to allow this module to work when a second organism is added
        the three lines above have been replaced in the three next lines by
        """

        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for ns in list(organism.find("NervousSystem")):
                if list(ns) == []:
                    if verbose > 2:
                        print("No NeuralModule")
                elif list(ns) != []:
                    if verbose > 2:
                        print(list(ns))
                    for mod in ns:
                        if mod.find("ModuleName").text == 'IntegrateFireSim':
                            for el in list(mod.find("Neurons")):
                                lookupAppend(el, "Neurons")
                        elif mod.find("ModuleName").text == 'PhysicsModule':
                            for el in list(mod.find("Adapters")):
                                lookupAppend(el, "Adapters")

        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for ns in list(organism.find("NervousSystem")):
                if list(ns) == []:
                    if verbose > 2:
                        print("No NeuralModule")
                elif list(ns) != []:
                    if verbose > 2:
                        print(list(ns))
                    for mod in ns:
                        if mod.find("ModuleName").text == 'IntegrateFireSim':
                            for syn in list(mod.find("Synapses")):
                                # print syn
                                for el in syn:
                                    lookupAppend(el, "Synapses")

        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for ns in list(organism.find("NervousSystem")):
                if list(ns) == []:
                    if verbose > 2:
                        print("No NeuralModule")
                elif list(ns) != []:
                    if verbose > 2:
                        print(list(ns))
                    for mod in ns:
                        if mod.find("ModuleName").text == 'IntegrateFireSim':
                            for el in list(mod.find("Connexions")):
                                lookupAppend2(el, "Connexions")

        for el in list(root.find("DataCharts")):
            lookupAppend(el, "Chart")

        """
        path = "DataCharts/DataChart/DataColumns"
        modules = list(root.find(path))
        for el in modules:
            lookupAppend3(el, "ChartcolName")
        """

        ch = 0
        for module in list(root.find("DataCharts")):
            if verbose > 2:
                print(module.find("Name").text)
            for el in list(module.find("DataColumns")):
                typ = "ChartCol" + str(ch)
                lookupAppend3(el, typ)
            ch += 1

        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for ns in list(organism.find("NervousSystem")):
                if list(ns) == []:
                    if verbose > 2:
                        print("No NeuralModule")
                elif list(ns) != []:
                    if verbose > 2:
                        print(list(ns))
                    for module in ns:
                        if module.find("ModuleName").text == 'FiringRateSim':
                            for el in list(module.find("Neurons")):
                                lookupAppend(el, "NeuronsFR")

        path = "Environment/Organisms"
        organisms = list(root.find(path))
        for organism in organisms:
            for ns in list(organism.find("NervousSystem")):
                if list(ns) == []:
                    if verbose > 2:
                        print("No NeuralModule")
                elif list(ns) != []:
                    if verbose > 2:
                        print(list(ns))
                    for module in ns:
                        if module.find("ModuleName").text == 'FiringRateSim':
                            for el in list(module.find("Neurons")):
                                NeurID = el.find("ID").text
                                for syn in list(el.find("Synapses")):
                                    lookupAppend4(syn, "SynapsesFR", NeurID)

        self.lookup = {}
        self.lookup["Type"] = lookupType
        self.lookup["ID"] = lookupID
        self.lookup["Name"] = lookupName
        self.lookup["Element"] = lookupElement

    def getElementByType(self, elType):
        """
        getElementByType(elType)
        Returns an array of XML elements with the type, elType

        elType          Options: "Neurons", "ExternalStimuli", "Adapters"

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
        return np.array(self.lookup["Element"], dtype=object
                        )[np.where(np.array(self.lookup["Type"]) == elType)[0]]

    def getElementByType2(self, elType):
        """
        getElementByType(elType)
        Returns an array of XML elements with the type, elType

        elType          Options: "Neurons", "ExternalStimuli", "Adapters"

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
        return np.array(self.lookup["Element"], dtype=object
                        )[np.where(np.array(self.lookup["Type"]) == elType)[0]]

    def getElementByName(self, elName):
        """
        getElementByName(elName)
        Returns an XML element with the specified name, elName

        elName          AnimatLab name of the desired element

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
        matches = np.array(self.lookup["Element"], dtype=object
                           )[np.where(np.array(self.lookup["Name"]
                                               ) == elName)[0]]
        if len(matches) > 1:
            warning = "WARNING: More than one element with name found!!\n\n \
                        %i instance(s) with name %s"
            print(warning % (len(matches), elName))
            return matches
        elif len(matches) == 1:
            return matches[0]
        else:
            warning = "WARNING: No matches found for elements with name:\n%s"
            print(warning % elName)
            return None

    def getElementByID(self, elID):
        """
        getElementByID(elID)
        Returns an XML element by the AnimatLab ID

        elID            Specifies the AnimatLab ID of the desired element

        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
        matches = np.array(self.lookup["Element"], dtype=object
                           )[np.where(np.array(self.lookup["ID"]) == elID)[0]]
        if len(matches) > 1:
            warning = "WARNING: More than one element with ID found!!\n\n \
                        %i instance(s) with ID %s"
            print(warning % (len(matches, elID)))
            return matches
        elif len(matches) == 1:
            return matches[0]
        else:
            print("WARNING: No matches found for elements with ID:\n%s" % elID)
            return None

"""
if __name__ == '__main__':
    folders = FolderOrg(subdir="ArmSPike13e2")
    folders.affectDirectories()
    projectFolder = folders.animatlab_commonFiles_dir
    model = AnimatLabModel(folders.animatlab_commonFiles_dir)
    newMeshPath = "\\\\MAC\Home\Documents\Labo\Scripts\AnimatLabV2\Human\\"
    newMeshPath += "MaleSkeleton"
    model.changeMeshPath(newMeshPath)
    aprojSaveDir = folders.animatlab_rootFolder + "AprojFiles/"
    if not os.path.exists(aprojSaveDir):
        os.makedirs(aprojSaveDir)
    # model.saveXMLaproj(aprojSaveDir + "ArmSpike13.aproj")
"""
