WITH source_data AS (
    SELECT *, idade AS idade_duplicada
    FROM public.teste
)

SELECT * FROM source_data;
