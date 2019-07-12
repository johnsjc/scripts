# ankigen.py
# takes an excel document with two columns of sentences and definition(s)
# where the definition(s) match the bolded part of the sentence.
# multiple definitions are separated with a | delimiter.
# and generates question and answer pairs for flashcards.
# e.g.
# [puedes coger sin más **todo lo que se te antoje**.][whatever you want/fancy]
# [las hojas del **tilo** que **se erguía** junto a la careterra.][lime tree | loomed, towered]
#
# generates the following question/answer pairs:
# puedes coger sin más **todo lo que se te antoje**. => whatever you want/fancy
# las hojas del **tilo** que se erguía junto a la careterra. => lime tree
# las hojas del tilo que **se erguía** junto a la careterra. => loomed, towered

import xlrd

book = xlrd.open_workbook("ih.xls", formatting_info=True)
sheet = book.sheet_by_index(0)

for row in range(sheet.nrows):
    content = sheet.cell_value(row, 0).strip()
    definition = sheet.cell_value(row, 1).strip()
    formatting = book.xf_list[sheet.cell_xf_index(row, 0)]

    if not content:
        continue

    segments = []
    result = []

    runlist = sheet.rich_text_runlist_map.get((row, 0))
    if not runlist:
        result = [[content, definition]]
    if runlist:

        bolds = []

        if runlist[0][0] != 0:
            text = content[:runlist[0][0]]
            is_bold = not book.font_list[runlist[0][1]].bold
            if is_bold:
                bolds.append(text.strip())
                
        for i in range(len(runlist)):
            is_bold = book.font_list[runlist[i][1]].bold

            if is_bold:
                start = runlist[i][0]
                end = runlist[i+1][0] if i != len(runlist) - 1 else None
                text = content[start:end]
                bolds.append(text.strip())       

        definitions = definition.split('|')
        question = content
        
        if len(definitions) == 1:            
            for b in bolds:
                idx = question.find(b)
                question = "{}**{}**{}".format(
                    question[:idx], b, question[idx+len(b):])
            result = [[question, definitions[0]]]

        else:
            for b, d in zip(bolds, definitions):
                idx = content.find(b)
                question = "{}**{}**{}".format(
                    content[:idx], b, content[idx+len(b):])
                result.append([question.strip(), d.strip()])
                
    for r in result:
        segments.append(r)

    for q, a in segments:
        print("{}\n{}\n".format(q, a)
