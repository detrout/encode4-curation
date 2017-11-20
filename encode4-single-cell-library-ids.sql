-- \pset format unaligned
-- \pset fieldsep '\t'
with
  experiment as (
  select uri as Experiment,
         payload->>'accession' as Experiment_Accession,
         payload->>'description' as Experiment_Description,
         payload->>'status' as Experiment_Status,
         payload->>'date_released' as Experiment_Released,
         payload->>'assay_title' as Experiment_term_name,
         payload->>'assay_term_id' as Experiment_term_id,
         payload->>'award' as Award
  from item
  where object_type = 'Experiment' and
        payload->'lab' @> '"/labs/barbara-wold/"'::jsonb
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
           payload->>'biosample' as Biosample,
           substring(jsonb_array_elements_text(payload->'aliases') from 'barbara-wold:([0-9_A-Z]+)') as library_id
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
select distinct
  award.rfa,
  experiment.Experiment,
  library.library_id,
  experiment.Experiment_term_name,
  --experiment.Experiment_term_id
  --experiment.Experiment_Status,
  --experiment.Experiment_Released,
  --replicate.Replicate,
  library.Library,
  experiment.Experiment_Description
from experiment
     left join award on experiment.Award = award.Award
     left join replicate on replicate.Experiment = experiment.Experiment
     left join library on replicate.Library = library.Library
where experiment.Experiment_Status = 'released' and
      experiment.Experiment_term_id = 'NTR:0003082' and
      rfa = 'ENCODE4'
order by library.library_id
;
