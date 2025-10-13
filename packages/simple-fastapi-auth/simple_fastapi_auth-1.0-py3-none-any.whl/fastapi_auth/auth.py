from typing import Optional, List, Callable, Any, Dict, TypeVar, ParamSpec
import sqlite3, inspect, os, threading, time
from datetime import datetime, timedelta
from contextlib import contextmanager
from functools import wraps

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, status, Request, Depends
from passlib.context import CryptContext
from fastapi.routing import APIRoute
from jose import jwt as jose_jwt
from pydantic import BaseModel

# ------------------------------------------------------------------
# 1.  Re-usable Pydantic models
# ------------------------------------------------------------------
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ------------------------------------------------------------------
# 2.  Internal helpers
# ------------------------------------------------------------------
def _make_get_db(db_path: str):
    @contextmanager
    def get_db():
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    return get_db

def _make_init_db(db_path: str):
    def init_db():
        with _make_get_db(db_path)() as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_used_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS token_blacklist (
                    token TEXT PRIMARY KEY,
                    blacklisted_at TEXT NOT NULL
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_tokens_user_id ON tokens(user_id)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_tokens_expires_at ON tokens(expires_at)")
    return init_db

# ------------------------------------------------------------------
# 3.  AuthManager
# ------------------------------------------------------------------
class AuthManager:
    def __init__(
        self,
        *,
        auth_endpoint: str = "/auth/login",
        jwt_secret_key: str = "k2jl3h-29c8bv-iknsdgf7",
        access_token_expire_minutes: int = 1440,
        token_renewal_minutes: int = 30,
        database_path: str = "auth.db",
    ):
        self.jwt_secret_key = jwt_secret_key
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = access_token_expire_minutes
        self.token_renewal_minutes = token_renewal_minutes
        self.database_path = database_path
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl=auth_endpoint)
        self.get_db = _make_get_db(database_path)
        self.init_db = _make_init_db(database_path)
        self.init_db()

    # ------- password helpers -------
    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return self.pwd_context.verify(plain, hashed)

    # ------- token lifecycle -------
    def create_token(self, data: Dict[str, Any]) -> str:
        if "user_id" not in data:
            raise ValueError("data must contain 'user_id'")
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = data.copy()
        to_encode.update(exp=expire, iat=now, sub=str(data["user_id"]))
        token = jose_jwt.encode(to_encode, self.jwt_secret_key, algorithm=self.jwt_algorithm)
        with self.get_db() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO tokens (token, user_id, created_at, last_used_at, expires_at) VALUES (?,?,?,?,?)",
                (token, str(data["user_id"]), now.isoformat(), now.isoformat(), expire.isoformat())
            )
            # keep only last 3 tokens per user
            c.execute(
                """
                DELETE FROM tokens
                WHERE user_id=? AND token NOT IN (
                    SELECT token FROM tokens WHERE user_id=? ORDER BY created_at DESC LIMIT 3
                )
                """,
                (str(data["user_id"]), str(data["user_id"]))
            )
        return token

    def verify_token(self, token: str, allowed_roles: Optional[List[str]] = None) -> Dict[str, Any]:
        exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jose_jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise exc
        except jose_jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jose_jwt.JWTError:
            raise exc

        with self.get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT 1 FROM token_blacklist WHERE token=?", (token,))
            if c.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            row = c.execute(
                "SELECT last_used_at, expires_at FROM tokens WHERE token=?", (token,)
            ).fetchone()
            if not row:
                raise exc
            last_used = datetime.fromisoformat(row["last_used_at"])
            if datetime.utcnow() - last_used > timedelta(minutes=self.token_renewal_minutes):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token renewal period expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            c.execute("UPDATE tokens SET last_used_at=? WHERE token=?", (datetime.utcnow().isoformat(), token))

        user_role = payload.get("role")
        if allowed_roles and user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Allowed roles: {allowed_roles}",
            )
        return {"user_id": user_id, "role": user_role, "payload": payload}

    def blacklist_token(self, token: str):
        with self.get_db() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT OR IGNORE INTO token_blacklist (token, blacklisted_at) VALUES (?,?)",
                (token, datetime.utcnow().isoformat())
            )
            c.execute("DELETE FROM tokens WHERE token=?", (token,))

    def cleanup_expired_tokens(self):
        with self.get_db() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM tokens WHERE expires_at < ?", (datetime.utcnow().isoformat(),))
            cutoff = (datetime.utcnow() - timedelta(days=30)).isoformat()
            c.execute("DELETE FROM token_blacklist WHERE blacklisted_at < ?", (cutoff,))

