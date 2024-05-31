#!/bin/bash
#humann_databases --download utility_mapping full /data/umcg-tifn/rgacesa/dag3_pipeline_v3_dbs/chocophlan_201901/ --update-config yes
humann_databases --download uniref uniref90_diamond /data/umcg-tifn/rgacesa/dag3_pipeline_v3_dbs/chocophlan_201901/ --update-config yes
humann_databases --download chocophlan full /data/umcg-tifn/rgacesa/dag3_pipeline_v3_dbs/chocophlan_201901/ --update-config yes

