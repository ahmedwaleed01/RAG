from enum import Enum

class ResponeseEnum(Enum):

    FILE_VALIDATED_SUCCESS = "file_validate_successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"

    FILE_PROCESS_FAILED ="file_process_failed"
    NO_FILE_TO_PROCESS = "no_file_to_process"

    PROJECT_NOT_FOUND = "project_not_found"
    VECTOR_DB_ERROR = "error_vector_db_insertion"
    VECTOR_DB_SUCCESS = "success_vector_db_insertion"
