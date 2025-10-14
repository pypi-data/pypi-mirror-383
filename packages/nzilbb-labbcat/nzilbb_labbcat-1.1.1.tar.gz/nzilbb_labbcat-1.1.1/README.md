# nzilbb-labbcat

[![DOI](https://zenodo.org/badge/243340359.svg)](https://zenodo.org/badge/latestdoi/243340359)

Client library for communicating with [LaBB-CAT](https://labbcat.canterbury.ac.nz/)
servers using Python.

e.g.

```python
import labbcat

# Connect to the LaBB-CAT corpus
corpus = labbcat.LabbcatView("https://labbcat.canterbury.ac.nz/demo", "demo", "demo")

# Find all tokens of a word
matches = corpus.getMatches({"orthography":"quake"})

# Get the recording of that utterance
audio = corpus.getSoundFragments(matches)

# Get Praat TextGrids for the utterances
textgrids = corpus.getFragments(
    matches, ["utterance", "word","segment"],
    "text/praat-textgrid")
```

LaBB-CAT is a web-based linguistic annotation store that stores audio or video
recordings, text transcripts, and other annotations.

Annotations of various types can be automatically generated or manually added.

LaBB-CAT servers are usually password-protected linguistic corpora, and can be
accessed manually via a web browser, or programmatically using a client library like
this one.

The current version of this library requires LaBB-CAT version 20220307.1126.

**API documentation is available at https://nzilbb.github.io/labbcat-py/**

# Basic usage

*nzilbb-labbcat* is available in the Python Package Index
[here](https://pypi.org/project/nzilbb-labbcat/)

To install the module:

```
pip install nzilbb-labbcat
```

The following example shows how to:
1. upload a transcript to LaBB-CAT,
2. wait for the automatic annotation tasks to finish,
3. extract the annotation labels, and
4. delete the transcript from LaBB-CAT.

```python
import labbcat

# Connect to the LaBB-CAT corpus
corpus = labbcat.LabbcatEdit("http://localhost:8080/labbcat", "labbcat", "labbcat")

# List the corpora on the server
corpora = corpus.getCorpusIds()

# List the transcript types
transcript_type_layer = corpus.getLayer("transcript_type")
transcript_types = transcript_type_layer["validLabels"]

# Upload a transcript
corpus_id = corpora[0]
transcript_type = next(iter(transcript_types))
taskId = corpus.newTranscript(
    "test/labbcat-py.test.txt", None, None, transcript_type, corpus_id, "test")

# wait for the annotation generation to finish
corpus.waitForTask(taskId)
corpus.releaseTask(taskId)

# get the "POS" layer annotations
annotations = corpus.getAnnotations("labbcat-py.test.txt", "pos")
labels = list(map(lambda annotation: annotation["label"], annotations))

# find all /a/ segments (phones) in the whole corpus
results = corpus.getMatches({ "segment" : "a" })

# get the start/end times of the segments
segments = corpus.getMatchAnnotations(results, "segment", offsetThreshold=50)

# get F1/F2 at the midpoint of each /a/ vowel
formantsAtMidpoint = corpus.processWithPraat(
  labbcat.praatScriptFormants(), 0.025, results, segments)

# delete tha transcript from the corpus
corpus.deleteTranscript("labbcat-py.test.txt")
```

For batch uploading and other example code, see the *examples* subdirectory.

# Developers
Create a virtual environment (once only): 

```
python3 -m venv labbcat-env
```

Before running any of the commands below: 

```
source labbcat-env/bin/activate
```

To build, test, release, and document the module, the following prerequisites are required:

 - `pip3 install twine`
 - `pip3 install pathlib`
 - `pip3 install deprecated`
 - `pip3 install setuptools`
 - `sudo apt install python3-sphinx`

## Unit tests

```
python3 -m unittest
```

...or for specific test suites:

```
python3 -m unittest test.TestLabbcatAdmin
```

... or for specific tests:

```
python3 -m unittest test.TestLabbcatEdit.test_generateLayerUtterances
```

## Documentation generation

```
cd docs
make clean
make
```

## Publishing

```
rm dist/*
python3 setup.py sdist bdist_wheel
twine check dist/*
twine upload dist/*
```
