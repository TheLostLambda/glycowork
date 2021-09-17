# Glycowork



![CI](https://github.com/BojarLab/glycowork/workflows/CI/badge.svg)


<img src="glycowork_badge_wo_bg.jpg" width="200" style="max-width: 200px">

Glycans are a fundamental biological sequence, similar to DNA, RNA, or proteins. Glycans are complex carbohydrates that can form branched structures comprising monosaccharides and linkages as constituents. Despite being conspicuously absent from most research, glycans are ubiquitous in biology. They decorate most proteins and lipids and direct the stability and functions of biomolecules, cells, and organisms. This also makes glycans relevant to every human disease.

The analysis of glycans is made difficult by their nonlinearity and their astounding diversity, given the large number of monosaccharides and types of linkages. `Glycowork` is a Python package designed to process and analyze glycan sequences, with a special emphasis on glycan-focused data science and machine learning. Next to various functions to work with glycans, `Glycowork` also contains glycan data that can be used for glycan alignments, model pre-training, motif comparisons, etc.

If you use `glycowork` in your project, please cite [Thomes et al., 2021](https://academic.oup.com/glycob/advance-article/doi/10.1093/glycob/cwab067/6311240).

The inspiration for `glycowork` can be found in [Bojar et al., 2020](https://doi.org/10.1016/j.chom.2020.10.004) and [Burkholz et al., 2021](https://www.cell.com/cell-reports/fulltext/S2211-1247(21)00616-1). There, you can also find examples of possible use cases for the functions in `glycowork`.

The full documentation for `glycowork` can be found here: https://bojarlab.github.io/glycowork/

If you want to contribute to `glycowork`, the best place to start is to read our [contribution guidelines](https://github.com/BojarLab/glycowork/blob/master/CONTRIBUTING.md).

## Install

via pip: <br>
`pip install glycowork` <br>
`import glycowork`

alternative: <br>
`pip install git+https://github.com/BojarLab/glycowork.git` <br>
`import glycowork`

## How to use

`Glycowork` currently contains five main modules:
 - **`alignment`**
     - can be used to find similar glycan sequences by alignment according to a glycan-specific substitution matrix
 - **`glycan_data`**
     - stores several glycan datasets and contains helper functions
 - **`ml`**
     - here are all the functions for training and using machine learning models, including train-test-split, getting glycan representations, etc.
 - **`motif`**
     - contains functions for processing glycan sequences, identifying motifs and features, and analyzing them
 - **`network`**
     - contains functions for constructing and analyzing glycan networks (e.g., biosynthetic networks)
     
Below are some examples of what you can do with `glycowork`, be sure to check out the other `examples` in the full documentation for everything that's there.

```
#using graphs, you can easily check whether two glycans are the same - even if they use different bracket notations!
from glycowork.motif.graph import compare_glycans
print(compare_glycans('Man(a1-3)[Man(a1-6)]Man(b1-4)GlcNAc(b1-4)[Fuc(a1-6)]GlcNAc',
                     'Man(a1-6)[Man(a1-3)]Man(b1-4)GlcNAc(b1-4)[Fuc(a1-6)]GlcNAc'))
print(compare_glycans('Man(a1-3)[Man(a1-6)]Man(b1-4)GlcNAc(b1-4)[Fuc(a1-6)]GlcNAc',
                     'Man(a1-6)[Man(a1-3)]Man(b1-4)GlcNAc(b1-4)GlcNAc'))
```

```
#querying some of the stored databases
from glycowork.motif.query import get_insight
get_insight('Man(a1-3)[Man(a1-6)]Man(b1-4)GlcNAc(b1-4)[Fuc(a1-6)]GlcNAc')
```

```
#get motifs, graph features, and sequence features of a set of glycan sequences to train models or analyze glycan properties
glycans = ['Man(a1-3)[Man(a1-6)][Xyl(b1-2)]Man(b1-4)GlcNAc(b1-4)[Fuc(a1-3)]GlcNAc',
           'Man(a1-2)Man(a1-2)Man(a1-3)[Man(a1-3)Man(a1-6)]Man(b1-4)GlcNAc(b1-4)GlcNAc',
           'GalNAc(a1-4)GlcNAcA(a1-4)[GlcN(b1-7)]Kdo(a2-5)[Kdo(a2-4)]Kdo(a2-6)GlcN4P(b1-6)GlcN4P']
from glycowork.motif.annotate import annotate_dataset
out = annotate_dataset(glycans, feature_set = ['known', 'graph', 'exhaustive']).head()
```

```
#identify significant binding motifs with (for instance) Z-score data
from glycowork.motif.analysis import get_pvals_motifs
glycans = ['Man(a1-3)[Man(a1-6)][Xyl(b1-2)]Man(b1-4)GlcNAc(b1-4)[Fuc(a1-3)]GlcNAc',
           'Man(a1-2)Man(a1-2)Man(a1-3)[Man(a1-3)Man(a1-6)]Man(b1-4)GlcNAc(b1-4)GlcNAc',
           'GalNAc(a1-4)GlcNAcA(a1-4)[GlcN(b1-7)]Kdo(a2-5)[Kdo(a2-4)]Kdo(a2-6)GlcN4P(b1-6)GlcN4P',
           'Man(a1-2)Man(a1-3)[Man(a1-6)]Man(b1-4)GlcNAc(b1-4)GlcNAc',
           'Glc(b1-3)Glc(b1-3)Glc']
label = [3.234, 2.423, 0.733, 3.102, 0.108]
test_df = pd.DataFrame({'glycan':glycans, 'binding':label})
out = get_pvals_motifs(test_df, glycan_col_name = 'glycan', label_col_name = 'binding').iloc[:10,:]
```
