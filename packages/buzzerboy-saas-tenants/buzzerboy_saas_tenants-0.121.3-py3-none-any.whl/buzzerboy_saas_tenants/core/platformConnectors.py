import os, json

def getSecrets():
    secretString = os.environ.get('SECRET_STRING', None)
    secret_dict = None
    if secretString is not None:
        secret_dict = json.loads(secretString)
    return secret_dict


def getSiteUrl(default='http://localhost:8000'):
    site_url = os.environ.get('SITE_URL', default)
    if not site_url.startswith(('http://', 'https://')):
        site_url = f'http://{site_url}'
    return site_url





def getValueFromdDict(dict, key, default=""):
    if dict is not None:
        return dict.get(key, default)
    return default

def get_config_value(key, default=''):
    secrets = getSecrets()
    if secrets is not None:
        return getValueFromdDict(secrets, key, default)
    return os.environ.get(key, default)


def getSiteUrl(default='http://localhost:8000'):
    site_url = get_config_value('SITE_URL', default)
    if site_url:
        return site_url
    return default


def environConfig (key, default=""):
    return os.environ.get(key, default)

def getDebugValue(default=False): 
    return get_config_value('DEBUG', default)

def getAdvancedDebugValue(default=False):
    return get_config_value('ADVANCED_DEBUG', default)

def getDjangoSecretKey(default=""): 
    return get_config_value('DJANGO_SECRET_KEY', default)

# Security configs
def getSessionCookieSecure(default=False): 
    return get_config_value('session_cookie_secure', default)

def getSocialAuthRedirectIsHttps(default=False): 
    return get_config_value('social_auth_redirect_is_https', default)

def getAccountDefaultHttpProtocol(default='http'): 
    return get_config_value('account_default_http_protocol', default)

def getSecureProxySslHeader(default=('HTTP_X_FORWARDED_PROTO', 'http')): 
    return get_config_value('secure_proxy_ssl_header', default)

def getSecureSslRedirect(default=False): 
    return get_config_value('secure_ssl_redirect', default)

# Email configs
def getEmailHost(default=""): return get_config_value('email_host', default)
def getEmailPort(default=""): return get_config_value('email_port', default)
def getEmailUser(default=""): return get_config_value('email_user', default)
def getEmailPassword(default=""): return get_config_value('email_password', default)
def getEmailUseTLS(default=True): return get_config_value('email_use_tls', default)
def getEmailDefaultFromEmail(default=""): return get_config_value('email_default_from_email', default)
def getEmailBackend(default="django.core.mail.backends.console.EmailBackend"): return get_config_value('email_backend', default)

# Database configs
def getDBName(default=""): return get_config_value('dbname', default)
def getDBUser(default=""): return get_config_value('username', default)
def getDBHost(default=""): return get_config_value('host', default)
def getDBPort(default=""): return get_config_value('port', default)
def getDBPassword(default=""): return get_config_value('password', default)
def getDBEngine(default=""): return get_config_value('engine', default)

# AWS configs
def getRegionName(default=""): return get_config_value('region_name', default)
def getFileOverWrite(default=""): return get_config_value('file_overwrite', default)
def getACL(default=""): return get_config_value('default_acl', default)
def getSignatureVersion(default=""): return get_config_value('signature_version', default)
def getAWSAccessKey(default=""): return get_config_value('access_key', default)
def getAWSSecretKey(default=""): return get_config_value('secret_access_key', default)


# AWS LightSail configs
def getBucketName(default=""): return get_config_value('bucket_name', default)
def getLightSailBucketAccessId(default=""): return get_config_value('lightsail_bucket_access_id', default)
def getLightSailBucketSecretKey(default=""): return get_config_value('lightsail_bucket_secret_key', default)

# Microsoft Creds
def getMicrosoftClientID(default=""): return get_config_value('microsoft_client_id', default)
def getMicrosoftClientSecret(default=""): return get_config_value('microsoft_client_secret', default)
def getSecretgetBucketName(default=""): return get_config_value('secret_bucket_name', default)


# SAML configs
def getXMLSecBinaryPath(default=""): return get_config_value('xmlsec_binary_path', default)
def getSamlLoginURL(default=""): return get_config_value('saml_login_url', default)

# Google Creds
def getGoogleClientID(default=""): return get_config_value('google_client_id', default)
def getGoogleClientSecret(default=""): return get_config_value('google_client_secret', default)

# Account Email Subject Prefix
def getAccountEmailSubjectPrefix(default=""): return get_config_value('account_email_subject_prefix', default)

# Internal IP
def getInternalIPs(default=[]): return get_config_value('internal_ips', [])

# AWS Bedrock configs
def getBedrockModelId(default=""): return get_config_value('bedrock_model_id', default)

def getBedrockMaxTokens(default=0):
    value = get_config_value('bedrock_max_tokens', default)
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def getBedrockTemperature(default=0.0):
    value = get_config_value('bedrock_temperature', default)
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def getAIChatProfile(default="default"):
    return get_config_value('ai_chat_profile', default)