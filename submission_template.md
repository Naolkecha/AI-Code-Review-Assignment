# AI Code Review Assignment (Python)

## Candidate
- Name: Naol Kecha
- Approximate time spent: 1.5 hours

---

# Task 1 — Average Order Value

## 1) Code Review Findings
### Critical bugs
- Wrong denominator in calculation: The function divides by `len(orders)` (total count) instead of counting only non-cancelled orders. If you have 10 orders and 3 are cancelled, it divides by 10 instead of 7. This means the average will be wrong whenever there are cancelled orders. For a financial calculation like this, that's a serious problem - wrong averages lead to bad business decisions.

- Crashes on empty list: Pass an empty list and you get `ZeroDivisionError` immediately. Any code path with no orders (new customer, empty search results) will crash.

- Assumes perfect data: The code directly accesses `order["status"]` and `order["amount"]` without checking if those keys exist. Real-world data is messy - API responses have missing fields, database migrations leave gaps, upstream services send incomplete data. This function will crash on any of those scenarios.

### Edge cases & risks
- All cancelled orders results in division by zero
- Non-numeric amounts (like `None` or strings) will cause crashes
- Non-dictionary items in the list will raise `TypeError`
- Missing keys are not handled

### Code quality / design issues
- Missing docstring
- No input validation
- No error handling for malformed data

## 2) Proposed Fixes / Improvements
### Summary of changes

- Fixed the denominator bug: Added a `count` variable that only increments for valid, non-cancelled orders. Now the math is correct - we divide by the number of orders we actually summed.

- Added guard clause for empty lists: Returns 0 instead of crashing. I chose to return 0 rather than raise an exception because it's more defensive - calling code won't break. Could argue for raising `ValueError` to force explicit handling, but for a calculation function like this, returning a sensible default seems better. Documented this in the docstring.

- Used `.get()` for dictionary access: Instead of `order["status"]`, now using `order.get("status")`. Makes the function resilient to missing keys. I considered validating the entire order structure upfront, but that felt too rigid - this way we just skip bad records and process what we can.

- Wrapped float conversion in try-except: The `float(amount)` call now has error handling. Data validation might happen elsewhere in the system, so this function should be able to handle whatever gets thrown at it. Downside is that silently skipping bad data could hide quality issues - in production I'd add logging here to track how often this happens.

- Added docstring: Documents what goes in, what comes out, and how edge cases are handled.

- The overall approach is defensive programming - the function never crashes, always returns a number. For a calculation function that might be called from many places, this seems like the right tradeoff.

### Corrected code
See `correct_task1.py`

> Note: The original AI-generated code is preserved in `task1.py`.

### Testing Considerations
If you were to test this function, what areas or scenarios would you focus on, and why?

Calculation correctness (where the bug was):
- Mix of cancelled and non-cancelled orders - verify average excludes cancelled ones correctly
- Test case: `[{status: 'completed', amount: 100}, {status: 'cancelled', amount: 50}, {status: 'completed', amount: 200}]` should return 150, not 116.67

Edge cases:
- Empty list - should return 0 without crashing
- All cancelled orders - should return 0
- Single order - verify division by 1 works
- No cancelled orders - verify it still works when filter condition is never true

Error handling:
- Orders with missing "status" or "amount" keys - should skip gracefully
- Non-numeric amounts - should handle without crashing
- Non-dictionary items in the list - should skip them
- Decimal values - make sure float math works correctly

Additional testing:
- Property-based testing (hypothesis) to generate random order lists and verify invariants
- Test with real data from staging to catch unexpected patterns
- Wouldn't test extreme values (billions of orders) or concurrency - pure function, not a concern


## 3) Explanation Review & Rewrite
### AI-generated explanation (original)
> This function calculates average order value by summing the amounts of all non-cancelled orders and dividing by the number of orders. It correctly excludes cancelled orders from the calculation.

