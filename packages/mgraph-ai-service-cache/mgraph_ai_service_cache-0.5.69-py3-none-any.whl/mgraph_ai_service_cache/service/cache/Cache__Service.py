import gzip
import json
from typing                                                                              import Dict, Optional, Any, List
from memory_fs.schemas.Schema__Memory_FS__File__Metadata                                 import Schema__Memory_FS__File__Metadata
from memory_fs.schemas.Schema__Memory_FS__File__Config                                   import Schema__Memory_FS__File__Config
from osbot_utils.decorators.methods.cache_on_self                                        import cache_on_self
from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path        import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id          import Safe_Str__Id
from osbot_utils.utils.Files                                                             import file_extension, file_name_without_extension
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                    import Random_Guid
from osbot_utils.utils.Http                                                              import url_join_safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash import Safe_Str__Cache_Hash
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Refs         import Schema__Cache__File__Refs
from mgraph_ai_service_cache_client.schemas.cache.consts__Cache_Service                  import DEFAULT_CACHE__NAMESPACE
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Store__Strategy     import Enum__Cache__Store__Strategy
from mgraph_ai_service_cache_client.schemas.cache.store.Schema__Store__Context           import Schema__Store__Context
from mgraph_ai_service_cache.service.cache.Cache__Config                                 import Cache__Config
from mgraph_ai_service_cache.service.cache.Cache__Handler                                import Cache__Handler
from mgraph_ai_service_cache.service.cache.Cache__Hash__Config                           import Cache__Hash__Config
from mgraph_ai_service_cache.service.cache.Cache__Hash__Generator                        import Cache__Hash__Generator
from mgraph_ai_service_cache_client.schemas.cache.Schema__Cache__Store__Response         import Schema__Cache__Store__Response
from mgraph_ai_service_cache.service.cache.store.Cache__Service__Store__With_Strategy    import Cache__Service__Store__With_Strategy


