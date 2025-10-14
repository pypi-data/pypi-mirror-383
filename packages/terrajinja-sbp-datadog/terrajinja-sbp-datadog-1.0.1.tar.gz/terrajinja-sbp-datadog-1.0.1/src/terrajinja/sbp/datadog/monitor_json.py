from cdktf_cdktf_provider_datadog.monitor_json import MonitorJson
from constructs import Construct
import json
import re


def replace_template_variables(data, variables):
    if isinstance(data, dict):
        return {k: replace_template_variables(v, variables) for k, v in data.items()}
    if isinstance(data, list):
        return [replace_template_variables(i, variables) for i in data]
    if isinstance(data, str):
        for k, v in variables.items():
            data = data.replace(f"__{k.upper()}__", str(v))
    return data


def validate_no_placeholders(data):
    s = json.dumps(data)
    if re.search(r"__.+?__", s):
        raise ValueError(f"Unresolved placeholders found in JSON: {s}")


def _coerce_numeric(value):
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        s = value.strip()
        try:
            f = float(s)
            return int(f) if f.is_integer() and "." in s or "e" in s.lower() or s.isdigit() else (
                int(s) if s.lstrip("+-").isdigit() else f)
        except ValueError:
            return value
    return value


class SbpDatadogMonitorJson(MonitorJson):
    def __init__(self, scope: Construct, ns: str, monitor: str, template_variables: dict = None):
        monitor_dict = json.loads(monitor)
        if 'draft_status' not in monitor_dict:
            monitor_dict['draft_status'] = 'published'

        if template_variables:
            monitor_dict = replace_template_variables(monitor_dict, template_variables)
            validate_no_placeholders(monitor_dict)

        # make crit/warn thresholds a numeric value if they are a string
        thresholds = ((monitor_dict.get("options") or {}).get("thresholds") or {})
        for k in ("critical", "warning", "critical_recovery", "warning_recovery"):
            if k in thresholds:
                thresholds[k] = _coerce_numeric(thresholds[k])
        if "options" not in monitor_dict or monitor_dict["options"] is None:
            monitor_dict["options"] = {}
        monitor_dict["options"]["thresholds"] = thresholds

        super().__init__(scope=scope, id_=ns, monitor=json.dumps(monitor_dict))
