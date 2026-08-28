# DARTIS validation asset attribution

This case uses `ow-0010.jpg` and `ow-0010.xml` from:

Yang, Yi-Jie; Singha, Suman (2025): *Oil slicks, look-alikes and other remarkable SAR signatures in Sentinel-1 imagery in the Eastern Mediterranean Sea in 2019*. PANGAEA. <https://doi.org/10.1594/PANGAEA.980773>

- Dataset subset: `ow` (oil/water)
- Asset: `ow-0010`
- Source observation: Sentinel-1, 2019-01-19
- Licence: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
- Downloaded from: `https://download.pangaea.de/dataset/980773/files/`

The JPEG is an 8-bit normalized SAR patch and the XML annotation uses Pascal VOC bounding boxes. OCEANTRACE uses the largest labelled oil object for the displayed reference polygon and both XML objects when reporting best bounding-box IoU.
