from datetime import datetime
from typing import Literal

class DBUtils:
    def __init__():
        pass

    @staticmethod
    def _build_date_map(entries: list[dict]) -> dict:
        return {
            (
                entry["report_date"].isoformat()
                if isinstance(entry["report_date"], datetime)
                else entry["report_date"]
            ): entry
            for entry in entries
            if "report_date" in entry if entry["report_date"] is not None
        }
    
    @staticmethod
    def _merge_financials_by_date(
        primary: list[dict], 
        secondary: list[dict], 
        financial: Literal["financial_results.quarterly", "financial_results.yearly", "balance_sheet", "cash_flow"],
        skip_zeros: bool = False,
    ) -> list[dict]:
        """
        Merge two financial entry lists by date, merging at key level with primary preference.
        
        Args:
            primary: Preferred financial entries (e.g., consolidated).
            secondary: Backup financial entries (e.g., standalone).
            skip_zeros: If True, skip entries with no valid data.
            
        Returns:
            A merged, date-sorted list of financial entries with key-level merging.
        """
        primary_map = DBUtils._build_date_map(primary)
        secondary_map = DBUtils._build_date_map(secondary)
        
        all_dates = sorted(set(primary_map) | set(secondary_map), reverse=True)
        merged = []
        
        for date in all_dates:
            primary_entry = primary_map.get(date, {})
            secondary_entry = secondary_map.get(date, {})
            
            # If neither entry exists, skip
            if not primary_entry and not secondary_entry:
                continue
                
            # Get all unique keys from both entries
            all_keys = set(primary_entry.keys()) | set(secondary_entry.keys())
            
            # Merge at key level
            merged_entry = {}
            for key in all_keys:
                primary_value = primary_entry.get(key)
                secondary_value = secondary_entry.get(key)
                
                # Priority logic: use primary if it has valid value, otherwise secondary
                if primary_value is not None and primary_value != 0:
                    merged_entry[key] = primary_value
                elif secondary_value is not None and secondary_value != 0:
                    merged_entry[key] = secondary_value
                else:
                    # Both are None/0, prefer primary (could be None)
                    merged_entry[key] = primary_value if primary_value is not None else secondary_value
            
            # Skip if skip_zeros is True and key metric is invalid
            if skip_zeros and financial == "financial_results.quarterly" or financial == "financial_results.yearly":
                key_value = merged_entry.get("sales")
                if key_value in [0, None]:
                    continue
                    
            merged.append(merged_entry)
        return merged

    
    @staticmethod
    def _get_nested(doc: dict, dotted_key: str, default=None):
        keys = dotted_key.split(".")
        for key in keys:
            doc = doc.get(key)
            if doc is None:
                return default
        return doc