### Issues in original explanation
- Contradictory: Claims the function divides by "the number of orders" while also stating it "correctly excludes cancelled orders." The code divides by all orders, which is the bug.
- Overstates correctness: The phrase "correctly excludes" implies the implementation works as intended when it contains a critical mathematical error.
- Omits failure modes: Doesn't mention crashes on empty lists, missing keys, or other edge cases.
- Lacks detail: No discussion of limitations or error conditions.

### Rewritten explanation
This function calculates the average order value by iterating through orders, identifying those with non-cancelled status, summing their amounts, and dividing by the count of non-cancelled orders. It returns 0 for empty input or when no valid orders exist, and handles missing keys and invalid data types gracefully.

## 4) Final Judgment
- Decision: Request Changes
- Justification: There's a critical bug (wrong denominator) that produces incorrect results, and the function will crash on empty lists or malformed data. But the overall structure is fine - the developer understood the problem and got the algorithm right: loop through orders, check status, sum amounts. The bug is localized to one line and the fixes are straightforward. This feels like something that can be fixed with targeted changes rather than starting over. The summation logic works, the status checking works, the structure makes sense. Rejecting would mean throwing away code that's mostly correct. The fixes are surgical - change how we count and add some error handling. Tradeoffs: Returning 0 for edge cases instead of raising exceptions (more defensive but could hide data problems), added type checking and try-except blocks (adds overhead but correctness matters more), skipping invalid data silently (more forgiving but means bad data gets ignored - would add logging in production). Things I'm not sure about: What should happen for edge cases? Should we log when skipping invalid orders? Are there business rules about orders with amount = 0?
- Confidence & unknowns: High confidence the bug is clear and fix is well-defined. Core algorithm is salvageable.

---

# Task 2 — Count Valid Emails

## 1) Code Review Findings
### Critical bugs
- Insufficient validation: Just checking if "@" exists in the string? This accepts "@", "@@", "@domain", "user@", "user@@domain@extra" - basically anything with an @ character. That's not email validation, that's substring matching. In production this would let garbage into the database, leading to failed deliveries and bounced emails.

- No type safety: If the list contains None, numbers, or any non-string, the `in` operator will raise `TypeError` and crash.

- Missing domain validation: Even being lenient, emails need a domain with a dot and TLD. "user@domain" isn't a valid internet email address.

### Edge cases & risks
- Empty list works by accident (returns 0) rather than by design
- Emails with spaces like "user name@domain" are counted as valid
- Whitespace-padded emails like "  user@domain.com  " may not be handled properly
- Multiple @ symbols are accepted
- "@domain.com" (no local part) and "user@" (no domain) both pass validation
- A single "@" character passes validation

### Code quality / design issues
- Missing docstring
- Function name implies robust validation but implementation is minimal
- Should use regex or a validation library instead of substring checking
- Would allow invalid emails into production databases

## 2) Proposed Fixes / Improvements
### Summary of changes

- Rewrote validation with regex: Email validation is a solved problem - regex is the standard approach. The pattern I used (`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`) checks for: local part, @ symbol, domain, dot, and TLD. It's not RFC 5322 compliant (full email spec is insanely complex), but it's a practical compromise - strict enough to catch obvious garbage, lenient enough to accept real emails.

- Added type checking: Check `isinstance(email, str)` before validation so non-strings get skipped instead of crashing.

- Strip whitespace: User input often has accidental spaces. "  user@example.com  " should be valid. Small UX improvement.

- Added docstring and imported `re`: Documents what the function does and brings in the regex module.

I considered using a library like `email-validator` which would be more robust and handle internationalized domains, but that adds an external dependency. Could also do simpler checks (just verify "something@something.something" format) but that's barely better than the original. The regex approach seems like the right balance.

### Corrected code
See `correct_task2.py`

> Note: The original AI-generated code is preserved in `task2.py`. 


### Testing Considerations
If you were to test this function, what areas or scenarios would you focus on, and why?

