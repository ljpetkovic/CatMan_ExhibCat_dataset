# Automatic tag verification and correction

### Introduction

The current OCR model based on the manuscript sales catalogues is trained in the [Transkribus](https://transkribus.eu/Transkribus/) software and used on the _in-domain_ PDF scans from the `LAC` catalogues.<br>

This system takes into account the typographical information (represented by the mark-up tags `<b>`, `</b>`, for the bold text; and `<i>`, and `</i>` tags for the italicised text).

### Evaluation

The evaluation of the OCR performance is carried out on the exported `.txt` files. Two methods are possible:

1. Specifying a **single** file (e.g. `test.txt`) as a value of the variable `fichier` in the `scripts/score_corr.py` script, and running the script;

2. Running the `scripts/score_corr.sh` on one/**multiple** files located in the `doc` folder. 

   

The imperfect results of the OCR performance are noted in the `test.txt` file (sample output below):

```
[...]

u« >straité de paix signé et proclamé à Nantes, ou les Vendéens ont
« rendu les armes, détail sur le fameux dîner-de <i>Charelle,</i> etc.:


57.


12-
trois pièces signées par les administrateurs, 1794, anS’II et IV,
24 pièces in-8.
46 »
ENDÉE</b>. Guerre de la Vendée et des chouans, par <i>Lequinio</i>,
an III, causes de la guerre de la Vendée, par J.-A. <i>Viat,</i> Angers,
an TII, mémoires pour servir à l’histoire de la Vendée; par le
général <i>Turreau</i>, Evreux, an III, (1re édit.), rapport sur les
évènements de la guerre de la Vendée, par <i>Momoro</i>, campagne
du général <i>Westermann</i> dans la Vendée, interrogatoire de <i>Wes¬</i>
<i>lermann,</i> sa lettre à <i>Couthon</i>, mémoire pour <i>Grignon</i>, général¬
diyisionnaire de l’armée de l’ouest, mémoire historiqué et politique
des insurrections de l’ouest; par <i>Mériage,</i> mes rêves dans mon
493
exil, ou coup d’œil politique et militaire sur la Vendée, par
RDzE</b
<i>Legros</i>. Blois, an III, 10 broch. ou vols.
géi-8
 18 »
58.
DEUX-SÈVRES. Voyage dans ce département, an HII, carte et
4834.
fig. Rapport de <i>Gallois</i> et <i>Gensonnd,</i> commissaires, fêtes
-4457
dans ce département; quinze pièces émanées des autorités de
i3it
4794 à l’an IX,toutes signées et ayant un intérêt local; <i>L. ass</i>.
du général Gillibért, commandant à Niort en l’an IV; projet de
«n« lettre sur les troubles de Châtillon, 2 pages in-fole; <i>L. a.s</i>.
 de i>Easillequ,</i>, curé constitutionnel de Châtillon, relative aux
 
 [...]
```

 

### Tasks

##### Tag verification

1. Check automatically the well-formedness of the  `<b>`, `</b>`, `<i>`, `</i>` tags, whether any open tag is closed, and if the order of the tags is correct. 

2. Indicate the problems that cannot be solved automatically, *i.e.* the examples requiring manual correction:
   *e.g.*: `<>foo</>`

3. Calculate the scores which evaluate the overall OCR performance.

### Method 

Create regex in a fairly flexible format allowing to find *a priori* all the tags' anomalies with the following rules:

We consider that we are dealing with such a tag if we have a character string containing at most only the characters: `SPACE`, `<`, `{bi}`, `/`, `>`,

and containing at least either:

*  `<{bi}`
* `{bi}>`
* `</{bi}` 
*  `/{bi}>`

in order to correct errors such as: 

* `< b>`, `< <b>`, `<b<b>`, `<<b>`, `<< b >>>`, `<b`, `<   b `, `<b `, `b>`, ` b>`, ` b >` (opening tags) etc., into `<b>` and
* `</b>`, `<</b>`, `< / b>`, `/b>`, `/ b>>>`, `/ b >`, `/ b>`, `</b`, `/b>`, `/ b` (closing tags) etc., into `</b>`;

The same applies to the malformed `<i>` `</i>` tags.

### Workflow

1. define regex patterns for the opening and closing tags;
2. find the correct tags;
3. find the incorrect tags by ignoring the correct tags;
4. find the lines not containing any tag;
5. check the number of opening/closing tags;
6. check the opening/closing tags' order;
7. correct the tags if needed;
8. indicate the cases in which manual intervention is needed;
9. output the results.


### Output description

 The programme output is in the format of three columns:

* the 1<sup>st</sup> column is the original text line;
* the 2<sup>nd</sup> is the number indicating the possible tag scenarios (cf. below);
* the 3<sup>rd</sup> could be either the error signalisation or the suggestion of the correction. 

The possible code's outputs (corresponding to the situation after the possible correction):<br><br>
**0**: line with **no tags**, no error message;<br>

For the initially **well-formed** tags:

**1**: well-formed tags, respecting the order of opening and closing tags (including the original tag well-formedness and the well-formedness resulting from the corrections by the programme), no error message;<br>
**2**: well-formed tags, there are as many opening as closing tags, but the tag order is not respected, message error `WRONG TAG ORDER`;<br>
**3**: well-formed tags, but the number of opening and closing tags is not the same, message error `MISSING TAGS`;<br>
<br>
In the case of the initially **malformed** tags, the output of the corrected line is generated instead of the message errors :<br><br>
**1**: well-corrected tags, no message error, output of the corrected line;<br>
**2**: well-formed tags, no message error, output of the corrected line;<br>
**3**: no message error, output of the corrected line;<br>
**4**: there is at least potentially one erroneous tag which could not be corrected, no message error, output of the corrected line.<br>

Sample output:

```
Processing test.txt ...
Done.

[...]

u« >straité de paix signé et proclamé à Nantes, ou les Vendéens ont                            | 4 | u« >straité de paix signé et proclamé à Nantes, ou les Vendéens ont

« rendu les armes, détail sur le fameux dîner-de <i>Charelle,</i> etc.:                        | 1 | 
                                                                                               |   | 
                                                                                               |   | 
57.                                                                                            | 0 | 
                                                                                               |   | 
                                                                                               |   | 
12-                                                                                            | 0 | 
trois pièces signées par les administrateurs, 1794, anS’II et IV,                              | 0 | 
24 pièces in-8.                                                                                | 0 | 
46 »                                                                                           | 0 | 
ENDÉE</b>. Guerre de la Vendée et des chouans, par <i>Lequinio</i>,                            | 3 |  MISSING TAGS
an III, causes de la guerre de la Vendée, par J.-A. <i>Viat,</i> Angers,                       | 1 | 
an TII, mémoires pour servir à l’histoire de la Vendée; par le                                 | 0 | 
général <i>Turreau</i>, Evreux, an III, (1re édit.), rapport sur les                           | 1 | 
évènements de la guerre de la Vendée, par <i>Momoro</i>, campagne                              | 1 | 
du général <i>Westermann</i> dans la Vendée, interrogatoire de <i>Wes¬</i>                     | 1 | 
<i>lermann,</i> sa lettre à <i>Couthon</i>, mémoire pour <i>Grignon</i>, général¬              | 1 | 
diyisionnaire de l’armée de l’ouest, mémoire historiqué et politique                           | 0 | 
des insurrections de l’ouest; par <i>Mériage,</i> mes rêves dans mon                           | 1 | 
493                                                                                            | 0 | 
exil, ou coup d’œil politique et militaire sur la Vendée, par                                  | 0 | 
RDzE</b                                                                                        | 3 | RDzE</b> 

<i>Legros</i>. Blois, an III, 10 broch. ou vols.                                               | 1 | 
géi-8                                                                                          | 0 | 
18 »                                                                                           | 0 | 
58.                                                                                            | 0 | 
DEUX-SÈVRES. Voyage dans ce département, an HII, carte et                                      | 0 | 
4834.                                                                                          | 0 | 
fig. Rapport de <i>Gallois</i> et <i>Gensonnd,</i> commissaires, fêtes                         | 1 | 
-4457                                                                                          | 0 | 
dans ce département; quinze pièces émanées des autorités de                                    | 0 | 
i3it                                                                                           | 0 | 
4794 à l’an IX,toutes signées et ayant un intérêt local; <i>L. ass</i>.                        | 1 | 
du général Gillibért, commandant à Niort en l’an IV; projet de                                 | 0 | 
«n« lettre sur les troubles de Châtillon, 2 pages in-fole; <i>L. a.s</i>.                      | 1 | 
de i>Easillequ,</i>, curé constitutionnel de Châtillon, relative aux                           | 1 |  de <i>Easillequ,</i>  curé constitutionnel de Châtillon, relative aux

[...]
```

### Statistics

`test.txt`

| Type           | Nº of occurrences | %     |
| -------------- | ----------------- | ----- |
| Correct tags   | 514               | 28.43 |
| Incorrect tags | 156               | 8.63  |

##### 

| Type                          | Nº of occurrences | %    |
| ----------------------------- | ----------------- | ---- |
| Not automatically correctable | 28                | 1.55 |
| Automatically correctable     | 128               | 7.08 |



| Type                                     | Nº of occurrences | %     |
| :--------------------------------------- | ----------------- | ----- |
| No tags                                  | 1138              | 62.94 |
| Initially without problems with the tags | 514               | 28.43 |
| Initially well-formed tags               | 28                | 1.55  |
| - Wrong order                            | 0                 | 0.00  |
| - Missing tags                           | 28                | 1.55  |
| Initially malformed tags                 | 128               | 7.08  |
| - Well-corrected tags                    | 47                | 2.60  |
| - Well-corrected tags, bad order         | 0                 | 0.00  |
| - Well-corrected tags, missing tags      | 29                | 1.60  |
| - Well-corrected tags, empty tags        | 52                | 2.88  |

### Remarks

In order to avoid matching real words starting with `b` or `i` with an accidental `<` before (for example: `<boat`, 
`<in`), the regexes `[ <b>]*<[ <b>]*b([ <b>]*>[ <b>]*)*`, that is, `[ <i>]*<[ <i>]*i([ <i>]*>[ <i>]*)*)` should be tested beforehand. <br><br>As for the cases like `</bDES` or `</iDES`, in which the `[ <b>]*[]<[ <b>]*[\/]b([ <b>]*>[ <b>]*)*` and `[ <i>]*[]<[ <i>]*[\/]i([ <i>]*>[ <i>]*)*` should be tested. <br><br>
The script includes these regexes.<br>

We are not looking for the `/` in isolation, because of the presence of possible fractions (`1/2`).

This programme is supposed to generalise well in the cases of the individual tags `<b>text</b>` and `<i>text</i>`. <br>However, it does not take into account:

* the tags which could not be restored, because there are no indication whether they contain the `b` or `i` component: `<>unknown</>tag`;
* the nested tags (e.g. `<b><i>text</i></b>`, where the sequences `<b><i>` and `</i></b>` are treated as error).

Also:   

* `<b> </> < > </b>`  -------------> `<b> </b> <b> </b>` : can be corrected, no nested tags;
* `<b> < > < > </b>` --------------> `<b> < > <b> </b>` : corrected, but the original example is ambiguous (could be either `<b> </b> <b> </b>` or `<b> <i> </i> </b>`);
* `<b> < > </ > </b>` -------------> `<b> <> </> </b>`.  

### Related tasks

* Automatic correction of the malformed tags in the ALTO-XML files, using the `corr_ALTO.{py,sh}` script (cf. [here](https://github.com/ljpetkovic/OCR-cat/tree/GROBID_eval/ALTO_XML_trans/scripts));
* Manual correction of the text and the tags not recognised properly by the OCR model;
* Adding more test data to check the generalisability of the code;