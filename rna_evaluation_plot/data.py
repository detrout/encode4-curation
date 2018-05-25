import numpy
import logging
import os

import pandas
from bokeh import palettes

from models import load_quantifications, load_annotation


logger = logging.getLogger(__name__)

logger.info('loading quantifications')


quantifications = load_quantifications('evaluation.h5', experiments)
quantifications = numpy.log2(quantifications[quantifications.sum(axis=1) != 0] + .00001)

logger.info('Loading annotations')
if True:  # real loading is slow
    annotations = load_annotation(
        os.path.expanduser('~/proj/genome/GRCh38-V24-male/gencode.vV24-tRNAs-ERCC.h5'),
        '/GRCh38_v24'
    )
    spike_filter = annotations['source'] == 'spikein'
    annotations.loc[spike_filter, 'color'] = palettes.Reds3[0]
    annotations.fillna(palettes.Blues3[0], inplace=True)
    annotations['gene_name'].fillna('', inplace=True)
else:
    annotations = pandas.DataFrame(index=quantifications.index)
    annotations.loc[-98:, 'color'] = palettes.Reds3[0]
    annotations.fillna(palettes.Blues3[0], inplace=True)
logger.info('Done')
