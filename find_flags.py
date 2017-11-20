#!/usr/bin/python3

from collections import Counter
from htsworkflow.submission.encoded import ENCODED

import psycopg2
import pandas

def main(cmdline=None):
    server = ENCODED('www.encodeproject.org')
    server.load_netrc()

    with psycopg2.connect(database='htsworkflow', host='felcat.caltech.edu') as conn:
        term_ids = (
            'EFO:0001098',  # C2C12
            'EFO:0005714',  # LHCN-M2
            'CL:0000187',   # muscle cell, myocyte
            'CL:0000188',   # skeletal muscle cell
            'CL:0000515',   # skeletal muscle myoblast
            'CL:0000594',   # skeletal muscle satellite cell
            'CL:0002372'    # myotube
        )
        df = pandas.DataFrame(list(find_biosample_experiments_by_term_id(conn, term_ids)))

    flags = []
    for experiment in df['experiment']:
        current_flags = count_experiment_flags(server, experiment)
        current_flags['experiment'] = experiment
        flags.append(current_flags)

    flags = pandas.DataFrame(flags, columns=['experiment', 'Red', 'Orange', 'Yellow', 'DCC Todo'])
    df = df.merge(flags, on='experiment')
    df.to_csv(
        'biosample-experiment-report.tsv',
        sep='\t',
        index=False
    )


def find_biosample_experiments_by_term_id(connection, term_ids):
    cur = connection.cursor()
    cur.execute("""
with
  experiment as (
  select uri as Experiment,
        payload->>'accession' as Experiment_Accession,
        payload->>'description' as Experiment_Description,
        payload->>'status' as Experiment_Status,
        payload->>'date_released' as Experiment_Released,
        payload->>'assay_title' as Experiment_Type
  from item
  where object_type = 'Experiment'
  ),
  replicate as (
    select uri as Replicate,
        payload->>'experiment' as Experiment,
        payload->>'library' as Library
    from item
    where object_type = 'Replicate'
  ),
  library as (
    select uri as Library,
        payload->>'accession' as Library_Accession,
        payload->>'date_created' as Library_Created,
        payload->>'biosample' as Biosample
    from item
    where object_type = 'Library'
  ),
  biosample as (
    select uri as Biosample,
        payload->>'organism' as Organism,
        payload->>'summary' as Summary,
        payload->>'award' as award,
        payload->>'biosample_term_id' as biosample_term_id,
        payload->>'biosample_term_name' as biosample_term_name
    from item
    where object_type = 'Biosample'
  ),
  award as (
     select uri as Award,
            payload->>'rfa' as rfa
     from item
     where object_type = 'Award'
  )
select
    biosample.Biosample,
    award.rfa,
    experiment.Experiment_Type,
    experiment.Experiment,
    Organism,
    biosample.biosample_term_name,
    biosample.Summary
from library
    left join biosample on library.Biosample = biosample.Biosample
    left join replicate on replicate.Library = library.Library
    left join experiment on replicate.Experiment = experiment.Experiment
    left join award on biosample.award = award.Award
where experiment.Experiment_Status = 'released' and
      biosample.biosample_term_id in %(term_ids)s
    order by biosample.Biosample, award.rfa, Organism, experiment.Experiment_Type
;
    """, {'term_ids': term_ids})
    for row in cur:
        yield {
            'biosample': row[0],
            'rfa': row[1],
            'experiment_type': row[2],
            'experiment': row[3],
            'organism': row[4],
            'term_name': row[5],
            'biosample_summary': row[6]
        }


def count_experiment_flags(server, experiment):
    obj = server.get_json(experiment)

    counts = Counter()
    for level in obj.get('audit', []):
        category = set()
        for message in obj['audit'][level]:
            category.add(message.get('category'))
        counts[level] += len(category)

    return {
        'Red': str(counts.get('ERROR', ' ')),
        'Orange': str(counts.get('NOT_COMPLIANT', ' ')),
        'Yellow': str(counts.get('WARNING', ' ')),
        'DCC Todo': str(counts.get('DCC Todo', ' ')),
    }


if __name__ == '__main__':
    main()
