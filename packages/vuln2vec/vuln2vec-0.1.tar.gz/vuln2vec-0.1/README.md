<p align="center">
  <img src="./assets/logo.png" alt="Vuln2Vec Logo" width="300"/>
</p>

<p align="center">
  <a href="https://github.com/aissa302/vuln2vec/issues">
    <img src="https://img.shields.io/github/issues/aissa302/vuln2vec?style=for-the-badge" alt="Issues">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/aissa302/vuln2vec?style=for-the-badge" alt="License">
  </a>
</p>

# Vuln2Vec

**Vuln2Vec** is a domain-specific Word2Vec model for **cybersecurity text mining and NLP research**.  
It is trained on multiple heterogeneous sources, including:  

- [NVD](https://nvd.nist.gov/) – National Vulnerability Database  
- [CNVD](https://www.cnvd.org.cn/) – China National Vulnerability Database  
- [CNNVD](http://www.cnnvd.org.cn/) – China National Vulnerability Database  
- [VarIoT](https://variotdbs.fzi.de/) – IoT vulnerability database  
- English Wikipedia (**Security category**)  
- Computer Science–related **Stack Exchange Q&As**  

The goal is to provide **high-quality embeddings** that capture cybersecurity-specific terminology, making it easier to analyze vulnerabilities, exploits, and security-related discussions.

---

## 🚀 Features

- Preprocessing & normalization of raw text
- Tokenization with support for **multi-word expressions** (e.g., `cross_site`, `access_control`)
- Ready-to-use Word2Vec embeddings for cybersecurity research

---

## 🔧 Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/aissa302/vuln2vec.git
cd vuln2vec
pip install -r requirements.txt
```

## Tokenize into valid tokens

```python
from preprocessor import CBSPreprocessor

preprocessor = CBSPreprocessor('CBKywords_mapping.json')
valid_tokens = preprocessor.tokenize(
    "Amasty Blog is an extension of a website page of Amasty.AMASTY BLOG Pro 2.10.3 and 2.10.4 plug-in exist in cross-site scripting vulnerabilities. The attacker can use vulnerabilities to inject cross-site code to initiate XSS attacks."
)

print(valid_tokens)
# ['amasty','blog','is','an','extension','of', website','page','of','amasty','amasty',
#'blog','pro', '10', 'and', '10', 'plug_in','exist','in', 'cross_site_scripting', 
#'vulnerabilities','the','attacker','can','use','vulnerabilities',
#'to','inject','cross_site','code','to','initiate','xss','attacks']
```

## Loading the model

```python
from gensim.models.keyedvectors import KeyedVectors
v2v = KeyedVectors.load_word2vec_format("vuln2vec.bin", binary=True)
```

## Quering the model

```python
v2v.most_similar('sql_injection', topn=5)
#[('sqli', 0.6173917055130005), ('xss', 0.5865175127983093), ('injection', 0.5430627465248108), ('forwhat', 0.5152729153633118), ('blind', 0.5120295286178589)]
```

## Citation

```bash  g
@article{yahya2025improving,
  title={Improving critical infrastructure security through hybrid embeddings for vulnerability classification},
  author={Yahya, Aissa Ben and El Akhal, Hicham and El Alaoui, Abdelbaki El Belrhiti},
  journal={Journal of Information Security and Applications},
  volume={93},
  pages={104185},
  year={2025},
  publisher={Elsevier}
}
```
