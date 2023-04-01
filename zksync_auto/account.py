from zksync_auto import utils
from zksync_auto.config import ACC_PATH

COLUMN_MAPPING = {
    'Name': 'name',
    'Address': 'address',
    'Private Key': 'private_key',
    "Seed Phrase": 'seed_phrase',
    'Description': 'description',
}


class AccountLoader(object):
    def __init__(self, **kwargs):
        self.dir = ACC_PATH

    def parser_file(self):
        parsed_records = []
        raw_v_rows = []

        # region read file upload
        if self.dir.lower().endswith('.csv'):
            raw_v_rows = self._read_csv_file()
        elif self.dir.lower().endswith('.xlsx'):
            raw_v_rows = self._read_xlsx_file()
        else:
            raise Exception
        # endregion

        # region covert data
        parser_all = {
            'name': lambda v: str(v).strip() if v else None,
            'address': lambda v: str(v).strip() if v else None,
            'private_key': lambda v: str(v).strip() if v else None,
            'description': lambda v: str(v).strip() if v else None,
        }

        kept_as_is = lambda v: v
        for rvr in raw_v_rows:
            pr = dict()  # pr aka parsed_row
            for k, v in rvr.items():  # :k aka key, :v aka value
                parser_func = parser_all.get(k, kept_as_is)
                pr[k] = parser_func(v)
            parsed_records.append(pr)

        # endregion
        return parsed_records

    def _read_csv_file(self, column_mapping=None):
        if not column_mapping:
            column_mapping = COLUMN_MAPPING
        return utils.read_csv_file(dir_file=self.dir, column_mapping=column_mapping)

    def _read_xlsx_file(self, column_mapping=None):
        if not column_mapping:
            column_mapping = COLUMN_MAPPING
        return utils.read_xlsx_file(dir_file=self.dir, column_mapping=column_mapping)