Valid formats (should accept):
- Standard emails: "user@example.com", "first.last@company.co.uk"
- Special characters: "user+tag@example.com", "user_name@example.com"
- Subdomains: "user@mail.example.com"
- Whitespace handling: "  user@example.com  " should work after stripping

Invalid formats (should reject):
- No @ symbol: "notanemail", "user.example.com"
- Malformed: "@", "user@", "@domain.com", "user@@domain.com"
- Missing TLD: "user@domain"
- Incomplete domain: "user@domain."
- Multiple @ symbols: "user@domain@extra.com"
- Spaces in middle: "user name@domain.com"

Edge cases:
- None/numbers/lists in input - should skip gracefully
- Empty list - return 0
- All invalid emails - return 0
- Mixed valid/invalid - count only valid ones

Known limitations:
- Won't catch all edge cases (e.g., "user@domain.c" with 1-char TLD)
- Doesn't verify domain actually exists (would need DNS lookup)
- Doesn't support full RFC 5322 or internationalized domains
- False positives (accepting invalid) are worse than false negatives for this use case

## 3) Explanation Review & Rewrite
### AI-generated explanation (original)
> This function counts the number of valid email addresses in the input list. It safely ignores invalid entries and handles empty input correctly.

### Issues in original explanation
- Misleading: Claims to "safely ignore invalid entries" when it accepts nearly anything containing "@"
- Overstates robustness: Describes the validation as robust when it only performs a minimal substring check
- Incidental correctness: States it "handles empty input correctly" but this works by accident, not by design
- Lacks specificity: Doesn't explain what constitutes a "valid" email in this implementation
- Overly confident: Implies production-readiness when the implementation would accept many invalid emails

### Rewritten explanation
This function counts valid email addresses in a list by checking each entry against a regex pattern that validates the presence of a local part, "@" symbol, domain name, dot separator, and top-level domain. It handles non-string inputs gracefully by skipping them and strips whitespace before validation.

## 4) Final Judgment
- Decision: Reject
- Justification: The validation approach is fundamentally wrong. Checking for "@" is not email validation - it's substring matching. You can't fix this by adding more conditions to the substring check. The developer would need to start over with regex or a validation library. Email validation is a solved problem, and the solution isn't building your own string-checking logic. The entire approach needs to be replaced - trying to patch this with more `if` statements would create unmaintainable code. Tradeoffs in corrected version: Chose regex over library (more complex but avoids dependencies), regex is practical not RFC 5322 compliant (catches 99% of real emails while rejecting garbage), pattern errs on rejecting when in doubt. Things I'm not sure about: acceptable false positive/negative rate, do we need internationalized domain names (current regex only handles ASCII), should we verify domain exists via DNS lookup (currently just checking format)?
- Confidence & unknowns: High confidence in rejection. Email validation is well-understood and the original approach is fundamentally wrong.

---

# Task 3 — Aggregate Valid Measurements

## 1) Code Review Findings
### Critical bugs
- Wrong denominator: Same issue as Task 1. Divides by total count (including None) instead of counting only valid measurements. For `[10, None, 20, None, 30]`, it divides by 5 instead of 3. The math is wrong - if this is used for sensor data or analytics, decisions based on these averages would be flawed.

- Crashes on empty input: Empty list causes `ZeroDivisionError`.

- Unhandled type conversion: The `float(v)` call has no error handling. Real sensor data might have error codes like "N/A" or "ERROR" - this would crash on any of those.

### Edge cases & risks
- All None values results in division by zero
- Non-numeric strings like "N/A" or "error" cause crashes
- Invalid types (lists, dicts, objects) fail during `float()` conversion
- Empty list causes crash
- List of all invalid values causes crash

### Code quality / design issues
- Missing docstring
- Inconsistent error handling: checks for None but not other invalid types
- No try-except around type conversion
- Edge case behavior is undefined

