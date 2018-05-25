import pandas

from .models import load_quantifications, load_annotation


annotations = None
quantifications = None
data_loaded = False


def on_server_loaded(context):
    globals annotations, quantifications, data_loaded

    print('loading quantifications')
    store = pandas.HDFStore('evaluation.h5', 'r')
    experiments = store['/experiments']
    quantifications = load_quantifications(store, experiments)
    quantifications = numpy.log2(quantifications[quantifications.sum(axis=1) != 0] + .00001)
    store.close()

    print('Loading annotations')
    if True:
        genes = load_annotation()
        genes.loc[genes['source'] == 'spikein', 'color'] = palettes.Reds3[0]
        genes.fillna(palettes.Blues3[0], inplace=True)
        genes['gene_name'].fillna('', inplace=True)
    else:
        genes = pandas.DataFrame(index=quantifications.index)
        genes.loc[-98:, 'color'] = palettes.Reds3[0]
        genes.fillna(palettes.Blues3[0], inplace=True)
    print('Done')
