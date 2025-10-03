from werkzeug.datastructures import FileStorage
from dbfread import DBF
import pandas as pd
from io import BytesIO

class FileConverter:

    @staticmethod
    def dbf_to_xlsx(self, file: FileStorage) -> BytesIO:
        dbf = DBF(file, load=True, encoding="latin-1")

        # Convert DBF to DataFrame
        df = pd.DataFrame(iter(dbf))

        file_stream = BytesIO()

        # Save DataFrame to Excel
        df.to_excel(file_stream)
        file_stream.seek(0)

        return file_stream
