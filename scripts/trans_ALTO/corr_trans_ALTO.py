import lxml.etree as etree
import sys, argparse
import re, os, fileinput, subprocess


########### Getting the file path #######################

# fichier = sys.argv[1]
fichier = 'test.xml'
# base=os.path.basename(fichier) # getting the file name without the extension
# print('Processing ', os.path.splitext(base)[0], '.xml...\nDone.')

########### Getting the dpi #######################

#dpi = int(sys.argv[2]) # 254

########### Getting the file name #######################

pattern = r'[^/]+$'
p = re.compile(pattern)
result = p.search(fichier)
fileName = result.group()

##################################################################



parser_XML = etree.XMLParser(remove_blank_text=True) # </Styles> - new line - <Tags/> - indentation  
tree = etree.parse(fichier,parser_XML)
root = tree.getroot()


############## Adding the namespaces and the metadata to the header ##############

 
sourceImageInformationText = """
      <sourceImageInformation>
         <fileName>{}</fileName>
      </sourceImageInformation>
""".format(fileName[:-3] + 'jpg')

processingSoftwareText = """
            <processingSoftware>
               <softwareCreator>CONTRIBUTORS</softwareCreator>
               <softwareName>pdfalto</softwareName>
               <softwareVersion>0.1</softwareVersion>
            </processingSoftware>
"""
sourceImageInformation = etree.fromstring(sourceImageInformationText)
processingSoftware = etree.fromstring(processingSoftwareText)
for processing_software in root[0][1]:
    for p in processing_software.findall('{http://www.loc.gov/standards/alto/ns-v2#}processingSoftware'):
        processing_software.remove(p)

    
root[0].insert(1, sourceImageInformation)
root[0][2][0].insert(1, processingSoftware)

#############   Removing the redundant tags from the file     ################

tag_a_supprimer = ['{http://www.loc.gov/standards/alto/ns-v2#}TopMargin',
                   '{http://www.loc.gov/standards/alto/ns-v2#}LeftMargin',
                   '{http://www.loc.gov/standards/alto/ns-v2#}RightMargin',
                   '{http://www.loc.gov/standards/alto/ns-v2#}BottomMargin']

for page in root[2].iter('{http://www.loc.gov/standards/alto/ns-v2#}Page'):
    for tag in tag_a_supprimer:
        for elem in page.findall(tag):
            page.remove(elem)
    for printspace in page.findall('{http://www.loc.gov/standards/alto/ns-v2#}PrintSpace'):
        for textblock in printspace.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextBlock'):
            for shape in textblock.findall('{http://www.loc.gov/standards/alto/ns-v2#}Shape'):
                textblock.remove(shape)

    ### Handling the weird <ComposedBlock> occurrences and removing the redundant tags inside them (cf. Table in Layout in Transkribus)
                
        for composed_block in printspace.findall('{http://www.loc.gov/standards/alto/ns-v2#}ComposedBlock'):
            for textblock in composed_block.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextBlock'):
                for shape in textblock.findall('{http://www.loc.gov/standards/alto/ns-v2#}Shape'):
                    textblock.remove(shape)

############    Adding the <Styles> tag with its fonts to the header     ##########

stylesText = """
<Styles>
    <TextStyle  ID="FONT0"
                FONTFAMILY="unknown"
                FONTSIZE="unknown"
                FONTSTYLE="normal"/>
     <TextStyle ID="FONT1"
                FONTFAMILY="unknown"
                FONTSIZE="unknown"
                FONTSTYLE="bold"/>
     <TextStyle ID="FONT2"
                FONTFAMILY="unknown"
                FONTSIZE="unknown"
                FONTSTYLE="italics"/>
</Styles>
"""

styles = etree.fromstring(stylesText)
root.insert(1, styles)


#######  Getting and incrementally creating the <String> elements' ID based on the <TextLine> elements' ID #########

for page in root[3].iter('{http://www.loc.gov/standards/alto/ns-v2#}Page'):
    for printspace in page.findall('{http://www.loc.gov/standards/alto/ns-v2#}PrintSpace'):
        for textblock in printspace.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextBlock'):
            id_tex_block = textblock.attrib['ID']
            for textline in textblock.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextLine'):
                id_textline = textline.attrib['ID']
                for i, string in enumerate(textline.findall('{http://www.loc.gov/standards/alto/ns-v2#}String'),
                                           start=1):
                    string.set('ID', id_textline + "_{}".format(str(i)))

        ### Again, handling the weird <ComposedBlock> occurrences (cf. Table in Layout in Transkribus)

        for composed_block in printspace.findall('{http://www.loc.gov/standards/alto/ns-v2#}ComposedBlock'):
            id_comp_block = composed_block.attrib['ID']
            for textblock in composed_block.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextBlock'):
                id_tex_block = textblock.attrib['ID']
                for textline in textblock.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextLine'):
                    id_textline = textline.attrib['ID']
                    for i, string in enumerate(textline.findall('{http://www.loc.gov/standards/alto/ns-v2#}String'),
                                               start=1):
                        string.set('ID', id_textline + "_{}".format(str(i)))

                    

