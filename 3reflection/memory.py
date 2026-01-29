from typing import List, Dict, Any, Optional


class Memory:

    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def add_record(self, record_type: str, content: str):
        record = {"type": record_type, "content": content}
        self.records.append(record)

    def get_trajactory(self) -> str:
        trajactory_parts = []
        for record in self.records:
            if record["type"] == "execution":
                trajactory_parts.append(f"--former tried coede---\n{record['content']}")
            elif record["type"] == "reflection":
                trajactory_parts.append(f"--reflection---\n{record['content']}")
        return "\n\n".join(trajactory_parts)
    
    def get_last_execution(self) -> Optional[str]:
        for record in reversed(self.records):
            if record["type"] == "execution":
                return record["content"]
        return None
