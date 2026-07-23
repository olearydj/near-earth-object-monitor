# NEO Monitor Data Dictionary

The processed CSV is a small, validated view of NASA Near Earth Object Web
Service feed data. Create it with `--save-processed-csv` in the CLI or download
the selected rows from the dashboard.

## Processed CSV Fields

| Field | Type and format | Unit | Meaning and derivation |
| --- | --- | --- | --- |
| `approach_date` | date, `YYYY-MM-DD` | — | Close-approach date reported by NASA. |
| `name` | string | — | NASA's display name for the object. |
| `hazardous` | boolean, `true` or `false` | — | NASA's `is_potentially_hazardous_asteroid` flag. |
| `diameter_meters` | decimal, three places | meters | Mean of NASA's minimum and maximum estimated diameters in kilometers, converted to meters. It is an estimate, not a measured diameter. |
| `miss_distance_km` | decimal, three places | kilometers | Predicted distance between Earth and the object at closest approach. |
| `miss_distance_lunar` | decimal, three places | lunar distances | The same miss distance expressed relative to the average Earth–Moon distance. Lower values are closer. |
| `velocity_kph` | decimal, three places | kilometers per hour | Object velocity relative to Earth at close approach. |

Each row represents one object in the requested feed. If NASA supplies more
than one close-approach entry for an object, this introductory project uses the
first entry returned for the requested feed record.

## Selection and Ordering

The CLI and dashboard can filter processed rows by hazardous status, minimum
diameter, or maximum miss distance. They can then rank the selected rows by
closest approach, fastest velocity, or largest estimated diameter and keep a
requested number of rows. The high-level summary is calculated from the full
validated feed before those row-level selections.

## Missing and Invalid Values

The project does not impute required values. Before creating a processed row,
Pydantic validates the external fields and types used by the project. A missing
or unusable required value stops processing with a message identifying the
problem. Use `--save-raw` when the original response should be preserved even
if validation fails.

## Provenance

Source: NASA Near Earth Object Web Service NEO Feed API,
<https://api.nasa.gov/>.

Raw JSON output preserves the response received from NASA, formatted for
readability, except that API-key values echoed in provider link metadata are
redacted. It is kept separately because it contains more analytical fields than
this processed schema and provides evidence for later inspection.