####### Correcting the full tags ##########
patt_b_open = r'([ <](([< ])*b([ >])*)+[>])|([<](([< ])*b([ >])*)+[ >])|(^(([< ])*b([ >])*)+[>])|[ <b>]*<[ <b>]*b([ <b>]*>[ <b>]*)*|(?<=[(b>)])b>'
patt_i_open = r'([ <](([< ])*i([ >])*)+[>])|([<](([< ])*i([ >])*)+[ >])|(^(([< ])*i([ >])*)+[>])|[ <i>]*<[ <i>]*i([ <i>]*>[ <i>]*)*|(?<=[(i>)])i>'
patt_b_closed = r'(([<]*[ ]*[\/][ ]*b([ >])*)+[ >.,;])|(([<]*[ ]*[\/][ ]*b([ >])*)+$)|[ <b>]*<[ <b>]*[\/]b([ <b>]*>[ <b>]*)*|(?<=[(b>)])\/b>'
patt_i_closed = r'(([<]*[ ]*[\/][ ]*i([ >])*)+[ >.,;])|(([<]*[ ]*[\/][ ]*i([ >])*)+$)|[ <i>]*<[ <i>]*[\/]i([ <i>]*>[ <i>]*)*|(?<=[(i>)])\/i>'
pattern_regex_gen = re.compile(r'([<]+([<]*[ ]*[/]*[bi]*[ ]*[>]*)*)|(([<]*[ ]*[/]*[bi]*[ ]*[>]*)*[>]+)')

###### Correcting the empty tags #######                
def reco_balise(string_content,span):
    a,b = span
    if r'<b>' in string_content[a:b]:
        return 'open_b'
    elif r'<i>' in string_content[a:b]:
        return 'open_i'
    elif r'</b>' in string_content[a:b]:
        return 'close_b'
    elif r'</i>' in string_content[a:b]:
        return 'close_i'
    else:
        return 'other'
        

