# Types List

Open a bash or git bash terminal and run:

```bash
python -c "
from ci.transparency.cwe.types.cwe import results as cwe_results
from ci.transparency.cwe.types.standards import results as std_results
from ci.transparency.cwe.types.base import collections, counts, messages

print('CWE Results:')
print(cwe_results.__all__)
print('\nStandards Results:')
print(std_results.__all__)
print('\nBase Collections:')
print(collections.__all__)
print('\nBase Counts:')
print(counts.__all__)
print('\nBase Messages:')
print(messages.__all__)
"
```

```text
CWE Results:
['CweLoadingResult', 'CweValidationResult', 'CweRelationshipResult', 'CweRelationshipDict', 'CweRelationshipLike', 'CweDataDict', 'CweItemDict', 'ValidationResultsDict', 'ValidationDetailsDict', 'SeverityCountsDict', 'ErrorSummaryDict', 'LoadingSummaryDict', 'ValidationSummaryDict', 'RelationshipStatisticsDict', 'RelationshipSummaryDict', 'RelationshipType', 'add_cwe', 'track_invalid_file', 'track_skipped_cwe_file', 'validate_cwe', 'validate_cwe_field', 'batch_validate_cwes', 'analyze_relationships', 'get_cwe_loading_summary', 'get_cwe_validation_summary', 'get_relationship_summary']

Standards Results:
['StandardsLoadingResult', 'StandardsValidationResult', 'StandardsMappingResult', 'StandardsMappingDict', 'StandardsControlDict', 'StandardsItemDict', 'StandardsDataDict', 'ValidationResultsDict', 'ValidationDetailsDict', 'SeverityCountsDict', 'MappingResultsDict', 'MappingTypesDict', 'ErrorSummaryDict', 'LoadingSummaryDict', 'ValidationSummaryDict', 'MappingSummaryDict', 'FrameworkCollection', 'add_standard', 'track_invalid_standards_file', 'track_skipped_standards_file', 'validate_standard', 'validate_standards_field', 'batch_validate_standards', 'analyze_mappings', 'add_mapping', 'get_standards_loading_summary', 'get_standards_validation_summary', 'get_mapping_summary']

Base Collections:
['FrameworkStatsDict', 'RelationshipMapDict', 'RelationshipDepthsDict', 'RelationshipTypesDict', 'CategoryCollection', 'DuplicateCollection', 'FileCollection', 'FrameworkCollection', 'ReferenceCollection']

Base Counts:
['LoadingCounts', 'ProcessingCounts', 'ValidationCounts']

Base Messages:
['MessageCollection']
(civic-transparency-py-cwe-types)
edaci@Neo MINGW64 ~/Documents/civic-interconnect/civic-transparency-ecosystem/civic-transparency-py-cwe-types (main)
```
