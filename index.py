from os import listdir
import os.path
from git import Repo

smallLines = [
    "}", "});", "};", ");", ")", "]", "];"
]

firstThingSize = 70
forceNonGit = False

def getSell(text, size):
    spaces = size - len(text)
    output = text
    for i in range(spaces):
        output += " "
    return output

def repeat(text, size):
    output = ""
    for i in range(size):
        output += text
    return output

def startsWithCheck(line):
    for i in smallLines:
        if (line.startswith(i)):
            return True
    return False

def fileNameCutFromEndThing(fname: str, length: int):
    if len(fname) > length:
        out = "..."
        out += fname[len(fname) - length + 3:len(fname)]
        return out
    else:
        return fname

# Results:
# 0 - Full line
# 1 - Comments (DO Comment Block CHECKS AFTER)
# 2 - AutoGen
# 3 - Blank
# 4 - Small
def getLineResult(line: str) -> int:
    # Ignore // comments
    if (line.strip().startswith("//")):
        return 1

    # Ignore 'import' and 'package'
    if (line.strip().startswith("package ")):    
        return 2
    if (line.strip().startswith("import ")):
        return 2

    # Ignore @things
    if (line.strip().startswith("@") and 
        (line.strip().find("public") == -1 and line.strip().find("private") == -1
        and line.strip().find("static") == -1)):
        return 2

    # Ignore blank
    if (line.isspace()):
        return 3

    # Skip small
    if (len(line.strip()) < 3):
        return 4
    if (len(line.strip()) < 5 and startsWithCheck(line.strip())):
        return 4

    return 0

def getAllJavaFiles(dir):
    out = []
    if (os.path.isdir(dir)):
        #print (f"[DEBUG] Getting all java files from '{dir}'...")
        for f in listdir(dir):
            #print (f"[DEBUG] listdir - {f}")
            fpath = os.path.join(dir, f)
            #print (f"[DEBUG] fpath - {fpath}")
            if os.path.isfile(fpath):
                #print (f"[DEBUG] File found - {fpath}")
                if (fpath.endswith(".java")):
                    out.append(fpath)
                    #print (f"[DEBUG] Adding file - {fpath}")
                #else:
                    #print (f"[DEBUG] File is non-java - {fpath} ({f}). Ignoring...")
            elif os.path.isdir(fpath):
                #print (f"[DEBUG] Dir found - {fpath}")
                if not f.startswith("."):
                    #print (f"[DEBUG] Scanning dir - {fpath}")
                    for fd in getAllJavaFiles(fpath):
                        out.append(fd)
                #else:
                    #print (f"[DEBUG] Dir path starts with '.' - {fpath} ({f}). Ignoring...")
            #else:
                #print (f"[DEBUG] Path '{fpath}' isn't both file nor directory.")
    return out

