import json
import pathlib
from collections import Counter

class DeepSeekNormalizer:
    ROOT_DIR = pathlib.Path(__file__).parent.parent.parent
    
    def __init__(self, records_file: str = "re.json"):
        self.RAW_DATA_DIR = self.ROOT_DIR / "data" / "raw" / "deepseek_batches"
        self.records_file = self.RAW_DATA_DIR / records_file
        self.records = self.load_records()
        self.id = 1
        self.sense_id = 1
        self.dedup()

    def load_records(self):
        with open(self.records_file, "r") as f:
            return json.load(f)
    
    def normalize_record(self, record):    
        infl = record.get("infl", ["third_person_singular", "past_tense", "past_paticiple", "present_participle"]),
        i = infl[0] if infl else None
        normalized_record = {
            "id": self.id,
            "lemma": record.get("lemma", "").strip(),
            "inflections": {
                "third_person_singular": i[0] if i and len(i) > 0 else "",
                "past_tense": i[1] if i and len(i) > 1 else "",
                "past_participle": i[2] if i and len(i) > 2 else "",
                "present_participle": i[3] if i and len(i) > 3 else "",
            },
            "senses": [],
        }
        
        if "def" in record and record["def"]:
            normalized_record["senses"].append({
                "sense_id": f"{normalized_record['lemma']}_{self.sense_id}",
                "definition": record["def"].strip(),
                "examples": [record.get("ex", "").strip()] if record.get("ex") else []
            })
        
        if "senses" in record:
            for sense in record["senses"]:
                normalized_record["senses"].append({
                    "sense_id": f"{normalized_record['lemma']}_{self.sense_id}",
                    "definition": sense.get("def", "").strip(),
                    "examples": [sense.get("ex", "").strip()] if sense.get("ex") else []
                })
                self.sense_id += 1
        normalized_record["sources"] = [{"source_name": "DeepSeek", "source_url": "https://chat.deepseek.com"}]
        normalized_record["part_of_speech"] = "verb"
        normalized_record["generation_method"] = "ai"
        normalized_record["verification_status"] = "pending"
        self.id += 1
        return normalized_record
    
    def dedup(self):
        counts = Counter(
            record.get("lemma", "").strip().casefold()
            for record in self.records
            if isinstance(record.get("lemma"), str)
            and record["lemma"].strip()
        )

        duplicates = {
            lemma: count
            for lemma, count in counts.items()
            if count > 1
        }

        print(f"Input records: {len(self.records)}")
        print(f"Distinct lemmas: {len(counts)}")
        print(f"Lemmas appearing more than once: {len(duplicates)}")

        for lemma, count in duplicates.items():
            print(f"  {lemma}: {count} records")

        return duplicates
    
    def dump_records(self, output_file: str = "normalized_records.json", dudeup_out: str = "duplicates.json"):
        normalized_records = [self.normalize_record(record) for record in self.records]
        output_path = self.RAW_DATA_DIR / output_file
        with open(output_path, "w") as f:
            json.dump(normalized_records, f, indent=4)
        print(f"Normalized records dumped to {output_path}")

        duplicates = self.dedup()
        if duplicates:
            duplicates_path = self.RAW_DATA_DIR / dudeup_out
            with open(duplicates_path, "w") as f:
                json.dump(duplicates, f, indent=4)
            print(f"Duplicate records dumped to {duplicates_path}")
    
if __name__ == "__main__":
    normalizer = DeepSeekNormalizer()
    normalizer.dedup()
    normalizer.dump_records()
    print("Records Done")