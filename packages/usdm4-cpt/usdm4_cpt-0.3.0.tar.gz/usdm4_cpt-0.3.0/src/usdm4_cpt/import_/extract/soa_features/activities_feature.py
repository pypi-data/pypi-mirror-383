from typing import List, Dict
from simple_error_log import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_cpt.import_.extract.soa_features.expand_table import expand_table
from usdm4_cpt.import_.extract.soa_features.utility import cell_text, cell_references


class ActivitiesFeature:
    MODULE = (
        "usdm4_cpt.import_.extract.soa_features.activities_feature.ActivitiesFeature"
    )

    def __init__(self, errors: Errors):
        self._errors = errors

    def process(
        self, html_content: str, start_row: int, ignore_last: bool = False
    ) -> List[Dict]:
        """
        Extract parent and child activities from a Schedule of Activities HTML table.

        Args:
            html_content (str): HTML content containing the table
            start_row (int): Row number to start processing activities from.
            ignore_last (bool): Ignore the last column in the table (contains notes etc) (default False)

        Returns:
            List of activity dictionaries, either standalone activities or parent activities with nested children
        """

        # Parse HTML with BeautifulSoup
        results = {
            "found": False,
            "items": [],
        }
        table = expand_table(html_content)
        if not table:
            self._errors.error(
                "No table detected", KlassMethodLocation(self.MODULE, "process")
            )
            return results

        # Extract all table rows
        rows = table.find_all("tr")

        # Convert rows to list of cell contents
        table_data = []
        table_references = []
        for row in rows:
            cells = row.find_all(["td", "th"])
            row_cells = []
            row_references = []
            for c_index, cell in enumerate(cells):
                row_references.append(cell_references(cell))
                row_cells.append(cell_text(cell))
            table_data.append(row_cells)
            table_references.append(row_references)
        if not table_data:
            raise ValueError("No data found in table")

        # Extract activities
        # print(f"START ROW: {start_row}")
        results["items"] = self._extract_activities(
            table_data, table_references, start_row, ignore_last
        )
        results["found"] = True
        return results

    def _extract_activities(
        self,
        table_data: List[List[str]],
        table_references: List[List[str]],
        start_row: int,
        ignore_last: bool,
    ) -> List[Dict]:
        """
        Extract parent and child activities from the table data.

        Args:
            table_data: List of rows
            table_references: List of row references
            start_row: Row to start processing from
            ignore_last: Ignore last column if true (usually notes or similar)

        Returns:
            List of activity dictionaries
        """
        activities = []
        current_parent = None

        for i in range(start_row, len(table_data)):
            row = table_data[i]
            references = table_references[i]
            if not row:
                continue
            activity_name = row[0].strip()
            if not activity_name:
                self._errors.warning("Missing activity name in row {i + 1}")
                continue
            if self._is_parent(row, ignore_last):
                current_parent = {"name": activity_name, "index": i, "children": []}
                activities.append(current_parent)
            else:
                # Check if this row has "X" markers (indicating it's a child activity)
                has_x_markers = self._has_x_markers(row, ignore_last)
                has_text_markers = self._has_text_markers(row, ignore_last)
                if has_x_markers or has_text_markers:
                    activity = {
                        "name": activity_name,
                        "index": i,
                        "visits": self._extract_visits_for_activity(
                            row, references, ignore_last
                        ),
                        "references": references[0],
                    }
                    if current_parent:
                        current_parent["children"].append(activity)
                    else:
                        activities.append(activity)

        return activities

    def _has_x_markers(self, row: List[str], ignore_last) -> bool:
        """
        Check if a row contains "X" markers indicating scheduled activities.

        Args:
            row: List of cell contents for the row

        Returns:
            True if row contains X markers
        """
        check_cells = row[1:-1] if ignore_last else row[1:]
        return any(cell.strip().upper() == "X" for cell in check_cells if cell)

    def _has_text_markers(self, row: List[str], ignore_last: bool) -> bool:
        value = None
        check_cells = row[1:-1] if ignore_last else row[1:]
        for cell in check_cells:
            if value and cell == value:
                # At least two cells with same text together
                return True
            else:
                value = cell
        return False

    def _has_text_markers(self, row: List[str], ignore_last: bool) -> bool:
        value = None
        check_cells = row[1:-1] if ignore_last else row[1:]
        for cell in check_cells:
            if value and cell == value:
                # At least two cells with same text together
                return True
            else:
                value = cell
        return False

    def _is_parent(self, row: List[str], ignore_last: bool) -> bool:
        check_cells = row[0:-1] if ignore_last else row
        return all(x == check_cells[0] for x in check_cells)

    def _extract_visits_for_activity(
        self, row: list[str], references: list[str], ignore_last: bool
    ) -> list[str]:
        """
        Extract which visits an activity is scheduled for based on X markers.

        Args:
            row: Row data containing X markers
            visit_headers: List of visit identifiers

        Returns:
            List of visit names where activity is scheduled
        """
        visits = []
        # Check each cell for X markers, mapping to visit headers
        last_col = len(row) - 1 if ignore_last else len(row)
        for j in range(1, last_col):
            if row[j].strip().upper() == "X" or row[j].strip() != "":
                visits.append({"index": j - 1, "references": references[j]})
        return visits
