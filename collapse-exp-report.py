#!/usr/bin/python3
"""Flatten the output of one of the sql reports 

so its only one experiment per line, (so library information
is squished into a comma seperated list)
"""
import argparse
import pandas

def main(cmdline=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs=1)
    parser.add_argument('-o', '--output',
                        help='name to save file to')

    args = parser.parse_args(cmdline)

    with open(args.filename[0], 'rt') as instream:
        df = collapse(instream)
    if args.output:
        df.to_csv(args.output, sep='\t')
    else:
        print('summary')
        print(df.head())


def collapse(stream):
    df = pandas.read_csv(stream, '\t', dtype=str)

    exp = df[['experiment_accession',
              'experiment_type',
              'experiment_description',
              'experiment_status',
              'experiment_released',
              'organism',
              'library_created']].drop_duplicates().set_index('experiment_accession')
    lib = df[['experiment_accession',
              'library_accession',
              # 'biosample',
              # 'library_created',
              'jumpgate_library_id']]


    dcc_lib_ids = {}
    our_lib_ids = {}
    for i, row in lib.iterrows():
        dcc_lib_ids.setdefault(row.experiment_accession, []).append(row.library_accession)
        our_lib_ids.setdefault(row.experiment_accession, []).append(row.jumpgate_library_id)

    dcc_lib_ids = flatten_lib_id(dcc_lib_ids, 'library_accessions')
    our_lib_ids = flatten_lib_id(our_lib_ids, 'jumpgate_library_ids')

    exp = exp.merge(our_lib_ids, left_index=True, right_index=True)
    exp = exp.merge(dcc_lib_ids, left_index=True, right_index=True)

    return exp.sort_values(['experiment_type', 'experiment_released'])


def flatten_lib_id(lib_ids, name):
    result = {}
    for exp_id in lib_ids:
        result[exp_id] = ','.join([str(x) for x in lib_ids[exp_id]])
    result = pandas.Series(result)
    result.name = name
    df = pandas.DataFrame(result)
    return df

if __name__ == '__main__':
    main()
