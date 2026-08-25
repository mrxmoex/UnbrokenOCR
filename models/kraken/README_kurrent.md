# HTR Model for 19th century German Kurrent script

This repository contains the practical work of my bachelor thesis. It includes:

- 4 trained models, three with kraken and one with calamari in the Models folder
- A detailed description and link to the ground truth dataset used for training
- The Line Extractor tool for extracting segmented lines from PageXML files and corresponding images
- Evaluation results and description of datasets used for testing and validating the models


## Ground Truth Data used for model training

The dataset available at https://zenodo.org/records/17252677 created and used for my Bachelorthesis comprises handwritten manuscripts in **19th-century German Kurrent**, prepared for the training of a Handwritten Text Recognition (HTR) model. It contains a total of **9,317 text lines**. The data was sourced from the following repositories:

* **Senatsprotokolle**: [https://github.com/ubtue/Ground-Truth/tree/main/Senatsprotokolle](https://github.com/ubtue/Ground-Truth/tree/main/Senatsprotokolle)
* **Digitale Schriftkunde (Bayerisches Hauptstaatsarchiv)**:
  * [1806 Reichsstadt Nürnberg, Ratsverläße](https://www.gda.bayern.de/DigitaleSchriftkunde/1806_StAN_Reichsstadt-Nuernberg-Ratsverlaesse_4433.html)
  * [1824 Maria Theresia, Privatkorrespondenz](https://www.gda.bayern.de/DigitaleSchriftkunde/1824_StAM_Von-Armansperg_47_1x.html#)
  * [1894 Heroldenamt Akten](https://www.gda.bayern.de/DigitaleSchriftkunde/1894_BayHStA_Heroldenamt-Akten_134.html)
* **Deutsches Textarchiv (DTA)**:
  * [Libelt, Kosmos-Vorlesungen](https://www.deutschestextarchiv.de/book/show/libelt_hs6623ii_1828)
  * [Hufeland, Privatbesitz 1829](https://www.deutschestextarchiv.de/book/show/hufeland_privatbesitz_1829)
  * [Erbkam, Tagebuch 1842](https://www.deutschestextarchiv.de/book/view/erbkam_tagebuch01_1842)
  * [Auerbach, Sanders 1869](https://www.deutschestextarchiv.de/book/view/auerbach_sanders_1869)
  * [Auerbach, Sanders 1880](https://www.deutschestextarchiv.de/auerbach_sanders_1880)
  * [Auerbach, Sanders II 1880](https://www.deutschestextarchiv.de/book/view/auerbach_sanders2_1880)

For more details, see the README file of each dataset in the `data/pages/datasetname` folder.

### Dataset Splits

* **Training Set**:
  * 130 lines from Auerbach
  * 2,620 lines of low-quality Senatsprotokolle
  * 4,758 lines of high-quality Senatsprotokolle
  * 171 lines from Hufeland
  * 217 lines from Erbkam
  * **Total:** 7,896 lines

* **Validation Set**: Randomly selected ~10% of lines from the entire training dataset, including:
  * 16 lines from Auerbach
  * 716 lines of high-quality Senatsprotokolle
  * 21 lines from Hufeland
  * 27 lines from Erbkam
  * **Total:** 760 lines

* **Test Set**: Randomly selected ~10% of lines from the entire training dataset, including:
  * 16 lines from Auerbach Berthold
  * 292 low-quality Senatsprotokolle
  * 130 high-quality Senatsprotokolle
  * 21 lines from Hufeland
  * 27 lines from Erbkam
  * All lines from Libelt, Reichsstadt, Maria Theresia, and Heroldenamt Akten
  * **Total:** 640 lines (designed to include scribes not seen during training)

### Line Detection

For all datasets except the Senatsprotokolle (which already contained line annotations), line detection was performed automatically using **Transkribus**, followed by manual correction. Each line was extracted with ascenders and descenders fully included in the text region, while minimizing overlap with adjacent lines.


### Line Extraction

Line extraction was performed using a Python script, available at: https://github.com/MGJamJam/htr_german_kurrent_model/tree/main/LineExtractor


### Transcription Guidelines

Transcriptions were obtained from the original sources and adapted to follow the **OCR-D Level 2 transcription guidelines** to the best of the contributor’s knowledge and ability.

**Disclaimer:** I am not a professional linguist and do not read Kurrent fluently. Although care was taken to apply OCR-D Level 2 rules consistently, transcription errors or oversights cannot be fully excluded.

### Data Structure

The dataset available at https://zenodo.org/records/17252677 is organized as follows:

- lines/
    - TestSet/
        - PNG files: Line images
        - PageXML files: Transcriptions
    - TrainingSet/
        - PNG files: Line images
        - PageXML files: Transcriptions
    - ValidationSet/
        - PNG files: Line images
        - PageXML files: Transcriptions
- pages/
    - DatasetName/
        - annotatedJpeg/: full-page images with baselines and text areas visible
        - pngAndXml/: page images with corresponding PageXML
        - README.md: dataset-specific metadata and description

### License

* **Deutsches Textarchiv data:** All content is released under **[CC BY 4.0](http://creativecommons.org/licenses/by/4.0/)**.
* **Bayerische Schriftkunde data:**
  * **Digital reproductions (images):** CC0 / Public Domain Mark, per [Staatliche Archive Bayerns terms](https://www.gda.bayern.de/footer/nutzungsbedingungen).
  * **Editorial content and transcriptions:** CC BY-NC-SA 4.0
