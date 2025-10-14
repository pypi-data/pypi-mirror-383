from raw_docx.raw_docx import RawDocx, RawParagraph, RawSection
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_cpt.import_.extract.soa_features.activity_row_feature import (
    ActivityRowFeature,
)
from usdm4_cpt.import_.extract.soa_features.notes_feature import NotesFeature
from usdm4_cpt.import_.extract.soa_features.epochs_feature import EpochsFeature
from usdm4_cpt.import_.extract.soa_features.visits_feature import VisitsFeature
from usdm4_cpt.import_.extract.soa_features.timepoints_feature import TimepointsFeature
from usdm4_cpt.import_.extract.soa_features.windows_feature import WindowsFeature
from usdm4_cpt.import_.extract.soa_features.activities_feature import ActivitiesFeature
from usdm4_cpt.import_.extract.soa_features.conditions_feature import ConditionsFeature


class SoA:
    MODULE = "usdm4_cpt.import_.soa.SoA"

    def __init__(self, raw_docx: RawDocx, errors: Errors):
        self._raw_docx = raw_docx
        self._errors = errors

    def process(self, id: str) -> dict | None:
        try:
            self._id = id
            section = self._raw_docx.target_document.section_by_title(
                "Schedule of Activities"
            )
            if section:
                # soa_tables = self._merge_tables(section.tables())
                raw_result = self._decode_soa(section)
                # for item in section.items:
                #     if isinstance(item, RawParagraph):
                #         if item.items:
                #             print(f"\n\nPARAGRAPH:\n\n{item.to_dict()}")
                #     elif isinstance(item, RawTable):
                #         print(f"\n\nTABLE\n\n{item.to_dict()}")
            else:
                self._errors.error(
                    "Failed to find the SoA section in the document",
                    KlassMethodLocation(self.MODULE, "process"),
                )
                raw_result = None
            return raw_result
        except Exception as e:
            self._errors.exception(
                "Error processing SoA", e, KlassMethodLocation(self.MODULE, "process")
            )
            return None

    def _decode_soa(self, section: RawSection) -> dict | None:
        if soa_tables := section.tables():
            result = {}
            html = soa_tables[0].to_html()
            soa_index = section.index(soa_tables[0])
            # print(f"TABLE INDEX: {soa_index}")
            result["activity_row"] = ActivityRowFeature(self._errors).process(html)
            activity_row = result["activity_row"]["first_activity_row"]
            last_header_row = activity_row + 1
            result["notes"] = NotesFeature(self._errors).process(html)
            ignore_last = result["notes"]["found"]
            result["epochs"] = EpochsFeature(self._errors).process(html, ignore_last)
            result["visits"] = VisitsFeature(self._errors).process(
                html, last_header_row, ignore_last
            )
            result["timepoints"] = TimepointsFeature(self._errors).process(
                html, last_header_row, ignore_last
            )
            result["windows"] = WindowsFeature(self._errors).process(
                html, last_header_row, ignore_last
            )
            result["activities"] = ActivitiesFeature(self._errors).process(
                html, activity_row, ignore_last
            )
            result["conditions"] = ConditionsFeature(self._errors).process(
                self._extract_footnotes(section, soa_index)
            )
            return result
        else:
            self._errors.error(
                "No SoA found", KlassMethodLocation(self.MODULE, "_decode_soa")
            )
            return None

    def _extract_footnotes(self, section: RawSection, soa_index: int) -> str:
        items = section.items_between(soa_index + 1, len(section.items))
        text = ""
        for item in items:
            if isinstance(item, RawParagraph):
                text += item.to_html()
            else:
                break
        return text

    # def _merge_tables(self, tables: list[RawTable]) -> list[RawTable]:
    #     new_tables = []
    #     previous_table = None
    #     table: RawTable
    #     for index, table in enumerate(tables):
    #         if index > 0:
    #             matching, rows = self._matching_header(previous_table, table)
    #             if matching:
    #                 self._errors.info("Matching tables detected")
    #                 new_table = self._combine_tables(previous_table, table)
    #                 new_tables.append(new_table)
    #             else:
    #                 new_tables.append(table)
    #         else:
    #             new_tables.append(table)
    #         previous_table = table
    #     # self._dump_tables(new_tables, test_filename(self._id, ".html", "tables"))
    #     return new_tables

    # def _combine_tables(
    #     self, first_table: RawTable, second_table: RawTable
    # ) -> RawTable:
    #     self._errors.warning("Need to merge tables, but not yet implemented!")

    # def _matching_header(self, first_table: RawTable, second_table: RawTable) -> bool:
    #     match_count = 0
    #     for index, row in enumerate(first_table.rows):
    #         other_row = second_table.rows[index]
    #         if self._matching_row(row, other_row):
    #             match_count += 1
    #         else:
    #             break
    #     return (True, match_count) if match_count >= 2 else (False, 0)

    # def _matching_row(self, a: RawTableRow, b: RawTableRow) -> bool:
    #     result = True
    #     for index, cell in enumerate(a.cells):
    #         other_cell = b.cells[index]
    #         if cell.to_html() != other_cell.to_html():
    #             result = False
    #             break
    #     return result

    # def _dump_tables(self, tables: list[RawTable], filename):
    #     html = ""
    #     for table in tables[0:1]:
    #         # html += table.to_html()
    #         html += self._table_to_html(table)
    #     self._save_html(html, filename)

    # def _save_html(self, contents, filename):
    #     try:
    #         with open(filename, "w", encoding="utf-8") as f:
    #             f.write(contents)
    #     except Exception as e:
    #         self._errors.exception(
    #             "Exception saving timeline file",
    #             e,
    #             KlassMethodLocation(self.MODULE, "_save_html"),
    #         )

    # def _table_to_html(self, table: RawTable):
    #     lines = []
    #     open_tag = "<table>"
    #     lines.append(open_tag)
    #     for item in table.rows[0:12]:
    #         lines.append(item.to_html())
    #     lines.append("</table>")
    #     return ("\n").join(lines)
