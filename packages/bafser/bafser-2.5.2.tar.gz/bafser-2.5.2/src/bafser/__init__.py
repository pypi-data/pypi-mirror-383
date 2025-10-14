# base for flask server by Mixel Te

try:
    import bafser_config  # type: ignore
except ModuleNotFoundError:
    import os
    import sys
    sys.path.append(os.getcwd())
    try:
        import bafser_config
    except ModuleNotFoundError:
        import shutil
        current = os.path.dirname(__file__)
        cfg_src = os.path.join(current, "bafser_config.example.py")
        cfg_dst = os.path.join(os.getcwd(), "bafser_config.py")
        shutil.copy(cfg_src, cfg_dst)
        with_tgapi = False
        try:
            import bafser_tgapi  # type: ignore
        except ModuleNotFoundError:
            pass
        except Exception:
            with_tgapi = True
        if with_tgapi:
            cfg_tg_src = os.path.join(current, "bafser_config.tgapi.py")
            with open(cfg_tg_src, encoding="utf8") as f:
                cfg_tg = f.read()
            with open(cfg_dst, "a", encoding="utf8") as f:
                f.write("\n" + cfg_tg)

from .utils.response_msg import response_msg
from .utils.get_json_values import get_json_values, get_json_list

from .utils.create_file_response import create_file_response
from .utils.create_folder_for_file import create_folder_for_file
from .utils.get_datetime_now import get_datetime_now
from .utils.get_db_session import get_db_session, override_get_db_session
from .utils.get_json import get_json
from .utils.get_json_values_from_req import get_json_values_from_req, get_json_list_from_req
from .utils.get_userId import get_userId_required, get_userId
from .utils.ip_to_emoji import ip_to_emoji, emoji_to_ip
from .utils.jsonify_list import jsonify_list
from .utils.listfind import listfind
from .utils.parse_date import parse_date
from .utils.permission_required import create_permission_required_decorator
from .utils.permission_required import permission_required, permission_required_any
from .utils.randstr import randstr
from .utils.response_not_found import response_not_found
from .utils.use_db_session import use_db_session, use_db_sess
from .utils.use_user import use_user  # pyright: ignore[reportDeprecated]
from .utils.use_userId import use_userId  # pyright: ignore[reportDeprecated]

from .app import AppConfig, create_app, update_message_to_frontend, get_app_config
from .logger import get_logger_frontend, log_frontend_error, get_log_fpath, add_file_logger, ParametrizedLogger
from .authentication import create_access_token, get_user_by_jwt_identity, get_user_id_by_jwt_identity
from .jsonobj import JsonObj, JsonOpt, Undefined, JsonParseError
from .doc_api import doc_api, get_api_docs, JsonSingleKey, render_docs_page

from .db_session import SqlAlchemyBase
from .table_base import IdMixin, ObjMixin, SingletonMixin
from .data._tables import TablesBase
from .data._roles import RolesBase
from .data.operation import OperationsBase, OperationDict
from .data.user_role import UserRole
from .data.user import UserBase, UserKwargs, UserDict, UserDictFull, override_get_current_user
from .data.log import Log, LogDict
from .data.role import Role, RoleDict
from .data.image import Image, ImageKwargs, ImageDict, ImageJson


class M:
    DELETE = "DELETE"
    GET = "GET"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"


__all__ = [
    "M",
    "response_msg",
    "get_json_values", "get_json_list",

    "create_file_response",
    "create_folder_for_file",
    "create_permission_required_decorator",
    "get_datetime_now",
    "get_db_session", "override_get_db_session",
    "get_json",
    "get_json_values_from_req", "get_json_list_from_req",
    "get_userId_required", "get_userId",
    "ip_to_emoji", "emoji_to_ip",
    "jsonify_list",
    "listfind",
    "parse_date",
    "permission_required", "permission_required_any",
    "randstr",
    "response_not_found",
    "use_db_session", "use_db_sess",
    "use_user",
    "use_userId",

    "AppConfig", "create_app", "update_message_to_frontend", "get_app_config",
    "get_logger_frontend", "log_frontend_error", "get_log_fpath", "add_file_logger", "ParametrizedLogger",
    "create_access_token", "get_user_by_jwt_identity", "get_user_id_by_jwt_identity",
    "JsonObj", "JsonOpt", "Undefined", "JsonParseError",
    "doc_api", "get_api_docs", "JsonSingleKey", "render_docs_page",

    "SqlAlchemyBase",
    "IdMixin", "ObjMixin", "SingletonMixin",
    "TablesBase",
    "RolesBase",
    "OperationsBase", "OperationDict",
    "UserRole",
    "UserBase", "UserKwargs", "UserDict", "UserDictFull", "override_get_current_user",
    "Log", "LogDict",
    "Role", "RoleDict",
    "Image", "ImageKwargs", "ImageDict", "ImageJson",
]