## 2) Proposed Fixes / Improvements
### Summary of changes

- Fixed the denominator: Count variable now increments only after successful float conversion. Same fix as Task 1 - divide by the count of values we actually summed.

- Added early return for empty lists: Returns 0 instead of crashing. Consistent with how I handled Task 1.

- Wrapped `float()` in try-except: Real data has errors - sensor readings might be "ERROR", "N/A", or other placeholders. Catches `ValueError` (non-numeric strings) and `TypeError` (wrong types). Silently skips invalid values, though in production I'd add logging here to track data quality.

- Returns 0 when no valid measurements exist: Consistent with empty list behavior. Could return `None` to distinguish "no data" from "average is zero", but 0 is simpler for callers.

- Added docstring: Documents what goes in and out. Preserves the original intent (skip None values) while fixing the bugs.

The approach is forgiving with input (skip bad data) but correct in calculation. For data processing, you usually want to work with whatever valid data exists rather than failing on the first error.

### Corrected code
See `correct_task3.py`

> Note: The original AI-generated code is preserved in `task3.py`.

### Testing Considerations
If you were to test this function, what areas or scenarios would you focus on, and why?

Calculation correctness (the bug):
- `[10, None, 20, None, 30]` should return 20.0, not 12.0 - directly tests the denominator fix
- `[10, 20, 30]` all valid numbers - make sure None-skipping doesn't break normal case
- `[None, None, 42, None]` single valid value - edge case

Edge cases:
- Empty list - return 0
- All None values - return 0
- All invalid values like `["N/A", "error", []]` - return 0

Type handling:
- Mixed ints and floats: `[10, 20.5, 30]`
- Numeric strings: `["10", "20", "30"]` should convert correctly
- Precision with decimals - verify float arithmetic

Error resilience:
- Non-numeric strings mixed with valid numbers
- Invalid types like lists/dicts
- Combinations of everything

Additional testing:
- Property-based testing (hypothesis) to verify invariants: result between min/max of valid values, never crashes
- Wouldn't test extreme values (Python handles fine), performance (not a bottleneck), or concurrency (pure function)

## 3) Explanation Review & Rewrite
### AI-generated explanation (original)
> This function calculates the average of valid measurements by ignoring missing values (None) and averaging the remaining values. It safely handles mixed input types and ensures an accurate average

### Issues in original explanation
- Incorrect math: Claims to average "the remaining values" but divides by all values (including None), producing wrong results.
- False claim: States it "safely handles mixed input types" when it crashes on non-numeric strings.
- Overstates accuracy: Claims to "ensure an accurate average" despite the denominator bug.
- Omits failure modes: Doesn't mention crashes on empty lists, all-None inputs, or invalid types.
- Misleading: Implies robust error handling that doesn't exist.

### Rewritten explanation
This function calculates the average of valid measurements by iterating through a list, skipping None values, attempting to convert each value to float, summing successfully converted values, and dividing by the count of valid measurements. It returns 0 for empty input or when no valid measurements exist, and handles non-numeric values by skipping them.

## 4) Final Judgment
- Decision: Request Changes
- Justification: Same denominator bug as Task 1, and missing error handling for type conversion. But the structure is fine - the developer understood the requirement to skip None, and the summation logic works. Fixes are straightforward: count properly and add try-except. Targeted changes, not a rewrite. The None-checking works, the algorithm makes sense, the bug is localized. Rejecting would throw away code that's mostly correct. Tradeoffs: Skipping invalid values silently (forgiving but could hide data quality issues), returning 0 for no valid data (simple but loses information), accepting numeric strings (user-friendly but could mask issues). Things I'm not sure about: Should we distinguish between "no data" and "no valid data"? Should we log skipped values? Is 0 a valid measurement? Should numeric strings be accepted or rejected?
- Confidence & unknowns: High confidence the bug is clear and fix is well-defined. Core algorithm is salvageable.
