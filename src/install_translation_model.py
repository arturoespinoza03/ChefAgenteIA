"""Install the local Argos Translate English-to-Spanish model."""
import argostranslate.package
import argostranslate.translate


SOURCE_CODE = "en"
TARGET_CODE = "es"


def main() -> None:
    languages = argostranslate.translate.get_installed_languages()
    source_language = next(
        (language for language in languages if language.code == SOURCE_CODE),
        None,
    )
    target_language = next(
        (language for language in languages if language.code == TARGET_CODE),
        None,
    )
    if (
        source_language is not None
        and target_language is not None
        and source_language.get_translation(target_language) is not None
    ):
        print("El modelo local inglés-español ya está instalado.")
        return

    print("Descargando el modelo local inglés-español...")
    argostranslate.package.update_package_index()
    package_to_install = next(
        (
            package
            for package in argostranslate.package.get_available_packages()
            if package.from_code == SOURCE_CODE and package.to_code == TARGET_CODE
        ),
        None,
    )
    if package_to_install is None:
        raise RuntimeError("No se encontró el modelo local inglés-español.")

    package_path = package_to_install.download()
    argostranslate.package.install_from_path(package_path)
    print("Modelo local inglés-español instalado correctamente.")


if __name__ == "__main__":
    main()
