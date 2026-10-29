"""PySide6 desktop interface for searching recipes through the local API."""
import sys
from typing import Callable

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from api_client import ApiError, get_recipe_detail, search_recipes


class WorkerSignals(QObject):
    succeeded = Signal(object)
    failed = Signal(str)


class ApiWorker(QRunnable):
    def __init__(self, operation: Callable):
        super().__init__()
        self.operation = operation
        self.signals = WorkerSignals()

    def run(self):
        try:
            self.signals.succeeded.emit(self.operation())
        except ApiError as error:
            self.signals.failed.emit(str(error))


class ChefWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chef Personal - Recetas")
        self.setMinimumSize(900, 600)

        self.catalog = QComboBox()
        self.catalog.addItem("Todas las fuentes", "all")
        self.catalog.addItem("Kaggle", "kaggle")
        self.catalog.addItem("TheMealDB", "themealdb")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Busca una receta por nombre...")
        self.search_input.returnPressed.connect(self.search)

        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search)

        self.results = QListWidget()
        self.results.currentItemChanged.connect(self.show_recipe)

        self.thread_pool = QThreadPool.globalInstance()
        self._workers = set()
        self._search_generation = 0
        self._detail_generation = 0

        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Selecciona una receta para ver sus detalles.")

        search_row = QWidget()
        search_layout = QVBoxLayout(search_row)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.addWidget(QLabel("Catálogo"))
        search_layout.addWidget(self.catalog)
        search_layout.addWidget(QLabel("Nombre de la receta"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.results)
        splitter.addWidget(self.details)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.addWidget(search_row)
        layout.addWidget(splitter, 1)
        self.setCentralWidget(content)

        self.statusBar().showMessage(
            "Búsqueda en Supabase mediante el backend local."
        )

    def search(self):
        term = self.search_input.text().strip()
        self.results.clear()
        self.details.clear()
        if not term:
            self.statusBar().showMessage("Escribe el nombre o parte del nombre de una receta.")
            return

        selected_catalog = self.catalog.currentData()
        self._search_generation += 1
        generation = self._search_generation
        self.statusBar().showMessage("Buscando recetas...")
        self._dispatch(
            lambda: search_recipes(term, selected_catalog),
            lambda matches: self._show_search_results(matches, generation),
            lambda message: self._show_search_error(message, generation),
        )

    def _show_search_results(self, matches: list[dict], generation: int):
        if generation != self._search_generation:
            return
        for recipe in matches:
            item = QListWidgetItem(
                f"{recipe['name']}  ·  {self._source_label(recipe['source'])}"
            )
            item.setData(Qt.ItemDataRole.UserRole, recipe["source"])
            item.setData(Qt.ItemDataRole.UserRole + 1, recipe["id"])
            self.results.addItem(item)

        count = self.results.count()
        self.statusBar().showMessage(
            f"{count} resultado(s)." if count else "No se encontraron recetas con ese nombre."
        )

    def _show_search_error(self, message: str, generation: int):
        if generation != self._search_generation:
            return
        self.statusBar().showMessage("No se pudo completar la búsqueda.")
        QMessageBox.warning(self, "Error de búsqueda", message)

    def show_recipe(self, current, _previous):
        if current is None:
            self.details.clear()
            return

        source = current.data(Qt.ItemDataRole.UserRole)
        recipe_id = current.data(Qt.ItemDataRole.UserRole + 1)
        self._detail_generation += 1
        generation = self._detail_generation
        self.statusBar().showMessage("Cargando receta...")
        self._dispatch(
            lambda: get_recipe_detail(source, recipe_id),
            lambda recipe: self._show_recipe_detail(recipe, generation),
            lambda message: self._show_detail_error(message, generation),
        )

    def _show_detail_error(self, message: str, generation: int):
        if generation != self._detail_generation:
            return
        self.statusBar().showMessage("No se pudieron cargar los detalles.")
        QMessageBox.warning(self, "Error al cargar receta", message)

    def _show_recipe_detail(self, recipe: dict, generation: int):
        if generation != self._detail_generation:
            return

        if recipe is None:
            self.details.setPlainText("La receta ya no está disponible en el catálogo.")
            return

        source = recipe["source"]
        sections = [recipe["name"], f"Fuente: {self._source_label(source)}"]
        if source == "kaggle":
            sections.append("Instrucciones")
            sections.extend(
                f"{step['position']}. {step['instruction']}" for step in recipe["steps"]
            )
            if recipe["images"]:
                sections.append("Referencias de imágenes")
                sections.extend(recipe["images"])
        else:
            if recipe.get("category"):
                sections.append(f"Categoría: {recipe['category']}")
            if recipe.get("area"):
                sections.append(f"Origen: {recipe['area']}")
            sections.append("Ingredientes registrados")
            sections.extend(
                f"- {ingredient['ingredient']}"
                + (
                    f" — {ingredient['measure_raw']}"
                    if ingredient.get("measure_raw")
                    else ""
                )
                for ingredient in recipe["ingredients"]
            )
            sections.append("Instrucciones")
            sections.append(recipe.get("instructions") or "No hay instrucciones registradas.")
            if recipe.get("source_url"):
                sections.extend(("Fuente externa", recipe["source_url"]))

        sections.extend(
            (
                "",
                "Nota: los datos disponibles no garantizan información completa sobre "
                "alérgenos, cantidades, raciones o tiempos.",
            )
        )
        self.details.setPlainText("\n".join(sections))
        self.statusBar().showMessage("Receta cargada.")

    @staticmethod
    def _source_label(source: str) -> str:
        return "TheMealDB" if source == "themealdb" else "Kaggle"

    def _dispatch(
        self,
        operation: Callable,
        on_success: Callable,
        on_error: Callable[[str], None],
    ):
        worker = ApiWorker(operation)
        self._workers.add(worker)
        worker.signals.succeeded.connect(
            lambda result, current=worker: self._finish_worker(
                current, lambda: on_success(result)
            )
        )
        worker.signals.failed.connect(
            lambda message, current=worker: self._finish_worker(
                current, lambda: on_error(message)
            )
        )
        self.thread_pool.start(worker)

    def _finish_worker(self, worker: ApiWorker, callback: Callable):
        self._workers.discard(worker)
        callback()


def main():
    app = QApplication(sys.argv)
    window = ChefWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
