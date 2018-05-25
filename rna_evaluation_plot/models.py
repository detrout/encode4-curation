import pandas


def load_annotation(filename, genome):
    store = pandas.HDFStore(filename, mode='r')
    annotations = store[genome]
    gene_filter = (annotations['type'] == 'gene')
    spikein_filter = (annotations['source'] == 'spikein')
    trna_filter = (annotations['gene_type'] == 'tRNAscan')
    genes = annotations[gene_filter | spikein_filter | trna_filter]
    genes.set_index('gene_id', inplace=True)
    store.close()
    return genes


def load_quantifications(filename, experiments, name='FPKM'):
    store = pandas.HDFStore(filename, 'r')

    download_url = 'https://www.encodeproject.org/files/{accession}/@@download/{accession}.tsv'
    quantifications = []
    for accession, experiment in experiments.iterrows():
        file_accession = experiment['gene_quantification']
        path = '/gene_quantifications/{accession}'.format(accession=file_accession)
        if path not in store:
            store[path] = pandas.read_csv(download_url.format(accession=file_accession), sep='\t', index_col=0)
        q = store[path][name]
        q.name = file_accession
        quantifications.append(q)
    store.close()
    return pandas.DataFrame({x.name: x for x in quantifications})
