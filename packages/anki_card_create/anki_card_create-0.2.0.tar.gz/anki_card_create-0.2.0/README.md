# `kanki`: Create Korean Anki cards with Audios

Add Anki cards with audios (korean vocabulary) and translations simply with only one command: `kanki`.


## Features

- **Add a Single Anki Card via Command Line**: Easily add individual Anki cards directly from the command line.
- **Add a Batch of Anki Cards via Command Line**: Quickly add multiple Anki cards at once using a file input.
- **Automatically Generate Audios and Translations**: Automatically generate audio pronunciations and translations for the added Anki cards.



## Installation
### Prerequisites

- Python 3.11
- Anki with AnkiConnect plugin installed and running

    > Open Anki, go to Tools -> Add-ons -> Get Add-ons... and enter the code `2055492159` to install AnkiConnect.



### Package Setup

Set up the package using: 
```sh
pip install anki-card-create
```

## Usage

1. Ensure that Anki has been running in the background. 

2. Ensure that anki-connect has been installed. 

3. Create a single anki card using: 
    ```sh
    kanki -w 안녕하세요
    ```

4. Or, create multiple anki cards using: 
    ```sh
    kanki -f <file-with-korean-vocabularies-listed>
    ```

5. Specify the target deck name using: 
    ```sh 
    kanki -w 안녕하세요 -d korean
    ```

6. Specify the model name of the Anki card you want to create using: 
    ```sh 
    kanki -w 안녕하세요 -m Basic (裏表反転カード付き)+sentense 
    ```