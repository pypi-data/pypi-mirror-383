# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

OEO_TEMPLATE = {
    "base": {
        "@context": "https://raw.githubusercontent.com/OpenEnergyPlatform/oemetadata/production/oemetadata/latest/context.json",
        "name": "<schema:metadata:name>_result_metadata",
        "title": "Results for <schema:metadata:name> run <scenario:metadata:RunId>.",
        "description": """Input compiled with FAME-Io <execution:InputCompilation:SoftwareVersions:FameIo>.
        Simulated by FAME-Core <execution:ModelRun:SoftwareVersions:FameCore>.
        Extracted by FAME-Io <execution:OutputExtraction:SoftwareVersions:FameIo>.""",
        "resources": ["{{perAgent}}"],
        "metaMetadata": {
            "metadataVersion": "OEMetadata-2.0.4",
            "metadataLicense": {
                "name": "CC0-1.0",
                "title": "Creative Commons Zero v1.0 Universal",
                "path": "https://creativecommons.org/publicdomain/zero/1.0",
            },
        },
    },
    "perAgent": {
        "name": "(agent).*.csv",
        "topics": [],
        "title": "Results for (agent)",
        "path": "./(agent).*.csv",
        "description": "Simulation outputs by simulated time of agent type '(agent)'",
        "languages": ["en-GB"],
        "subject": "<schema:AgentTypes:(agent):metadata:subject>",
        "keywords": "<schema:AgentTypes:(agent):metadata:keywords>",
        "publicationDate": "<scenario:metadata:output:publicationDate>",
        "embargoPeriod": "<scenario:metadata:output:embargoPeriod>",
        "context": {
            "title": "<schema:metadata:title>",
            "homepage": "<schema:metadata:homepage>",
            "documentation": "<schema:metadata:documentation>",
            "sourceCode": "<schema:metadata:sourceCode>",
            "publisher": "<schema:metadata:publisher>",
            "publisherLogo": "<schema:metadata:publisherLogo>",
            "contact": "<schema:metadata:contact>",
            "fundingAgency": "<schema:metadata:fundingAgency>",
            "fundingAgencyLogo": "<schema:metadata:fundingAgencyLogo>",
            "grantNo": "<schema:metadata:grantNo>",
        },
        "spatial": {},
        "temporal": {},
        "sources": [],
        "licenses": "<scenario:metadata:output:licenses>",
        "contributors": "<schema:metadata:contributors>",
        "type": "table",
        "format": "CSV",
        "encoding": "UTF-8",
        "schema": {
            "fields": [
                {
                    "name": "AgentId",
                    "description": "Unique ID of the agent in the simulation",
                    "type": "integer",
                    "nullable": False,
                    "unit": "n/a",
                    "isAbout": [],
                    "valueReference": [],
                },
                {
                    "name": "TimeStep",
                    "description": "Simulated time these values are associated with",
                    "type": "integer or time stamp",
                    "nullable": False,
                    "unit": "n/a",
                    "isAbout": [
                        {"name": "TimeStamp", "@id": "https://openenergyplatform.org/ontology/oeo/OEO_00140043"}
                    ],
                    "valueReference": [],
                },
                "{{perColumn}}",
            ],
            "primaryKey": ["AgentId", "TimeStep"],
            "foreignKeys": [],
            "dialect": {"delimiter": ";", "decimalSeparator": "."},
            "review": {},
        },
    },
    "perColumn": {
        "name": "(column)",
        "description": "<schema:AgentTypes:(agent):outputs:(column):metadata:description>",
        "type": "decimal",
        "nullable": True,
        "unit": "<schema:AgentTypes:(agent):outputs:(column):metadata:unit>",
        "isAbout": "<schema:AgentTypes:(agent):outputs:(column):metadata:isAbout>",
        "valueReference": "<schema:AgentTypes:(agent):outputs:(column):metadata:valueReference>",
    },
}
