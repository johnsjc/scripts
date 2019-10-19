# ankicloze.py
#
# Requirements:
# xlrd (Install via pip)
# input file (MUST be .XLS as .XLSX is not yet supported by xlrd)
#
# Takes an excel document with the following format and turns it into cloze cards
# that can be imported into Anki
#
# Column 1: Sentence with bolded sections (clozes)
# Column 2: Hints/definitions of the bolded sections (in order)
#
# Multiple hints are separated with a | delimeter.
#
# e.g. (bolded parts are surrounded by **)
#
# Column 1: Президе́нт США **похвали́л** Эрдогана **за согла́сие на** прекраще́ние огня́
# Column 2: praised | for agreeing to
#
# Results in a multiple cloze (that will generate 2 cards in anki, one for each cloze):
# Президе́нт США {{c1::похвали́л::praised}} Эрдогана
#  {{c2::за согла́сие на::for agreeing to}} прекраще́ние огня
#

import xlrd

book = xlrd.open_workbook("input.xls", formatting_info=True)
sheet = book.sheet_by_index(0)

def get_terms(sentence, row):
    runlist = sheet.rich_text_runlist_map.get((row, 0))
    terms = []

    if runlist[0][0] != 0:
        text = sentence[:runlist[0][0]]
        is_bold = not book.font_list[runlist[0][1]].bold
        if is_bold:
            terms.append(text.strip())

    for i in range(len(runlist)):
        is_bold = book.font_list[runlist[i][1]].bold

        if is_bold:
            start = runlist[i][0]
            end = runlist[i+1][0] if i != len(runlist) - 1 else None
            text = sentence[start:end]
            terms.append(text.strip())

    return terms

def make_cloze(sentence, terms, hints, depth=1):
    if not terms:
        return sentence
    
    term_index = sentence.find(terms[0])
    return "{0}{{{{c{1}::{2}::{3}}}}}{4}".format(
        sentence[:term_index],
        depth,
        terms[0],
        hints[0],
        make_cloze(sentence[term_index + len(terms[0]):],
                   terms[1:],
                   hints[1:],
                   depth + 1))

with open('output.txt', 'w', encoding='utf-8') as f:
    for row in range(sheet.nrows):
        sentence = sheet.cell_value(row, 0).strip()
        terms = get_terms(sentence, row)
        hints = [hint.strip() for hint in sheet.cell_value(row, 1).split('|')]

        f.write("{}\n\n".format(make_cloze(sentence, terms, hints)))
        print("Processing: {}".format(sentence))

print("\nDone. Generated {} clozes in output.txt\n".format(sheet.nrows))
