# Transformation of the ALTO-XML files 

### Introduction

In this phase, the OCR output (text + typographical information) is manually corrected (according to the indications made by [this script](https://github.com/ljpetkovic/CatMan_ExhibCat_dataset/tree/main/scripts/eval_OCR)), and then exported from Transkribus into the ALTO-XML format (at the word level), in order to be further processed and injected into the GROBID-dictionaries. However, two problems have been noticed which prevent this injection: <br>

* the ALTO-XML structure of the exported files did not correspond to the structure which could be accepted by the GROBID-dictionaries;<br>
* the markup is stored in attribute values, and such a design is fundamentally flawed (e.g. `<String CONTENT="&lt;b&gt;Août"`, where `&lt;b&gt;` is equivalent to the tag `<b>` indicating the word in bold).<br>

The original (flawed) structure of a sample ALTO-XML file (sample below):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<alto xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns="http://www.loc.gov/standards/alto/ns-v2#"
      xmlns:page="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
      xsi:schemaLocation="http://www.loc.gov/standards/alto/ns-v2# http://www.loc.gov/standards/alto/alto.xsd">
   <Description>
      <MeasurementUnit>pixel</MeasurementUnit>
      <OCRProcessing ID="IdOcr">
         <ocrProcessingStep>
            <processingDateTime>2020-05-17T21:22:02.419+02:00</processingDateTime>
            <processingSoftware>
               <softwareCreator>READ COOP</softwareCreator>
               <softwareName>Transkribus</softwareName>
            </processingSoftware>
         </ocrProcessingStep>
      </OCRProcessing>
   </Description> -------------------- the <Styles> tag with its fonts needs to be placed below 
   <Tags/>
   <Layout>
      <Page ID="Page1" PHYSICAL_IMG_NR="1" HEIGHT="2885" WIDTH="1858">    
         <TopMargin HEIGHT="5" WIDTH="1858" VPOS="0" HPOS="0"/>  ------------ unnecessary
         <LeftMargin HEIGHT="2614" WIDTH="0" VPOS="5" HPOS="0"/> ------------ unnecessary
         <RightMargin HEIGHT="2614" WIDTH="179" VPOS="5" HPOS="1679"/> 	----- unnecessary, convert into pixels
         <BottomMargin HEIGHT="266" WIDTH="1858" VPOS="2619" HPOS="0"/> ----- unnecessary, convert into pixels
         <PrintSpace HEIGHT="2614" WIDTH="1679" VPOS="5" HPOS="0">
            <TextBlock ID="r2" HEIGHT="241" WIDTH="34" VPOS="2334" HPOS="249">
               <Shape> 	---------------------------------------------------------- unnecessary
                  <Polygon POINTS="249,2334 249,2575 283,2575 283,2334"/> -------- unnecessary
               </Shape>
              ...
               <TextLine ID="r3l1"
                         BASELINE="175"
                         HEIGHT="65"
                         WIDTH="300"
                         VPOS="110"
                         HPOS="1319">
                  <String HEIGHT="65" ------ String needs the incremental ID and STYLEREFS attributes (the latter with the value FONT{0,1,2})
                          WIDTH="236"
                          VPOS="110"
                          HPOS="1298"
                          CONTENT="&lt;b&gt;Août"/>
                  <SP HEIGHT="65" WIDTH="21" VPOS="110" HPOS="1533"/>
                  <String HEIGHT="65"
                          WIDTH="171"
                          VPOS="110"
                          HPOS="1448"
                          CONTENT="1874.."/>
               </TextLine>
...
```

<!-- The core idea of redesigning the ALTO-XML files in order to be injected into the GROBID-dictionaries is available [here](https://github.com/ljpetkovic/OCR-cat/blob/GROBID_eval/ALTO_XML_trans/ALTO-transformation.md).<br>-->

<!-- This is the updated version of the code, which includes the transformation of **all the files** in all the catalogue folders.<br> -->

### Task

Correcting automatically the malformed ALTO-XML exported from Transkribus at the word level (according to the suggestions for the corrections indicated by [this script](https://github.com/ljpetkovic/CatMan_ExhibCat_dataset/tree/main/scripts/eval_OCR)), and transforming them into the ALTO-XML files which could be accepted by the GROBID dictionaries.

### Preliminaries

If you want to use the virtual environment, you will need to have **Python 3** and **pip/pip3** installed. <br>

To create your Python virtual environment (optional):

1. Install the `virtualenv` PyPI library: <br>

   `pip3 install virtualenv` <br>

2. Move to the project directory:<br>

   `cd path/to/my/project/directory`

3. Set up your Python virtual environment in the project directory (this will create the `env` sub-directory):<br>

   `virtualenv -p python3 env`<br> (you can use any name instead of `env`)

4. Activate the environment:<br>

   `source env/bin/activate`<br>

5. Install libraries and dependencies:

   `pip3 install -r requirements.txt`<br>

   <!--In order to install the `imagemagick` library on macOS/Linux, it is necessary to install [Homebrew](https://brew.sh) (The Missing Package Manager for macOS/Linux).<br>-->
   
   <!--After you installed `homebrew`, type:-->
   
   <!--`brew bundle`-->
   
   <!--This command installs the `imagemagick` library on macOS/Linux (indicated in the `Brewfile`), and it is mandatory for the mm10 to pixels conversion.<br>-->

*NB*:

* To deactivate the virtual environment:<br>

  `deactivate`

* Allow user to read and execute scripts:<br>

  `chmod 755 myScript.sh`

### Features of the `corr_trans_ALTO.{py,sh}` scripts

* Iterative transformation of all `.xml` files in all the `doc` catalogues (the transformed files obtain the `_trans.xml` extension);
* Removing escape sequences of the markup tags from the attribute values (e.g. `BELLE` instead of `&lt;b&gt;BELLE`)

* Adding the `<Styles>` tag content:

```xml
<Styles>
     <TextStyle ID="FONT0" FONTSTYLE=""/>
     <TextStyle ID="FONT1" FONTSTYLE="bold"/>
     <TextStyle ID="FONT2" FONTSTYLE="italics"/>
</Styles>
```

- <!-- no need to register the namespace (unlike with the previously used `etree` command `ET.register_namespace`);-->
- <!--preserving the `xmlns:page="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"` namespace from the original ALTO-XML files;-->
- Displaying the `-h` (help) description text of the Bash script: `./corr_trans_ALTO.sh -h`

```
            ########## Help ##########
Flag description:
	-a 	Transform all files in all catalogue folders, whether they have already been transformed or not;
		Intended to handle the situations if somebody incorrectly modifies the transformed file, so we want to make sure that all the files are transformed in a regular way defined by the .py and .sh scripts:

	-d 	When we add new (non-transformed) files, we can transform only those files, and ignore those already transformed;
		Run the code, followed by the -d flag and the folder name containing those files;
		For the already transformed files, the script throws the error that these files have already been transformed.

	-h 	Get help/text description of the flags.

For the detailed explanation of the script, go to https://github.com/ljpetkovic/CatMan_ExhibCat_dataset/tree/main/scripts/trans_ALTO.
```


### Running the scripts

#### Demo

When in `trans_ALTO` folder, in order to transform only one file, run:<br>

```bash
python3 corr_trans_alto.py test.xml 
```

<!--The above command runs the Python transforming script `corr_XML_dpi_test.py` on the input file `../test/1871_08_RDA_N028-1.xml`, while performing the mm10 to pixels conversion using the `imagemagick` library with the command `$(convert ../test/1871_08_RDA_N028-1.jpg -format "%x" info:)` (the `"%x"` indicates the horizontal resolution).-->

If you uncomment

```
# base=os.path.basename(fichier) # pour récupérer le nom du fichier sans extension
# print('Processing ', os.path.splitext(base)[0], '.xml...\nDone.')
```

The output of the terminal would be:<br>

```bash
Processing 1871_08_RDA_N028-1.xml...
Done
```

Output of the transformed file `test.xml_trans`:<br>

```xml
<?xml version='1.0' encoding='UTF8'?>
<alto xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.loc.gov/standards/alto/ns-v2#" xmlns:page="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15" xsi:schemaLocation="http://www.loc.gov/standards/alto/ns-v2# http://www.loc.gov/standards/alto/alto.xsd">
  <Description>
    <MeasurementUnit>pixel</MeasurementUnit>
    <sourceImageInformation>
         <fileName>test.xml</fileName>
      </sourceImageInformation>
    <OCRProcessing ID="IdOcr">
      <ocrProcessingStep>
        <processingDateTime>2020-11-06T13:44:37.698+01:00</processingDateTime>
        <processingSoftware>
               <softwareCreator>CONTRIBUTORS</softwareCreator>
               <softwareName>pdfalto</softwareName>
               <softwareVersion>0.1</softwareVersion>
            </processingSoftware>
      </ocrProcessingStep>
    </OCRProcessing>
  </Description>
  <Styles>
     <TextStyle ID="FONT0" FONTSTYLE=""/>
     <TextStyle ID="FONT1" FONTSTYLE="bold"/>
     <TextStyle ID="FONT2" FONTSTYLE="italics"/>
</Styles>
  <Tags/>
  <Layout>
    <Page ID="Page1" PHYSICAL_IMG_NR="1" HEIGHT="2205" WIDTH="1081">
      <PrintSpace HEIGHT="2146" WIDTH="1032" VPOS="40" HPOS="36">
        <TextBlock ID="r_1_1" HEIGHT="73" WIDTH="934" VPOS="46" HPOS="83">
          <TextLine ID="tl_1" BASELINE="143" HEIGHT="119" WIDTH="945" VPOS="24" HPOS="78">
            <String HEIGHT="119" WIDTH="630" VPOS="24" HPOS="39" CONTENT="LIBRAIRIE" ID="tl_1_1" STYLEREFS="FONT1"/>
            <SP HEIGHT="119" WIDTH="39" VPOS="24" HPOS="669"/>
            <String HEIGHT="119" WIDTH="512" VPOS="24" HPOS="511" CONTENT="ANCIENNE" ID="tl_1_2" STYLEREFS="FONT1"/>
          </TextLine>
        </TextBlock>
        <TextBlock ID="r_1_2" HEIGHT="126" WIDTH="618" VPOS="155" HPOS="273">
          <TextLine ID="tl_2" BASELINE="212" HEIGHT="70" WIDTH="351" VPOS="142" HPOS="370">
            <String HEIGHT="70" WIDTH="150" VPOS="142" HPOS="353" CONTENT="ET" ID="tl_2_1" STYLEREFS="FONT1"/>
            <SP HEIGHT="70" WIDTH="17" VPOS="142" HPOS="504"/>
            <String HEIGHT="70" WIDTH="284" VPOS="142" HPOS="437" CONTENT="AUTOGRAPHES" ID="tl_2_2" STYLEREFS="FONT1"/>
          </TextLine>
          <TextLine ID="tl_3" BASELINE="298" HEIGHT="79" WIDTH="477" VPOS="219" HPOS="311">
            <String HEIGHT="79" WIDTH="226" VPOS="219" HPOS="286" CONTENT="DE" ID="tl_3_1" STYLEREFS="FONT1"/>
            <SP HEIGHT="79" WIDTH="25" VPOS="219" HPOS="512"/>
            <String HEIGHT="79" WIDTH="377" VPOS="219" HPOS="411" CONTENT="CHARAYAY," ID="tl_3_2" STYLEREFS="FONT1"/>
          </TextLine>
        </TextBlock>
        ...
        <TextBlock ID="r_3_2" HEIGHT="148" WIDTH="1005" VPOS="769" HPOS="51">
          <TextLine ID="tl_12" BASELINE="835" HEIGHT="86" WIDTH="991" VPOS="749" HPOS="70">
            <String HEIGHT="86" WIDTH="73" VPOS="749" HPOS="55" CONTENT="." ID="tl_12_1" STYLEREFS="FONT0"/>
            <SP HEIGHT="86" WIDTH="15" VPOS="749" HPOS="128"/>
            <String HEIGHT="86" WIDTH="175" VPOS="749" HPOS="85" CONTENT="ANTIGONE" ID="tl_12_2" STYLEREFS="FONT0"/>
            <SP HEIGHT="86" WIDTH="15" VPOS="749" HPOS="259"/>
            <String HEIGHT="86" WIDTH="102" VPOS="749" HPOS="216" CONTENT="par" ID="tl_12_3" STYLEREFS="FONT0"/>
            <SP HEIGHT="86" WIDTH="15" VPOS="749" HPOS="318"/>
            <String HEIGHT="86" WIDTH="291" VPOS="749" HPOS="274" CONTENT="Pitdnéns," ID="tl_12_4" STYLEREFS="FONT2"/>
            <SP HEIGHT="86" WIDTH="15" VPOS="749" HPOS="565"/>
            <String HEIGHT="86" WIDTH="87" VPOS="749" HPOS="522" CONTENT="2é" ID="tl_12_5" STYLEREFS="FONT0"/>
            <SP HEIGHT="86" WIDTH="15" VPOS="749" HPOS="609"/>
            <String HEIGHT="86" WIDTH="160" VPOS="749" HPOS="566" CONTENT="édition" ID="tl_12_6" STYLEREFS="FONT0"/>
            <SP HEIGHT="86" WIDTH="15" VPOS="749" HPOS="726"/>
            <String HEIGHT="86" WIDTH="131" VPOS="749" HPOS="682" CONTENT="oinée" ID="tl_12_7" STYLEREFS="FONT0"/>
            <SP HEIGHT="86" WIDTH="15" VPOS="749" HPOS="813"/>
            <String HEIGHT="86" WIDTH="102" VPOS="749" HPOS="770" CONTENT="dlé" ID="tl_12_8" STYLEREFS="FONT0"/>
            <SP HEIGHT="86" WIDTH="15" VPOS="749" HPOS="872"/>
            <String HEIGHT="86" WIDTH="102" VPOS="749" HPOS="828" CONTENT="six" ID="tl_12_9" STYLEREFS="FONT0"/>
            <SP HEIGHT="86" WIDTH="15" VPOS="749" HPOS="930"/>
            <String HEIGHT="86" WIDTH="146" VPOS="749" HPOS="886" CONTENT="jolies" ID="tl_12_10" STYLEREFS="FONT0"/>
            <SP HEIGHT="86" WIDTH="15" VPOS="749" HPOS="1032"/>
            <String HEIGHT="86" WIDTH="87" VPOS="749" HPOS="974" CONTENT="gra" SUBS_TYPE="HypPart1" SUBS_CONTENT="graulm«" ID="tl_12_11" STYLEREFS="FONT0"/>
            <HYP CONTENT="-"/>
          </TextLine>
          ...
```

#### Full version

From the same folder, run either:

`./corr_trans_ALTO.sh` &mdash; transforms all files in all catalogue folders, if they have not been transformed before;

`./corr_trans_ALTO.sh -a` &mdash; transforms all files in all catalogue folders, whether they have already been transformed or not;

`./corr_trans_ALTO.sh -d someCatalogue` &mdash; transforms all files in one specific catalogue (not previously transformed);

Sample terminal output:<br>

```bash
Processing /Volumes/LaCie/Toolkit/Mirror/CatMan_dataset/scripts/trans_ALTO/doc/LAC/1845_11_LAC_N01
Processing /Volumes/LaCie/Toolkit/Mirror/CatMan_dataset/scripts/trans_ALTO/doc/LAC/1845_11_LAC_N01/1845_11_LAC_N01_1.xml
...
Processing /Volumes/LaCie/Toolkit/Mirror/CatMan_dataset/scripts/trans_ALTO/doc/LAC/1846_01_LAC_N03
Processing /Volumes/LaCie/Toolkit/Mirror/CatMan_dataset/scripts/trans_ALTO/doc/LAC/1846_01_LAC_N03/1846_01_LAC_N03_1.xml
...
```

<!--Output of the transformed file `1845_05_14_CHA-0008.xml_trans.xml`:<br>-->