if __name__ == "__main__":
    print ("Count Lines of Code (Java) by SuperNeon4ik\n")
    path = input ("Directory or File Path to scan: ")

    if not os.path.exists(path):
        print ("File or directory does not exist! Please double-check the path you've entered.")
    else:
        print ("Fetching files...")
        files = []
        if os.path.isfile(path):
            files.append(path)
        elif os.path.isdir(path):
            files = getAllJavaFiles(path)

        for f in files:
            print (f"Found '{f}'.")

        print ("Done fetching files!")
        print ()
            
        totalLines = 0
        totalSkippedComments = 0
        totalSkippedBlank = 0
        totalSkippedAutogenerated = 0
        totalSkippedSmall = 0

        fileInfoOutputs = []

        gitRepo = None
        if not forceNonGit:
            if (os.path.exists(os.path.join(path, ".git")) and os.path.isdir(os.path.join(path, ".git"))):
                print ("Git directory found! Also additionally scanning for user data...")
                gitRepo = Repo(path)
                assert not gitRepo.bare
        
        gitUserData = {}
        for f in files:
            scanOld = False
            if (gitRepo != None):
                print (f"Scanning git info from file '{f}'...")

                skippedComments = 0
                skippedBlank = 0
                skippedAutogenerated = 0
                skippedSmall = 0

                skippedLines = []

                isBlockComment = False
                index = 0

                fileLines = 0

                try:
                    for commit, lines in gitRepo.blame('HEAD', f):
                        author = gitRepo.git.show("-s", "--format=Author: %an <%ae>", commit.hexsha)
                        #print("%s changed these lines: %s" % (author, lines))   

                        totalLines += len(lines)
                        fileLines += len(lines)

                        uComments = 0
                        uAutogen = 0
                        uBlank = 0
                        uSmall = 0
                        for line in lines:
                            index += 1

                            # Check for comment block
                            if (isBlockComment):
                                skippedLines.append(f"Line #{index} (Comment Block) Skipped: " + line.strip())
                                skippedComments += 1
                                totalSkippedComments += 1
                                uComments += 1

                                if (line.strip().startswith("*/")):
                                    isBlockComment = False
                                continue
                            if (line.strip().startswith("/*") or line.strip().startswith("/**")):
                                isBlockComment = True
                                skippedLines.append(f"Line #{index} (Comment Block) Skipped: " + line.strip())
                                skippedComments += 1
                                totalSkippedComments += 1
                                uComments += 1
                                continue

                            result = getLineResult(line)
                            if (result == 1):
                                skippedComments += 1
                                totalSkippedComments += 1
                                uComments += 1
                                skippedLines.append(f"Line #{index} (Comment) Skipped: " + line.strip())
                            elif (result == 2):
                                skippedAutogenerated += 1
                                totalSkippedAutogenerated += 1
                                uAutogen += 1
                                skippedLines.append(f"Line #{index} (AutoGen) Skipped: " + line.strip())
                            elif (result == 3):
                                skippedBlank += 1
                                totalSkippedBlank += 1
                                uBlank += 1
                                skippedLines.append(f"Line #{index} (Blank) Skipped: " + line.strip())
                            elif (result == 4):
                                skippedSmall += 1
                                totalSkippedSmall += 1
                                uSmall += 1
                                skippedLines.append(f"Line #{index} (Small) Skipped: " + line.strip())

                        #uResult = len(lines) - skippedComments - skippedAutogenerated - skippedSmall - skippedBlank                        
                        data = gitUserData.get(author)
                        if data != None:
                            #data = gitUserData[author]
                            data["total"] += len(lines)
                            data["comments"] += uComments
                            data["autogen"] += uAutogen
                            data["small"] += uSmall
                            data["blank"] += uBlank
                            gitUserData[author] = data
                        else:
                            data = {
                                "total": len(lines),
                                "comments": uComments,
                                "autogen": uAutogen,
                                "small": uSmall,
                                "blank": uBlank
                            }
                            gitUserData[author] = data        

                    print(f"Logging and saving info from '{f}'...")
                    result = fileLines - skippedComments - skippedAutogenerated - skippedSmall - skippedBlank
                    fileInfoOutputs.append(getSell(fileNameCutFromEndThing(f, firstThingSize - 2), firstThingSize) + "|" + getSell(str(fileLines), 15) + "|" + getSell(str(result), 15) + "|" + getSell(str(skippedComments), 15) + "|" + getSell(str(skippedAutogenerated), 15) + "|" + getSell(str(skippedSmall), 15) + "|" + getSell(str(skippedBlank), 15))           
                except:
                    print(f"Failed to scan file '{f}'! Scanning using casual method...")
                    scanOld = True
            else:
                scanOld = True
            
            if scanOld:
                print (f"Openning '{f}'...")
                with open(f) as file:
                    lines = file.readlines()
                    print (f"Successfully opened '{f}'! Counting...")

                    skippedComments = 0
                    skippedBlank = 0
                    skippedAutogenerated = 0
                    skippedSmall = 0

                    skippedLines = []

                    isBlockComment = False
                    index = 0
                    totalLines += len(lines)
                    for line in lines:
                        index += 1

                        # Check for comment block
                        if (isBlockComment):
                            skippedLines.append(f"Line #{index} (Comment Block) Skipped: " + line.strip())
                            skippedComments += 1
                            totalSkippedComments += 1

                            if (line.strip().startswith("*/")):
                                isBlockComment = False
                            continue
                        if (line.strip().startswith("/*") or line.strip().startswith("/**")):
                            isBlockComment = True
                            skippedLines.append(f"Line #{index} (Comment Block) Skipped: " + line.strip())
                            skippedComments += 1
                            totalSkippedComments += 1
                            continue

                        result = getLineResult(line)
                        if (result == 1):
                            skippedComments += 1
                            totalSkippedComments += 1
                            skippedLines.append(f"Line #{index} (Comment) Skipped: " + line.strip())
                        elif (result == 2):
                            skippedAutogenerated += 1
                            totalSkippedAutogenerated += 1
                            skippedLines.append(f"Line #{index} (AutoGen) Skipped: " + line.strip())
                        elif (result == 3):
                            skippedBlank += 1
                            totalSkippedBlank += 1
                            skippedLines.append(f"Line #{index} (Blank) Skipped: " + line.strip())
                        elif (result == 4):
                            skippedSmall += 1
                            totalSkippedSmall += 1
                            skippedLines.append(f"Line #{index} (Small) Skipped: " + line.strip())
            
                    print

                    print(f"Logging and saving info from '{f}'...")
                    result = len(lines) - skippedComments - skippedAutogenerated - skippedSmall - skippedBlank
                    fileInfoOutputs.append(getSell(fileNameCutFromEndThing(f, firstThingSize - 2), firstThingSize) + "|" + getSell(str(len(lines)), 15) + "|" + getSell(str(result), 15) + "|" + getSell(str(skippedComments), 15) + "|" + getSell(str(skippedAutogenerated), 15) + "|" + getSell(str(skippedSmall), 15) + "|" + getSell(str(skippedBlank), 15))      

                    data = gitUserData.get("Non-Git")
                    if data != None:
                        #data = gitUserData["Non-Git"]
                        data["total"] += len(lines)
                        data["comments"] += skippedComments
                        data["autogen"] += skippedAutogenerated
                        data["small"] += skippedSmall
                        data["blank"] += skippedBlank
                        gitUserData["Non-Git"] = data
                    else:
                        data = {
                            "total": len(lines),
                            "comments": skippedComments,
                            "autogen": skippedAutogenerated,
                            "small": skippedSmall,
                            "blank": skippedBlank
                        }
                        gitUserData["Non-Git"] = data

        print()
        print()
        print()                
        print(getSell("File", firstThingSize) + "|" + getSell("Total", 15) + "|" + getSell("Result", 15) + "|" + getSell("Comments", 15) + "|" + getSell("AutoGen", 15) + "|" + getSell("Small", 15) + "|" + getSell("Blank", 15))
        print(repeat("-", firstThingSize) + "+" + repeat("-", 15) + "+" + repeat("-", 15) + "+" + repeat("-", 15) + "+" + repeat("-", 15) + "+" + repeat("-", 15) + "+" + repeat("-", 15))
        totalResult = totalLines - totalSkippedComments - totalSkippedAutogenerated - totalSkippedSmall - totalSkippedBlank
        print(getSell("Total", firstThingSize) + "|" + getSell(str(totalLines), 15) + "|" + getSell(str(totalResult), 15) + "|" + getSell(str(totalSkippedComments), 15) + "|" + getSell(str(totalSkippedAutogenerated), 15) + "|" + getSell(str(totalSkippedSmall), 15) + "|" + getSell(str(totalSkippedBlank), 15))      
        print(repeat(" ", firstThingSize) + "|" + repeat(" ", 15) + "|" + repeat(" ", 15) + "|" + repeat(" ", 15) + "|" + repeat(" ", 15) + "|" + repeat(" ", 15) + "|" + repeat(" ", 15))
        for o in fileInfoOutputs:
            print(o)

        print()
        print()
        print(getSell("User", firstThingSize) + "|" + getSell("Total", 15) + "|" + getSell("Result", 15) + "|" + getSell("Comments", 15) + "|" + getSell("AutoGen", 15) + "|" + getSell("Small", 15) + "|" + getSell("Blank", 15))
        print(repeat("-", firstThingSize) + "+" + repeat("-", 15) + "+" + repeat("-", 15) + "+" + repeat("-", 15) + "+" + repeat("-", 15) + "+" + repeat("-", 15) + "+" + repeat("-", 15))
        totalResult = totalLines - totalSkippedComments - totalSkippedAutogenerated - totalSkippedSmall - totalSkippedBlank
        print(getSell("Total", firstThingSize) + "|" + getSell(str(totalLines), 15) + "|" + getSell(str(totalResult), 15) + "|" + getSell(str(totalSkippedComments), 15) + "|" + getSell(str(totalSkippedAutogenerated), 15) + "|" + getSell(str(totalSkippedSmall), 15) + "|" + getSell(str(totalSkippedBlank), 15))      
        print(repeat(" ", firstThingSize) + "|" + repeat(" ", 15) + "|" + repeat(" ", 15) + "|" + repeat(" ", 15) + "|" + repeat(" ", 15) + "|" + repeat(" ", 15) + "|" + repeat(" ", 15))
        for userKey in gitUserData.keys():
            user = gitUserData[userKey]
            uTotal = user["total"]
            uComments = user["comments"]
            uAutogen = user["autogen"]
            uSmall = user["small"]
            uBlank = user["blank"]

            uResult = uTotal - uComments - uAutogen - uSmall - uBlank

            print(getSell(fileNameCutFromEndThing(userKey, firstThingSize - 2), firstThingSize) + "|" + getSell(str(uTotal), 15) + "|" + getSell(str(uResult), 15) + "|" + getSell(str(uComments), 15) + "|" + getSell(str(uAutogen), 15) + "|" + getSell(str(uSmall), 15) + "|" + getSell(str(uBlank), 15))           