class Cache__Service(Type_Safe):                                                    # Main cache service orchestrator
    cache_config      : Cache__Config                                               # Configuration object
    cache_handlers    : Dict[Safe_Str__Id, Cache__Handler]                          # Multiple cache handlers by namespace
    hash_config       : Cache__Hash__Config                                         # Hash generation config
    hash_generator    : Cache__Hash__Generator                                      # Hash generator instance

    # todo: I think we can now remove this file and just use the self.storage_fs()
    @cache_on_self
    def storage_backend(self):                                                      # Create and cache the storage backend
        return self.cache_config.create_storage_backend()

    @cache_on_self
    def storage_fs(self):                                                           # Return storage backend for direct operations
        return self.storage_backend()                                               # This is used for admin operations that need direct storage access

    # todo: this logic is starting to be quite complex to be in a method, I think we can refactor this logic into a separate class and have methods for
    #       each logic step/action
    def delete_by_id(self, cache_id: Random_Guid, namespace: Safe_Str__Id = None) -> Dict[str, Any]:
        namespace = namespace or Safe_Str__Id("default")
        handler   = self.get_or_create_handler(namespace)

        with handler.fs__refs_id.file__json(Safe_Str__Id(str(cache_id))) as ref_fs:
            if not ref_fs.exists():
                return {"status": "not_found", "message": f"Cache ID {cache_id} not found"}

            id_ref_data  = ref_fs.content()
            all_paths    = id_ref_data.get("all_paths", {})
            cache_hash   = id_ref_data.get("cache_hash")
            strategy     = id_ref_data.get("strategy")

        deleted_paths = []                                                                          # Track deletion results
        failed_paths  = []

        fs_data = handler.get_fs_for_strategy(strategy)                                             # Delete data files first (use the appropriate fs based on strategy)
        for path in all_paths.get("data", []):
            try:
                if fs_data.storage_fs.file__delete(path):
                    deleted_paths.append(path)
                else:
                    failed_paths.append(path)
            except Exception as e:
                failed_paths.append(f"{path}: {str(e)}")

        if cache_hash:                                                                              # Update hash reference (remove this cache_id from the list)
            with handler.fs__refs_hash.file__json(Safe_Str__Id(cache_hash)) as ref_fs:
                if ref_fs.exists():
                    refs                   = ref_fs.content()
                    refs["cache_ids"]      = [entry for entry in refs["cache_ids"]                  # Remove this cache_id from the list
                                              if entry["cache_id"] != str(cache_id)]
                    refs["total_versions"] -= 1

                    if refs["total_versions"] > 0:
                        if refs["latest_id"] == str(cache_id) and refs["cache_ids"]:                # Update the latest_id if needed
                            refs["latest_id"] = refs["cache_ids"][-1]["cache_id"]
                        ref_fs.update(file_data=refs)
                    else:
                        for path in all_paths.get("by_hash", []):                                   # No more versions, delete the hash reference files
                            try:
                                if handler.fs__refs_hash.storage_fs.file__delete(path):
                                    deleted_paths.append(path)
                                else:
                                    failed_paths.append(path)
                            except Exception as e:
                                failed_paths.append(f"{path}: {str(e)}")

        for path in all_paths.get("by_id", []):                                                 # Finally, delete the ID reference files
            try:
                if handler.fs__refs_id.storage_fs.file__delete(path):
                    deleted_paths.append(path)
                else:
                    failed_paths.append(path)
            except Exception as e:
                failed_paths.append(f"{path}: {str(e)}")

        return { "status"        : "success" if not failed_paths else "partial",                    # todo: this should be a Type_Safe class
                 "cache_id"      : str(cache_id)        ,
                 "deleted_count" : len(deleted_paths)   ,
                 "failed_count"  : len(failed_paths)    ,
                 "deleted_paths" : deleted_paths        ,
                 "failed_paths"  : failed_paths         }

    def get_all_namespaces_stats(self) -> Dict[str, Any]:                          # Get file counts for all active namespaces
        all_stats = {}

        for namespace in self.cache_handlers.keys():
            counts_data = self.get_namespace__file_counts(namespace)
            all_stats[str(namespace)] = {
                'total_files': counts_data['total_files'],
                'file_counts': counts_data['file_counts']
            }

        return { 'namespaces'       : all_stats                 ,                               # todo: this should be a Type_Safe class
                 'total_namespaces' : len(self.cache_handlers)  ,
                 'grand_total_files': sum(ns['total_files'] for ns in all_stats.values()),
                 'storage_mode'     : self.cache_config.storage_mode.value                }     # Include storage mode in stats


    def get_namespace__file_hashes(self, namespace: Safe_Str__Id) -> List[str]:
        file_hashes = []
        handler = self.get_or_create_handler(namespace)

        parent_folder = url_join_safe(str(namespace), "refs/by-hash")                                           # Build the namespace-specific folder path

        for file_path in handler.fs__refs_hash.storage_fs.folder__files__all(parent_folder=parent_folder):      # Use folder__files__all to get only files in this namespace's refs/by-hash folder
            if file_extension(file_path) == '.json':
                file_id     = file_name_without_extension(file_path)                                            # Extract just the hash part (last segment after any sharding)
                hash_parts  = file_id.split('/')
                if hash_parts:
                    file_hashes.append(hash_parts[-1])
        return file_hashes

    def get_namespace__file_ids(self, namespace: Safe_Str__Id) -> List[str]:
        file_ids = []
        handler = self.get_or_create_handler(namespace)

        parent_folder = url_join_safe(str(namespace), "refs/by-id")                                             # Build the namespace-specific folder path

        for file_path in handler.fs__refs_id.storage_fs.folder__files__all(parent_folder=parent_folder):        # Use folder__files__all to get only files in this namespace's refs/by-id folder
            if file_extension(file_path) == '.json':
                file_id = file_name_without_extension(file_path)
                id_parts = file_id.split('/')                                                                   # Extract just the ID part (last segment after any sharding)
                if id_parts:
                    file_ids.append(id_parts[-1])
        return file_ids

    def get_namespace__file_counts(self, namespace: Safe_Str__Id = None) -> Dict[str, Any]:       # Get file counts for all strategies in a namespace
        namespace = namespace or Safe_Str__Id("default")
        handler = self.get_or_create_handler(namespace)

        file_counts = {}
        total_files = 0

        for strategy in ["direct", "temporal", "temporal_latest", "temporal_versioned"]:
            try:
                fs = handler.get_fs_for_strategy(strategy)
                if fs and fs.storage_fs:
                    count = len(fs.storage_fs.files__paths())
                    file_counts[f"{strategy}_files"] = count
                    total_files += count
                else:
                    file_counts[f"{strategy}_files"] = 0
            except Exception:
                file_counts[f"{strategy}_files"] = 0

        # Count reference store files
        try:
            refs_hash_count = len(handler.fs__refs_hash.storage_fs.files__paths())
            file_counts['refs_hash_files'] = refs_hash_count
            total_files += refs_hash_count
        except Exception:
            file_counts['refs_hash_files'] = 0

        try:
            refs_id_count = len(handler.fs__refs_id.storage_fs.files__paths())
            file_counts['refs_id_files'] = refs_id_count
            total_files += refs_id_count
        except Exception:
            file_counts['refs_id_files'] = 0

        file_counts['total_files'] = total_files

        return {
            'namespace': str(namespace),
            'handler': handler,
            'file_counts': file_counts,
            'total_files': total_files,
            'storage_mode': self.cache_config.storage_mode.value                   # Include storage mode
        }

    def get_or_create_handler(self, namespace: Safe_Str__Id = DEFAULT_CACHE__NAMESPACE) -> Cache__Handler:
        if namespace not in self.cache_handlers:                                                         # Create handler with shared storage backend and namespace
            handler = Cache__Handler(storage_backend  = self.storage_backend(),                          # Shared storage backend
                                     namespace        = str(namespace),                                  # Namespace for path prefixing
                                     cache_ttl_hours  = self.cache_config.default_ttl_hours).setup()
            self.cache_handlers[namespace] = handler
        return self.cache_handlers[namespace]

    def get_storage_info(self) -> Dict[str, Any]:                                  # Get information about current storage configuration
        return self.cache_config.get_storage_info()

    # todo: see if we can't use the Schema__Store__Context as the main param here
    def store_with_strategy(self, storage_data     : Any                                             ,
                                  cache_hash       : Safe_Str__Cache_Hash                            ,
                                  strategy         : Enum__Cache__Store__Strategy                    ,
                                  cache_id         : Random_Guid           = None                    ,
                                  cache_key        : Safe_Str__File__Path  = None                    ,
                                  file_id          : Safe_Str__Id          = None                    ,
                                  namespace        : Safe_Str__Id          = DEFAULT_CACHE__NAMESPACE,
                                  content_encoding : Safe_Str__Id          = None                    ,
                                  metadata         : Dict[str, Any]        = None
                            ) -> Schema__Cache__Store__Response:                    # Store data using the specified strategy

        if not cache_hash:
            raise ValueError("in Cache__Service.store_with_strategy, the cache_hash must be provided")          # Validate inputs

        # todo this logic can be refactored to store_strategy.execute
        cache_id  = cache_id or Random_Guid()
        cache_key = Safe_Str__File__Path(cache_key) if cache_key else None
        file_id   = Safe_Str__Id(file_id or cache_id or Random_Guid())
        handler   = self.get_or_create_handler(namespace)
        context = Schema__Store__Context(storage_data     = storage_data     ,                                  # Build context with all parameters
                                         cache_hash       = cache_hash       ,
                                         cache_id         = cache_id         ,
                                         cache_key        = cache_key        ,
                                         file_id          = file_id          ,
                                         namespace        = namespace        ,
                                         strategy         = strategy         ,
                                         content_encoding = content_encoding ,
                                         handler          = handler          ,
                                         metadata         = metadata         )

        store_strategy = Cache__Service__Store__With_Strategy()
        return store_strategy.execute(context)                                                  # Execute storage strategy

    def retrieve_by_hash(self, cache_hash : Safe_Str__Cache_Hash,
                               namespace  : Safe_Str__Id = None
                          ) -> Optional[Dict[str, Any]]:                        # Retrieve latest by hash"""
        namespace = namespace or Safe_Str__Id("default")
        handler   = self.get_or_create_handler(namespace)

        with handler.fs__refs_hash.file__json(Safe_Str__Id(cache_hash)) as ref_fs:   # Get hash->ID mapping
            if not ref_fs.exists():
                return None
            refs = ref_fs.content()
            latest_id = refs.get("latest_id")

        if not latest_id:
            return None

        return self.retrieve_by_id(Random_Guid(latest_id), namespace)           # Delegate to retrieve_by_id which handles the path lookup

    # todo: same as with the delete method above,  this logic is starting to be too complex to be all in one method
    #       also I think we are doing too much here, with far too many calls to the file system
    #       at least we should just return the data (i.e. we don't need to return the metadata here (since there is an enpoint to get that)
    def retrieve_by_id(self, cache_id  : Random_Guid,
                             namespace : Safe_Str__Id = DEFAULT_CACHE__NAMESPACE
                        ):  #  -> Optional[Dict[str, Any]]:                     # todo: review this return value, since we had some exceptions here
        handler   = self.get_or_create_handler(namespace)

        # Get ID reference with content path
        with handler.fs__refs_id.file__json(Safe_Str__Id(cache_id)) as ref_fs:
            if not ref_fs.exists():
                return None
            ref_data = ref_fs.content()

        paths__content = ref_data.get("file_paths", {}).get("content_files")
        file_type     = ref_data.get("file_type", "json")

        if not paths__content:
            return None

        # Get the storage backend
        storage = handler.fs__refs_id.storage_fs

        # Read the content file directly (first path is the main content)
        content_path = paths__content[0] if paths__content else None

        if content_path and storage.file__exists(content_path):
            if file_type == "binary":
                data = storage.file__bytes(content_path)
            else:
                data = storage.file__json(content_path)

            # Read metadata                                         # todo: review the use of metadata here, since this probably one extra call we don't need to make (since we already have the data from the by-refs file
            metadata_path = content_path + '.metadata'              # todo: review this usage since we should have a much better way to do this using Memory_FS
            metadata_data = {}

            if storage.file__exists(metadata_path):
                metadata_raw = storage.file__json(metadata_path)
                # Convert metadata keys to Safe_Str__Id for consistency
                metadata_data = metadata_raw.get('data')            # todo: use native Memory_FS methods here (and we should be using a Type_Safe class here)

            # Get content encoding from metadata
            content_encoding = metadata_data.get('content_encoding')

            # Handle decompression if needed
            if content_encoding == 'gzip' and isinstance(data, bytes):
                data = gzip.decompress(data)
                # After decompression, determine if it's JSON or remains binary
                try:                                            # todo: we should know this from the metadata/config
                    data = json.loads(data.decode('utf-8'))
                    data_type = "json"
                except (json.JSONDecodeError, UnicodeDecodeError):
                    data_type = "binary"
            else:
                data_type = self.determine_data_type(data)

            return { "data"            : data             ,                     # ths should be a Type_Safe class
                     "metadata"        : metadata_data    ,
                     "data_type"       : data_type        ,
                     "content_encoding": content_encoding }

        return None

    def retrieve_by_id__config(self, cache_id  : Random_Guid,
                                     namespace : Safe_Str__Id
                                ) -> Schema__Memory_FS__File__Config:                    #   Retrieve by cache ID using direct path from reference
        handler   = self.get_or_create_handler(namespace)

        with handler.fs__refs_id.file__json(Safe_Str__Id(cache_id)) as ref_fs:           # get the main by-id file, which contains pointers to the other files
            return ref_fs.config()

    def retrieve_by_id__metadata(self, cache_id  : Random_Guid,
                                     namespace : Safe_Str__Id
                                ) -> Schema__Memory_FS__File__Metadata:                  #   Retrieve by cache ID using direct path from reference
        handler   = self.get_or_create_handler(namespace)

        with handler.fs__refs_id.file__json(Safe_Str__Id(cache_id)) as ref_fs:           # get the main by-id file, which contains pointers to the other files
            return ref_fs.metadata()

    def retrieve_by_id__refs(self, cache_id  : Random_Guid,
                                   namespace : Safe_Str__Id
                                ) -> Schema__Cache__File__Refs:                      #   Retrieve by cache ID using direct path from reference
        if cache_id:
            handler   = self.get_or_create_handler(namespace)
            with handler.fs__refs_id.file__json(Safe_Str__Id(cache_id)) as ref_fs:           # get the main by-id file, which contains pointers to the other files
                json_data = ref_fs.content()                                                 # todo refactor this so that we get the Schema__Cache__File__Refs directly from fs__refs_id
                if json_data:
                    return Schema__Cache__File__Refs.from_json(json_data)
        return None

    def determine_data_type(self, data) -> str:
        if isinstance(data, bytes):
            return "binary"
        elif isinstance(data, dict) or isinstance(data, list):
            return "json"
        else:
            return "string"

    def hash_from_string(self, data: str) -> Safe_Str__Cache_Hash:                       # Calculate hash from string
        return self.hash_generator.from_string(data)

    def hash_from_bytes(self, data: bytes) -> Safe_Str__Cache_Hash:                      # Calculate hash from bytes
        return self.hash_generator.from_bytes(data)

    def hash_from_json(self, data          : dict        ,                               # Calculate hash from JSON
                             exclude_fields : List[str] = None
                        ) -> Safe_Str__Cache_Hash:
        return self.hash_generator.from_json(data, exclude_fields)