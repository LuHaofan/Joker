import string
import spacy
from spacy.lang.en import English
from sympy import false, true


class KeywordExtractor():
    def __init__(self, text = ""):
        self.punctuations = string.punctuation
        self.nlp = spacy.load("en_core_web_sm")
        self.stop_words = spacy.lang.en.stop_words.STOP_WORDS
        self.my_stop_words = ["example", "opportunity", "first", "existing"]
        self.text = text

    def setText(self, text):
        self.text = text

    def wordfreqAnalysis(self, tokens):
        d = {}
        for word in tokens:
            if word in d.keys():
                d[word] += 1
            else:
                d[word] = 1
        res = list(d.keys())
        res.sort(key = len, reverse=True)
        return res

    def containNumbers(self, word):
        for c in word:
            if c >= "0" and c <= "9":
                return True
        return False

    def containStopWords(self, word):
        l = word.split()
        for w in l:
            if w in self.stop_words or w in self.my_stop_words:
                return True
        return False

    def getTokens(self, text):
        doc = self.nlp(text)
        mytokens = [chunk.text for chunk in doc.noun_chunks]
        mytokens = [word.lower().strip() for word in mytokens]
        mytokens = [word for word in mytokens if word not in self.stop_words and word not in self.punctuations and not self.containNumbers(word) and not self.containStopWords(word)]
        return mytokens

    def getKeywords(self):
        tokens = self.getTokens(self.text)
        tokens = self.wordfreqAnalysis(tokens)
        return tokens

# if __name__ == "__main__":
#     s = "WiFi backscatter communication has the potential to enable battery-free sensors which can transmit data using a WiFi network. In order for WiFi backscatter systems to be practical they should be compatible with existing WiFi networks without any hardware or software modifications. Moreover, they should work with networks that use encryption. In this paper, we present WiTAG which achieves these requirements, making the implementation and deployment of WiFi backscatter communication more practical. In contrast with existing systems which utilize the physical layer for backscatter communication, we take a different approach by leveraging features of the MAC layer to communicate. WiTAG is designed to send data by selectively interfering with subframes (MPDUs) in an aggregated frame (A-MPDU). This enables standard compliant communication using modern, open or encrypted 802.11n and 802.11ac networks without requiring hardware or software modifications to any devices. We implement WiTAG using off-the-shelf components and evaluate its performance in line-of-sight and non-line-of-sight scenarios. We show that WiTAG achieves a throughput of up to 4 Kbps without impacting other devices in the network."
#     ke = KeywordExtractor(s)
#     print(ke.getKeywords())
