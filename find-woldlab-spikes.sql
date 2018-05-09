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
           payload->>'spikeins_used' as spikeins,
           substring(jsonb_array_elements_text(payload->'aliases') from 'barbara-wold:([0-9_A-Z]+)') as library_id
    from item
    where object_type = 'Library'
  ),
  award as (
     select uri as Award,
            payload->>'rfa' as rfa
     from item
     where object_type = 'Award'
  )
select distinct
  experiment.Experiment,
  library.library_id,
  experiment.Experiment_term_name,
  library_id,
  spikeins
  --experiment.Experiment_Description
from experiment
     left join award on experiment.Award = award.Award
     left join replicate on replicate.Experiment = experiment.Experiment
     left join library on replicate.Library = library.Library
order by spikeins
;
