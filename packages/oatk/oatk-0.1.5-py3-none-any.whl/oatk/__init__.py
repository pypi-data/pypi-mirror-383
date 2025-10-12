__version__ = "0.1.5"

import logging

import json
import uuid

import jwt
from authlib.jose import jwk

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from functools import wraps
from flask import request, Response

import requests

from oatk import fake

logger = logging.getLogger(__name__)

try:
  from AppKit import NSPasteboard, NSStringPboardType
  pb = NSPasteboard.generalPasteboard()
except ModuleNotFoundError:
  logger.debug("No AppKit installed, so no MacOS clipboard support!")
  pb = None

class OAuthToolkit():
  def __init__(self):
    self._encoded      = None
    self._provider_url = None
    self._certs        = {}
    logger.warning("certs init")
    self._private_key  = None
    self._public_key   = None
    self._alg          = "RS256"
    self._kid          = str(uuid.uuid4())
    self._claims       = {}
    self._client_id    = None

    self.server        = fake.server
    self.server.oatk   = self

  def _log_certs(self, msg):
    logger.info(msg)
    logger.info(json.dumps(list(self._certs.keys()), indent=2, default=str))

  @property
  def version(self):
    return __version__

  def with_private(self, path):
    with open(path, "rb") as fp:
      self._private_key = serialization.load_pem_private_key(
        fp.read(),
        password=None,
        backend=default_backend()
      )
    return self

  def with_public(self, path):
    with open(path, "rb") as fp:
      self._public_key = serialization.load_pem_public_key(
        fp.read(),
        backend=default_backend()
      )
    self._certs = { self._kid : self._public_key }
    self._log_certs("certs set from path to")
    return self

  def using_provider(self, provider_url):
    self._provider_url = provider_url
    return self.init_from_provider()

  def init_from_provider(self):
    if not self._provider_url:
      raise ValueError("missing provider url, use `using_provider` to supply")
    try:
      config = json.loads(requests.get(self._provider_url).content)
    except Exception:
      logger.exception("could not retrieve openid configuration")
      return
    try:
      self.with_jwks(requests.get(config["jwks_uri"]).content)
    except Exception:
      logger.exception("could not import jwks")
      return
    logger.info(f"successfully configured from {self._provider_url}")
    return self

  def with_client_id(self, client_id):
    self._client_id = client_id
    return self

  @property
  def jwks(self):
    return json.dumps({
      "keys" : [
        jwk.dumps(self._public_key, kty="RSA", alg=self._alg, kid=self._kid)
      ]
    }, indent=2)

  def with_jwks(self, path_or_string_or_obj):
    try:
      with open(path_or_string_or_obj) as fp:
        jwks = json.load(fp)
    except Exception:
      try:
        jwks = json.loads(path_or_string_or_obj)
      except Exception:
        jwks = path_or_string_or_obj
    assert isinstance(jwks, dict)
    self._certs = {
      key["kid"] : jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
      for key in jwks["keys"]
    }
    self._log_certs("certs set from jwks to")

    if jwks["keys"]:
      self._kid = jwks["keys"][0]["kid"]
    return self

  def from_clipboard(self):
    encoded = pb.stringForType_(NSStringPboardType)
    if encoded[:6] == "Bearer":
      encoded = encoded[7:]
    self._encoded = encoded.strip() # strip to remove trailing newline
    return self

  def from_file(self, path):
    with open(path) as fp:
      self._encoded = fp.read().strip() # strip to remove trailing newline
    return self

  def header(self, token=None):
    if not token:
      token = self._encoded
    return jwt.get_unverified_header(token)

  def claims(self, claimsdict=None, **claimset):
    if claimsdict is None:
      claimsdict = {}
    self._claims = claimset
    self._claims.update(claimsdict)
    return self

  @property
  def token(self):
    if self._private_key:
      return jwt.encode(
        self._claims, self._private_key, algorithm=self._alg,
        headers={ "kid": self._kid, "alg" : self._alg }
      )
    return None

  def validate(self, token=None):
    kid = self.header(token)["kid"]
    alg = self.header(token)["alg"]
    if not token:
      token = self._encoded
    try:
      cert = self._certs[kid]
    except KeyError:
      self._log_certs(f"unknown cert? {kid}")
      logger.error("retrying provider initialization")
      _ = self.init_from_provider()
      try:
        cert = self._certs[kid]
      except KeyError:
        self._log_certs(f"retry failed, still unknown cert? {kid}")
      raise
    jwt.decode(token, cert, algorithms=[alg], audience=self._client_id )

  def decode(self, token=None):
    if not token:
      token = self._encoded
    return jwt.decode(token, options={"verify_signature": False})

  def execute_authenticated(self, f, required_claims=None, *args, **kwargs):
    if "Authorization" not in request.headers:
      return Response("Missing Authorization", 401)

    token = request.headers["Authorization"][7:]
    code  = 403
    msg   = ""

    try:
      self.validate(token)
      if required_claims:
        claims = self.decode(token)
        for claim, value in required_claims.items():
          if claim not in claims:
            raise ValueError(f"required claim {claim} is missing")
          if callable(value):
            if not value(claims[claim]):
              raise ValueError(f"claim {claim} doesn't match required criteria")
          elif type(value) is list:
            if value not in claims[claim]:
              raise ValueError(f"claim {claim} is missing required value")
          elif value != claims[claim]:
            raise ValueError(f"claim {claim} doesn't equal required value")
      # authenticated -> execute
      return f(*args, **kwargs)
    except ValueError as e:
      msg = str(e)
      logger.warning(msg)
    except Exception as e:
      msg = repr(e)
      # [oatk] [WARNING] unexpected exception: KeyError('17f0f0f14e9cafa9ab5180150ae714c9fd1b5c26')
      logger.warning(f"unexpected exception: {msg}")
    return Response(msg, code)

  def authenticated(self, f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      return self.execute_authenticated(f, None, *args, **kwargs)
    return wrapper

  def authenticated_with_claims(self, **required_claims):
    def decorator(f):
      @wraps(f)
      def wrapper(*args, **kwargs):
        return self.execute_authenticated(f, required_claims, *args, **kwargs)
      return wrapper
    return decorator