for page in root[3].iter('{http://www.loc.gov/standards/alto/ns-v2#}Page'):
    for printspace in page.findall('{http://www.loc.gov/standards/alto/ns-v2#}PrintSpace'):
        for textblock in printspace.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextBlock'):
            for textline in textblock.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextLine'):
                count = 0
                for string in textline.findall('{http://www.loc.gov/standards/alto/ns-v2#}String'):
                    count += 1
                    # Correcting the full tags
                    if re.search(patt_b_open,string.attrib['CONTENT']): 
                        string.attrib['CONTENT'] = re.sub(patt_b_open,'<b>',string.attrib['CONTENT'])
                        #print(string.attrib['CONTENT'])
                    if re.search(patt_i_open,string.attrib['CONTENT']): 
                        string.attrib['CONTENT'] = re.sub(patt_i_open,'<i>',string.attrib['CONTENT'])
                        #print(string.attrib['CONTENT'])
                    if re.search(patt_b_closed,string.attrib['CONTENT']): 
                        string.attrib['CONTENT'] = re.sub(patt_b_closed,'</b>',string.attrib['CONTENT'])
                       #print(string.attrib['CONTENT'])
                    if re.search(patt_i_closed,string.attrib['CONTENT']): 
                        string.attrib['CONTENT'] = re.sub(patt_i_closed,'</i>',string.attrib['CONTENT'])
                        #print(string.attrib['CONTENT'])


                ###### Correcting the empty tags #######        
                count = 0
                liste_balises_ligne = []
                for string in textline.findall('{http://www.loc.gov/standards/alto/ns-v2#}String'):
                    string_content = string.attrib['CONTENT']
                    matches_balises = pattern_regex_gen.finditer(string_content) # itérator
                    for match in matches_balises:
                        span = match.span()
                        res = [count, span, reco_balise(string_content,span)]
                        liste_balises_ligne.append(res)
                    count += 1
                long_string = len(liste_balises_ligne)
                #print(liste_balises_ligne)
                for i, l in enumerate(liste_balises_ligne):
                    if l[2] == "other":
                        if i >= 1 and liste_balises_ligne[i-1][2] == 'open_b':
                            k = l[0]
                            a,b = l[1]
                            string_content = textline[2*k].attrib['CONTENT']
                            string_content_cor = string_content
                            N = len(string_content)
                            string_content_cor = string_content_cor[:-(N-a)] + '</b>' + string_content[b:]
                            textline[2*k].attrib['CONTENT'] = string_content_cor
                        elif i >= 1 and liste_balises_ligne[i-1][2] == 'open_i':
                            k = l[0]
                            a,b = l[1]
                            string_content = textline[2*k].attrib['CONTENT']
                            string_content_cor = string_content
                            N = len(string_content)
                            string_content_cor = string_content_cor[:-(N-a)] + '</i>' + string_content[b:]
                            textline[2*k].attrib['CONTENT'] = string_content_cor                   
                        elif i < long_string - 1 and liste_balises_ligne[i+1][2] == 'close_b':
                            k = l[0]
                            a,b = l[1]
                            string_content = textline[2*k].attrib['CONTENT']
                            string_content_cor = string_content
                            N = len(string_content)
                            string_content_cor = string_content_cor[:-(N-a)] + '<b>' + string_content[b:]
                            textline[2*k].attrib['CONTENT'] = string_content_cor
                        elif i < long_string - 1 and liste_balises_ligne[i+1][2] == 'close_i':
                            k = l[0]
                            a,b = l[1]
                            string_content = textline[2*k].attrib['CONTENT']
                            string_content_cor = string_content
                            N = len(string_content)
                            string_content_cor = string_content_cor[:-(N-a)] + '<i>' + string_content[b:]
                            textline[2*k].attrib['CONTENT'] = string_content_cor

            ##### <ComposedBlock>

        for composed_block in printspace.findall('{http://www.loc.gov/standards/alto/ns-v2#}ComposedBlock'):
            for textblock in composed_block.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextBlock'):
                for textline in textblock.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextLine'):
                    count = 0
                    for string in textline.findall('{http://www.loc.gov/standards/alto/ns-v2#}String'):
                        count += 1
                        # Correcting the full tags
                        if re.search(patt_b_open,string.attrib['CONTENT']): 
                            string.attrib['CONTENT'] = re.sub(patt_b_open,'<b>',string.attrib['CONTENT'])
                            #print(string.attrib['CONTENT'])
                        if re.search(patt_i_open,string.attrib['CONTENT']): 
                            string.attrib['CONTENT'] = re.sub(patt_i_open,'<i>',string.attrib['CONTENT'])
                            #print(string.attrib['CONTENT'])
                        if re.search(patt_b_closed,string.attrib['CONTENT']): 
                            string.attrib['CONTENT'] = re.sub(patt_b_closed,'</b>',string.attrib['CONTENT'])
                           #print(string.attrib['CONTENT'])
                        if re.search(patt_i_closed,string.attrib['CONTENT']): 
                            string.attrib['CONTENT'] = re.sub(patt_i_closed,'</i>',string.attrib['CONTENT'])
                            #print(string.attrib['CONTENT'])


                                            ###### Correcting the empty tags #######        
                count = 0
                liste_balises_ligne = []
                for string in textline.findall('{http://www.loc.gov/standards/alto/ns-v2#}String'):
                    string_content = string.attrib['CONTENT']
                    matches_balises = pattern_regex_gen.finditer(string_content) # itérator
                    for match in matches_balises:
                        span = match.span()
                        res = [count, span, reco_balise(string_content,span)]
                        liste_balises_ligne.append(res)
                    count += 1
                long_string = len(liste_balises_ligne)
                #print(liste_balises_ligne)
                for i, l in enumerate(liste_balises_ligne):
                    if l[2] == "other":
                        if i >= 1 and liste_balises_ligne[i-1][2] == 'open_b':
                            k = l[0]
                            a,b = l[1]
                            string_content = textline[2*k].attrib['CONTENT']
                            string_content_cor = string_content
                            N = len(string_content)
                            string_content_cor = string_content_cor[:-(N-a)] + '</b>' + string_content[b:]
                            textline[2*k].attrib['CONTENT'] = string_content_cor
                        elif i >= 1 and liste_balises_ligne[i-1][2] == 'open_i':
                            k = l[0]
                            a,b = l[1]
                            string_content = textline[2*k].attrib['CONTENT']
                            string_content_cor = string_content
                            N = len(string_content)
                            string_content_cor = string_content_cor[:-(N-a)] + '</i>' + string_content[b:]
                            textline[2*k].attrib['CONTENT'] = string_content_cor                   
                        elif i < long_string - 1 and liste_balises_ligne[i+1][2] == 'close_b':
                            k = l[0]
                            a,b = l[1]
                            string_content = textline[2*k].attrib['CONTENT']
                            string_content_cor = string_content
                            N = len(string_content)
                            string_content_cor = string_content_cor[:-(N-a)] + '<b>' + string_content[b:]
                            textline[2*k].attrib['CONTENT'] = string_content_cor
                        elif i < long_string - 1 and liste_balises_ligne[i+1][2] == 'close_i':
                            k = l[0]
                            a,b = l[1]
                            string_content = textline[2*k].attrib['CONTENT']
                            string_content_cor = string_content
                            N = len(string_content)
                            string_content_cor = string_content_cor[:-(N-a)] + '<i>' + string_content[b:]
                            textline[2*k].attrib['CONTENT'] = string_content_cor
                        


