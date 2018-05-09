\pset format unaligned
\pset fieldsep '\t'
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
  where object_type = 'Experiment'
  ),
  file as (
  select uri as File,
         payload->>'accession' as File_Accession,
         payload->>'dataset' as dataset,
         payload->>'status' as File_Status,
         payload->>'assembly' as assembly,
         payload->>'file_format' as file_format,
         payload->>'output_type' as output_type,
         payload->>'submitted_file_name' as filename,
         payload->>'biological_replicates' as biorep,
         payload->>'technical_replicates' as techrep,
         payload->>'notes' as notes
  from item
  where object_type= 'File' and
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
  --experiment.Experiment_Description,
  Library_Accession,
  File,
  file_status,
  assembly,
  file_format,
  output_type,
  notes,
  filename
from file
     left join experiment on file.dataset = experiment.Experiment
     left join award on experiment.Award = award.Award
     left join replicate on replicate.Experiment = experiment.Experiment
     left join library on replicate.Library = library.Library
where file_status in ('archived', 'revoked')
--('"archived"'::jsonb, '"revoked"'::jsonb)
;
