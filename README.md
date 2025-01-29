# A Vosk-based Chinese-English bilingual speech recognition Python Application

## 😊Introduction

**[Vosk](https://alphacephei.com/vosk/index)** is an open source **speech recognition** toolk. It focused on providing efficient and accurate speech-to-text functionality. It is based on Kaldi (another famous speech recognition toolkit), but compared to Kaldi, Vosk is more **lightweight** and easy to use, and is suitable for embedding into various applications.

This application is developed on the basis of vosk, implementing **real-time bilingual speech-to-text function**.

> All the installation and usage are demonstrated under **Win 11 Systems**.

## 🚀Installation

### Requirements

You need to prepare these stuffs in advance:

- 🐍Available Python Environments (**Python >= 3.6**)
  - **WE RECOMMEND Python 3.9!**
- 🪟Windows Operating Systems
  - **Maybe in MacOS works.** (I don't have a Macbook. 🤑)
- 🎙️Available Micro devices.

We strongly recommend you to install **[Anaconda](https://docs.anaconda.com/getting-started/) or [Miniconda](https://docs.anaconda.com/miniconda/)** to create a virtual environment to run the python code.

### Clone the project

Clone the remote repository from Git to obtain the Python source code.

```bash
git clone https://github.com/xiyuanyang-code/voice_translation.git
```

Open the folder as the current directory.

```bash
cd voice_translation
```

### Create Python environments

#### 🥳If you have installed Anaconda...

Great! Now run the following commands in the command line:

```bash
conda create -n translate python=3.9
```

This would create a new **Conda** environment named **"translate"**. You can also customize your own environment name!

After that, switch to activate the new environment to install the required packages.

```bash
conda activate translate
# or change to your own virtual environment name!
```

Then install the required packages.

```bash
pip install -r requirements.txt
```

You can also **install packages manually**:

```bash
pip install sounddevice numpy vosk
```

#### 🙂‍↕️If not?

Then go to install [Anaconda](https://docs.anaconda.com/getting-started/) first!😋

Just a joke. Anaconda is too huge for its size. You can still install these packages using:

```bash
pip install sounddevice numpy vosk
```

#### Required packages

Required packages are as follows:

1. **tkinter**: This is the standard GUI toolkit for Python, allowing developers to create graphical user interfaces easily. (Standard Library)

2. **threading**: A standard library module that provides a way to create and manage threads, enabling concurrent execution of code. (Standard Library)

3. **queue**: This standard library module provides a thread-safe FIFO implementation, useful for managing tasks between threads. (Standard Library)

4. **time**: A standard library module that provides various time-related functions, including time manipulation and formatting. (Standard Library)

5. **json**: This standard library module is used for parsing JSON data and converting Python objects to JSON format. (Standard Library)

6. **sounddevice**: A third-party library that allows for audio input and output using NumPy arrays, facilitating sound processing tasks. **(Requires manual installation)**

7. **numpy**: A widely-used third-party library for numerical computations in Python, providing support for large, multi-dimensional arrays and matrices. **(Requires manual installation)**

8. **vosk**: A third-party library for speech recognition that provides models for various languages using Kaldi's speech recognition capabilities. **(Requires manual installation)**

9. **os**: A standard library module that provides a way to interact with the operating system, including file and directory management functions. (Standard Library)

10. **platform**: This standard library module allows access to underlying platform’s identifying data, such as OS type and version. (Standard Library)

## 💓Usage

**Make sure you have passed through the `installation` section successfully.** 

### Create a folder to store results

Firstly, create a folder named **"results"** in the current directory.

- For **Bash**

```bash
mkdir results
```

- For **Powershell**

```powershell
New-Item -Path . -Name "results" -ItemType Directory
```

### Download and Unzip the vosk-model

For the core part of the translation model, we use **Vosk-model**, which is both lightweight and powerful.

For **Bash** and **Powershell** both:

```bash
# Install the Chinese packages
wget https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip

# Install the English packages
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
```

> Or you can just download the zip file online and drag the zip-file into the current folder.

Then extract the downloaded ZIP file:

```bash
unzip vosk-model-cn-0.22.zip

unzip vosk-model-en-us-0.22.zip
```

(Optional) After the unzip process, you can delete the `zip` file, it's too huge!

After all these requirements, your current directory should be like this:

```bash
.
├── LICENSE
├── README.md
├── main
│   └── main.py
├── requirements.txt
├── results
├── vosk-model-cn-0.22
│   ├── README
│   ├── am
│   │   └── final.mdl
│   ├── conf
│   │   ├── mfcc.conf
│   │   └── model.conf
│   ├── graph
│   │   ├── HCLG.fst
│   │   ├── phones
│   │   │   └── word_boundary.int
│   │   └── words.txt
│   ├── ivector
│   │   ├── final.dubm
│   │   ├── final.ie
│   │   ├── final.mat
│   │   ├── global_cmvn.stats
│   │   ├── online_cmvn.conf
│   │   └── splice.conf
│   ├── rescore
│   │   ├── G.carpa
│   │   └── G.fst
│   └── rnnlm
│       ├── feat_embedding.final.mat
│       ├── features.txt
│       ├── final.raw
│       ├── oov.txt
│       ├── special_symbol_opts.conf
│       ├── special_symbol_opts.txt
│       └── word_feats.txt
└── vosk-model-en-us-0.22
    ├── README
    ├── am
    │   ├── final.mdl
    │   └── tree
    ├── conf
    │   ├── ivector.conf
    │   ├── mfcc.conf
    │   └── model.conf
    ├── graph
    │   ├── HCLG.fst
    │   ├── disambig_tid.int
    │   ├── num_pdfs
    │   ├── phones
    │   │   ├── align_lexicon.int
    │   │   ├── align_lexicon.txt
    │   │   ├── disambig.int
    │   │   ├── disambig.txt
    │   │   ├── optional_silence.csl
    │   │   ├── optional_silence.int
    │   │   ├── optional_silence.txt
    │   │   ├── silence.csl
    │   │   ├── word_boundary.int
    │   │   └── word_boundary.txt
    │   ├── phones.txt
    │   └── words.txt
    ├── ivector
    │   ├── final.dubm
    │   ├── final.ie
    │   ├── final.mat
    │   ├── global_cmvn.stats
    │   ├── online_cmvn.conf
    │   └── splice.conf
    ├── rescore
    │   ├── G.carpa
    │   └── G.fst
    └── rnnlm
        ├── feat_embedding.final.mat
        ├── final.raw
        ├── special_symbol_opts.conf
        ├── special_symbol_opts.txt
        └── word_feats.txt
```

Check your current directory or simply using **tree** command for WSL.

### Run Python code

You should run the python code using the conda environment you have created **accordingly**!

Switch to the `main` folder and run `main.py`:

```bash
cd main
python main.py
```

You will probably see the following pop-up window as follows.

![Demo 1](https://ooo.0x0.ooo/2025/01/29/OGRa7L.png)

We have three modes to choose from, including "Chinese Mode", "English Mode" and "Bilingual Mode".

Choose the mode you like and then the translation will begin!

> **Warning:** It may take approximately 10~20 seconds for the code to load the **Vosk-model**, for the Bilingual one, it may even take longer.😭Sorry about that.

After the long wait, you will see a green-colored information said "Model loaded successfully!" That means you can begin your words now!

- The results of the conversion will be displayed in real-time in the terminal.
- To end the conversion process, you can **right-click your mouse**, which will terminate the program.
- For the bilingual model, you can click on `Select Language` in the middle to switch languages.
  ![demo 2](https://ooo.0x0.ooo/2025/01/29/OGRqXX.png)

### Obtain transcriptions

You can get the transcriptions in the `results` folder, including the `.txt` file and `.md` file.

## 🤖Discussion

### Advantages

- If you want to get the voice transcriptions for free instead of paying for professional apps. This one is suitable for you!
- You can modify the source code to customize your own GUI interface or implement some advanced functions on your own!
  - I think it's a great chance to learn Python, isn't it?

### ~~Disadvantages~~ FUTURE OUTLOOK

- WE WILL create a more lightweight version.
- WE WILL implement the speech-to-text conversion for mixed input of Chinese and English.
- WE WILL build a more aesthetically pleasing GUI.
- WE WILL optimize the transcriptions, including automatically add punctuation, segment text, and organize it into a coherent article.

## 👍Advertisement

My personal Blog: [Xiyuan Yang's Blog](https://xiyuanyang-code.github.io/)