# ------------------------------------------------------------------
# 4.  Global singleton + auto-start cleanup
# ------------------------------------------------------------------
_auth_manager: Optional[AuthManager] = None
_cleanup_thread: Optional[threading.Thread] = None
_lock = threading.Lock()

def _start_cleanup(mgr: AuthManager) -> None:
    """Ensure the janitor thread is running exactly once."""
    global _cleanup_thread
    if _cleanup_thread is None or not _cleanup_thread.is_alive():
        _cleanup_thread = start_cleanup_worker(mgr)

def get_auth_manager() -> AuthManager:
    global _auth_manager
    if _auth_manager is None:
        with _lock:
            if _auth_manager is None:
                _auth_manager = AuthManager()
                _start_cleanup(_auth_manager)
    return _auth_manager

def setup_auth(**kwargs) -> AuthManager:
    global _auth_manager
    with _lock:
        _auth_manager = AuthManager(**kwargs)
        _start_cleanup(_auth_manager)
    return _auth_manager

# ------------------------------------------------------------------
# 5.  Built-in auth router
# ------------------------------------------------------------------
P = ParamSpec("P")
T = TypeVar("T")

class AuthRouterBuilder:
    """
    Builds a ready-to-mount /auth router with login/logout/register
    while letting the caller supply only two functions:
        1. authenticate_user(username, password) -> Optional[dict]   (must return at least {"user_id": str, "role": str})
        2. create_user(user_dict) -> None   (user_dict contains username, password, role, and any extra metadata)
    """
    def __init__(
        self,
        *,
        authenticate_user: Callable[[str, str], Optional[Dict[str, Any]]],
        create_user: Callable[[Dict[str, Any]], None],
        auth_manager: Optional[AuthManager] = None,
        register_model: Optional[type[BaseModel]] = None,
    ):
        self.am = auth_manager or get_auth_manager()
        self.authenticate = authenticate_user
        self.create_user_fn = create_user
        # allow caller to supply a custom register model with extra fields
        self.RegisterModel = register_model or UserRegister

    def router(self) -> APIRouter:
        router = APIRouter(prefix="/auth", tags=["Auth"])

        @router.post("/login", response_model=TokenResponse)
        async def login(form_data: OAuth2PasswordRequestForm = Depends()):
            user = self.authenticate(form_data.username, form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            token = self.am.create_token({"user_id": user["user_id"], "role": user["role"]})
            return TokenResponse(access_token=token, token_type="bearer")

        @router.post("/logout")
        async def logout(request: Request):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authorization header",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            token = auth_header.replace("Bearer ", "")
            self.am.blacklist_token(token)
            return {"message": "Logged out successfully"}

        @router.post("/register")
        async def register(body: self.RegisterModel):  # type: ignore
            # body is an instance of UserRegister (or custom model)
            user_dict = body.dict()
            # quick uniqueness check (optional – can be removed if you want to handle in create_user)
            # here we just call the supplied function and let it raise if desired
            self.create_user_fn(user_dict)
            return {"message": "User registered successfully"}

        return router

# Convenience Factory
def build_auth_router(
    *,
    authenticate_user: Callable[[str, str], Optional[Dict[str, Any]]],
    create_user: Callable[[Dict[str, Any]], None],
    auth_manager: Optional[AuthManager] = None,
    register_model: Optional[type[BaseModel]] = None,
) -> APIRouter:
    return AuthRouterBuilder(
        authenticate_user=authenticate_user,
        create_user=create_user,
        auth_manager=auth_manager,
        register_model=register_model,
    ).router()

# ------------------------------------------------------------------
# 6.  Decorator that validates the token and roles
# ------------------------------------------------------------------
def restrict(roles_allowed: Optional[List[str]] = None, inject_user: bool = False):
    """
    Decorator that adds role-based JWT validation.
    
    Args:
        roles_allowed: List of allowed roles
        inject_user: If True, injects 'current_user' dict into the endpoint
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        mgr = get_auth_manager()
        
        def _check_auth(request: Request, token: str = Depends(mgr.oauth2_scheme)) -> Dict[str, Any]:
            data = mgr.verify_token(token, allowed_roles=roles_allowed)
            request.state.user_id = data["user_id"]
            request.state.role = data["role"]
            request.state.token_payload = data["payload"]
            return data
        
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        
        request_param = inspect.Parameter(
            'request',
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Request
        )
        auth_data_param = inspect.Parameter(
            '_auth_data',
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=Depends(_check_auth),
            annotation=Dict[str, Any]
        )
        
        # Add request if not present
        if 'request' not in sig.parameters:
            params.insert(0, request_param)
        
        # Add current_user parameter if requested and not present
        if inject_user and 'current_user' not in sig.parameters:
            user_param = inspect.Parameter(
                'current_user',
                inspect.Parameter.KEYWORD_ONLY,
                annotation=Dict[str, Any]
            )
            params.append(user_param)
        
        params.append(auth_data_param)
        new_sig = sig.replace(parameters=params)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_data = kwargs.pop('_auth_data', None)
            
            # Inject current_user if requested
            if inject_user and auth_data:
                kwargs['current_user'] = {
                    "user_id": auth_data["user_id"],
                    "role": auth_data["role"],
                    "payload": auth_data["payload"]
                }
            
            # Remove request if original function doesn't expect it
            if 'request' not in sig.parameters:
                kwargs.pop('request', None)
            
            return func(*args, **kwargs)
        
        wrapper.__signature__ = new_sig
        return wrapper
    
    return decorator

# ------------------------------------------------------------------
# 7.  One-line protect_router(router)” helper
# ------------------------------------------------------------------
def protect_router(router: APIRouter, *, manager: Optional[AuthManager] = None) -> None:
    """
    Ensures every route in *router* that uses @restrict gets the automatic
    Request injection resolved by FastAPI.
    """
    mgr = manager or get_auth_manager()
    scheme_dep = Depends(mgr.oauth2_scheme)

    for route in router.routes:
        if not isinstance(route, APIRoute):
            continue
        # skip if already protected
        if any(
            getattr(dep, "dependency", None) is mgr.oauth2_scheme
            for dep in (route.dependencies or [])
        ):
            continue

        # if the endpoint function was wrapped by @restrict, add its own dependency
        endpoint = route.endpoint
        if hasattr(endpoint, "_dependency"):
            route.dependencies = [endpoint._dependency, scheme_dep, *(route.dependencies or [])]
        else:
            route.dependencies = [scheme_dep, *(route.dependencies or [])]

def get_current_user(request: Request) -> Dict[str, Any]:
    """Extract authenticated user from request.state"""
    return {
        "user_id": request.state.user_id,
        "role": request.state.role,
        "payload": request.state.token_payload
    }

# ------------------------------------------------------------------
# 8.  Non-blocking periodic cleanup
# ------------------------------------------------------------------
DEFAULT_CLEANUP_INTERVAL = int(os.getenv("AUTH_CLEANUP_INTERVAL_MIN", "15"))      # minutes
CLEANUP_CHUNK_SIZE       = int(os.getenv("AUTH_CLEANUP_CHUNK_SIZE", "500"))       # rows
CLEANUP_BATCH_PAUSE      = float(os.getenv("AUTH_CLEANUP_BATCH_PAUSE_MS", "150"))  # ms

def _cleanup_once(manager: AuthManager) -> None:
    """Delete expired tokens and very old blacklist entries in small chunks."""
    now = datetime.utcnow().isoformat()
    cutoff_blacklist = (datetime.utcnow() - timedelta(days=30)).isoformat()

    with manager.get_db() as conn:
        cur = conn.cursor()

        # 1. expired tokens
        while True:
            cur.execute(
                "DELETE FROM tokens WHERE expires_at < ? LIMIT ?",
                (now, CLEANUP_CHUNK_SIZE)
            )
            deleted = cur.rowcount
            conn.commit()
            if deleted < CLEANUP_CHUNK_SIZE:
                break
            time.sleep(CLEANUP_BATCH_PAUSE / 1000.0)

        # 2. stale blacklist
        while True:
            cur.execute(
                "DELETE FROM token_blacklist WHERE blacklisted_at < ? LIMIT ?",
                (cutoff_blacklist, CLEANUP_CHUNK_SIZE)
            )
            deleted = cur.rowcount
            conn.commit()
            if deleted < CLEANUP_CHUNK_SIZE:
                break
            time.sleep(CLEANUP_BATCH_PAUSE / 1000.0)

def _worker(manager: AuthManager, interval_minutes: int):
    while True:
        try:
            print(f"Starting cleanup thread (interval {interval_minutes} minutes)")
            time.sleep(interval_minutes * 60)
            _cleanup_once(manager)
        except Exception as exc:
            print(f"Error in cleanup thread: {exc}", )

def start_cleanup_worker(
    manager: Optional[AuthManager] = None,
    interval_minutes: int = DEFAULT_CLEANUP_INTERVAL
) -> threading.Thread:
    """Launch daemon thread.  Call once per process that keeps the DB open."""
    mgr = manager or get_auth_manager()
    t = threading.Thread(
        target=_worker,
        args=(mgr, interval_minutes),
        daemon=True,
        name="auth-cleanup"
    )
    t.start()
    return t
