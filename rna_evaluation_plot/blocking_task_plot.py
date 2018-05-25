from functools import partial
import os
from threading import Thread

import numpy
import pandas

from bokeh.models import ColumnDataSource
from bokeh.plotting import curdoc, figure
from bokeh import palettes

from tornado import gen

from models import load_annotation, load_quantifications

experiments = pandas.DataFrame({
    'assay': {'ENCSR000AEC': 'total RNA-seq',
              'ENCSR000AED': 'polyA RNA-seq',
              'ENCSR000AEE': 'total RNA-seq',
              'ENCSR000AEF': 'polyA RNA-seq',
              'ENCSR000AEG': 'polyA RNA-seq',
              'ENCSR000AEH': 'polyA RNA-seq',
              'ENCSR000AEM': 'polyA RNA-seq',
              'ENCSR000AEN': 'total RNA-seq',
              'ENCSR000AEO': 'polyA RNA-seq',
              'ENCSR000AEP': 'polyA RNA-seq',
              'ENCSR000AEQ': 'polyA RNA-seq'},
    'biosample_term_name': {'ENCSR000AEC': 'GM12878',
                            'ENCSR000AED': 'GM12878',
                            'ENCSR000AEE': 'GM12878',
                            'ENCSR000AEF': 'GM12878',
                            'ENCSR000AEG': 'GM12878',
                            'ENCSR000AEH': 'GM12878',
                            'ENCSR000AEM': 'K562',
                            'ENCSR000AEN': 'K562',
                            'ENCSR000AEO': 'K562',
                            'ENCSR000AEP': 'K562',
                            'ENCSR000AEQ': 'K562'},
    'gene_quantification': {'ENCSR000AEC': 'ENCFF906LSJ',
                            'ENCSR000AED': 'ENCFF902UYP',
                            'ENCSR000AEE': 'ENCFF306TLL',
                            'ENCSR000AEF': 'ENCFF456WWG',
                            'ENCSR000AEG': 'ENCFF392CRO',
                            'ENCSR000AEH': 'ENCFF200USH',
                            'ENCSR000AEM': 'ENCFF472EUD',
                            'ENCSR000AEN': 'ENCFF553DDU',
                            'ENCSR000AEO': 'ENCFF427EWZ',
                            'ENCSR000AEP': 'ENCFF461HPX',
                            'ENCSR000AEQ': 'ENCFF868MFR'},
    'lab': {'ENCSR000AEC': 'Thomas Gingeras, CSHL',
            'ENCSR000AED': 'Thomas Gingeras, CSHL',
            'ENCSR000AEE': 'Brenton Graveley, UConn',
            'ENCSR000AEF': 'Brenton Graveley, UConn',
            'ENCSR000AEG': 'Barbara Wold, Caltech',
            'ENCSR000AEH': 'Barbara Wold, Caltech',
            'ENCSR000AEM': 'Thomas Gingeras, CSHL',
            'ENCSR000AEN': 'Brenton Graveley, UConn',
            'ENCSR000AEO': 'Brenton Graveley, UConn',
            'ENCSR000AEP': 'Barbara Wold, Caltech',
            'ENCSR000AEQ': 'Barbara Wold, Caltech'},
    'rep': {'ENCSR000AEC': '1_1',
            'ENCSR000AED': '1_1',
            'ENCSR000AEE': '1_1',
            'ENCSR000AEF': '2_1',
            'ENCSR000AEG': '2_1',
            'ENCSR000AEH': '2_1',
            'ENCSR000AEM': '2_1',
            'ENCSR000AEN': '1_1',
            'ENCSR000AEO': '1_1',
            'ENCSR000AEP': '2_1',
            'ENCSR000AEQ': '2_1'}})

columns = ['ENCFF200USH', 'ENCFF306TLL', 'ENCFF392CRO', 'ENCFF427EWZ',
           'ENCFF456WWG', 'ENCFF461HPX', 'ENCFF472EUD', 'ENCFF553DDU',
           'ENCFF868MFR', 'ENCFF902UYP', 'ENCFF906LSJ',
           'chromosome', 'source', 'type', 'start', 'stop', 'score',
           'strand', 'frame', 'gene_type', 'gene_status', 'gene_name',
           'level', 'havana_gene', 'transcript_id', 'transcript_type',
           'transcript_status', 'transcript_name', 'tag',
           'transcript_support_level', 'havana_transcript',
           'exon_number', 'exon_id', 'ont', 'protein_id',
           'ccdsid', 'color']

# this must only be modified from a Bokeh session callback
source = ColumnDataSource(data={k: [] for k in columns})

# This is important! Save curdoc() to make sure all threads
# see the same document.
doc = curdoc()


@gen.coroutine
def update(df):
    source.data = ColumnDataSource.from_df(df)


class blocking_task:
    def __init__(self):
        print('load_quantifications')
        quantifications = load_quantifications('evaluation.h5', experiments)
        quantifications = numpy.log2(quantifications[quantifications.sum(axis=1) != 0] + .00001)
        print('load_annotation')
        annotations = load_annotation(
            os.path.expanduser('~/proj/genome/GRCh38-V24-male/gencode.vV24-tRNAs-ERCC.h5'),
            '/GRCh38_v24'
        )
        spike_filter = annotations['source'] == 'spikein'
        annotations.loc[spike_filter, 'color'] = palettes.Reds3[0]
        annotations.fillna(palettes.Blues3[0], inplace=True)
        annotations['gene_name'].fillna('', inplace=True)

        self.df = quantifications.merge(annotations, left_index=True, right_index=True)
        print('done')

    def __call__(self):
        # but update the document from callback
        doc.add_next_tick_callback(partial(update, self.df))


plot = figure(plot_width=800, plot_height=800)
scatter = plot.circle(x='ENCFF200USH', y='ENCFF306TLL', color='color', source=source)

doc.add_root(plot)

thread = Thread(target=blocking_task)
thread.start()
