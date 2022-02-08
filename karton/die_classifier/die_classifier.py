# -*- coding: utf-8 -*-

from karton.core import Config, Karton, Task
import subprocess
import logging
import json
import re

from .__version__ import __version__

log = logging.getLogger(__name__)


class DieClassifier(Karton):
    """
    Scan a given sample with Detect-It-Easy tool
    """

    identity = "karton.die-classifier"
    version = __version__
    filters = [
        {"type": "sample", "stage": "recognized"},
        {"type": "sample", "kind": "raw"},
    ]

    def __init__(
        self,
        config: Config = None,
        identity: str = None,
    ) -> None:
        super().__init__(config=config, identity=identity)

    def _format_sign(self, entry: dict) -> str:
        """Formats DIE JSON result to a suitable tag format

        Args:
            entry (dict): detection signatures as returned by DIE

        Returns:
            str: rielaborated signature in tag format
        """

        def replace(rep: dict, text: str):
            for r in list(rep):
                text = re.sub(r, rep[r], text)

            if "build" in text:
                text = "_".join(text.split("build")[:-1])

            return text.lower()

        fields_to_extract = {
            "name": None,
            "version": None,
            "options": None,
        }

        patterns_sting = {
            "[_\]\[(),\/#><\-*\s]": "_",
            r"(_)\1+": "_",
            r"^_|_$": "",
        }

        formatted_string = ""
        for field in list(fields_to_extract):
            if not entry.get(field, None):
                continue

            if (
                "zip" in entry["name"].lower()
                and field == "options"
                and "encrypted" not in entry.get("options", "").lower()
            ):
                continue

            elif (
                "zip" in entry["name"].lower()
                and "encrypt" in entry.get("options", "").lower()
            ):
                entry["options"] = "encrypted"

            if len(entry[field]) != 0:
                formatted_string += (
                    replace(patterns_sting, entry[field]) + "_"
                )

        return formatted_string.rstrip("_")

    def process_sample(self, sample_path: str) -> list:
        """Analyze a given sample

        Args:
            sample_path (str): path to file

        Returns:
            list: a list of tags consumable by MWDB
                  e.g. 
                        [ 
                            "die:library_.net_v4.0.30319",
                            "die:archive_rar_5",
                            "die:overlay_rar_archive"
                        ]
        """
        diec_res = subprocess.check_output(
            [
                "diec",
                "-j",
                sample_path,
            ],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        try:
            diec_res_json = json.loads(diec_res)
        except Exception as err:
            self.log.error(err)
            return None
        else:

            diec_mapping: dict = {
                "compiler": None,
                "archive": None,
                "protector": None,
                "installer": None,
                "overlay": None,
                "sfx": None,
                "library": None,
                "packer": None,
            }

            for detect in diec_res_json["detects"]:
                for entry in detect["values"]:
                    for field, result in diec_mapping.items():
                        if entry.get("type", "").lower() == field:
                            diec_mapping[field] = self._format_sign(entry)

            signature_matches = list()
            for field, result in diec_mapping.items():
                if result:
                    signature_matches.append(f"die:{field}_{result}")

            return signature_matches

    def process(self, task: Task) -> None:
        sample = task.get_resource("sample")
        if task.headers["type"] == "sample":
            self.log.info(f"Processing sample {sample.metadata['sha256']}")
            with sample.download_temporary_file() as f:
                sample_path = f.name
                die_signatures: list = self.process_sample(sample_path)

        if not die_signatures:
            self.log.info("Could not match signatures")
            return None

        tag_task = Task(
            headers={"type": "sample", "stage": "analyzed"},
            payload={"sample": sample, "tags": die_signatures},
        )

        self.send_task(tag_task)
