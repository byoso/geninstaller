
from geninstaller.silly_engine import JsonDb


def mig_2_1_0(db: JsonDb) -> None:
    applications = db.collection("applications")
    for app in applications.all():
        if "pre_install_file" in app:
            app["pre_install_script"] = app["pre_install_file"]
            del app["pre_install_file"]
        if "post_install_file" in app:
            app["post_install_script"] = app["post_install_file"]
            del app["post_install_file"]
        if "pre_uninstall_file" in app:
            app["pre_uninstall_script"] = app["pre_uninstall_file"]
            del app["pre_uninstall_file"]
        if "post_uninstall_file" in app:
            del app["post_uninstall_file"]
        applications.update(app)