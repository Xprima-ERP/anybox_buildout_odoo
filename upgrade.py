# -*- python -*-
"""This is a template upgrade script.

The purpose is both to cover the most common use-case (updating all modules)
and to provide an example of how this works.
"""
import ConfigParser
import pkg_resources as pkr


def vers_cmp(ver1, ver2):
    """Compare versions using pkg_resources parse_version"""
    if pkr.parse_version(ver1) == pkr.parse_version(ver2):
        return 0
    elif pkr.parse_version(ver1) < pkr.parse_version(ver2):
        return -1
    else:
        return 1


def run(session, logger):
    """Update all modules, or install modules if db_version is lagging behind"""
    config = ConfigParser.SafeConfigParser(allow_no_value=True)
    config.read("addons_modules_db_version.cfg")

    db_version = session.db_version
    package_version = session.package_version
    session.update_modules_list()

    # If db version and VERSION.txt are the same, update all modules.
    if db_version == package_version:
        logger.info("Default upgrade procedure : updating all modules.")
        session.update_modules(['all'])
    else:
        # If db version is behind the version in VERSION.txt update db to
        # the current version by installing missing modules.
        logger.info("db version is behind package version, install modules to "
                    "update db to latest version")
        package_versions = config.sections()
        package_new_versions = []
        for version in package_versions:
            ver_db = vers_cmp(version, str(db_version)) == 1
            ver_pkc = vers_cmp(version, str(package_version)) <= 0
            if ver_db and ver_pkc:
                package_new_versions.append(version)
        package_new_versions.sort(vers_cmp)
        # Get modules for each new version.
        install_modules = []
        for version in package_new_versions:
            install_modules.extend(
                [module[0] for module in config.items(version)]
            )
        if install_modules:
            session.install_modules(install_modules)