#### Applying three styles (FONT0, FONT1, FONT2) to all the <String> elements in <TextBlock> 	######

for page in root[3].iter('{http://www.loc.gov/standards/alto/ns-v2#}Page'):
    for printspace in page.findall('{http://www.loc.gov/standards/alto/ns-v2#}PrintSpace'):
        for textblock in printspace.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextBlock'):
            for textline in textblock.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextLine'):
                start_b = False
                start_i = False
                for string in textline.findall('{http://www.loc.gov/standards/alto/ns-v2#}String'):
                    string.set('STYLEREFS', 'FONT0')
                    if '<b>' in string.attrib['CONTENT']:
                        start_b = True
                        string.attrib['CONTENT'] = string.attrib['CONTENT'].replace('<b>', '')
                    elif '<i>' in string.attrib['CONTENT']:
                        start_i = True
                        string.attrib['CONTENT'] = string.attrib['CONTENT'].replace('<i>', '')
                    if start_b == True:
                        string.set('STYLEREFS', 'FONT1')
                    if start_i == True:
                        string.set('STYLEREFS', 'FONT2')
                    if '</b>' in string.attrib['CONTENT']:
                        start_b = False
                        string.attrib['CONTENT'] = string.attrib['CONTENT'].replace('</b>', '')
                    elif '</i>' in string.attrib['CONTENT']:
                        start_i = False
                        string.attrib['CONTENT'] = string.attrib['CONTENT'].replace('</i>', '')


                    #### Idem for the <ComposedBlock>	######

        for composed_block in printspace.findall('{http://www.loc.gov/standards/alto/ns-v2#}ComposedBlock'):
            for textblock in composed_block.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextBlock'):
                for textline in textblock.findall('{http://www.loc.gov/standards/alto/ns-v2#}TextLine'):
                    start_b = False
                    start_i = False
                    for string in textline.findall('{http://www.loc.gov/standards/alto/ns-v2#}String'):
                        string.set('STYLEREFS', 'FONT0')
                        if '<b>' in string.attrib['CONTENT']:
                            start_b = True
                            string.attrib['CONTENT'] = string.attrib['CONTENT'].replace('<b>', '')
                        elif '<i>' in string.attrib['CONTENT']:
                            start_i = True
                            string.attrib['CONTENT'] = string.attrib['CONTENT'].replace('<i>', '')
                        if start_b == True:
                            string.set('STYLEREFS', 'FONT1')
                        if start_i == True:
                            string.set('STYLEREFS', 'FONT2')
                        if '</b>' in string.attrib['CONTENT']:
                            start_b = False
                            string.attrib['CONTENT'] = string.attrib['CONTENT'].replace('</b>', '')
                        elif '</i>' in string.attrib['CONTENT']:
                            start_i = False
                            string.attrib['CONTENT'] = string.attrib['CONTENT'].replace('</i>', '')             

######  mm10 to pixels conversion  #######

##liste_attribut = ["HPOS", "VPOS", "HEIGHT", "WIDTH"]
##for elt in root.iter():
##    dic = elt.attrib
##    for l in liste_attribut:
##        if l in dic.keys():
##            mm10 = dic[l]
##            pixels = str(int(mm10) * dpi / 254)
##            elt.set(l, pixels)


tree.write(fichier + '_trans.xml', encoding='utf8', pretty_print=True, xml_declaration=True, method='xml')

# subprocess.call(["sed", "-i", '', 's/xsi\:schemaLocation\=\"http\:\/\/www\.loc\.gov\/standards\/alto\/ns\-v2\#\ http\:\/\/www\.loc\.gov\/standards\/alto\/alto\.xsd"/xsi\:schemaLocation\=\"http\:\/\/www\.loc\.gov\/standards\/alto\/ns\-v2\#\ alto\_v2\_schema\.xml\"/g', fichier_mod])
# for f in fichier:
    # subprocess.call(["sed", "-i", '', 's/pixel/mm10/g', f])
subprocess.call(["sed", "-i", '', 's/pixel/mm10/g', fichier])
