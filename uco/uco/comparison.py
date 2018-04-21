from difflib import Differ
from difflib import SequenceMatcher

# compares a and b and outputs a HTML table of the changes. 

def compare(old,new,filename):
    out = get_differences(old,new)
    out_new = compute_word_diffs(out)
    make_html_table(out_new,filename)

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

def compute_word_diffs(out):
    # out is of the format
    # [['-','text','removed'],['+','text','added'],['?','text','uncertain'],['text','unchanged']]
    out = split_changes(out)
    # out is of the format
    # [['-','text removed'],['+','text added'],['#','text unchanged']]
    ans = []
    i=-1
    while i < len(out)-2:
        i+=1
        line = out[i]
        next = out[i+1]
        s = SequenceMatcher(None, ''.join(line[1]), ''.join(next[1]))
        # calculate similarity score of two lines
        ratio = s.ratio()
        if ratio < 0.75:
            ans.append(line)
        else:
            # print(ratio)
            # print(''.join(line[1])+"\n")
            # print(''.join(next[1])+"\n")
            new_line = ["+/-", word_by_word_changes(line[1],next[1])]
            ans.append(new_line)
            i +=1
    return ans

def split_changes(out):
    ans = []
    for line in out:
        if len(line) <1 or line[0] == "?":
            continue
        elif line[0] == "+" or line[0] == "-":
            ans.append([line[0],' '.join(line[1:])])
        else:
            ans.append(['#',' '.join(line)])
    return ans

def word_by_word_changes(old,new):
    ans=[]
    old = old.split(" ")
    new = new.split(" ")
    ans = calc_removals(old,new,ans)
    ans = calc_additions(old,new,ans)
    print(" ".join(ans))
    return " ".join(ans)

def calc_removals(old,new, ans):
    for word in old:
        if word in new:
            ans.append(word)
        else:
            ans.append("-"+word)
    return ans

def calc_additions(old,new, ans):
    offset = 0
    for i in range(len(new)):
        word = new[i]
        if word not in old:
            ans.insert(i+offset,"+"+word)
            offset+=1
    return ans
            
# created an html table that assigns a class to the rows
# that have been added and removed
def make_html_table(l,name):
    print(l[0:10])
    ans = ['''{% extends "changes_base.html" %}\n''','''{% block body %}\n''','<table>\n']
    for line in l:
        front = '\t<tr>\n\t\t<td>'
        words = line[1]
        if line[0] == "-":
            front = '\t<tr>\n\t\t<td class ='+'"removed">'
        elif line[0] == "+":
            front = '\t<tr>\n\t\t<td class ='+'"added">'
        elif line[0] == "+/-":
            words = calc_line(line[1])
        ans.append(str(add_line(words,front)))
    ans.append('</table>\n')
    ans.append('''{% endblock %}''')
    write_file(ans,name)

def calc_line(line):
    ans = []
    for word in line.split(" "):
        if word[0] == "+":
            word = '<p class = '+'"added">'+word[1:]+'</p>'
        elif word[0] == "-":
            word = '<p class = '+'"removed">'+word[1:]+'</p>'
        ans.append(word)
    return ' '.join(ans)

def add_line(line,front):
    end = '</td>\n\t</tr>\n'
    return front+line+end

def write_file(l,name):
    f = open(name,"w+")
    for line in l:
        f.write(str(line))
    f.close()