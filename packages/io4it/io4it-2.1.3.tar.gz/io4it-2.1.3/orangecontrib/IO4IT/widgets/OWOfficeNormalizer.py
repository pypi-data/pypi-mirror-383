import os
import sys
from pathlib import Path
import shutil

from AnyQt.QtWidgets import QApplication
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.data import Domain, StringVariable, Table, DiscreteVariable

# --- Ajout pour l'écriture Excel ---
from openpyxl import Workbook

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.IO4IT.utils import utils_md
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
else:
    from orangecontrib.IO4IT.utils import utils_md
    from orangecontrib.AAIT.utils.import_uic import uic


class OWOfficeNormalizer(widget.OWWidget):
    name = "Office Normalizer"
    description = "Convertit .doc→.docx et .ppt→.pptx via COM (Windows + Office)"
    category = "AAIT - TOOLBOX"
    icon = "icons/office_normalizer.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/office_normalizer.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owofficenormalizer.ui")
    want_control_area = False
    priority = 1003

    class Inputs:
        data = Input("Files Table", Table)

    class Outputs:
        data = Output("Normalized Files", Table)
        status_data = Output("Status Table", Table)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(470)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)

        self.data = None
        self.autorun = True
        self.result = None
        self.processed_statuses = []
        self.post_initialized()

    @Inputs.data
    def set_data(self, in_data: Table | None):
        self.data = in_data
        if self.autorun:
            self.run()

    def run(self):
        if self.data is None:
            self.Outputs.data.send(None)
            self.Outputs.status_data.send(None)
            return

        self.error("")
        try:
            self.data.domain["file_path"]
        except KeyError:
            self.error("You need a 'file_path' column in input data.")
            return

        self.progressBarInit()
        self.processed_statuses = []
        self.Outputs.status_data.send(None)

        # Process files directly without a separate thread
        result_table = self._normalize_files(self.data)

        # Send the final results to the primary output
        self.Outputs.data.send(result_table)
        self.progressBarFinished()

    def _normalize_files(self, in_data: Table) -> Table:
        rows = []
        file_paths = [str(x) for x in in_data.get_column("file_path")]
        total_files = len(file_paths)

        if not file_paths:
            return Table.from_list(
                Domain([], metas=[StringVariable("src_path"), StringVariable("dst_path"), StringVariable("status")]),
                [])

        common_path = Path(os.path.commonpath(file_paths))
        output_base_dir = common_path / "office_normalisation"
        output_base_dir.mkdir(parents=True, exist_ok=True)

        # Gère le nom du fichier Excel avec incrémentation
        base_name = "normalization_results"
        excel_path = output_base_dir / f"{base_name}.xlsx"
        counter = 1
        while excel_path.exists():
            excel_path = output_base_dir / f"{base_name}_{counter}.xlsx"
            counter += 1

        # Initialise le classeur Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Normalization Results"
        headers = ["src_path", "dst_path", "status", "details"]
        ws.append(headers)

        for i, path_str in enumerate(file_paths):
            self.progressBarSet(i / total_files * 100)

            src = Path(path_str)
            dst_path = ""
            status_text = ""
            status_short = ""
            details = ""

            if not src.exists():
                status_short = "ko"
                details = "not found"
                status_text = f"ko: {details}"
            else:
                try:
                    relative_path_from_common = src.parent.relative_to(common_path)
                    dst_dir = output_base_dir / relative_path_from_common
                    dst_dir.mkdir(parents=True, exist_ok=True)

                    if src.suffix.lower() == ".doc":
                        dst = utils_md.convert_doc_to_docx(src, dst_dir)
                        dst_path = str(dst)
                        status_short = "ok"
                        details = "doc->docx"
                        status_text = f"ok: {details}"
                    elif src.suffix.lower() == ".ppt":
                        dst = utils_md.convert_ppt_to_pptx(src, dst_dir)
                        dst_path = str(dst)
                        status_short = "ok"
                        details = "ppt->pptx"
                        status_text = f"ok: {details}"
                    else:
                        dst = dst_dir / src.name
                        if not dst.exists():
                            shutil.copy(src, dst)
                        dst_path = str(dst)
                        status_short = "ok"
                        details = "unchanged"
                        status_text = f"ok: {details}"
                except Exception as e:
                    error_msg = str(e)
                    status_short = "ko"
                    details = f"error: {error_msg}"
                    status_text = f"ko: {details}"

            # Ajoute la ligne de résultat à la table Excel et la sauvegarde
            result_row = [path_str, dst_path, status_short, details]
            ws.append(result_row)
            wb.save(excel_path)

            # Append to the final results list for Orange table
            rows.append([path_str, dst_path, status_text])

            # Append to the status update list and send the incremental table
            self.processed_statuses.append([path_str, status_short, details])
            self._send_status_table()

            # This is crucial for UI updates, including the progress bar
            QApplication.processEvents()

        self.progressBarSet(100)

        # Create and return the final output table
        domain = Domain([], metas=[
            StringVariable("src_path"),
            StringVariable("dst_path"),
            StringVariable("status")
        ])
        return Table.from_list(domain, rows)

    def _send_status_table(self):
        """Sends an incremental table to the status_data output."""
        domain = Domain([], metas=[
            StringVariable("src_path"),
            DiscreteVariable("status", values=["ok", "ko"]),
            StringVariable("details")
        ])
        status_table = Table.from_list(domain, self.processed_statuses)
        self.Outputs.status_data.send(status_table)

    def handle_progress(self, value: float) -> None:
        self.progressBarSet(value)

    def post_initialized(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWOfficeNormalizer()
    my_widget.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()