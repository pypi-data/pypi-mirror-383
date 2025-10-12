from typing import Optional, TYPE_CHECKING

from parsedatetime import Calendar, VERSION_CONTEXT_STYLE
from pytz import timezone

from mojentic.llm.tools.llm_tool import LLMTool

# Avoid circular imports with TYPE_CHECKING
if TYPE_CHECKING:
    from mojentic.llm.llm_broker import LLMBroker


class ResolveDateTool(LLMTool):
    def run(self, relative_date_found: str, reference_date_in_iso8601: Optional[str] = None) -> dict[str, str]:
        cal = Calendar(version=VERSION_CONTEXT_STYLE)

        if reference_date_in_iso8601:
            reference_date, _ = cal.parseDT(reference_date_in_iso8601)
        else:
            reference_date = None

        resolved_date, parse_status = cal.parseDT(datetimeString=relative_date_found, sourceTime=reference_date,
                                                  tzinfo=timezone("America/Toronto"))

        return {
            "relative_date": relative_date_found,
            "resolved_date": resolved_date.strftime('%Y-%m-%d'),
            "summary": f"The date on '{relative_date_found}' is {resolved_date.strftime('%Y-%m-%d')}"
        }

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "resolve_date",
                "description": "Take text that specifies a relative date, and output an absolute date. If no reference date is available, the current date is used.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_date_found": {
                            "type": "string",
                            "description": "The text referencing to a relative date."
                        },
                        "reference_date_in_iso8601": {
                            "type": "string",
                            "description": "The date from which the resolved date should be calculated, in YYYY-MM-DD"
                                           " format. Do not provide if you weren't provided one, I will assume the current date."
                        }
                    },
                    "additionalProperties": False,
                    "required": ["relative_date_found"]
                },
            }
        }
