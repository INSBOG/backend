
from flask import Blueprint
from app.controllers.access_key import AccessKeyController
from app.services.auth import AuthService
from app.middlewares.deps import load_dependencies
from app.controllers.auth import AuthController
from app.controllers.storage import StorageController
from app.middlewares.auth import auth_required
from app.services.storage import StorageService

main = Blueprint('main', __name__)


@main.get("/session")
# @auth_required
@load_dependencies((AuthController, [AuthService]))
def session(controller: AuthController):
    return controller.validate()

@main.post("/login")
@load_dependencies((AuthController, [AuthService]))
def login(controller: AuthController):
    return controller.login()

@main.get("/logout")
@auth_required
@load_dependencies((AuthController, [AuthService]))
def logout(controller: AuthController):
    return controller.logout()


@main.post("/register")
@auth_required
@load_dependencies((AuthController, [AuthService]))
def register(controller: AuthController):
    return controller.register()


@main.put("/change-password")
@auth_required
@load_dependencies((AuthController, [AuthService]))
def change_password(controller: AuthController):
    return controller.change_password()


@main.post("/upload")
@auth_required
@load_dependencies((StorageController, [StorageService]))
def upload(controller: StorageController):
    return controller.storage_service.upload_file()

@main.post("/download")
@auth_required
@load_dependencies((StorageController, [StorageService]))
def download(controller: StorageController):
    return controller.storage_service.download_files()

@main.get("/reports")
@auth_required
@load_dependencies((StorageController, [StorageService]))
def reports(controller: StorageController):
    return controller.storage_service.get_reports()

@main.post("/delete-reports")
@auth_required
@load_dependencies((StorageController, [StorageService]))
def delete(controller: StorageController):
    return controller.storage_service.delete_data()

@main.get("/locations")
#@auth_required
@load_dependencies((StorageController, [StorageService]))
def get_locations(controller: StorageController):
    return controller.get_dptos()

@main.post("/verify")
@load_dependencies((AuthController, [AuthService]))
def verify(controller: AuthController):
    return controller.verify()

@main.post("/access-key/register-options")
@load_dependencies((AccessKeyController))
def register_options(controller: AccessKeyController):
    return controller.get_register_options()

@main.post("/access-key/register")
@load_dependencies((AccessKeyController))
def register_access_key(controller: AccessKeyController):
    return controller.handle_register()

@main.post("/access-key/authenticate-options")
@load_dependencies((AccessKeyController))
def authenticate_options(controller: AccessKeyController):
    return controller.get_auth_options()

@main.post("/access-key/authenticate")
@load_dependencies((AccessKeyController))
def authenticate_access_key(controller: AccessKeyController):
    return controller.handle_auth()



