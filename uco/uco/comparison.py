from difflib import Differ

# compares a and b and outputs a HTML table of the changes. 

def compare(old,new,filename):
    out = get_differences(old,new)
    make_html_table(out,filename)

# using the Differ module of the difflib library to compare 
# outputs a generator object that is converted into a list of 
# the changes of the form [[added/removed, line]]
# - -> line was removed
# + -> line was added
def get_differences(old,new):
    old = old.replace("\r","")
    old_list = old.split("\n")
    new_list = split_txt(new)
    d = Differ()
    result = list(d.compare(old_list,new_list))
    for i in range(0,len(result)):
        result[i]=result[i].split()
    return result

def split_txt(txt):
    f = open(txt,"r+")
    ans = f.read().splitlines()
    f.close()
    return ans

# created an html table that assigns a class to the rows
# that have been added and removed
def make_html_table(l,name):
    ans = ['''{% extends "changes_base.html" %}\n''','''{% block body %}\n''','<table>\n']
    for line in l:
        front = '\t<tr>\n\t\t<td>'
        if len(line) == 0 :
            continue
        elif line[0] == "?":
            continue
        elif line[0] == "-":
            front = '\t<tr>\n\t\t<td class ='+'"removed">'
        elif line[0] == "+":
            front = '\t<tr>\n\t\t<td class ='+'"added">'
        ans.append(str(add_line(line,front)))
    ans.append('</table>\n')
    ans.append('''{% endblock %}''')
    write_file(ans,name)

def add_line(line,front):
    end = '</td>\n\t</tr>\n'
    if (line[0] == "+" or line[0] == "-"):
        line = line[1:]
    return front+" ".join(line)+end

def write_file(l,name):
    f = open(name,"w+")
    for line in l:
        f.write(str(line))
    f.close()