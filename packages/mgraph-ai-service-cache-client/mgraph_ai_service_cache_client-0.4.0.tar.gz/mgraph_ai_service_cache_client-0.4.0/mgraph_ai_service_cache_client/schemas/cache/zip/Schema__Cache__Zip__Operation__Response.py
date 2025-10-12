from typing                                                                                      import List, Dict, Any, Optional
from osbot_utils.type_safe.Type_Safe                                                             import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                             import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                            import Random_Guid
from mgraph_ai_service_cache_client.schemas.cache.zip.enums.Enum__Cache__Zip__Operation                 import Enum__Cache__Zip__Operation
from mgraph_ai_service_cache_client.schemas.cache.zip.safe_str.Safe_Str__Cache__Zip__Operation__Message import Safe_Str__Cache__Zip__Operation__Message


class Schema__Cache__Zip__Operation__Response(Type_Safe):                                  # Response from zip operation
    success           : bool                                                                # Whether operation succeeded
    operation         : Enum__Cache__Zip__Operation                                         # Operation that was performed
    cache_id          : Random_Guid                                 = None                  # ID of the zip file operated on
    original_cache_id : Optional[Random_Guid]                       = None
    message           : Safe_Str__Cache__Zip__Operation__Message    = None                  # Optional status message
    file_list         : List[Safe_Str__File__Path]                                         # For list operation
    file_content      : bytes                                                              # For get operation
    file_size         : Safe_UInt                                                          # Size of retrieved file
    files_affected    : List[Safe_Str__File__Path]                                          # Files that were changed
    error_details     : Safe_Str__Cache__Zip__Operation__Message                          # Error information if failed