DELETE{ ?s ?p ?o. }
WHERE { ?s ?p ?o. filter(contains(str(?s), "http://purl.obolibrary.org/obo/FBbt_"))}
