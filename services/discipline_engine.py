class DisciplineEngine:
    def sort_key_for_mode(self, mode: str, item: dict):
        status = item["status_flag"]
        status_rank = 0 if status == "OK" else 1

        primary_value = item["primary_value"]
        secondary_value = item["secondary_value"]

        pv_missing = primary_value is None
        sv_missing = secondary_value is None

        if mode == "TIME_WITH_DISTANCE_FALLBACK":
            return (
                status_rank,
                0 if not pv_missing else 1,
                primary_value if primary_value is not None else 10**12,
                0 if not sv_missing else 1,
                -(secondary_value if secondary_value is not None else -1),
            )

        if mode in ("AMRAP_REPS", "AMRAP_DISTANCE", "MAX_WEIGHT_WITHIN_CAP"):
            return (
                status_rank,
                0 if not pv_missing else 1,
                -(primary_value if primary_value is not None else -1),
            )

        if mode == "RELAY_DUAL_METRIC":
            return (
                status_rank,
                0 if not pv_missing else 1,
                -(primary_value if primary_value is not None else -1),
                0 if not sv_missing else 1,
                secondary_value if secondary_value is not None else 10**12,
            )

        return (
            status_rank,
            0 if not pv_missing else 1,
            -(primary_value if primary_value is not None else -1),
        )
