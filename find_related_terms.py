#!/usr/bin/python3

import json
from SPARQLWrapper import SPARQLWrapper, POST
import psycopg2
import pandas


def main():
    conn = psycopg2.connect(database='htsworkflow', host='felcat.caltech.edu')

    #total = 0
    #total += display_subclass_tree('http://purl.obolibrary.org/obo/UBERON_0001134', conn=conn)
    #total += display_subclass_tree('http://purl.obolibrary.org/obo/UBERON_0001015', conn=conn)
    #total += display_subclass_tree('http://purl.obolibrary.org/obo/UBERON_0011906', conn=conn)
    #total += display_subclass_tree('http://purl.obolibrary.org/obo/UBERON_0014892', conn=conn)
    #total += display_subclass_tree('http://purl.obolibrary.org/obo/CL_0000187', conn=conn)
    #total += display_subclass_tree('http://purl.obolibrary.org/obo/CL_0000188', conn=conn)
    #print('Found {} biosaples'.format(total))

    tables = []
    #tables.extend(find_biosamples('http://purl.obolibrary.org/obo/UBERON_0001134', conn=conn))
    #tables.extend(find_biosamples('http://purl.obolibrary.org/obo/UBERON_0001015', conn=conn))
    #tables.extend(find_biosamples('http://purl.obolibrary.org/obo/UBERON_0011906', conn=conn))
    #tables.extend(find_biosamples('http://purl.obolibrary.org/obo/UBERON_0014892', conn=conn))
    tables.extend(find_biosamples('http://purl.obolibrary.org/obo/CL_0000187', conn=conn))
    tables.extend(find_biosamples('http://purl.obolibrary.org/obo/CL_0000515', conn=conn))
    df = pandas.DataFrame(tables)
    print(df)
    df.to_csv('/tmp/cell-line-terms.csv')


def count_biosamples(conn, term_id):
    cur = conn.cursor()
    cur.execute("""
select count(*)
from item
where
  object_type='Biosample' and
  payload->>'biosample_term_id' = %s""", (term_id,))
    count = cur.fetchone()
    return count[0]


def find_biosample_term_name(conn, term_id):
    cur = conn.cursor()
    cur.execute("""
select payload->>'biosample_term_name' as biosample_term_name
from item
where
  object_type='Biosample' and
  payload->>'biosample_term_id' = %s
  limit 1""", (term_id,))
    result = cur.fetchone()
    if result is not None:
        return result[0]


def find_sql_biosamples(conn, term_id):
    cur = conn.cursor()
    cur.execute("""
    select uri,
           payload->>'accession' as accession,
           payload->>'description' as description,
           payload->>'biosample_term_name' as term_name,
           payload->>'date_created' as date_created,
           payload->>'organism' as organism,
           payload->>'status' as status,
           payload->>'source' as source
from item
where
  object_type='Biosample' and
  payload->>'biosample_term_id' = %s
order by term_name, date_created""", (term_id,))
    for row in cur:
        yield {'uri': row[0],
               'accession': row[1],
               'description': row[2],
               'biosample_term_name': row[3],
               'date_created': row[4],
               'organism': row[5],
               'status': row[6],
               'source': row[7],
        }


def format_term(term):
    path, term_id = term.rsplit('/', maxsplit=1)
    return term_id.replace('_', ':')


def find_biosamples(term, parent=None, conn=None, seen=None):
    table = []
    if seen is None:
        seen = set()
    print(parent, term, len(seen))

    if term in seen:
        return []

    term_id = format_term(term)
    # if we don't have the term in our dump its not present
    label = find_biosample_term_name(conn, term_id)
    for biosample in find_sql_biosamples(conn, term_id):
        cur_row = {
            'term': term,
            'parent': parent,
            'biosample_term_name': label,
        }
        cur_row.update(biosample)
        table.append(cur_row)

    seen.add(term)
    children = ontobee_find_subclass_of(term)
    for row in children:
        table.extend(find_biosamples(row['child'], term, conn, seen))
    return table


def display_subclass_tree(term, indent=0, conn=None):
    total = 0
    template = '{indent}{term_id:15} {count:5} {label}'
    if indent == 0:
        term_id = format_term(term)
        results = list(ontobee_find_label(term))
        label = results[0].get('label') if len(results) > 0 else 'Unlabeled'
        count = count_biosamples(conn, term_id) if conn is not None else ''
        total += count
        print(template.format(indent='', term_id=term_id, count=count, label=label))

    indent += 2
    results = ontobee_find_subclass_of(term)
    for row in results:
        term_id = format_term(row['term'])
        count = count_biosamples(conn, term_id) if conn is not None else ''
        total += count
        print(template.format(
            indent=' ' * indent,
            term_id=term_id,
            count=count,
            label=row['label']))
        if row.get('child') is not None:
            count += display_subclass_tree(row['child'], indent=indent+2, conn=conn)
    return total


def ontobee_find_label(term):
    query = '''SELECT distinct ?label 
WHERE {{ 
   <{term}> rdfs:label ?label .
}}'''.format(term=term)
    yield from ontobee_query(query)


def ontobee_find_subclass_of(term):
    query = '''prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix owl: <http://www.w3.org/2002/07/owl#> 
SELECT distinct ?child
WHERE {{ 
 ?child rdfs:subClassOf <{}> .
}}'''.format(term)
    yield from ontobee_query(query)


def ontobee_query(query):
    sparql = SPARQLWrapper('http://www.ontobee.org/library/php/remote.php?')
    sparql.setQuery(query)
    sparql.setMethod(POST)
    sparql.returnFormat = 'application/sparql-results+json'

    results = sparql.query().convert().decode('latin1')
    # magically trim off some of the comment headers that break the json parser
    # probably should be parsing <!-- --> blocks
    payload = json.loads(results[1050:])
    datatypes = set()
    for row in payload['results']['bindings']:
        result = {}
        for term in row:
            datatype = row[term].get('datatype')
            value = row[term]['value']
            datatypes.add(datatype)
            if datatype == 'http://www.w3.org/2001/XMLSchema#integer':
                value = int(value)
            result[term] = value
        yield result

    # print('seen datatypes', datatypes)

if __name__ == '__main__':
    main()
