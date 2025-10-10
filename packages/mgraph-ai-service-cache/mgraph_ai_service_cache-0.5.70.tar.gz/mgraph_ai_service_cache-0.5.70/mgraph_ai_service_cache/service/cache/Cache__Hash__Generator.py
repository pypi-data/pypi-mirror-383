import hashlib
import json
from typing                                                      import List
from osbot_utils.type_safe.Type_Safe                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash                      import Safe_Str__Cache_Hash
from mgraph_ai_service_cache.service.cache.Cache__Hash__Config   import Cache__Hash__Config, Enum__Hash__Algorithm

class Cache__Hash__Generator(Type_Safe):                                           # Generate consistent hashes from various input types
    config: Cache__Hash__Config

    def calculate(self, data: bytes) -> Safe_Str__Cache_Hash:                      # Calculate hash from raw bytes
        if self.config.algorithm == Enum__Hash__Algorithm.MD5:
            hash_full = hashlib.md5(data).hexdigest()
        elif self.config.algorithm == Enum__Hash__Algorithm.SHA256:
            hash_full = hashlib.sha256(data).hexdigest()
        elif self.config.algorithm == Enum__Hash__Algorithm.SHA384:
            hash_full = hashlib.sha384(data).hexdigest()

        return Safe_Str__Cache_Hash(hash_full[:self.config.length])

    def from_string(self, data: str) -> Safe_Str__Cache_Hash:                       # Hash from string
        return self.calculate(data.encode('utf-8'))

    def from_bytes(self, data: bytes) -> Safe_Str__Cache_Hash:                      # Hash from bytes
        return self.calculate(data)

    def from_json(self, data      : dict     ,                                      # Hash JSON with optional field exclusion
                        exclude_fields: List[str] = None
                   ) -> Safe_Str__Cache_Hash:
        if exclude_fields:
            data = {k: v for k, v in data.items() if k not in exclude_fields}
        json_str = json.dumps(data, sort_keys=True)
        return self.from_string(json_str)

    def from_type_safe(self, obj           : Type_Safe     ,                      # Hash Type_Safe object
                            exclude_fields : List[str] = None
                       ) -> Safe_Str__Cache_Hash:
        return self.from_json(obj.json(), exclude_fields)