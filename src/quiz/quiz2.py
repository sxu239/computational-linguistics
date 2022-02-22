# ========================================================================
# Copyright 2022 Emory University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========================================================================
import json
from typing import Dict, Any, List, Tuple

from collections import Counter

import math
import requests

def term_frequencies(fables) -> Dict[str, Counter]:
    def key(t): return t[t.rfind('&') + 1:]

    return {key(fable['source']): Counter(fable['tokens'].split()) for fable in fables}


def document_frequencies(fables) -> Dict[str, int]:
    dfs = Counter()
    for fable in fables:
        dfs.update(set(fable['tokens'].split()))
    return dfs


def tf_idfs(fables) -> Dict[str, Dict[str, int]]:
    tfs = term_frequencies(fables)
    dfs = document_frequencies(fables)
    out = dict()
    D = len(tfs)

    for dkey, term_counts in tfs.items():
        out[dkey] = {t: tf * math.log(D / dfs[t]) for t, tf in term_counts.items()}

    return out


def euclidean(x1: Dict[str, float], x2: Dict[str, float]) -> float:
    t = sum(((s1 - x2.get(term, 0)) ** 2 for term, s1 in x1.items()))
    t += sum((s2 ** 2 for term, s2 in x2.items() if term not in x1))
    return t

def most_similar(Y: Dict[str, Dict[str, float]], x: Dict[str, float]) -> str:
    m, t = -1, None
    for title, y in Y.items():
        d = cosine(x, y)
        if m < 0 or d > m:
            m, t = d, title
    return t

def cosine(x1: Dict[str, float], x21: Dict[str, float]) -> float:
    # TODO: to be updated: not necessairly better than euclidean
    t = 0
    for term, s1 in x1.items():
        t = t + s1 * x21.get(term,0)
    b1 = 0
    b2 = 0
    for term, s1 in x1.items():
        b1 = b1 + s1**2
    b1 = math.sqrt(b1)
    for term, s2 in x21.items():
        b2 = b2 + s2**2
    b2 = math.sqrt(b2)
    r = t/(b1*b2)
    return r

def vectorize(documents: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    # Feel free to update this function
    new_dict = tf_idfs(documents)
    return new_dict

    '''
    # try wftd
    for i in new_dict:
        for j in new_dict[i]:
            if new_dict[i][j]>0:
                new_dict[i][j] = 1 + math.log(new_dict[i][j])
            else:
                new_dict[i][j] = 0
    '''

    # try nftd
    alpha = 0.5
    for i in new_dict:
        # find max first 
        max = 0 
        for j in new_dict[i]:
            if new_dict[i][j]>max:
                max = new_dict[i][j]
        
        for k in new_dict[i]:
            new_dict[i][j] = alpha + (1-alpha)*new_dict[i][j]/max

    return new_dict


def similar_documents(X: Dict[str, Dict[str, float]], Y: Dict[str, Dict[str, float]]) -> Dict[str, str]:
    # Feel free to update this function
    def most_similar(Y: Dict[str, Dict[str, float]], x: Dict[str, float]) -> str:
        m, t = -1, None
        for title, y in Y.items():
            d = cosine(x, y)
            if m < 0 or d > m:
                m, t = d, title
        return t

    return {k: most_similar(Y, x) for k, x in X.items()}


if __name__ == '__main__':
    fables = json.load(open('res/vsm/aesopfables.json'))
    fables_alt = json.load(open('res/vsm/aesopfables-alt.json'))

    v_fables = vectorize(fables)
    v_fables_alt = vectorize(fables_alt)

    f = open("cos_td","a")
    for x, y in similar_documents(v_fables_alt, v_fables).items():
        f.write('{} -> {}'.format(x, y))
        f.write('\n')
    f.close()

    # Some conclusion regarding accuracy: 
    # for eu_td and eu_nftd (slightly better effect) no. 5 & 37: alpha does not really make a difference 
    # cosine does a lot better than euclidean: here, nftd does not maje a difference  
