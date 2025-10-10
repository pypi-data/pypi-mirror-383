from typing                                                                         import Union
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path   import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid               import Random_Guid
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id     import Safe_Str__Id
from mgraph_ai_service_cache_client.schemas.cache.consts__Cache_Service                    import DEFAULT_CACHE__NAMESPACE
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type             import Enum__Cache__Data_Type


class Schema__Cache__Data__Store__Request(Type_Safe):
    cache_id    : Random_Guid               = None
    data        : Union[str, dict, bytes]   = None                           # Data to store as child
    data_type   : Enum__Cache__Data_Type    = None                           # Type: 'string', 'json', or 'binary'
    data_key    : Safe_Str__File__Path      = None
    data_file_id: Safe_Str__Id              = None
    namespace   : Safe_Str__Id              = DEFAULT_CACHE__NAMESPACE