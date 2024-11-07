from typing import Annotated
from keycloak import KeycloakOpenID
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

kc_server = os.environ.get('KC_SERVER', 'localhost')
home_server = os.environ.get('HM_SERVER', 'localhost')

keycloak_openid = KeycloakOpenID(server_url="http://{}:8080/".format(kc_server),
                                 client_id="userclient",
                                 realm_name="userrealm",
                                 client_secret_key="T173C1G9fWviL36t1WCvl55klaBy4Jlv")

# Get WellKnown
config_well_known = keycloak_openid.well_known()
# print(config_well_known)
# Get Code With Oauth Authorization Request
auth_url = keycloak_openid.auth_url(
    redirect_uri="http://{}:8501/auth_redirect".format(home_server),
    scope="email",
    state="your_state_info"
    )

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

auth_scheme = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    sub: str
    email_verified: bool
    email: str | None = None
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    preferred_username: str | None = None


def decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = keycloak_openid.userinfo(token['credentials'])
    return user


async def get_current_user(token: Annotated[str,Depends(auth_scheme)]):
    try:
        token = dict(token)
        print(token)
        user = decode_token(token)
    except Exception as e:
        user = None
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.get("/", response_class=HTMLResponse)
async def get_login_page():
    with open("login.html") as f:
        return HTMLResponse(content=f.read())

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    token = keycloak_openid.token(form_data.username, form_data.password)
    return token


@app.get("/user")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user

@app.get("/greet", response_class=HTMLResponse)
async def greet_user(request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # return HTMLResponse(f"<h1>Welcome, {current_user['email']}!</h1>")
    return templates.TemplateResponse(
        request=request, name="home.html", context={"email": current_user['email']})

if __name__ == "__main__":
    uvicorn.run("keycloak_login:app", host="0.0.0.0", port=int(os.environ.get('PORT', 8501)), log_level="info")
