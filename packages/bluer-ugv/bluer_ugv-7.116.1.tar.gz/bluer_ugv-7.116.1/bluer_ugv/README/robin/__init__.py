from bluer_sbc.parts.db import db_of_parts
from bluer_sbc.parts.consts import parts_url_prefix

from bluer_ugv.designs.robin.README import items
from bluer_ugv.designs.robin.parts import dict_of_parts


docs = [
    {
        "items": items,
        "path": "../docs/robin",
    },
    {
        "path": "../docs/robin/parts.md",
        "items": db_of_parts.as_images(
            dict_of_parts,
            reference=parts_url_prefix,
        ),
        "macros": {
            "parts:::": db_of_parts.as_list(
                dict_of_parts,
                reference=parts_url_prefix,
                log=False,
            ),
        },
    },
]
