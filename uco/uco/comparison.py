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
    write_html_files(old_list,new_list)
    d = Differ()
    result = list(d.compare(old_list,new_list))
    for i in range(0,len(result)):
        result[i]=result[i].split()
    return result

def write_html_files(old,new):
    ans = ['''{% extends "alt_display.html" %}\n''','''{% block changes %}\n''','<table class="box" id="old">\n']
    for line in old:
        front = '\t<tr>\n\t\t<td>'
        words = line
        # skip if change only involves a blank line
        if len(words) == 0:
            continue
        else:
            ans.append(str(add_line(words,front,0,"#")))
    ans.append('</table>\n')

    ans.append('<table class="box" id="new">\n')
    for line in new:
        front = '\t<tr>\n\t\t<td>'
        words = line
        # skip if change only involves a blank line
        if len(words) == 0:
            continue
        else:
            ans.append(str(add_line(words,front,0,"#")))
    ans.append('</table>\n')
    ans.append('''{% endblock %}''')
    write_file(ans,"uco/uco/templates/split_changes.html")

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
    dividing_point = 0.75
    i=-1
    while i < len(out)-2:
        i+=1
        line = out[i]
        next = out[i+1]
        s = SequenceMatcher(None, ''.join(line[1]), ''.join(next[1]))
        # calculate similarity score of two lines
        ratio = s.ratio()
        # don't do anything if lines are different
        if ratio < dividing_point:
            ans.append(line)
        # if lines are reasonably similar assume they are the same line that's been changed
        else:
            new_line = ["+/-", word_by_word_changes(line[1],next[1])]
            ans.append(new_line)
            i +=1
    return ans

# splits the output into ["+/-/#", "text"]
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

# takes in a line of old text and new text
# calculates what's been removed and added
# returns a string with + in front of additions and - in front of deletions
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
    ans = ['''{% extends "changes_base.html" %}\n''','''{% block body %}\n''','<table>\n']
    section_id = 1
    for line in l:
        front = '\t<tr>\n\t\t<td>'
        words = line[1]
        # skip if change only involves a blank line
        if len(words) == 0:
            continue
        # if a line that's been removed
        if line[0] == "-":
            # front = '\t<tr>\n\t\t<td><p class="removed">'
            ans.append(str(add_line(words,front,section_id,"-")))
        # if a line that's been added
        elif line[0] == "+":
            # front = '\t<tr>\n\t\t<td><p class="added">'
            ans.append(str(add_line(words,front,section_id,"+")))
        # if a line that's been changed
        elif line[0] == "+/-":
            words = calc_line(line[1])
            ans.append(str(add_line(words,front,section_id,"+/-")))
        else:
            ans.append(str(add_line(words,front,section_id,"#")))
        section_id+=1
    ans.append('</table>\n')
    ans.append('''{% endblock %}''')
    write_file(ans,name)

# write the html line if there are additions and deletions in a line
def calc_line(line):
    ans = []
    # add a <p> for each word that's been added or deleted
    for word in line.split(" "):
        if word[0] == "+":
            word = '<div class = '+'"added">'+word[1:]+'</div>'
        elif word[0] == "-":
            word = '<div class = '+'"removed">'+word[1:]+'</div>'
        ans.append(word)
    return ' '.join(ans)

def add_line(line,front,section_id,category):
    if category == "+":
        front = front+'<p data-section-id = "%s" class="commentable-section added">' % section_id
    elif category == "-":
        front = front+'<p data-section-id = "%s" class="commentable-section removed">' % section_id
    else:
        front = front+'<p data-section-id = "%s" class="commentable-section">' % section_id
    end = '</p></td>\n\t</tr>\n'
    return front+line+end

def write_file(l,name):
    f = open(name,"w+")
    for line in l:
        f.write(str(line))
    f.close()