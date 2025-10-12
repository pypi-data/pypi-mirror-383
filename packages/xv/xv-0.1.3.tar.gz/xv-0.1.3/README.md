# xv

Access to arxiv data

To install:	```pip install xv```


# Examples


```python
from xv import *
```

## Raw store

At the point of writing this, my attempts enable `graze` to automatically confirm download in the googledrive downloads (which, when downloading too-big files, will tell the user it can't scan the file and ask the user to confirm the download).

Therefore, the following files need to be downloaded manually:
* **titles**: https://drive.google.com/file/d/1Ul5mPePtoPKHZkH5Rm6dWKAO11dG98GN/view?usp=share_link
* **abstracts**: https://drive.google.com/file/d/1g3K-wlixFxklTSUQNZKpEgN4WNTFTPIZ/view?usp=share_link

(If those urls don't work, perhaps they were updated: See here: https://alex.macrocosm.so/download .)

You can then copy them over to the place graze will look for by doing:

```python
from pathlib import Path
from xv.util import Graze
from xv.data_access import urls


g[urls['titles']] = Path('TITLES_DATA_LOCAL_FILEPATH').read_bytes()
g[urls['abstracts']] = Path('ABSTRACTS_DATA_LOCAL_FILEPATH').read_bytes()
```


```python
# from imbed.mdat.arxiv import urls
# from pathlib import Path

# g[urls['titles']] = Path('FILE_WHERE_YOU_DOWNLOADED_TITLES_DATA').read_bytes()
# g[urls['abstracts']] = Path('FILE_WHERE_YOU_DOWNLOADED_TITLES_DATA').read_bytes()

```


```python
from xv.util import Graze

g = Graze()
list(g)
```




    ['https://drive.google.com/file/d/1Ul5mPePtoPKHZkH5Rm6dWKAO11dG98GN/view?usp=share_link',
     'https://drive.google.com/file/d/1g3K-wlixFxklTSUQNZKpEgN4WNTFTPIZ/view?usp=share_link',
     'https://arxiv.org/pdf/0704.0001']




```python
from xv import raw_sources

list(raw_sources)
```




    ['titles', 'abstracts']






```python
raw = raw_sources['titles']
list(raw)
```




    ['titles_7.parquet',
     'titles_23.parquet',
     'titles_15.parquet',
     'verifyResults.py',
     'titles_14.parquet',
     'titles_22.parquet',
     'titles_6.parquet',
     'titles_16.parquet',
     'titles_20.parquet',
     'titles_4.parquet',
     'titles_5.parquet',
     'titles_21.parquet',
     'params.txt',
     'titles_17.parquet',
     'exampleEmbed.py',
     'titles_12.parquet',
     'README.md',
     'titles_9.parquet',
     'titles_1.parquet',
     'titles_13.parquet',
     'titles_8.parquet',
     'titles_18.parquet',
     'titles_3.parquet',
     'titles_11.parquet',
     'titles_10.parquet',
     'titles_19.parquet',
     'titles_2.parquet']




```python
print(raw['exampleEmbed.py'].decode())
```

    from InstructorEmbedding import INSTRUCTOR
    
    model = INSTRUCTOR('hkunlp/instructor-xl')
    sentence = "3D ActionSLAM: wearable person tracking in multi-floor environments"
    instruction = "Represent the Research Paper title for retrieval; Input:"
    embeddings = model.encode([[instruction,sentence]])
    print(embeddings)



```python
from InstructorEmbedding import INSTRUCTOR

model = INSTRUCTOR('hkunlp/instructor-xl')

```

    /Users/thorwhalen/.pyenv/versions/3.10.13/envs/p10/lib/python3.10/site-packages/InstructorEmbedding/instructor.py:7: TqdmExperimentalWarning: Using `tqdm.autonotebook.tqdm` in notebook mode. Use `tqdm.tqdm` instead to force console mode (e.g. in jupyter console)
      from tqdm.autonotebook import trange


    load INSTRUCTOR_Transformer
    max_seq_length  512



```python
sentence = "3D ActionSLAM: wearable person tracking in multi-floor environments"
instruction = "Represent the Research Paper title for retrieval; Input:"
embeddings = model.encode([[instruction, sentence]])

```


```python
print(raw['params.txt'].decode())
```

    prompt: Represent the Research Paper title for retrieval; Input:
    type: title
    time string: 20230518-185428
    model: InstructorXL
    version: 2.0



```python
print(raw['exampleEmbed.py'].decode())
```

    from InstructorEmbedding import INSTRUCTOR
    
    model = INSTRUCTOR('hkunlp/instructor-xl')
    sentence = "3D ActionSLAM: wearable person tracking in multi-floor environments"
    instruction = "Represent the Research Paper title for retrieval; Input:"
    embeddings = model.encode([[instruction,sentence]])
    print(embeddings)


## The imbedding data store

And now, we'll transform the raw store to get a convenient interface to the actual data of interest.


```python
b = raw['titles_1.parquet']
len(b)
```




    313383694




```python
from xv import sources  # raw store + wrapper. See parquet_codec code.

titles_tables = sources['titles']
abstract_tables = sources['abstracts']
print(list(titles_tables))
```

    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]



```python
titles_df = titles_tables[1]
titles_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>title</th>
      <th>embeddings</th>
      <th>doi</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Calculation of prompt diphoton production cros...</td>
      <td>[-0.050620172, 0.041436385, 0.05363288, -0.029...</td>
      <td>0704.0001</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Sparsity-certifying Graph Decompositions</td>
      <td>[0.014515653, 0.023809524, -0.028145121, -0.04...</td>
      <td>0704.0002</td>
    </tr>
    <tr>
      <th>2</th>
      <td>The evolution of the Earth-Moon system based o...</td>
      <td>[-4.766115e-05, 0.017415706, 0.04146007, -0.03...</td>
      <td>0704.0003</td>
    </tr>
    <tr>
      <th>3</th>
      <td>A determinant of Stirling cycle numbers counts...</td>
      <td>[0.027208889, 0.046175897, 0.0010913888, -0.01...</td>
      <td>0704.0004</td>
    </tr>
    <tr>
      <th>4</th>
      <td>From dyadic $\Lambda_{\alpha}$ to $\Lambda_{\a...</td>
      <td>[0.0113909235, 0.0042667952, -0.0008565594, -0...</td>
      <td>0704.0005</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>99995</th>
      <td>Multiple Time Dimensions</td>
      <td>[0.02682626, -0.0015173098, -0.0019915192, -0....</td>
      <td>0812.3869</td>
    </tr>
    <tr>
      <th>99996</th>
      <td>Depth Zero Representations of Nonlinear Covers...</td>
      <td>[-0.02740943, 0.011689809, -0.0105154915, -0.0...</td>
      <td>0812.3870</td>
    </tr>
    <tr>
      <th>99997</th>
      <td>Decting Errors in Reversible Circuits With Inv...</td>
      <td>[0.0072460608, 0.0028085636, -0.015064359, -0....</td>
      <td>0812.3871</td>
    </tr>
    <tr>
      <th>99998</th>
      <td>Unveiling the birth and evolution of the HII r...</td>
      <td>[0.009408689, -0.0047120117, 0.0021392817, -0....</td>
      <td>0812.3872</td>
    </tr>
    <tr>
      <th>99999</th>
      <td>The K-Receiver Broadcast Channel with Confiden...</td>
      <td>[-0.0026305509, -0.006502139, 0.013400236, -0....</td>
      <td>0812.3873</td>
    </tr>
  </tbody>
</table>
<p>100000 rows × 3 columns</p>
</div>




```python
abstract_df = abstract_tables[1]
abstract_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>abstract</th>
      <th>embeddings</th>
      <th>doi</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>A fully differential calculation in perturba...</td>
      <td>[-0.035151865, 0.022851437, 0.025942933, -0.02...</td>
      <td>0704.0001</td>
    </tr>
    <tr>
      <th>1</th>
      <td>We describe a new algorithm, the $(k,\ell)$-...</td>
      <td>[0.035485767, -0.0015772493, -0.0016615744, -0...</td>
      <td>0704.0002</td>
    </tr>
    <tr>
      <th>2</th>
      <td>The evolution of Earth-Moon system is descri...</td>
      <td>[-0.014510429, 0.010210799, 0.049661566, -0.01...</td>
      <td>0704.0003</td>
    </tr>
    <tr>
      <th>3</th>
      <td>We show that a determinant of Stirling cycle...</td>
      <td>[0.029191103, 0.047992915, -0.0061754594, -0.0...</td>
      <td>0704.0004</td>
    </tr>
    <tr>
      <th>4</th>
      <td>In this paper we show how to compute the $\L...</td>
      <td>[-0.015174898, 0.01603887, 0.04062805, -0.0246...</td>
      <td>0704.0005</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>99995</th>
      <td>The possibility of physics in multiple time ...</td>
      <td>[0.016121766, 0.011126887, 0.018650021, -0.044...</td>
      <td>0812.3869</td>
    </tr>
    <tr>
      <th>99996</th>
      <td>We generalize the methods of Moy-Prasad, in ...</td>
      <td>[-7.164341e-05, -0.007114291, -0.008979887, -0...</td>
      <td>0812.3870</td>
    </tr>
    <tr>
      <th>99997</th>
      <td>Reversible logic is experience renewed inter...</td>
      <td>[0.03194286, -0.00771745, 0.015977046, -0.0474...</td>
      <td>0812.3871</td>
    </tr>
    <tr>
      <th>99998</th>
      <td>Based on a multiwavelength study, the ISM ar...</td>
      <td>[-0.012340169, -0.021712925, 0.00806009, -0.00...</td>
      <td>0812.3872</td>
    </tr>
    <tr>
      <th>99999</th>
      <td>The secrecy capacity region for the K-receiv...</td>
      <td>[0.0012416588, 0.0006933478, -0.0057888636, -0...</td>
      <td>0812.3873</td>
    </tr>
  </tbody>
</table>
<p>100000 rows × 3 columns</p>
</div>




```python
abstract_df['doi'].values
```




    array(['0704.0001', '0704.0002', '0704.0003', ..., '0812.3871',
           '0812.3872', '0812.3873'], dtype=object)




```python
from xv import arxiv_url

doi = abstract_df['doi'].values[0]
arxiv_url(doi)
```




    'https://arxiv.org/abs/0704.0001'




```python
from xv.data_access import resource_descriptions
resource_descriptions
```




    {'abs': 'Main page of article. Contains links to all other relevant information.',
     'pdf': 'Direct link to article pdf',
     'format': 'Page giving access to other formats',
     'src': 'Access to the original source files submitted by the authors.',
     'cits': 'Tracks citations of the article across various platforms and databases.',
     'html': 'Link to the ar5iv html page for the article.'}




```python
doi = '0704.0001'

for resource, description in resource_descriptions.items():
    print(f"{resource}: {description}")
    print(f"Example: {arxiv_url(doi, resource)}")
    print("")

```

    abs: Main page of article. Contains links to all other relevant information.
    Example: https://arxiv.org/abs/0704.0001
    
    pdf: Direct link to article pdf
    Example: https://arxiv.org/pdf/0704.0001
    
    format: Page giving access to other formats
    Example: https://arxiv.org/format/0704.0001
    
    src: Access to the original source files submitted by the authors.
    Example: https://arxiv.org/src/0704.0001
    
    cits: Tracks citations of the article across various platforms and databases.
    Example: https://arxiv.org/cits/0704.0001
    
    html: Link to the ar5iv html page for the article.
    Example: https://ar5iv.labs.arxiv.org/html/0704.0001
    



```python
arxiv_url(doi, 'pdf')
```


    'https://arxiv.org/pdf/0704.0001'



```python
pdf_bytes = g[arxiv_url(doi, 'pdf')]
```

    The contents  (~1.647MB) of https://arxiv.org/pdf/0704.0001 are being downloaded...



```python
abstract_df.embeddings.values[0].shape
```




    (768,)

